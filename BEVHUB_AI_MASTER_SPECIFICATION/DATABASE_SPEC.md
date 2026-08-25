# DATABASE SPECIFICATION
## RELATIONAL DATABASE SCHEMA & INDEXES

This document specifies the PostgreSQL tables, relational constraints, datatypes, and indices for the BevHub AI Platform.

---

### 1. Table: `core_tenant` (Organizations)
*   **Purpose**: Manages SaaS tenants/organizations.
*   **Fields**:
    *   `id` (UUID, Primary Key, default `gen_random_uuid()`)
    *   `company_name` (VARCHAR(150), Unique)
    *   `plan_level` (VARCHAR(50), default `'free'`) - Values: `free`, `pro`, `business`, `enterprise`
    *   `created_at` (TIMESTAMP WITH TIME ZONE, default `now()`)
*   **Indexes**:
    *   `idx_tenant_plan`: Index on `plan_level`

---

### 2. Table: `core_user` (Users)
*   **Purpose**: Authentication records and tenant association.
*   **Fields**:
    *   `id` (BIGINT, Primary Key, Auto-increment)
    *   `username` (VARCHAR(150), Unique)
    *   `email` (VARCHAR(254), Unique)
    *   `tenant_id` (UUID, Foreign Key referencing `core_tenant.id`)
    *   `preferred_language` (VARCHAR(50), default `'English'`)
    *   `created_at` (TIMESTAMP WITH TIME ZONE)

---

### 3. Table: `core_project` (Projects)
*   **Purpose**: Workspace application directories.
*   **Fields**:
    *   `id` (UUID, Primary Key)
    *   `tenant_id` (UUID, Foreign Key referencing `core_tenant.id`)
    *   `project_name` (VARCHAR(200))
    *   `subdomain` (VARCHAR(100), Unique)
    *   `design_system` (JSONB) - Theme colors, fonts, layout mode
    *   `created_at` (TIMESTAMP WITH TIME ZONE)
*   **Indexes**:
    *   `idx_project_subdomain`: Unique index on `subdomain`

---

### 4. Table: `projects_projectfile` (Source Files)
*   **Purpose**: Synthesized workspace source files.
*   **Fields**:
    *   `id` (UUID, Primary Key)
    *   `project_id` (UUID, Foreign Key referencing `core_project.id`, ON DELETE CASCADE)
    *   `path` (VARCHAR(500))
    *   `content` (TEXT)
    *   `updated_at` (TIMESTAMP WITH TIME ZONE)
*   **Indexes**:
    *   `idx_file_project_path`: Composite index on `(project_id, path)`

---

### 5. Table: `ai_aitask` (AI Agent Job Requests)
*   **Purpose**: Tracking status and progress of generation jobs.
*   **Fields**:
    *   `id` (UUID, Primary Key)
    *   `project_id` (UUID, Foreign Key referencing `core_project.id`)
    *   `prompt` (TEXT)
    *   `status` (VARCHAR(50)) - `pending`, `running`, `completed`, `failed`
    *   `progress` (INT, default `0`)
    *   `created_at` (TIMESTAMP WITH TIME ZONE)

---

### 6. Table: `core_deployment` (Deployment Snapshot History)
*   **Purpose**: Live web previews and rollback checkpoints.
*   **Fields**:
    *   `id` (UUID, Primary Key)
    *   `project_id` (UUID, Foreign Key referencing `core_project.id`)
    *   `status` (VARCHAR(50)) - `building`, `success`, `failed`
    *   `deploy_url` (VARCHAR(300))
    *   `logs` (TEXT)
    *   `created_at` (TIMESTAMP WITH TIME ZONE)

---

### 7. Table: `ai_creditbalance` & `ai_credittransaction` (Token Economy)
*   **Purpose**: Credits tracking per tenant.
*   **Fields (`ai_creditbalance`)**:
    *   `id` (UUID, Primary Key)
    *   `tenant_id` (UUID, Foreign Key referencing `core_tenant.id`)
    *   `balance` (DECIMAL(10,2))
*   **Fields (`ai_credittransaction`)**:
    *   `id` (UUID, Primary Key)
    *   `tenant_id` (UUID, Foreign Key referencing `core_tenant.id`)
    *   `amount_consumed` (DECIMAL(10,2))
    *   `task_description` (TEXT)
    *   `created_at` (TIMESTAMP WITH TIME ZONE)
*   **Indexes**:
    *   `idx_tx_tenant`: Index on `tenant_id`

---

### 8. Table: `ai_sessionrecord` & `ai_sessionstep` (AI Session Recorder)
*   **Purpose**: Step-by-step rewinding of AI decisions.
*   **Fields (`ai_sessionrecord`)**:
    *   `id` (UUID, Primary Key)
    *   `task_id` (UUID, Foreign Key referencing `ai_aitask.id`)
    *   `started_at` (TIMESTAMP WITH TIME ZONE)
    *   `completed_at` (TIMESTAMP WITH TIME ZONE)
*   **Fields (`ai_sessionstep`)**:
    *   `id` (UUID, Primary Key)
    *   `session_id` (UUID, Foreign Key referencing `ai_sessionrecord.id`)
    *   `name` (VARCHAR(200))
    *   `type` (VARCHAR(50)) - `planning`, `context_fetch`, `llm_call`, `validation`, `deploy`
    *   `status` (VARCHAR(50)) - `success`, `failed`
    *   `payload` (JSONB) - Inputs, prompt, response, or error payload
    *   `duration_ms` (INT)
    *   `timestamp` (TIMESTAMP WITH TIME ZONE)
