from django.contrib import admin
from billing.models import SubscriptionPlan, Subscription, Invoice, PromoCode
from billing.services import BillingService

@admin.action(description="Manually settle selected invoices as Paid")
def settle_invoices(modeladmin, request, queryset):
    for invoice in queryset:
        BillingService.settle_invoice_payment(invoice.invoice_number)

@admin.action(description="Cancel selected subscriptions")
def cancel_subscriptions(modeladmin, request, queryset):
    queryset.update(status='canceled')


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'monthly_price', 'ai_credits_allowance', 'projects_limit')
    search_fields = ('name', 'slug')

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'plan', 'status', 'renewal_date', 'trial_end')
    list_filter = ('status', 'plan')
    search_fields = ('tenant__company_name',)
    actions = [cancel_subscriptions]

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'tenant', 'amount', 'status', 'payment_provider', 'created_at')
    list_filter = ('status', 'payment_provider')
    search_fields = ('invoice_number', 'tenant__company_name')
    actions = [settle_invoices]

class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'extra_credits', 'is_active', 'expiration_date')
    list_filter = ('is_active', 'expiration_date')
    search_fields = ('code',)

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(PromoCode, PromoCodeAdmin)
