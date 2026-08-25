from django.db import models
from core.domain.models import BaseModel, Tenant

class PaymentAttempt(BaseModel):
    """
    Audit log record of payment transaction events.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    provider = models.CharField(max_length=50, help_text="Stripe, PayPal, Click, Payme, Uzum")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    raw_response = models.JSONField(default=dict, blank=True, help_text="Raw payload returned by provider webhook")

    class Meta:
        db_table = 'payment_attempts'
        indexes = [
            models.Index(fields=['tenant', 'status']),
        ]

    def __str__(self):
        return f"{self.provider} Payment {self.id} - {self.status}"
