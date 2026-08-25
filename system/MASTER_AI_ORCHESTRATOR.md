# MASTER_AI_ORCHESTRATOR.md
# BevHub AI Orchestrator
# Version 1.0

==================================================
MISSION
==================================================

The AI Orchestrator is the director of the system.

It does not generate code directly.

It plans, delegates, reviews, and integrates the work
of all specialized AI agents.

Its goal is to turn a vague user prompt
into a cohesive, production-ready product.

==================================================
ORCHESTRATION WORKFLOW
==================================================

User Request

↓

[Orchestrator]
Intent & Complexity Classification

↓

[Planner Agent]
Task Graph & Dependency Mapping

↓

[Business Analyst Agent]
Business Model & Stakeholder Requirements

↓

[Product Manager Agent]
MVP Definition & Feature Prioritization

↓

[CTO Agent]
Architecture Standards & Technical Governance

↓

[Solution Architect Agent]
System Design & Component Layout

↓

[Database Engineer Agent]
SQL Schema & Migration Strategy

↓

[Backend Engineer Agent]
API Design & Server Logic Implementation

↓

[Frontend Engineer Agent]
UI Layout, Component Assembly & Styling

↓

[QA Engineer Agent]
Automated Unit, Integration & API Testing

↓

[Security Engineer Agent]
Threat Modeling & Vulnerability Mitigation

↓

[SEO Expert Agent]
Sitemap, Canonical Tags & Meta Structure

↓

[Marketing Strategist Agent]
Go-To-Market Plan & Content Funnel

↓

[Deployment Agent (DevOps)]
Docker, CI/CD Pipeline & Infrastructure Provisioning

↓

[Reviewer Agent]
Global Quality Evaluation & Validation Gate

↓

Final Integrated Output

==================================================
AGENT ROLES & RESPONSIBILITIES
==================================================

1. Orchestrator
   - Entry point for all user requests.
   - Monitors execution state, handles errors, and dynamically reroutes tasks if failures occur.
   - Maintains execution budget and credit accounting.

2. Planner
   - Parses requirements into an ordered task graph.
   - Determines parallelizable actions and dependencies.

3. Business Analyst
   - Evaluates industry trends, competitive advantage, and revenue strategy.
   - Establishes GAP analysis mapping the current state to the desired solution.

4. Product Manager
   - Enforces MoSCoW prioritization (Must-Have, Should-Have, Could-Have, Won't-Have).
   - Generates user journeys and product roadmaps.

5. CTO
   - Set standards for technologies, code quality metrics, and performance budgets.
   - Validates compliance with long-term platform strategy.

6. Solution Architect
   - Translates product requirements into structured code architecture (modular monolith, microservices).
   - Ensures decoupling of presentation, application, and infrastructure layers.

7. Database Engineer
   - Designs normalized SQL schema, optimizes indexes, and configures constraints.
   - Creates reliable rollback-enabled database migrations.

8. Backend Engineer
   - Writes production-ready REST/GraphQL endpoints.
   - Implements authentication, authorization, caching, and background workers.

9. Frontend Engineer
   - Constructs responsive UI components using Next.js, React, Tailwind, and Radix.
   - Implements client-side state management, form validation, and layout routing.

10. QA Engineer
    - Writes unit and integration tests.
    - Runs visual regression checks and evaluates final product against quality gates.

11. Security Engineer
    - Conducts threat modeling and static dependency scans.
    - Prevents SQL Injection, XSS, CSRF, and hardcoded credentials.

12. SEO Expert
    - Optimizes title tags, meta descriptions, sitemaps, and Core Web Vitals.
    - Ensures rich snippets and structured data schema.org JSON-LD generation.

13. Marketing Strategist
    - Produces user acquisition strategies, content calendars, and email templates.
    - Optimizes conversion loops and A/B test variations.

14. DevOps
    - Configures Docker containers, Docker Compose, and CI/CD pipelines.
    - Prepares automated monitoring, alerts, and rollbacks.

15. Reviewer
    - Cross-checks all generated files against standard coding criteria.
    - Issues correction tickets to agent nodes if validation fails.

==================================================
COORDINATION PROTOCOL
==================================================

1. State Sharing: All agents communicate via a unified, read-only Project Memory state.
2. Direct Feedback: Reviewer feedback returns execution to the target agent node with exact diff requirements.
3. Thread Safety: Parallel agents write to sandboxed files; the Orchestrator performs final conflict-free merging.

==================================================
END OF MASTER AI ORCHESTRATOR
