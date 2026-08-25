import json
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.domain.models import Project, Tenant, Workspace, Page, Deployment, ProjectFile, ProjectReview
from core.serializers.project_serializers import (
    ProjectCreateRequestSerializer,
    ProjectDetailSerializer,
    ProjectReviewSerializer,
    ProjectFixRunSerializer
)
from core.services.generation_service import GenerationService

class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing generated projects. 
    Enforces Tenant & Workspace isolation.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.tenant:
            return Project.objects.none()
        
        queryset = Project.objects.filter(tenant=user.tenant)
        
        # Workspace scoping
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
            
        # Archiving filter
        include_archived = self.request.query_params.get('include_archived') == 'true'
        if not include_archived:
            queryset = queryset.exclude(status='archived')
            
        return queryset

    @extend_schema(
        request=ProjectCreateRequestSerializer,
        responses={201: ProjectDetailSerializer},
        description="Submit a prompt to plan, design, and trigger building a full online business."
    )
    @action(detail=False, methods=['post'], url_path='generate')
    def generate_project(self, request):
        serializer = ProjectCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        # Auto-provision tenant if missing for sandbox testing environment
        if not user.tenant:
            tenant = Tenant.objects.create(company_name=f"{user.username}'s Workspace")
            user.tenant = tenant
            user.save(update_fields=['tenant'])

        workspace_id = request.data.get('workspace_id')
        workspace_id_str = str(workspace_id) if workspace_id else None

        from core.domain.models import UserJourneyEvent
        # Log prompt_entered and generation_started telemetry
        UserJourneyEvent.objects.create(
            user=user,
            step='prompt_entered',
            status='success',
            logs=serializer.validated_data['prompt'],
            workspace_id=workspace_id_str
        )
        UserJourneyEvent.objects.create(
            user=user,
            step='generation_started',
            status='success',
            workspace_id=workspace_id_str
        )

        try:
            from core.domain.models import AITask
            from apps.ai.services.orchestrator import AIOrchestrator

            task = AITask.objects.create(
                prompt=serializer.validated_data['prompt'],
                status='queued',
                progress=0
            )

            if workspace_id:
                workspace = Workspace.objects.filter(id=workspace_id, tenant=user.tenant).first()
                if workspace:
                    task.workspace = workspace
                    task.save()

            orchestrator = AIOrchestrator(task)
            project = orchestrator.execute(user)

            if workspace_id:
                workspace = Workspace.objects.filter(id=workspace_id, tenant=user.tenant).first()
                if workspace:
                    project.workspace = workspace
                    project.save(update_fields=['workspace'])

            # Log generation_completed success telemetry
            UserJourneyEvent.objects.create(
                user=user,
                step='generation_completed',
                status='success',
                workspace_id=workspace_id_str
            )

            output_serializer = ProjectDetailSerializer(project)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log generation_completed failed telemetry
            UserJourneyEvent.objects.create(
                user=user,
                step='generation_completed',
                status='failed',
                error_message=str(e),
                workspace_id=workspace_id_str
            )
            raise e

    @action(detail=True, methods=['post'], url_path='update-page')
    def update_page(self, request, pk=None):
        project = self.get_object()
        slug = request.data.get('slug')
        raw_content = request.data.get('raw_content')
        if not slug or raw_content is None:
            return Response({"error": "slug and raw_content are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            page = project.pages.get(slug=slug)
            page.raw_content = raw_content
            page.save()
            return Response(ProjectDetailSerializer(project).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='ai-edit')
    def ai_edit(self, request, pk=None):
        project = self.get_object()
        prompt = request.data.get('prompt')
        filepath = request.data.get('filepath') or 'src/pages/index.html'
        
        if not prompt:
            return Response({"error": "prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        import os
        standard_path = filepath.replace('\\', '/')
        if '..' in standard_path or standard_path.startswith('/') or os.path.isabs(standard_path) or ':' in standard_path:
            return Response({"error": "Invalid or unsafe filepath"}, status=status.HTTP_400_BAD_REQUEST)
            
        clean_path = os.path.normpath(standard_path).replace('\\', '/')
        if (
            not clean_path or
            clean_path in ['.', './'] or
            clean_path.startswith('/') or
            '..' in clean_path.split('/')
        ):
            return Response({"error": "Invalid or unsafe filepath"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the target project file
            proj_file = project.files.filter(path=clean_path).first()
            if not proj_file:
                # If project file doesn't exist, check pages
                slug = clean_path.split("/")[-1].replace(".html", "")
                page = project.pages.filter(slug=slug).first()
                if page:
                    proj_file = ProjectFile.objects.create(
                        project=project,
                        path=clean_path,
                        content=page.raw_content
                    )
                else:
                    return Response({"error": f"File '{clean_path}' not found in project"}, status=status.HTTP_404_NOT_FOUND)
            
            # Retrieve compiler/styling context
            ds = project.design_system
            
            # Select LLM provider
            from core.services.ai_router import AIRouterService
            router = AIRouterService()
            provider_name = router.select_best_provider_for_task("layout_code_generation")
            provider = router.get_provider(provider_name)
            
            sys_instruction = (
                "You are the AI Visual Editor of BevHub AI. Your task is to update the provided HTML/CSS source code "
                "based on the user's edit instructions. You must maintain all existing structure and style elements, "
                "applying ONLY the requested styling, component additions, or text content modifications. "
                "Return ONLY the updated, complete HTML code. Do NOT wrap it in backticks, markdown formatting, "
                "or write any conversational text before/after the code block. Return only valid HTML code."
            )
            
            user_msg = (
                f"Design System:\n{json.dumps(ds)}\n\n"
                f"Existing Code for {clean_path}:\n"
                f"<!-- START CODE -->\n{proj_file.content}\n<!-- END CODE -->\n\n"
                f"User Edit Instruction: '{prompt}'\n\n"
                f"Please apply the requested changes and output the entire updated source code."
            )
            
            result = provider.generate_text(
                prompt=user_msg,
                system_instruction=sys_instruction
            )
            
            updated_content = result.text.strip()
            # Clean up potential LLM code block wraps
            if updated_content.startswith("```html"):
                updated_content = updated_content[7:]
            if updated_content.startswith("```"):
                updated_content = updated_content[3:]
            if updated_content.endswith("```"):
                updated_content = updated_content[:-3]
            updated_content = updated_content.strip()
            
            # Save updated content
            proj_file.content = updated_content
            proj_file.save()
            
            # Sync with Page if applicable
            if clean_path.startswith("src/pages/"):
                slug = clean_path.split("/")[-1].replace(".html", "")
                Page.objects.update_or_create(
                    project=project,
                    slug=slug,
                    defaults={"title": slug.capitalize(), "raw_content": updated_content}
                )
                
            return Response(ProjectDetailSerializer(project).data)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='deploy')
    def deploy_project(self, request, pk=None):
        project = self.get_object()
        workspace_id_str = str(project.workspace.id) if project.workspace else None

        from core.domain.models import UserJourneyEvent
        # Log deploy_clicked telemetry
        UserJourneyEvent.objects.create(
            user=request.user,
            step='deploy_clicked',
            status='success',
            workspace_id=workspace_id_str
        )

        deployment = project.deployments.order_by('-created_at').first()
        if not deployment:
            from core.domain.models import Deployment
            deployment = Deployment.objects.create(project=project)

        # Build & Validation check with Auto-Fix (3-5 retries limit)
        max_iterations = 3
        current_iteration = 0
        build_successful = False
        build_errors = []

        while current_iteration < max_iterations:
            current_iteration += 1
            build_errors = self._validate_project_build(project)
            if not build_errors:
                build_successful = True
                break
            
            # If build fails, try to auto-fix using AI
            try:
                self._fix_build_errors(project, build_errors)
            except Exception as e:
                build_errors.append(f"Auto-fix execution failed: {str(e)}")
                break

        if not build_successful:
            deployment.status = 'failed'
            deployment.save()

            # Log deployment_completed failed telemetry
            UserJourneyEvent.objects.create(
                user=request.user,
                step='deployment_completed',
                status='failed',
                error_message=f"Build failed after {current_iteration} attempts: {'; '.join(build_errors)}",
                workspace_id=workspace_id_str
            )
            return Response(
                {"error": f"Deployment failed: build errors could not be resolved. Details: {'; '.join(build_errors)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            deployment.status = 'success'
            host = request.get_host()
            deployment.deploy_url = f"http://{host}/deployed/{project.subdomain}/"
            deployment.save()

            # Log deployment_completed success telemetry
            UserJourneyEvent.objects.create(
                user=request.user,
                step='deployment_completed',
                status='success',
                workspace_id=workspace_id_str
            )
        except Exception as e:
            deployment.status = 'failed'
            deployment.save()

            UserJourneyEvent.objects.create(
                user=request.user,
                step='deployment_completed',
                status='failed',
                error_message=str(e),
                workspace_id=workspace_id_str
            )
            raise e

        return Response(ProjectDetailSerializer(project).data)

    def _validate_project_build(self, project) -> list:
        errors = []
        files = project.files.all()
        pages = project.pages.all()
        if not files.exists() and not pages.exists():
            errors.append("No build targets: project contains no files or pages.")
            return errors

        for f in files:
            if f.path.endswith('.html'):
                content = f.content.strip()
                if not content:
                    errors.append(f"Syntax error in {f.path}: Empty file.")
                    continue
                
                # Check html/head/body balance
                if "<html>" in content and "</html>" not in content:
                    errors.append(f"Compilation error in {f.path}: Opened <html> tag without closing </html>.")
                if "<head>" in content and "</head>" not in content:
                    errors.append(f"Compilation error in {f.path}: Opened <head> tag without closing </head>.")
                if "<body>" in content and "</body>" not in content:
                    errors.append(f"Compilation error in {f.path}: Opened <body> tag without closing </body>.")
                
                open_divs = content.count("<div")
                close_divs = content.count("</div>")
                if open_divs != close_divs:
                    errors.append(f"Linter warning in {f.path}: Unbalanced div tags. Found {open_divs} opening tags and {close_divs} closing tags.")
                    
                open_mains = content.count("<main")
                close_mains = content.count("</main")
                if open_mains != close_mains:
                    errors.append(f"Linter warning in {f.path}: Unbalanced main tags. Found {open_mains} opening tags and {close_mains} closing tags.")
        return errors

    def _fix_build_errors(self, project, errors):
        from core.services.ai_router import AIRouterService
        router = AIRouterService()
        provider_name = router.select_best_provider_for_task("layout_code_generation")
        provider = router.get_provider(provider_name)

        for err in errors:
            target_path = "src/pages/index.html"
            for f in project.files.all():
                if f.path in err:
                    target_path = f.path
                    break
            
            proj_file = project.files.filter(path=target_path).first()
            if not proj_file:
                slug = target_path.split("/")[-1].replace(".html", "")
                page = project.pages.filter(slug=slug).first()
                if page:
                    proj_file = ProjectFile.objects.create(
                        project=project,
                        path=target_path,
                        content=page.raw_content
                    )
                else:
                    continue

            sys_instruction = (
                "You are the Lead QA compiler of BevHub AI. Your job is to fix syntax and linter errors in HTML code. "
                "Return ONLY the updated, complete HTML code. Do NOT wrap it in backticks, markdown formatting, "
                "or write any explanation text before/after the code. Return only valid HTML code."
            )

            user_msg = (
                f"Code with errors:\n"
                f"<!-- START CODE -->\n{proj_file.content}\n<!-- END CODE -->\n\n"
                f"Build Errors:\n{err}\n\n"
                f"Please fix all build errors listed and return the corrected complete code."
            )

            result = provider.generate_text(prompt=user_msg, system_instruction=sys_instruction)
            updated_content = result.text.strip()
            
            if updated_content.startswith("```html"):
                updated_content = updated_content[7:]
            if updated_content.startswith("```"):
                updated_content = updated_content[3:]
            if updated_content.endswith("```"):
                updated_content = updated_content[:-3]
            updated_content = updated_content.strip()

            proj_file.content = updated_content
            proj_file.save()

            if target_path.startswith("src/pages/"):
                slug = target_path.split("/")[-1].replace(".html", "")
                Page.objects.update_or_create(
                    project=project,
                    slug=slug,
                    defaults={"title": slug.capitalize(), "raw_content": updated_content}
                )

    @action(detail=True, methods=['post'], url_path='archive')
    def archive_project(self, request, pk=None):
        project = self.get_object()
        project.status = 'archived'
        project.save(update_fields=['status'])
        return Response(ProjectDetailSerializer(project).data)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore_project(self, request, pk=None):
        project = self.get_object()
        project.status = 'active'
        project.save(update_fields=['status'])
        return Response(ProjectDetailSerializer(project).data)

    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate_project(self, request, pk=None):
        import uuid
        project = self.get_object()
        
        with transaction.atomic():
            # Create duplicate project
            dup = Project.objects.create(
                tenant=project.tenant,
                workspace=project.workspace,
                owner=request.user,
                project_name=f"{project.project_name} Copy",
                subdomain=f"copy-{uuid.uuid4().hex[:6]}-{project.subdomain[:20]}",
                design_system=project.design_system,
                prompt=project.prompt,
                status='active'
            )

            # Duplicate pages
            for page in project.pages.all():
                Page.objects.create(
                    project=dup,
                    slug=page.slug,
                    title=page.title,
                    layout_ast=page.layout_ast,
                    raw_content=page.raw_content
                )

            # Duplicate files
            for f in project.files.all():
                ProjectFile.objects.create(
                    project=dup,
                    path=f.path,
                    content=f.content
                )

            # Duplicate deployment
            Deployment.objects.create(
                project=dup,
                status='success',
                deploy_url=f"https://{dup.subdomain}.bevhub.ai"
            )

        return Response(ProjectDetailSerializer(dup).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='review')
    def review_project(self, request, pk=None):
        project = self.get_object()
        try:
            from ai.services.review_engine import ReviewService
            service = ReviewService()
            review = service.perform_code_review(project)
            return Response(ProjectReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='reviews')
    def get_reviews(self, request, pk=None):
        project = self.get_object()
        reviews = project.reviews.order_by('-created_at')
        return Response(ProjectReviewSerializer(reviews, many=True).data)

    @action(detail=True, methods=['post'], url_path='fix')
    def fix_project(self, request, pk=None):
        project = self.get_object()
        try:
            from apps.ai.services.bug_fixer import BugFixService
            service = BugFixService()
            result = service.run_bug_fix_pipeline(project)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='fixes')
    def get_fixes(self, request, pk=None):
        project = self.get_object()
        fixes = project.fix_runs.order_by('-created_at')
        return Response(ProjectFixRunSerializer(fixes, many=True).data)


from django.http import HttpResponse, Http404

def serve_deployed_project(request, subdomain, slug='index'):
    try:
        project = Project.objects.get(subdomain=subdomain)
        
        # Check ProjectFile first
        filename = f"src/pages/{slug}.html"
        proj_file = project.files.filter(path__in=[filename, f"{slug}.html"]).first()
        if proj_file:
            return HttpResponse(proj_file.content, content_type="text/html")
            
        # Fallback to Page object
        page = project.pages.filter(slug=slug).first()
        if page:
            return HttpResponse(page.raw_content, content_type="text/html")
            
        # Fallback to any index page
        index_file = project.files.filter(path__icontains="index").first()
        if index_file:
            return HttpResponse(index_file.content, content_type="text/html")
            
        index_page = project.pages.filter(slug='index').first() or project.pages.first()
        if index_page:
            return HttpResponse(index_page.raw_content, content_type="text/html")
            
        return HttpResponse("<h1>Project has no pages generated yet.</h1>", status=404)
    except Project.DoesNotExist:
        raise Http404("Project not found")



