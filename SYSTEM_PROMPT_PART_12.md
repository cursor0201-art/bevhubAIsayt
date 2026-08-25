# SYSTEM_PROMPT_PART_12.md
# DJANGO • DRF • BACKEND IMPLEMENTATION BIBLE

==================================================
MISSION
==================================================

The backend is the source of truth.

It must remain reliable under high load,
easy to maintain,
easy to extend,
easy to test.

Never sacrifice architecture for speed.

==================================================
GENERAL PRINCIPLES
==================================================

Business Logic

↓

Service Layer

Database Access

↓

Repository / ORM Layer

API

↓

ViewSets

Validation

↓

Serializers

Configuration

↓

Settings

Never mix responsibilities.

==================================================
DJANGO APPS
==================================================

apps/

authentication/

users/

organizations/

projects/

workspaces/

ai/

billing/

payments/

credits/

notifications/

media/

analytics/

deployments/

admin_panel/

core/

==================================================
MODELS
==================================================

Every model must include

UUID

created_at

updated_at

created_by

updated_by

Soft Delete Support

Indexes

Meaningful Constraints

Never create unnecessary tables.

==================================================
MODEL RULES
==================================================

Models store data.

Models do not contain business workflows.

Complex logic belongs inside Services.

==================================================
SERIALIZERS
==================================================

Serializer responsibilities

Validate input

Validate output

Transform data

Nothing else.

Never implement business logic inside serializers.

==================================================
VIEWSETS
==================================================

ViewSets should

Authenticate

Authorize

Call Services

Return Responses

Nothing more.

==================================================
SERVICE LAYER
==================================================

Every important feature must have a Service.

Examples

UserService

ProjectService

WebsiteBuilderService

CreditsService

BillingService

DeploymentService

NotificationService

AnalyticsService

LogoGeneratorService

==================================================
TRANSACTIONS
==================================================

Always use database transactions when

Money changes

Credits change

Multiple tables change

Subscriptions change

AI usage changes

Project publishing

==================================================
ORM RULES
==================================================

Always

select_related()

prefetch_related()

bulk_create()

bulk_update()

annotate()

aggregate()

Avoid

N+1 Queries

Duplicate Queries

Repeated ORM Calls

==================================================
CACHE
==================================================

Redis

Cache

Dashboard

Settings

Feature Flags

Frequently Used Objects

AI Pricing

Subscription Plans

==================================================
CELERY
==================================================

Run asynchronously

AI Requests

Deployments

Emails

SMS

Image Generation

Video Generation

PDF

SEO Scan

Analytics

==================================================
API RESPONSES
==================================================

Every response

Success

Message

Data

Pagination

Metadata

Errors

==================================================
PAGINATION
==================================================

Cursor Pagination Preferred

Fallback

Page Number

Limit

Offset

==================================================
LOGGING
==================================================

Every request logs

Execution Time

User

Workspace

Endpoint

Status

Latency

IP

==================================================
RATE LIMIT
==================================================

Anonymous

Authenticated

Premium

Enterprise

Admin

Each level configurable.

==================================================
FILE STORAGE
==================================================

Separate storage.

Never store uploads inside application folder.

Support

Images

Videos

Documents

Generated Assets

==================================================
TESTS
==================================================

Every endpoint

Unit Tests

API Tests

Permission Tests

Edge Cases

Load Tests

Regression Tests

==================================================
DOCUMENTATION
==================================================

Every endpoint documents

Description

Authentication

Permissions

Examples

Responses

Errors

==================================================
FINAL RULE
==================================================

Backend code must be understandable by a new senior engineer
within minutes.

Architecture must always be more important than shortcuts.

==================================================
END OF PART 12
