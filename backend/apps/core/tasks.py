import logging
import threading
from celery import shared_task
from django.db import transaction
from core.domain.models import Project, User, Page

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────
# Guarantees that background work actually runs:
#   1. If BEVHUB_USE_CELERY=True → dispatch through the Celery broker.
#   2. Otherwise (local dev default) → execute in a daemon thread inside the
#      Django process so generation never gets stuck at 0% waiting for a
#      worker process that is not running.
#   3. If Celery dispatch itself fails (broker down, transport error such as
#      the historical pywintypes crash) → automatically fall back to thread
#      execution instead of losing the task silently.

def _run_in_background_thread(fn, *args):
    """
    Run `fn(*args)` in a non-daemon thread so gunicorn doesn't kill it
    before it finishes. The thread closes the inherited DB connection
    immediately so Django opens a fresh one when it first hits the DB.
    """
    # Capture args in the closure — do NOT pass them via Thread(args=...) or
    # _runner() would receive them as positional arguments and raise TypeError.
    captured_args = args

    def _runner():
        from django.db import connection
        connection.close()          # drop inherited request-thread connection
        try:
            logger.info("[Dispatcher] Background thread starting: %s %s", fn.__name__, captured_args[:1])
            fn(*captured_args)
            logger.info("[Dispatcher] Background thread finished: %s", fn.__name__)
        except Exception:
            logger.exception("[Dispatcher] Background thread execution FAILED for %s", fn.__name__)
        finally:
            connection.close()      # return connection to pool cleanly

    # daemon=False — keeps the process alive until the task finishes.
    # This is critical on gunicorn: daemon threads are killed when the
    # request-handling thread exits, which would abort generation mid-run.
    thread = threading.Thread(target=_runner, daemon=False, name="bevhub-bg-task")
    thread.start()
    logger.info("[Dispatcher] Background thread started (id=%s)", thread.ident)
    return thread


def dispatch_background_task(celery_task, *args):
    """
    Dispatch a task via Celery when enabled; otherwise run it in a background
    thread. Never raises — dispatch failures degrade gracefully to thread execution.
    """
    from django.conf import settings

    if getattr(settings, "BEVHUB_USE_CELERY", False):
        try:
            celery_task.delay(*args)
            logger.info("[Dispatcher] Task %s queued via Celery broker", celery_task.name)
            return
        except Exception as exc:
            logger.error(
                "[Dispatcher] Celery dispatch failed for %s (%s). "
                "Falling back to in-process background thread.",
                celery_task.name, exc,
            )

    logger.info("[Dispatcher] Dispatching %s via background thread (args=%s)", celery_task.name, args[:1])
    _run_in_background_thread(celery_task.run, *args)


# ─────────────────────────────────────────────────────────────────────────────
# PROJECT GENERATION WORKFLOW TASK
# ─────────────────────────────────────────────────────────────────────────────

def _execute_generation_workflow(project_id: str, user_id: int, user_prompt: str):
    """
    Plain-function body of the multi-agent WorkflowEngine pipeline.
    Shared by the Celery task and the local thread fallback.
    """
    logger.info(f"[Celery] Beginning background AI agent generation task for Project: {project_id}")

    try:
        project = Project.objects.get(id=project_id)
        user = User.objects.get(id=user_id)
    except Exception as e:
        logger.error(f"[Celery] Failed to find project or user records in database: {e}")
        return {"status": "error", "message": str(e)}

    try:
        from ai.services.workflow_engine import WorkflowEngine
        workflow = WorkflowEngine()
        workflow_results = workflow.execute_business_generation_workflow(project, user, user_prompt)
    except Exception as e:
        logger.error(f"[Celery] WorkflowEngine execution crashed in background task: {e}")
        # Fallback: update deployment to failed
        deployment = project.deployments.order_by('-created_at').first()
        if deployment:
            deployment.status = 'failed'
            deployment.save(update_fields=['status'])
        return {"status": "error", "message": f"WorkflowEngine failed: {e}"}

    # Step 3: Update database records with agent outputs
    with transaction.atomic():
        if "design_system" in workflow_results:
            project.design_system = workflow_results["design_system"]
            project.save(update_fields=["design_system"])

        # Update index page content with copywriting agent outputs
        copy_text = workflow_results.get("copy", "")
        if copy_text:
            try:
                index_page = project.pages.get(slug="index")
                colors = project.design_system.get("colors", ["#8b5cf6"])
                primary_color = colors[0] if colors else "#8b5cf6"

                # Format layout content with the generated style palette and text copy
                index_page.raw_content = (
                    f"<div style='font-family: sans-serif; padding: 40px; color: #fff; background-color: #000; min-height: 100vh;'>"
                    f"  <header style='margin-bottom: 40px; border-bottom: 1px solid #222; padding-bottom: 20px;'>"
                    f"    <h1 style='color: {primary_color}; font-size: 2.5em; margin: 0;'>{project.project_name}</h1>"
                    f"  </header>"
                    f"  <main style='max-width: 800px;'>"
                    f"    <p style='font-size: 1.25em; line-height: 1.6; color: #e4e4e7;'>{copy_text}</p>"
                    f"  </main>"
                    f"  <footer style='margin-top: 60px; border-top: 1px solid #222; padding-top: 20px; color: #52525b; font-size: 0.85em;'>"
                    f"    <p>&copy; {project.project_name}. Powered by BevHub AI Multi-Agent OS.</p>"
                    f"  </footer>"
                    f"</div>"
                )
                index_page.save(update_fields=["raw_content"])
            except Page.DoesNotExist:
                pass

        # Complete and activate deployment log
        deployment = project.deployments.order_by('-created_at').first()
        if deployment:
            deployment.status = 'success'
            deployment.deploy_url = f"https://{project.subdomain}.bevhub.ai"
            deployment.save(update_fields=['status', 'deploy_url'])

    logger.info(f"[Celery] Background AI agent generation finished for Project: {project_id}")
    return {"status": "success", "project_id": project_id}


@shared_task(name="core.tasks.run_project_generation_workflow_task")
def run_project_generation_workflow_task(project_id: str, user_id: int, user_prompt: str):
    """
    Background Celery task that executes the WorkflowEngine multi-agent pipeline
    to configure theme styles, copywriting copy, and SEO meta elements.
    """
    return _execute_generation_workflow(project_id, user_id, user_prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AI ORCHESTRATOR TASK
# ─────────────────────────────────────────────────────────────────────────────

def _execute_ai_orchestrator(task_id: str, user_id: int):
    """
    Plain-function body of the 10-agent orchestration sequence.
    Uses an atomic status claim so the same task can never be executed twice
    (e.g. Celery worker + thread fallback racing on each other).
    """
    from core.domain.models import AITask, User
    from ai.services.orchestrator import AIOrchestrator

    # Atomic claim: only the first runner transitions queued -> running.
    claimed = AITask.objects.filter(id=task_id, status='queued').update(status='running')
    if claimed == 0:
        logger.warning(
            "[Celery Orchestrator] Task %s was already claimed by another runner. Skipping.",
            task_id,
        )
        return {"status": "skipped", "task_id": task_id}

    try:
        task = AITask.objects.get(id=task_id)
        user = User.objects.get(id=user_id)
    except Exception as e:
        logger.error(f"[Celery Orchestrator] Task or User lookup failed: {e}")
        return {"status": "error", "message": str(e)}

    try:
        orchestrator = AIOrchestrator(task)
        orchestrator.execute(user)
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        logger.exception(f"[Celery Orchestrator] Execution failed: {e}")
        # Safety net: guarantee the task never hangs in a non-terminal state.
        task.refresh_from_db()
        if task.status not in ('completed', 'failed'):
            task.status = 'failed'
            task.save(update_fields=['status'])
        return {"status": "error", "message": str(e)}


@shared_task(name="core.tasks.run_ai_orchestrator_task")
def run_ai_orchestrator_task(task_id: str, user_id: int):
    """
    Background Celery task that executes the complete 10-agent AI Orchestration sequence.
    """
    return _execute_ai_orchestrator(task_id, user_id)