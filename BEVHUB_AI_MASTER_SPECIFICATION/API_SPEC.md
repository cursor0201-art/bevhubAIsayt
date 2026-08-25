# API CONTRACT SPECIFICATION
## FRONTEND TO BACKEND REST CONTRACTS

This document outlines the JSON request/response structures, authorization requirements, and endpoint handlers for the BevHub AI REST API.

---

### 1. Authentication Endpoints

#### POST `/api/auth/register/`
*   **Method**: `POST`
*   **Request Payload**:
    ```json
    {
      "username": "developer101",
      "email": "dev@bevhub.ai",
      "password": "SecretPassword123"
    }
    ```
*   **Success Response (201 Created)**:
    ```json
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": { "id": 1, "username": "developer101", "email": "dev@bevhub.ai" }
    }
    ```

---

### 2. Workspace & Projects Endpoints

#### GET `/api/projects/`
*   **Method**: `GET`
*   **Headers**: `Authorization: Bearer <token>`
*   **Success Response (200 OK)**:
    ```json
    [
      {
        "id": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
        "project_name": "Luxury Watches",
        "subdomain": "luxury-watches",
        "design_system": { "colors": ["#111", "#fff"], "font": "Inter" },
        "created_at": "2026-07-15T08:00:00Z"
      }
    ]
    ```

#### POST `/api/projects/`
*   **Method**: `POST`
*   **Request Payload**:
    ```json
    {
      "project_name": "E-Commerce portal",
      "subdomain": "my-ecommerce",
      "design_system": { "colors": ["#8b5cf6"] }
    }
    ```
*   **Success Response (201 Created)**:
    ```json
    {
      "id": "e2f3a4b5-c6d7-8e9f-0a1b-2c3d4e5f6a7b",
      "project_name": "E-Commerce portal",
      "subdomain": "my-ecommerce"
    }
    ```

---

### 3. Codebase / Files Endpoints

#### GET `/api/projects/{project_id}/files/`
*   **Method**: `GET`
*   **Success Response (200 OK)**:
    ```json
    [
      { "path": "README.md", "updated_at": "2026-07-15T08:00:00Z" },
      { "path": "src/pages/index.html", "updated_at": "2026-07-15T08:01:00Z" }
    ]
    ```

#### GET `/api/projects/{project_id}/files/detail/?path={path}`
*   **Method**: `GET`
*   **Success Response (200 OK)**:
    ```json
    {
      "path": "src/pages/index.html",
      "content": "<!DOCTYPE html><html><body>Home</body></html>"
    }
    ```

#### PUT `/api/projects/{project_id}/files/detail/`
*   **Method**: `PUT`
*   **Request Payload**:
    ```json
    {
      "path": "src/pages/index.html",
      "content": "Updated content..."
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    { "status": "saved" }
    ```

---

### 4. AI Orchestration Tasks

#### POST `/api/tasks/`
*   **Method**: `POST`
*   **Request Payload**:
    ```json
    {
      "project_id": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
      "prompt": "Add a Dark Mode toggle to the home screen."
    }
    ```
*   **Success Response (202 Accepted)**:
    ```json
    {
      "task_id": "t1u2v3w4-x5y6-7z8a-9b0c-d1e2f3a4b5c6",
      "status": "pending",
      "progress": 0
    }
    ```

#### GET `/api/tasks/{task_id}/`
*   **Method**: `GET`
*   **Success Response (200 OK)**:
    ```json
    {
      "task_id": "t1u2v3w4-x5y6-7z8a-9b0c-d1e2f3a4b5c6",
      "status": "completed",
      "progress": 100,
      "logs": ["Planning completed", "Code generated", "Verification passed"]
    }
    ```

---

### 5. AI Session Recording Endpoints

#### GET `/api/sessions/{session_id}/`
*   **Method**: `GET`
*   **Success Response (200 OK)**:
    ```json
    {
      "sessionId": "session-101",
      "taskPrompt": "Build a dashboard app",
      "steps": [
        {
          "name": "Planning step",
          "type": "planning",
          "status": "success",
          "payload": { "tasksCount": 5 },
          "durationMs": 120
        }
      ]
    }
    ```

#### POST `/api/sessions/{session_id}/rewind/`
*   **Method**: `POST`
*   **Request Payload**:
    ```json
    {
      "stepName": "Planning step"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "status": "rewound",
      "activeSteps": [
        { "name": "Planning step", "type": "planning", "status": "success" }
      ]
    }
    ```
