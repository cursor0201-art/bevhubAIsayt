# SYSTEM_PROMPT_PART_02.md
# BevHub AI Global Architecture

==================================================
GLOBAL PRODUCT ARCHITECTURE
==================================================

The entire platform must be designed as an enterprise SaaS application.

The architecture must remain scalable, modular and maintainable for at least the next five years.

No architectural decision should create unnecessary technical debt.

==================================================
MAIN PRODUCT MODULES
==================================================

The platform consists of the following major systems.

Authentication

User Management

Organization Management

Workspace

Dashboard

AI Router

AI Chat

Website Builder

Landing Page Builder

Logo Generator

Banner Generator

Image Generator

Content Generator

SEO Generator

Marketing Generator

Analytics

Billing

Subscriptions

AI Credits

Project Manager

Media Library

File Storage

Template Marketplace

Notifications

Admin Panel

Developer API

Documentation

Audit Logs

Monitoring

Settings

==================================================
HIGH LEVEL STRUCTURE
==================================================

Frontend

↓

API Gateway

↓

Application Layer

↓

Business Services

↓

AI Router

↓

Database

↓

Background Workers

↓

External Services

==================================================
FRONTEND
==================================================

Frontend must be completely separated from backend.

Technology stack:

Next.js

TypeScript

Tailwind CSS

React

Shadcn UI

Framer Motion

React Query

React Hook Form

Zod

No business logic should exist inside UI components.

Pages must remain thin.

Business logic belongs to services.

==================================================
BACKEND
==================================================

Technology

Python

Django

Django REST Framework

Celery

Redis

PostgreSQL

JWT

Swagger

OpenAPI

Backend follows layered architecture.

Presentation Layer

↓

Application Layer

↓

Domain Layer

↓

Infrastructure Layer

==================================================
DATABASE
==================================================

Every entity must use UUID.

Every table contains

id

created_at

updated_at

deleted_at (where required)

Indexes must exist for all high traffic queries.

Never store duplicated data.

Relationships must use foreign keys.

==================================================
AI ROUTER
==================================================

The AI Router is the heart of BevHub AI.

Responsibilities:

Receive user request.

Understand intent.

Split request into tasks.

Choose best AI provider.

Execute tasks.

Merge responses.

Return final result.

The router must support:

OpenAI

Claude

Gemini

DeepSeek

OpenRouter

Future providers.

Providers must be replaceable without changing business logic.

==================================================
BACKGROUND WORKERS
==================================================

Heavy tasks must never block users.

Move into queues:

Image generation

SEO generation

Website deployment

Email sending

AI processing

Large exports

PDF generation

Analytics processing

Workers communicate through Redis.

==================================================
FILE STORAGE
==================================================

Separate file storage from application server.

Support:

Images

Videos

Documents

Generated Assets

User Uploads

Future migration between providers must be simple.

==================================================
EVENT SYSTEM
==================================================

Every major action generates events.

Examples

UserRegistered

ProjectCreated

CreditsUsed

SubscriptionPurchased

WebsitePublished

PaymentSucceeded

Events should be reusable by future modules.

==================================================
MICROSERVICE READINESS
==================================================

Although version 1 starts as a modular monolith,

every module must be capable of extraction into its own microservice.

No tight coupling allowed.

==================================================
SCALABILITY
==================================================

Architecture must support:

100 users

↓

10,000 users

↓

100,000 users

↓

1,000,000 users

↓

10,000,000 users

without requiring a complete rewrite.

==================================================
GLOBAL DEVELOPMENT RULE
==================================================

Before implementing any feature ask internally:

Can this feature scale?

Can it be tested?

Can it be replaced?

Can another developer understand it six months later?

If the answer is no,

redesign before implementation.

==================================================
END OF PART 02
