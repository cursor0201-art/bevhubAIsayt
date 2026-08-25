from django.contrib import admin
from payments.models import PaymentAttempt

@admin.action(description="Mark selected payment attempts as Refunded")
def refund_payments(modeladmin, request, queryset):
    queryset.update(status='refunded')


class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'amount', 'currency', 'provider', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'provider', 'created_at')
    search_fields = ('transaction_id', 'tenant__company_name')
    actions = [refund_payments]

admin.site.register(PaymentAttempt, PaymentAttemptAdmin)
