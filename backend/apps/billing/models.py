from django.db import models
from core.domain.models import BaseModel, Tenant

class SubscriptionPlan(BaseModel):
    """
    Stores SaaS tiered subscription pricing, quotas, and limits.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
    ai_credits_allowance = models.IntegerField(default=100)
    storage_limit_gb = models.IntegerField(default=5)
    projects_limit = models.IntegerField(default=3)
    team_members_limit = models.IntegerField(default=1)
    feature_flags = models.JSONField(default=dict, blank=True, help_text="Enabled premium modules/capabilities")

    class Meta:
        db_table = 'subscription_plans'

    def __str__(self):
        return f"{self.name} Plan (${self.monthly_price}/mo)"


class Subscription(BaseModel):
    """
    Tracks Organization's active pricing tier, period renewal boundaries, and trial parameters.
    """
    STATUS_CHOICES = [
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid')
    ]

    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    renewal_date = models.DateTimeField()
    expiration_date = models.DateTimeField(null=True, blank=True)
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'subscriptions'
        indexes = [
            models.Index(fields=['tenant', 'status']),
        ]

    def __str__(self):
        return f"{self.tenant.company_name} - {self.plan.name} ({self.status})"


class Invoice(BaseModel):
    """
    Stores ledger invoices for billing transactions.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('uncollectible', 'Uncollectible'),
        ('refunded', 'Refunded')
    ]

    invoice_number = models.CharField(max_length=100, unique=True, db_index=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    payment_provider = models.CharField(max_length=50, help_text="e.g. Stripe, PayPal, Payme, Click")
    invoice_pdf_url = models.URLField(max_length=1024, blank=True)

    class Meta:
        db_table = 'invoices'

    def __str__(self):
        return f"Invoice {self.invoice_number} ({self.status}) - {self.currency} {self.amount}"


class PromoCode(BaseModel):
    """
    Discount promotional keys.
    """
    code = models.CharField(max_length=100, unique=True, db_index=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    extra_credits = models.IntegerField(default=0)
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'promo_codes'

    def __str__(self):
        return self.code
