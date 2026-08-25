from django.db import models
from django.conf import settings
from core.domain.models import BaseModel, Project

class ProjectMemory(BaseModel):
    """
    Persists context parameters, preferences, and details across multiple AI generations for a single Project.
    """
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='memory')
    industry = models.CharField(max_length=255, blank=True)
    target_audience = models.TextField(blank=True)
    brand_voice = models.CharField(max_length=100, blank=True)
    preferred_language = models.CharField(max_length=50, default='English')
    products_metadata = models.JSONField(default=dict, blank=True, help_text="Metadata of products or services offered")
    user_preferences = models.JSONField(default=dict, blank=True, help_text="Custom key-value user preferences")
    metadata_store = models.JSONField(default=dict, blank=True, help_text="Historical values from previous AI outputs")

    class Meta:
        db_table = 'project_memories'

    def __str__(self):
        return f"Memory for Project: {self.project.project_name}"


class UserMemory(BaseModel):
    """
    Tracks and personalizes user preferences across all projects.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memory')
    writing_style = models.CharField(max_length=100, default='Professional')
    favorite_colors = models.JSONField(default=list, blank=True)
    preferred_language = models.CharField(max_length=50, default='English')
    last_active_project_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = 'user_memories'

    def __str__(self):
        return f"Memory for User: {self.user.email}"


class AICreditBalance(BaseModel):
    """
    Maintains the credit balance of a Tenant.
    """
    tenant = models.OneToOneField('core.Tenant', on_delete=models.CASCADE, related_name='credit_balance')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=100.00)

    class Meta:
        db_table = 'ai_credit_balances'

    def __str__(self):
        return f"{self.tenant.company_name} Balance: {self.balance} Credits"


class AICreditTransaction(BaseModel):
    """
    Audit log tracking credit usages, inputs, outputs, models, and costs.
    """
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='credit_transactions')
    model_name = models.CharField(max_length=100)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    amount_consumed = models.DecimalField(max_digits=8, decimal_places=4)
    task_description = models.CharField(max_length=255)
    is_image_generation = models.BooleanField(default=False)

    class Meta:
        db_table = 'ai_credit_transactions'
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
        ]

    def __str__(self):
        return f"{self.tenant.company_name} - {self.amount_consumed} Credits for {self.task_description}"
