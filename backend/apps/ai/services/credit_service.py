from decimal import Decimal
from django.db import transaction
from core.domain.models import Tenant
from ai.models import AICreditBalance, AICreditTransaction

class CreditService:
    """
    Handles credit cost calculation, checks, and transactional balance updates.
    """
    
    # Cost per 1000 tokens/units in Credits
    MODEL_COSTS = {
        "openai": Decimal("0.02"),
        "claude": Decimal("0.03"),
        "gemini": Decimal("0.005"),
        "deepseek": Decimal("0.002"),
        "openrouter": Decimal("0.015"),
    }

    IMAGE_GENERATION_COST = Decimal("1.5")  # Cost per image generation task

    @classmethod
    def calculate_cost(cls, provider: str, input_tokens: int, output_tokens: int, is_image: bool = False) -> Decimal:
        if is_image:
            return cls.IMAGE_GENERATION_COST
        
        rate = cls.MODEL_COSTS.get(provider.lower(), Decimal("0.01"))
        total_tokens = input_tokens + output_tokens
        return (Decimal(total_tokens) / Decimal(1000)) * rate

    @classmethod
    def has_sufficient_credits(cls, tenant: Tenant, estimated_cost: Decimal) -> bool:
        balance, _ = AICreditBalance.objects.get_or_create(tenant=tenant, defaults={'balance': Decimal("100.00")})
        return balance.balance >= estimated_cost

    @classmethod
    @transaction.atomic
    def record_usage(
        cls, 
        tenant: Tenant, 
        provider: str, 
        input_tokens: int, 
        output_tokens: int, 
        task_desc: str,
        is_image: bool = False
    ) -> Decimal:
        cost = cls.calculate_cost(provider, input_tokens, output_tokens, is_image)
        
        # Deduct balance
        balance, _ = AICreditBalance.objects.get_or_create(tenant=tenant, defaults={'balance': Decimal("100.00")})
        balance.balance = max(Decimal("0.00"), balance.balance - cost)
        balance.save()

        # Log audit record
        AICreditTransaction.objects.create(
            tenant=tenant,
            model_name=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            amount_consumed=cost,
            task_description=task_desc,
            is_image_generation=is_image
        )

        return cost
