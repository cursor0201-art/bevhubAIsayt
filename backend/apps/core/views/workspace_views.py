import time

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction, OperationalError
from core.domain.models import Workspace, AITask, ProjectFile, Project, Page
from core.serializers.project_serializers import (
    WorkspaceSerializer,
    AITaskSerializer,
    ProjectFileSerializer,
    ProjectDetailSerializer,
    GenerationStepSerializer
)
from core.tasks import dispatch_background_task, run_ai_orchestrator_task

class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    Manages Workspace sandboxes. Enforces Tenant-level data isolation.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.tenant:
            return Workspace.objects.none()
        return Workspace.objects.filter(tenant=user.tenant)

    def perform_create(self, serializer):
        user = self.request.user
        with transaction.atomic():
            if not user.tenant:
                # Auto-provision tenant in sandbox environment if needed
                from core.domain.models import Tenant
                tenant = Tenant.objects.create(company_name=f"{user.username}'s Workspace")
                user.tenant = tenant
                user.save(update_fields=['tenant'])
            workspace = serializer.save(tenant=user.tenant)

            # Log workspace creation telemetry
            from core.domain.models import UserJourneyEvent
            UserJourneyEvent.objects.create(
                user=user,
                step='workspace_created',
                status='success',
                workspace_id=str(workspace.id)
            )


class AITaskViewSet(viewsets.ModelViewSet):
    """
    Handles AI Chat execution requests and polling.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AITaskSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.tenant:
            return AITask.objects.none()
        return AITask.objects.filter(workspace__tenant=user.tenant)

    def _create_task_with_retry(self, user, workspace_id, project_id, prompt) -> AITask:
        """
        Creates the AITask inside an atomic transaction, retrying transient
        SQLite write-lock collisions ("database is locked") instead of failing
        the user's generation request.
        """
        last_error = None
        for attempt in range(1, 4):
            try:
                with transaction.atomic():
                    # Retrieve/verify workspace
                    try:
                        workspace = Workspace.objects.get(id=workspace_id, tenant=user.tenant)
                    except Exception:
                        # If no workspace specified, fetch or create a default one
                        workspace = Workspace.objects.filter(tenant=user.tenant).first()
                        if not workspace:
                            workspace = Workspace.objects.create(tenant=user.tenant, name="Default Sandbox")

                    # Create AITask record
                    task = AITask.objects.create(
                        workspace=workspace,
                        prompt=prompt,
                        status='queued',
                        progress=0
                    )

                    if project_id:
                        try:
                            project = Project.objects.get(id=project_id, tenant=user.tenant)
                            task.project = project
                            task.save(update_fields=['project'])
                        except Project.DoesNotExist:
                            pass

                    # Dispatch after commit — returns immediately, HTTP 201 goes back to client.
                    # Uses the resilient dispatcher: Celery when enabled, otherwise an
                    # in-process background thread so the task never sits unclaimed.
                    transaction.on_commit(
                        lambda task_id=str(task.id), uid=user.id: dispatch_background_task(
                            run_ai_orchestrator_task, task_id, uid
                        )
                    )

                return task
            except OperationalError as e:
                last_error = e
                time.sleep(0.5 * attempt)

        raise last_error

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            workspace_id = request.data.get('workspace_id')
            project_id = request.data.get('project_id')
            prompt = request.data.get('prompt', '')

            if not prompt or not str(prompt).strip():
                return Response({"error": "prompt field is required"}, status=status.HTTP_400_BAD_REQUEST)

            task = self._create_task_with_retry(user, workspace_id, project_id, str(prompt).strip())

            from core.serializers.project_serializers import AITaskSerializer
            return Response(AITaskSerializer(task).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write("ERROR IN CREATE:\n" + traceback.format_exc() + '\n\n')
            raise e

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='stream')
    def stream(self, request, pk=None):
        task = self.get_object()
        
        def event_stream():
            import redis
            import json
            from django.conf import settings
            r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
            pubsub = r.pubsub()
            channel_name = f"task_{task.id}_events"
            pubsub.subscribe(channel_name)
            
            # Send initial state
            initial_data = {
                "task_id": str(task.id),
                "type": "initial",
                "prompt": task.prompt,
                "status": task.status,
                "progress": task.progress,
                "logs": task.logs,
            }
            yield f"data: {json.dumps(initial_data)}\n\n"
            
            # Listen to updates
            try:
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        data = message['data'].decode('utf-8')
                        yield f"data: {data}\n\n"
                        try:
                            payload = json.loads(data)
                            if payload.get("status") in ["completed", "failed"]:
                                break
                        except Exception:
                            pass
            except Exception:
                pass
            finally:
                pubsub.unsubscribe(channel_name)
                pubsub.close()
                
        from django.http import StreamingHttpResponse
        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='progress')
    def progress(self, request, pk=None):
        task = self.get_object()

        # Watchdog: if a queued task was never claimed (e.g. no worker running),
        # fail it explicitly so clients stop polling forever instead of sitting
        # at 0% indefinitely.
        if task.status == 'queued':
            from django.utils import timezone as _tz
            queued_age = (_tz.now() - task.created_at).total_seconds()
            if queued_age > 60:
                task.status = 'failed'
                task.logs = (
                    (task.logs or "")
                    + "\n[Watchdog] Task was not picked up within 60 seconds "
                      "(background worker unavailable). Please retry generation."
                ).strip()
                task.save(update_fields=['status', 'logs'])

        steps = task.steps.all()
        
        # Calculate current stage
        active_step = steps.filter(status='RUNNING').first()
        current_stage = active_step.step_name if active_step else (steps.last().step_name if steps.exists() else "Initializing")
        
        # Calculate used model
        active_model = active_step.model_name if active_step else (steps.last().model_name if steps.exists() else "gpt-4o")
        
        # Calculate accumulated cost
        from django.db.models import Sum
        total_cost = steps.aggregate(total=Sum('cost'))['total'] or 0.0
        
        # Calculate estimated remaining time
        import django.utils.timezone as tz
        elapsed = (tz.now() - task.created_at).total_seconds()
        estimated_total = 90.0
        remaining_time = max(0.0, estimated_total - elapsed)
        if task.status in ['completed', 'failed']:
            remaining_time = 0.0

        # Get last log
        log_lines = [line.strip() for line in (task.logs or "").split("\n") if line.strip()]
        last_log = log_lines[-1] if log_lines else "Queueing task..."

        return Response({
            "task_id": str(task.id),
            "status": task.status,
            "progress_percent": task.progress,
            "current_stage": current_stage,
            "active_model": active_model,
            "total_cost": float(total_cost),
            "estimated_remaining_seconds": round(remaining_time, 1),
            "last_log": last_log,
            "steps": GenerationStepSerializer(steps, many=True).data
        })


class ProjectFileViewSet(viewsets.ModelViewSet):
    """
    Exposes direct CRUD edits over code files inside a Project for auto-saving.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectFileSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.tenant:
            return ProjectFile.objects.none()
        return ProjectFile.objects.filter(project__tenant=user.tenant)

    def perform_create(self, serializer):
        project_id = self.request.data.get('project_id')
        project = Project.objects.get(id=project_id, tenant=self.request.user.tenant)
        
        # If writing to src/pages/index.html, automatically sync with Page raw_content
        path = serializer.validated_data.get('path')
        content = serializer.validated_data.get('content', '')
        
        with transaction.atomic():
            file_obj = serializer.save(project=project)
            
            if path.startswith("src/pages/"):
                slug = path.split("/")[-1].replace(".html", "")
                Page.objects.update_or_create(
                    project=project,
                    slug=slug,
                    defaults={"title": slug.capitalize(), "raw_content": content}
                )

    def perform_update(self, serializer):
        with transaction.atomic():
            file_obj = serializer.save()
            
            # Sync with Page raw_content if it's a page file
            if file_obj.path.startswith("src/pages/"):
                slug = file_obj.path.split("/")[-1].replace(".html", "")
                Page.objects.update_or_create(
                    project=file_obj.project,
                    slug=slug,
                    defaults={"title": slug.capitalize(), "raw_content": file_obj.content}
                )


from rest_framework.views import APIView
from core.domain.models import IntegrationConfig, Deployment, UserJourneyEvent
from core.serializers.project_serializers import DeploymentSerializer

class IntegrationViewSet(viewsets.ViewSet):
    """
    Manages tenant-isolated third-party integrations (GitHub, Vercel, Stripe, OpenAI, Telegram).
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response([])

        providers = ['github', 'vercel', 'stripe', 'openai', 'telegram']
        existing = {ic.provider: ic for ic in IntegrationConfig.objects.filter(tenant=tenant)}

        result = []
        for p in providers:
            ic = existing.get(p)
            result.append({
                "provider": p,
                "is_connected": ic.is_connected if ic else False,
                "updated_at": ic.updated_at.isoformat() if ic else None
            })
        return Response(result)

    @action(detail=False, methods=['post'], url_path='(?P<provider>[^/.]+)/connect')
    def connect(self, request, provider=None):
        tenant = request.user.tenant
        if not tenant:
            return Response({"error": "No active tenant"}, status=status.HTTP_400_BAD_REQUEST)

        config_data = request.data.get('config', {})
        ic, _ = IntegrationConfig.objects.get_or_create(tenant=tenant, provider=provider)
        ic.is_connected = True
        ic.config = config_data
        ic.save()

        # Log journey event
        UserJourneyEvent.objects.create(
            user=request.user,
            step='integration_connected',
            status='success',
            logs=f"Connected provider: {provider}"
        )

        return Response({"message": f"{provider.capitalize()} connected successfully!", "is_connected": True})

    @action(detail=False, methods=['post'], url_path='(?P<provider>[^/.]+)/disconnect')
    def disconnect(self, request, provider=None):
        tenant = request.user.tenant
        if not tenant:
            return Response({"error": "No active tenant"}, status=status.HTTP_400_BAD_REQUEST)

        ic = IntegrationConfig.objects.filter(tenant=tenant, provider=provider).first()
        if ic:
            ic.is_connected = False
            ic.config = {}
            ic.save()

        # Log journey event
        UserJourneyEvent.objects.create(
            user=request.user,
            step='integration_disconnected',
            status='success',
            logs=f"Disconnected provider: {provider}"
        )

        return Response({"message": f"{provider.capitalize()} disconnected successfully!", "is_connected": False})


class DeploymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes list and detailed inspection over Deployment build metrics.
    Enforces tenant isolation.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DeploymentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.tenant:
            return Deployment.objects.none()
        return Deployment.objects.filter(project__tenant=user.tenant).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='redeploy')
    def redeploy(self, request, pk=None):
        deployment = self.get_object()
        project = deployment.project

        # Execute project deployment pipeline
        from core.views.project_views import ProjectViewSet
        pv = ProjectViewSet()
        pv.request = request
        return pv.deploy_project(request, pk=project.id)


class TemplateListView(APIView):
    """
    Exposes curated starter templates across 9 categories.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = [
            {
                "id": "saas-starter",
                "name": "SaaS Platform Pro",
                "category": "SaaS",
                "description": "Full-stack SaaS application with dark mode UI, auth modals, pricing table, and analytics metrics.",
                "prompt": "Build a modern dark-themed SaaS landing page and dashboard for an AI code assistant. Include header with gradient logo, dynamic features grid, interactive pricing calculator with Monthly/Yearly toggle, client testimonials, and a live dark preview."
            },
            {
                "id": "ecom-marketplace",
                "name": "E-Commerce Storefront",
                "category": "E-commerce",
                "description": "High-converting online store with product filtering, dynamic cart drawer, checkout flow, and hero banner.",
                "prompt": "Create a modern luxury e-commerce storefront for premium headphones. Include responsive navbar with cart count, video hero banner, product grid with hover zoom, add-to-cart interactive state, and instant checkout drawer."
            },
            {
                "id": "landing-agency",
                "name": "Digital Agency Landing",
                "category": "Landing",
                "description": "Ultra-sleek landing page with high-impact typography, project showcase, interactive contact form, and smooth animations.",
                "prompt": "Design a high-converting digital agency landing page with bold typography, dark glassmorphism card layouts, interactive portfolio grid, team statistics counter, and a lead capture booking form."
            },
            {
                "id": "portfolio-dev",
                "name": "Developer Portfolio",
                "category": "Portfolio",
                "description": "Minimalist developer portfolio with live project previews, tech stack badges, terminal widget, and contact modal.",
                "prompt": "Build a clean developer portfolio with a terminal welcome widget, interactive experience timeline, pinned GitHub projects with star counts, and a direct message contact form."
            },
            {
                "id": "agency-growth",
                "name": "Growth Agency Portal",
                "category": "Agency",
                "description": "B2B growth agency site with client logos marquee, case studies grid, revenue ROI calculator, and lead capture.",
                "prompt": "Create a B2B marketing agency website with client logo ticker, interactive ROI calculator, video case studies, and a multi-step consultation booking modal."
            },
            {
                "id": "tech-blog",
                "name": "Tech & AI Blog",
                "category": "Blog",
                "description": "Clean reading experience with article search, tag filters, newsletter subscription widget, and dark aesthetic.",
                "prompt": "Design a modern tech blog with featured post hero, category pill filters, reading time indicators, inline code highlighting, and newsletter signup box."
            },
            {
                "id": "admin-dashboard",
                "name": "Executive Dashboard",
                "category": "Dashboard",
                "description": "Data-rich analytics workspace with financial charts, activity stream, project tables, and export controls.",
                "prompt": "Build an executive analytics dashboard with live KPI metric cards, line charts for revenue trends, recent orders table with status badges, and quick action buttons."
            },
            {
                "id": "gourmet-restaurant",
                "name": "Gourmet Bistro & Bar",
                "category": "Restaurant",
                "description": "Sophisticated dining experience featuring visual menu, table reservation modal, image gallery, and location map.",
                "prompt": "Create an elegant restaurant website with full-bleed hero video, interactive food and wine menu tabs, online table reservation modal, and chef specials carousel."
            },
            {
                "id": "startup-launch",
                "name": "AI Startup Launch",
                "category": "Startup",
                "description": "Waitlist landing page with product screenshot preview, feature walkthrough tabs, and early access signup form.",
                "prompt": "Design an AI startup waitlist page with glowing hero section, animated waitlist counter, feature breakdown cards, and instant email access form."
            }
        ]
        return Response(templates)


class UserJourneyHistoryView(APIView):
    """
    Exposes audit log events for the user's organization with search and category filters.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.tenant:
            return Response([])

        queryset = UserJourneyEvent.objects.filter(user__tenant=user.tenant).order_by('-created_at')

        # Filter by search
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(step__icontains=search) | 
                Q(logs__icontains=search) | 
                Q(error_message__icontains=search)
            )

        # Filter by step/status
        status_filter = request.query_params.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)

        events = queryset[:100]
        data = [{
            "id": str(e.id),
            "timestamp": e.created_at.isoformat(),
            "event": e.step,
            "status": e.status,
            "details": e.logs or e.error_message or "",
            "workspace_id": e.workspace_id or "default-sandbox",
            "user": e.user.username if e.user else "System"
        } for e in events]

        return Response(data)

