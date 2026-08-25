from django.contrib import admin
from decimal import Decimal
from ai.models import ProjectMemory, UserMemory, AICreditBalance, AICreditTransaction

@admin.action(description="Award 100 promotional credits to selected accounts")
def award_promotional_credits(modeladmin, request, queryset):
    for balance in queryset:
        balance.balance += Decimal("100.00")
        balance.save()

@admin.action(description="Reset selected credit balances to zero")
def reset_credits_to_zero(modeladmin, request, queryset):
    queryset.update(balance=Decimal("0.00"))


class ProjectMemoryAdmin(admin.ModelAdmin):
    list_display = ('project', 'industry', 'brand_voice', 'preferred_language')
    search_fields = ('project__project_name', 'industry')

class UserMemoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'writing_style', 'preferred_language')
    search_fields = ('user__username', 'user__email')

class AICreditBalanceAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'balance', 'updated_at')
    search_fields = ('tenant__company_name',)
    actions = [award_promotional_credits, reset_credits_to_zero]

class AICreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'model_name', 'amount_consumed', 'task_description', 'created_at')
    list_filter = ('model_name', 'created_at')
    search_fields = ('tenant__company_name', 'task_description')
    readonly_fields = ('amount_consumed', 'input_tokens', 'output_tokens')

admin.site.register(ProjectMemory, ProjectMemoryAdmin)
admin.site.register(UserMemory, UserMemoryAdmin)
admin.site.register(AICreditBalance, AICreditBalanceAdmin)
admin.site.register(AICreditTransaction, AICreditTransactionAdmin)
