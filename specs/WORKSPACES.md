# BevHub AI Subsystem Specification — Workspaces

This document provides the technical blueprint for the **Workspaces** layer in BevHub AI.

---

## 1. Overview & Objective
A **Workspace** is an isolated logical sandbox inside a Tenant's account. It acts as a project container where users can run specialist agents, test ideas, and allocate generation credits.
- **Scoping**: All projects must exist within a workspace.
- **Configurability**: Workspaces have a `settings` JSON field to store workspace-wide environment configurations, API integrations, and developer preferences.

---

## 2. Database Model & Schema

### `Workspace`
- `id` (UUID, PK)
- `tenant` (ForeignKey to `Tenant`, CASCADE)
- `name` (CharField, limit 255)
- `settings` (JSONField, default `dict`, blank=True)
- `created_at` / `updated_at` / `deleted_at`

#### Common Settings Keys:
```json
{
  "default_model": "gpt-4o",
  "deployment_region": "us-east-1",
  "branding_preset": "elegant_dark",
  "allowed_domains": ["sandbox.bevhub.ai"]
}
```

---

## 3. API Contracts

### List Workspaces
- **Endpoint**: `GET /api/workspaces/`
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "e44c2055-6677-44aa-bb88-dd99cc11ff22",
      "name": "Tea Sandbox",
      "settings": {
        "default_model": "gemini-1.5-pro"
      },
      "created_at": "2026-07-12T10:00:00Z"
    }
  }
  ```

### Create Workspace
- **Endpoint**: `POST /api/workspaces/`
- **Request Payload**:
  ```json
  {
    "name": "Dev Sandbox",
    "settings": {
      "default_model": "gemini-1.5-pro"
    }
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "f55d3166-7788-55bb-cc99-ee00dd22aa33",
    "name": "Dev Sandbox",
    "settings": {
      "default_model": "gemini-1.5-pro"
    }
  }
  ```

### Update Workspace Settings
- **Endpoint**: `PATCH /api/workspaces/<uuid>/`
- **Request Payload**:
  ```json
  {
    "settings": {
      "default_model": "claude-3-5-sonnet",
      "allowed_domains": ["custom-domain.com"]
    }
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "id": "f55d3166-7788-55bb-cc99-ee00dd22aa33",
    "name": "Dev Sandbox",
    "settings": {
      "default_model": "claude-3-5-sonnet",
      "allowed_domains": ["custom-domain.com"]
    }
  }
  ```

---

## 4. Multi-Tenant Constraints

- Query queryset is strictly locked:
  ```python
  class WorkspaceViewSet(viewsets.ModelViewSet):
      def get_queryset(self):
          return Workspace.objects.filter(tenant=self.request.user.tenant)
  ```
- On workspace creation, the system must automatically inject the requesting user's `tenant` model to ensure complete data integrity.
