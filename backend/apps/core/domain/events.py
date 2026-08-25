from datetime import datetime
from uuid import UUID
from typing import Callable, Dict, List, Type
from pydantic import BaseModel, Field

class BaseDomainEvent(BaseModel):
    """
    Standard schema for all system-wide domain events.
    """
    event_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        frozen = True


class UserRegisteredEvent(BaseDomainEvent):
    user_id: UUID
    email: str
    tenant_id: UUID | None


class ProjectCreatedEvent(BaseDomainEvent):
    project_id: UUID
    tenant_id: UUID
    project_name: str


class CreditsUsedEvent(BaseDomainEvent):
    tenant_id: UUID
    user_id: UUID
    credits_amount: int
    operation_type: str


class SubscriptionPurchasedEvent(BaseDomainEvent):
    tenant_id: UUID
    plan_level: str
    amount: float


class WebsitePublishedEvent(BaseDomainEvent):
    project_id: UUID
    subdomain: str
    custom_domain: str | None
    deployment_id: UUID


class PaymentSucceededEvent(BaseDomainEvent):
    tenant_id: UUID
    invoice_id: str
    amount: float


# Event Dispatcher for Microservice Readiness
class EventDispatcher:
    """
    Decoupled sync/async event router. 
    Allows modules to register listeners without direct imports.
    """
    _listeners: Dict[Type[BaseDomainEvent], List[Callable]] = {}

    @classmethod
    def register(cls, event_type: Type[BaseDomainEvent], listener: Callable):
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(listener)

    @classmethod
    def dispatch(cls, event: BaseDomainEvent):
        event_type = type(event)
        if event_type in cls._listeners:
            for listener in cls._listeners[event_type]:
                try:
                    # In production this could dispatch tasks directly to a Celery queue
                    # or an external Kafka / RabbitMQ system for full microservices.
                    listener(event)
                except Exception as e:
                    # Implement proper production logging
                    print(f"Error executing listener {listener.__name__} for event {event_type.__name__}: {e}")
