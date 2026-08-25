from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.domain.models import (
    Tenant, 
    Workspace, 
    User, 
    Project, 
    Page, 
    Asset, 
    Deployment, 
    ProjectVersion, 
    AIExecution, 
    AuditLog
)

@admin.action(description="Suspend selected user accounts")
def suspend_users(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description="Activate selected user accounts")
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'tenant', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    actions = [suspend_users, activate_users]
    
    # Custom fields mapping
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SaaS Multi-Tenancy', {'fields': ('tenant', 'role')}),
        ('User Preferences', {'fields': ('display_name', 'avatar_url', 'language', 'timezone', 'theme')}),
    )

class TenantAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'plan_level', 'is_active', 'created_at')
    list_filter = ('plan_level', 'is_active')
    search_fields = ('company_name',)

class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('name',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'tenant', 'subdomain', 'custom_domain', 'version', 'created_at')
    search_fields = ('project_name', 'subdomain', 'custom_domain')
    list_filter = ('tenant', 'version')

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'slug', 'created_at')
    search_fields = ('title', 'slug')
    list_filter = ('project',)

class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_type', 'project', 'storage_url', 'created_at')
    list_filter = ('asset_type', 'project')

class DeploymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'status', 'commit_hash', 'deploy_url', 'created_at')
    list_filter = ('status', 'project')
    readonly_fields = ('logs',)

class ProjectVersionAdmin(admin.ModelAdmin):
    list_display = ('project', 'version_number', 'created_by', 'created_at')
    list_filter = ('project',)
    readonly_fields = ('layout_ast_snapshot', 'design_system_snapshot')

class AIExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'provider', 'model_name', 'credits_used', 'latency_ms', 'success', 'created_at')
    list_filter = ('provider', 'model_name', 'success')
    readonly_fields = ('prompt', 'error_message')

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    readonly_fields = ('payload', 'user_agent')

# Register in Django Admin Site
admin.site.register(User, UserAdmin)
admin.site.register(Tenant, TenantAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Deployment, DeploymentAdmin)
admin.site.register(ProjectVersion, ProjectVersionAdmin)
admin.site.register(AIExecution, AIExecutionAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
