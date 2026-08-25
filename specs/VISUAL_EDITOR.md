# BevHub AI Subsystem Specification — Visual Editor

This document provides the technical blueprint for the **Visual Editor** and version snapshots in BevHub AI.

---

## 1. Overview & Objective
The **Visual Editor** enables real-time visual editing of generated web pages.
- **AST Mutations**: Instead of direct HTML text edits, edits modify the page `layout_ast`. The server then compiles the updated AST into raw HTML.
- **Undo / Redo / Snapshot History**: Tracks project snapshots (`ProjectVersion`) on major layout updates to allow rollbacks.

---

## 2. Database Models & Schema

### `ProjectVersion`
- `id` (UUID, PK)
- `project` (ForeignKey to `Project`, CASCADE)
- `version_number` (IntegerField)
- `layout_ast_snapshot` (JSONField containing a dictionary of page slug to AST mapping)
- `design_system_snapshot` (JSONField)
- `created_by` (ForeignKey to `User`, SET_NULL)
- `description` (CharField, blank=True)

---

## 3. AST Manipulation API Contracts

### Update Page Layout AST
- **Endpoint**: `PUT /api/pages/<uuid>/ast/`
- **Request Payload**:
  ```json
  {
    "layout_ast": {
      "sections": [
        {
          "id": "hero_section",
          "type": "hero",
          "elements": [
            { "tag": "h1", "text": "New Visual Heading Title" }
          ]
        }
      ]
    }
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "id": "e44c2055-6677-44aa-bb88-dd99cc11ff22",
    "slug": "index",
    "title": "Home",
    "layout_ast": { ... },
    "raw_content": "<!DOCTYPE html><html>... <h1>New Visual Heading Title</h1> ...</html>"
  }
  ```

---

## 4. History Rollback Contracts

### Create Restore Snapshot
- **Endpoint**: `POST /api/projects/<uuid>/versions/`
- **Request Payload**:
  ```json
  {
    "description": "Pre-launch copywriting updates"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "version_number": 4,
    "created_at": "2026-07-13T16:20:00Z"
  }
  ```

### Rollback to Version
- **Endpoint**: `POST /api/projects/<uuid>/versions/restore/`
- **Request Payload**:
  ```json
  {
    "version_number": 2
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "restored",
    "active_version": 2
  }
  ```
