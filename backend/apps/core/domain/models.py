import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class BaseModel(models.Model):
    """
    Base structural model for all platform entities.
    Enforces UUIDs, creation, modification, and soft-delete metrics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Managers
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])


class Tenant(BaseModel):
    """
    Represents an Organization / SaaS Subscriber account.
    """
    company_name = models.CharField(max_length=255)
    plan_level = models.CharField(
        max_length=50, 
        choices=[('free', 'Free'), ('growth', 'Growth'), ('enterprise', 'Enterprise')],
        default='free'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'tenants'
        indexes = [
            models.Index(fields=['plan_level']),
        ]

    def __str__(self):
        return self.company_name


class Workspace(BaseModel):
    """
    An isolated workspace sandbox environment containing projects, credits, and members.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='workspaces')
    name = models.CharField(max_length=255)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'workspaces'
        indexes = [
            models.Index(fields=['tenant']),
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant.company_name})"


class User(AbstractUser, BaseModel):
    """
    SaaS User account containing personalized preferences, roles, and context.
    """
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.PROTECT, 
        related_name='users', 
        null=True, 
        blank=True
    )
    role = models.CharField(
        max_length=50, 
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Admin'), 
            ('developer', 'Developer'), 
            ('viewer', 'Viewer')
        ],
        default='admin'
    )
    display_name = models.CharField(max_length=255, blank=True)
    avatar_url = models.URLField(max_length=1024, blank=True)
    language = models.CharField(max_length=50, default='en')
    timezone = models.CharField(max_length=100, default='UTC')
    country = models.CharField(max_length=100, blank=True)
    theme = models.CharField(max_length=50, default='dark')

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.email or self.username} ({self.role})"


class Project(BaseModel):
    """
    Represents an AI-generated website project.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='projects')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='owned_projects', null=True, blank=True)
    project_name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=100, unique=True, db_index=True)
    custom_domain = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    design_system = models.JSONField(default=dict, help_text="Core CSS style variables mapping")
    prompt = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='active')
    version = models.IntegerField(default=1)

    class Meta:
        db_table = 'projects'

    def __str__(self):
        return self.project_name


class Page(BaseModel):
    """
    Dynamic page layouts generated within a Project scope.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pages')
    slug = models.SlugField(max_length=255, db_index=True)
    title = models.CharField(max_length=255)
    layout_ast = models.JSONField(default=dict, help_text="AST mapping containing structured grid sections")
    raw_content = models.TextField()

    class Meta:
        db_table = 'pages'
        unique_together = ('project', 'slug')
        indexes = [
            models.Index(fields=['project', 'slug']),
        ]

    def __str__(self):
        return f"{self.title} (/{self.slug})"


class Asset(BaseModel):
    """
    Media library manager (logos, banners, custom images).
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(
        max_length=50, 
        choices=[('logo', 'Logo'), ('banner', 'Banner'), ('image', 'General Image'), ('document', 'Document')]
    )
    storage_url = models.URLField(max_length=1024)
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'assets'

    def __str__(self):
        return f"{self.asset_type}: {self.storage_url}"


class Deployment(BaseModel):
    """
    Build & Deploy event metrics.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='deployments')
    status = models.CharField(
        max_length=50,
        choices=[('queued', 'Queued'), ('building', 'Building'), ('success', 'Success'), ('failed', 'Failed')],
        default='queued'
    )
    commit_hash = models.CharField(max_length=40, blank=True)
    deploy_url = models.URLField(max_length=1024, null=True, blank=True)
    logs = models.TextField(blank=True)

    class Meta:
        db_table = 'deployments'
        indexes = [
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"Deployment {self.id} - {self.status}"


class ProjectVersion(BaseModel):
    """
    Stores history snapshots of Project states to support Undo, Redo, and Restore capabilities.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    layout_ast_snapshot = models.JSONField(help_text="Snapshot of the project pages layouts AST")
    design_system_snapshot = models.JSONField(help_text="Snapshot of the theme design variables")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'project_versions'
        unique_together = ('project', 'version_number')

    def __str__(self):
        return f"{self.project.project_name} v{self.version_number}"


class AIExecution(BaseModel):
    """
    Audit log of every single model request and usage cost transaction.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ai_executions')
    prompt = models.TextField()
    provider = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    execution_time_ms = models.IntegerField(default=0)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=0.00)
    latency_ms = models.IntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'ai_executions'

    def __str__(self):
        return f"AIExecution {self.id} - {self.provider}/{self.model_name}"


class AuditLog(BaseModel):
    """
    Security audit trails tracking structural platform actions.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'audit_logs'

    def __str__(self):
        return f"{self.action} by {self.user.username if self.user else 'System'} at {self.created_at}"


class ProjectFile(BaseModel):
    """
    Represents a virtual workspace file system entity containing generated code.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    path = models.CharField(max_length=512)
    content = models.TextField()

    class Meta:
        db_table = 'project_files'
        unique_together = ('project', 'path')

    def __str__(self):
        return f"{self.project.project_name} - {self.path}"


class AITask(BaseModel):
    """
    Represents an active multi-agent AI workspace execution task.
    """
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='ai_tasks', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ai_tasks', null=True, blank=True)
    prompt = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    files = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=50, default='queued')
    progress = models.IntegerField(default=0)
    logs = models.TextField(blank=True)
    tokens_used = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)

    class Meta:
        db_table = 'ai_tasks'

    def __str__(self):
        return f"AITask {self.id} ({self.status}) - {self.prompt[:30]}"


class UserJourneyEvent(BaseModel):
    """
    Tracks telemetry events along the user journey funnel for Product Intelligence.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey_events')
    step = models.CharField(max_length=100, db_index=True) # e.g. registration, workspace_created, etc.
    status = models.CharField(max_length=50, default='success') # success, failed, dropped
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    workspace_id = models.CharField(max_length=255, blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True)
    device = models.CharField(max_length=255, blank=True)
    version = models.CharField(max_length=50, default='v1.0.0-rc')
    logs = models.TextField(blank=True, help_text="Collect Logs, Planner State, Worker, Model, Context, Prompt, Stack Trace")

    class Meta:
        db_table = 'user_journey_events'
        indexes = [
            models.Index(fields=['step', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"UserJourneyEvent {self.step} ({self.status}) - {self.created_at}"


class ProjectReview(BaseModel):
    """
    Stores AI Code Reviewer reports for a project.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    overall_score = models.IntegerField()
    architecture_score = models.IntegerField()
    performance_score = models.IntegerField()
    security_score = models.IntegerField()
    seo_score = models.IntegerField()
    accessibility_score = models.IntegerField()
    ux_score = models.IntegerField()
    typescript_score = models.IntegerField()
    react_score = models.IntegerField()
    deployment_score = models.IntegerField()
    issues = models.JSONField(default=list, help_text="Detailed issues identified")
    recommendations = models.JSONField(default=list, help_text="List of recommendations")
    raw_report = models.JSONField(default=dict, help_text="Raw JSON response from the Review Engine")

    class Meta:
        db_table = 'project_reviews'

    def __str__(self):
        return f"Review for {self.project.project_name} - Score: {self.overall_score}"


class ProjectSnapshot(BaseModel):
    """
    Stores full codebase and page layout snapshots for rollback safety.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='snapshots')
    snapshot_data = models.JSONField(help_text="Complete files and pages data backup")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'project_snapshots'

    def __str__(self):
        return f"Snapshot {self.id} for {self.project.project_name} at {self.created_at}"


class ProjectFixRun(BaseModel):
    """
    Stores history and telemetry logs for AI Bug Fix executions.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='fix_runs')
    before_score = models.IntegerField()
    after_score = models.IntegerField()
    fixed_count = models.IntegerField(default=0)
    remaining_count = models.IntegerField(default=0)
    rollback_applied = models.BooleanField(default=False)
    snapshot = models.ForeignKey(ProjectSnapshot, on_delete=models.SET_NULL, null=True, blank=True)
    logs = models.JSONField(default=list, help_text="Detailed step-by-step logs of executed fixes")

    class Meta:
        db_table = 'project_fix_runs'

    def __str__(self):
        return f"FixRun {self.id} for {self.project.project_name} - Before: {self.before_score}, After: {self.after_score}"


class GenerationStep(BaseModel):
    """
    Stores metrics and execution state for each stage of the AI Orchestrator 2.0 pipeline.
    """
    task = models.ForeignKey(AITask, on_delete=models.CASCADE, related_name='steps')
    step_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50,
        choices=[('PENDING', 'Pending'), ('RUNNING', 'Running'), ('FAILED', 'Failed'), ('SUCCESS', 'Success')],
        default='PENDING'
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(default=0.0)
    tokens_used = models.IntegerField(default=0)
    model_name = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.000000)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'generation_steps'
        ordering = ['created_at']


class IntegrationConfig(BaseModel):
    """
    Stores tenant-isolated connection credentials and active status for third-party tools.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='integrations')
    provider = models.CharField(max_length=50) # github, vercel, stripe, openai, telegram
    is_connected = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'integration_configs'
        unique_together = ('tenant', 'provider')

    def __str__(self):
        return f"{self.tenant.company_name} - {self.provider} ({'Connected' if self.is_connected else 'Disconnected'})"




