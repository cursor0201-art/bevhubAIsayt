# BevHub AI Subsystem Specification — Authentication & Multi-Tenancy

This document provides the technical blueprint for the **Authentication** and **Multi-Tenancy** engine in BevHub AI.

---

## 1. Overview & Objective
BevHub AI is built as a multi-tenant SaaS application. Every resource (workspace, project, page, deployment) belongs to a **Tenant**.
- **Isolation**: Tenant data must remain completely isolated. A user under Tenant A cannot view or manipulate data belonging to Tenant B.
- **Access Control**: Users have roles (`owner`, `admin`, `developer`, `viewer`) that determine permission scopes.
- **Authentication**: Stateless authentication using SimpleJWT tokens (JSON Web Tokens).

---

## 2. Database Models & Schema

### `Tenant`
Represents the organization/billing account subscribing to BevHub AI.
- `id` (UUID, PK)
- `company_name` (CharField, limit 255)
- `plan_level` (CharField choices: `free`, `growth`, `enterprise`)
- `is_active` (BooleanField, default `True`)
- `created_at` / `updated_at` / `deleted_at`

### `User`
Extends Django's `AbstractUser` and maps to a Tenant.
- `id` (UUID, PK)
- `tenant` (ForeignKey to `Tenant`, PROTECT, nullable for platform admins)
- `role` (CharField choices: `owner`, `admin`, `developer`, `viewer`, default `admin`)
- `display_name` (CharField, blank=True)
- `avatar_url` (URLField, blank=True)
- `language` / `timezone` / `country` / `theme`
- Standard AbstractUser fields: `username`, `email`, `is_staff`, `is_active`, etc.

---

## 3. JWT API Contracts

### Token Obtain (Login)
- **Endpoint**: `POST /api/token/`
- **Request Payload**:
  ```json
  {
    "username": "builder@tea.co",
    "password": "securepassword"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access": "eyJhbGciOi...",
    "refresh": "eyJhbGciOi..."
  }
  ```

### Token Refresh
- **Endpoint**: `POST /api/token/refresh/`
- **Request Payload**:
  ```json
  {
    "refresh": "eyJhbGciOi..."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access": "eyJhbGciOi..."
  }
  ```

### User Profile Info
- **Endpoint**: `GET /api/users/me/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (200 OK)**:
  ```json
  {
    "id": "e43b1850-84c2-4632-a5e2-b01c10d3e5df",
    "email": "builder@tea.co",
    "display_name": "Tea Builder",
    "role": "admin",
    "tenant": {
      "id": "a98f121e-d4c2-4a58-8b5e-001d12fc8e33",
      "company_name": "Tea Co",
      "plan_level": "growth"
    }
  }
  ```

---

## 4. Security & Permissions Layer

- **Tenant Middleware / Query Filters**:
  Every model service and view must automatically filter database queries by the current user's `tenant_id` to prevent cross-tenant exposure:
  ```python
  # Example pattern
  queryset = Project.objects.filter(tenant=request.user.tenant)
  ```
- **Role Permissions**:
  - `owner` / `admin`: Full configuration, billing access, member invites, sandbox generation.
  - `developer`: Write files, edit AST layouts, trigger deployments.
  - `viewer`: Read-only access to files, previewing sites.
