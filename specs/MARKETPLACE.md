# BevHub AI Subsystem Specification — Marketplace & Templates

This document provides the technical blueprint for the **Marketplace** system in BevHub AI.

---

## 1. Overview & Objective
The **Marketplace** allows developers and agencies to list and install custom page designs, branding sets, and agent plugins.
- **Sharing**: Users can share their project layout ASTs as templates.
- **Installation**: One-click install clones a marketplace layout AST directly into a project page.

---

## 2. Conceptual Schema

### `MarketplaceItem`
- `id` (UUID, PK)
- `name` (CharField, limit 255)
- `description` (TextField)
- `item_type` (CharField choices: `template`, `design_preset`, `plugin`)
- `layout_ast_payload` (JSONField containing the layout structure)
- `price_usd` (DecimalField, for paid items)
- `author` (ForeignKey to `User`)
- `downloads_count` (IntegerField)

---

## 3. API Contracts

### List Marketplace Templates
- **Endpoint**: `GET /api/marketplace/?type=template`
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "e44c2055-6677-44aa-bb88-dd99cc11ff22",
      "name": "Luxury Coffee Landing",
      "description": "Minimalist dark theme landing page design.",
      "item_type": "template",
      "price_usd": "0.00",
      "downloads_count": 142
    }
  ]
  ```

### Install Template to Project Page
- **Endpoint**: `POST /api/marketplace/<uuid>/install/`
- **Request Payload**:
  ```json
  {
    "project_id": "abc12344-5566-7788-9900-aabbccddeeff",
    "target_slug": "landing-page"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "installed",
    "page": {
      "id": "d88b22cc-33dd-44ee-55ff-66aa77bb88cc",
      "slug": "landing-page",
      "title": "Luxury Coffee Landing"
    }
  }
  ```
---

## 4. Security Verification
All templates submitted to the marketplace must run through an sanitization utility to ensure:
- No malicious external JavaScript scripts are inside layout widgets.
- Style variables are fully normalized and don't overwrite global dashboard styles.
