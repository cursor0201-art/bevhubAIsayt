# BevHub AI Subsystem Specification — Projects

This document provides the technical blueprint for the **Projects** data layer in BevHub AI.

---

## 1. Overview & Objective
A **Project** represents a logical website codebase containing virtual files, templates, pages, assets, deployments, and styling details.
- **Subdomain Routing**: Each project is assigned a unique, slugified subdomain under `*.bevhub.ai` for automated previews.
- **Design System Tokens**: Projects maintain styling details (`primary_color`, `font_family`, `border_radius`) in a JSON database schema which is injected into the templates.
- **Virtual Filesystem**: Contains project assets (`ProjectFile` and `Page` objects) to decouple building from local OS path dependencies.

---

## 2. Database Models & Schema

### `Project`
- `id` (UUID, PK)
- `tenant` (ForeignKey to `Tenant`, CASCADE)
- `workspace` (ForeignKey to `Workspace`, CASCADE, nullable)
- `owner` (ForeignKey to `User`, PROTECT)
- `project_name` (CharField, limit 255)
- `subdomain` (CharField, unique, index)
- `custom_domain` (CharField, unique, nullable, index)
- `design_system` (JSONField mapping color and typography tokens)
- `prompt` (TextField)
- `status` (CharField default `active`)
- `version` (IntegerField default 1)

### `ProjectFile`
- `id` (UUID, PK)
- `project` (ForeignKey to `Project`, CASCADE, related_name `files`)
- `path` (CharField, max 512, unique per project)
- `content` (TextField)

---

## 3. API Contracts

### Create Project Shell
- **Endpoint**: `POST /api/projects/`
- **Request Payload**:
  ```json
  {
    "workspace_id": "e44c2055-6677-44aa-bb88-dd99cc11ff22",
    "project_name": "Luxury Tea Subscription",
    "prompt": "Luxury tea box delivery services"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "abc12344-5566-7788-9900-aabbccddeeff",
    "project_name": "Luxury Tea Subscription",
    "subdomain": "luxury-tea-subscription-123",
    "status": "active"
  }
  ```

### Get Project Filesystem
- **Endpoint**: `GET /api/projects/<uuid>/files/`
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "99aa88bb-77cc-66dd-55ee-44ff33aa22bb",
      "path": "README.md",
      "size": 1024
    },
    {
      "id": "77aa88cc-88dd-99ee-11ff-22aa33bb44cc",
      "path": "src/pages/index.html",
      "size": 4096
    }
  ]
  ```

### Retrieve File Content
- **Endpoint**: `GET /api/projects/<uuid>/files/read/?path=src/pages/index.html`
- **Response (200 OK)**:
  ```json
  {
    "path": "src/pages/index.html",
    "content": "<!DOCTYPE html><html><body>...</body></html>"
  }
  ```

---

## 4. Subdomain Generation Rules
To prevent subdomain clashes:
- Run string cleanup (lowercase, remove non-alphas).
- Truncate to 60 characters.
- Check existence. If duplicates exist, append a secure random 4-digit numeric string (e.g. `-1245`).
