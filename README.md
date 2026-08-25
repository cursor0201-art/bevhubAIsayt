# BevHub AI

> One Prompt. Unlimited Possibilities.

BevHub AI is an enterprise-grade multi-tenant SaaS website builder powered by AI agents, allowing entrepreneurs to deploy entire custom web presences from a single prompt.

---

## 🚀 Architectural Overview

We adopt a **Decoupled Frontend / Layered Backend Architecture** with asynchronous background execution:
*   **Frontend Client**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn UI, Framer Motion, React Query, and Zod.
*   **Backend Server**: Python, Django, Django REST Framework (DRF), Celery, Redis, and PostgreSQL.
*   **AI Routing**: Adapter-based interface supporting OpenAI, Claude, Gemini, DeepSeek, and OpenRouter.

For a detailed breakdown of our system components, database schemas, agent workflows, and multi-tenant security architecture, refer to:
*   [Technical Architecture Blueprint](docs/architecture_blueprint.md)
*   [Global System Prompt — Part 1](SYSTEM_PROMPT_PART_01.md)
*   [Global Architecture Prompt — Part 2](SYSTEM_PROMPT_PART_02.md)

---

## 📁 Repository Structure

```
bevhub-ai/
├── apps/
│   ├── frontend/             # Next.js customer web console (Thin pages, decoupled logic)
│   └── backend/              # Django core REST API (Presentation, Application, Domain, Infra)
├── services/
│   └── workers/              # Celery workers for async tasks (Images, deployments)
├── packages/
│   └── database/             # Shared migrations & DB configuration scripts
├── docs/                     # Specifications, architecture plans, and OpenAPI schemas
├── SYSTEM_PROMPT_PART_01.md
├── SYSTEM_PROMPT_PART_02.md
└── README.md
```

---

## 🛠️ Design Philosophy & Quality Bar

We maintain a software quality standard on par with platforms like **Stripe**, **Linear**, and **Vercel**:
*   **Decoupled Modules**: Every service is independent and replaceable.
*   **Layered Separation**: No business logic resides inside React UI components or Django View presentation layers.
*   **UUID Primary Keys**: Absolute consistency in schema design, featuring UUIDs and audit logs across all entities.
*   **Zero Compromise on Reliability**: Asynchronous task scheduling via Celery avoids blocking request pipelines.
