# BevHub AI Subsystem Specification — Deployment

This document provides the technical blueprint for the **Deployment** system in BevHub AI.

---

## 1. Overview & Objective
The **Deployment** module handles building the synthesized project files (using Docker, node static build, or edge publishing) and provisioning live preview subdomains.
- **Log Streaming**: Captures build output and stores it in the database for debugging.
- **Preview Domains**: Generates isolated `https://<subdomain>.bevhub.ai` links pointing to the static page bundle.

---

## 2. Database Model & Schema

### `Deployment`
- `id` (UUID, PK)
- `project` (ForeignKey to `Project`, CASCADE)
- `status` (CharField choices: `queued`, `building`, `success`, `failed`, default `queued`)
- `commit_hash` (CharField, blank=True)
- `deploy_url` (URLField, nullable)
- `logs` (TextField containing build scripts output)
- `created_at` / `updated_at` / `deleted_at`

---

## 3. API Contracts

### Trigger Deployment
- **Endpoint**: `POST /api/projects/<uuid>/deploy/`
- **Request Payload**: `{}`
- **Response (202 Accepted)**:
  ```json
  {
    "deployment_id": "d77b83aa-99bb-44cc-88dd-11eecc22ff33",
    "status": "queued"
  }
  ```

### Get Deployment Logs & Status
- **Endpoint**: `GET /api/deployments/<uuid>/`
- **Response (200 OK)**:
  ```json
  {
    "id": "d77b83aa-99bb-44cc-88dd-11eecc22ff33",
    "status": "building",
    "deploy_url": null,
    "logs": "Step 1/3: Reading file assets...\nStep 2/3: Validating HTML configurations...\n"
  }
  ```

---

## 4. Asynchronous Build Worker (Celery task)

When a deployment is triggered:
1. An `AITask` or Celery build job is queued.
2. The worker retrieves the project's `ProjectFile` records.
3. It bundles the files, triggers static builds, or writes the static files to an edge bucket directory (e.g. AWS S3 or a local path served by Nginx).
4. The deployment status is updated to `success` or `failed`, and the `deploy_url` is saved.
