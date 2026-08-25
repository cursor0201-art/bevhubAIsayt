from uuid import uuid4
from django.db import transaction
from core.domain.models import Tenant, Project, Page, Asset, Deployment
from core.domain.events import EventDispatcher, ProjectCreatedEvent
from core.services.ai_router import AIRouterService

class GenerationService:
    """
    Main application orchestrator coordinating project planning, code output generation,
    database writing, and event triggers.
    """
    def __init__(self):
        self.ai_router = AIRouterService()

    def generate_business_infrastructure(self, tenant: Tenant, user_prompt: str, user=None) -> Project:
        """
        Parses intent, creates project records, sets up default empty page entities,
        and fires off domain events.
        """
        # Step 1: Decompose Prompt Intent
        blueprint = self.ai_router.parse_intent(user_prompt)

        if not user:
            user = tenant.users.first()

        # Step 2: Atomic DB writes
        with transaction.atomic():
            # Create Project
            project = Project.objects.create(
                tenant=tenant,
                project_name=blueprint.business_name,
                subdomain=f"{uuid4().hex[:8]}-{blueprint.business_name.lower().replace(' ', '-')}",
                design_system={
                    "colors": blueprint.theme_colors,
                    "typography": {
                        "heading": "Outfit",
                        "body": "Inter"
                    },
                    "tone": blueprint.copywriting_tone
                }
            )

            # Trigger multi-agent generation pipeline in the background
            if user:
                try:
                    from core.tasks import dispatch_background_task, run_project_generation_workflow_task
                    transaction.on_commit(
                        lambda pid=str(project.id), uid=user.id, up=user_prompt: dispatch_background_task(
                            run_project_generation_workflow_task, pid, uid, up
                        )
                    )
                except Exception as e:
                    print(f"[GenerationService] Failed to queue background agent generation task: {e}")


            # Generate Pages metadata
            copy_text = f"Welcome to {project.project_name}. Design and assets are currently under generation."
            for slug in blueprint.pages_to_generate:
                title = slug.capitalize() if slug != 'index' else 'Home'
                colors = project.design_system.get("colors", ["#8b5cf6"])
                primary_color = colors[0] if colors else "#8b5cf6"
                page_html = (
                    f"<div style='font-family: sans-serif; padding: 20px; color: #fff;'>"
                    f"  <h1 style='color: {primary_color};'>{title} - {project.project_name}</h1>"
                    f"  <p style='color: #a3a3a3; font-style: italic;'>Tone: {blueprint.copywriting_tone}</p>"
                    f"  <div style='margin-top: 20px;'>"
                    f"    {copy_text if slug == 'index' else f'<p>Welcome to our {title} page.</p>'}"
                    f"  </div>"
                    f"</div>"
                )
                Page.objects.create(
                    project=project,
                    slug=slug,
                    title=title,
                    layout_ast={},
                    raw_content=page_html
                )

            # Create deployments log
            deployment = Deployment.objects.create(
                project=project,
                status='queued'
            )

        # Step 3: Dispatch Domain Event
        event = ProjectCreatedEvent(
            event_id=uuid4(),
            project_id=project.id,
            tenant_id=tenant.id,
            project_name=project.project_name
        )
        EventDispatcher.dispatch(event)

        # Step 4: Celery triggers for async assets generation would happen here:
        # from core.tasks import build_business_assets_task
        # build_business_assets_task.delay(project.id, blueprint.model_dump())

        return project

