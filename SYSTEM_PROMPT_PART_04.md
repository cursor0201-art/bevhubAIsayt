# SYSTEM_PROMPT_PART_04.md
# BACKEND ENGINEERING BIBLE

==================================================
MISSION
==================================================

The backend of BevHub AI is the foundation of the platform.

It must be secure, scalable, observable, testable and maintainable.

Never optimize for short-term speed.

Always optimize for long-term reliability.

==================================================
TECH STACK
==================================================

Language:
Python 3.13+

Framework:
Django

API:
Django REST Framework

Database:
PostgreSQL

Cache:
Redis

Background Jobs:
Celery

Authentication:
JWT + Refresh Tokens

Documentation:
OpenAPI + Swagger

Containerization:
Docker

==================================================
PROJECT STRUCTURE
==================================================

backend/

apps/

core/

api/

users/

projects/

billing/

payments/

ai/

analytics/

notifications/

media/

organizations/

admin_panel/

common/

config/

tests/

==================================================
CODING PRINCIPLES
==================================================

Use SOLID.

Use Clean Architecture.

Use Repository pattern where appropriate.

Avoid fat views.

Avoid fat serializers.

Business logic belongs inside services.

Views only orchestrate requests.

Models should not contain unrelated logic.

==================================================
API DESIGN
==================================================

RESTful by default.

Consistent naming.

Plural resource names.

Version every public API.

Example:

/api/v1/users/

/api/v1/projects/

/api/v1/ai/chat/

Never expose internal implementation details.

==================================================
VALIDATION
==================================================

Every endpoint validates:

Authentication

Authorization

Permissions

Input schema

Business rules

Rate limits

Request size

Never trust client input.

==================================================
DATABASE RULES
==================================================

Every model:

UUID primary key

created_at

updated_at

Indexes

Foreign Keys

Meaningful constraints

Never duplicate data.

Normalize until justified otherwise.

Use transactions for multi-step operations.

==================================================
SERVICES
==================================================

Each feature must expose a service layer.

Example:

ProjectService

BillingService

CreditsService

DeploymentService

AIService

NotificationService

Never call ORM directly from API views if business logic exists.

==================================================
BACKGROUND TASKS
==================================================

Move expensive operations to Celery.

Examples:

AI generation

Email

Image processing

PDF generation

Deployment

Analytics

Video rendering

Never block user requests.

==================================================
REDIS
==================================================

Use Redis for:

Caching

Rate limiting

Sessions

Queues

Temporary tokens

Feature flags

Do not use Redis as the primary database.

==================================================
ERROR HANDLING
==================================================

Every error:

Logged

Categorized

Traceable

Safe for user

Never expose stack traces.

Return structured JSON.

Example:

{
  "success": false,
  "error": {
      "code": "INVALID_TOKEN",
      "message": "Authentication required."
  }
}

==================================================
LOGGING
==================================================

Every important event must be logged.

Examples:

Login

Logout

Password Change

Payment

Subscription

Credits

Deployment

Admin Actions

API Errors

Security Events

==================================================
SECURITY
==================================================

JWT Authentication

Refresh Tokens

Password hashing

Rate Limiting

IP Protection

CSRF

CORS

SQL Injection Protection

XSS Protection

Content Security Policy

Input Sanitization

Audit Logs

Role-Based Access Control

Two-Factor Authentication Ready

==================================================
PERMISSIONS
==================================================

Roles:

Guest

User

Pro

Business

Enterprise

Moderator

Support

Administrator

Owner

Every endpoint must verify permissions before execution.

==================================================
PAYMENTS
==================================================

Support multiple providers.

Never store raw card data.

Verify payment callbacks.

Use idempotency keys.

Every payment must be auditable.

==================================================
AI MODULE
==================================================

The AI module must never depend on a single provider.

Providers must be interchangeable.

Support:

OpenAI

Anthropic Claude

Gemini

DeepSeek

OpenRouter

Future providers

==================================================
PERFORMANCE
==================================================

Optimize database queries.

Avoid N+1 queries.

Use select_related.

Use prefetch_related.

Paginate large datasets.

Compress responses.

Cache frequently accessed data.

==================================================
TESTING
==================================================

Every service:

Unit Tests

Integration Tests

API Tests

Permission Tests

Edge Cases

Regression Tests

Critical flows require automated testing.

==================================================
MONITORING
==================================================

Track:

API latency

Database performance

Queue health

AI response time

Memory usage

CPU usage

Error rate

Payment failures

==================================================
DOCUMENTATION
==================================================

Every endpoint:

Description

Authentication

Permissions

Parameters

Responses

Errors

Examples

==================================================
FINAL RULE
==================================================

The backend must remain understandable, secure and scalable even after five years of continuous development.

Never sacrifice architecture for convenience.

==================================================
END OF PART 04
