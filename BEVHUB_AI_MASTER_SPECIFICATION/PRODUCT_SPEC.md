# PRODUCT SPECIFICATION
## BEVHUB AI PRODUCT FLOW & SCREEN SPECIFICATION

This document outlines the user interface, screens, visual elements, and interactive flows for the BevHub AI Platform.

---

### Screen 1: Landing Page
*   **Purpose**: Introduce BevHub AI, explain the multi-agent code generation model, show real-time statistics, and drive sign-ups.
*   **Visual Layout**:
    *   **Hero Section**: Sleek dark HSL background with animated gradient mesh (purple/cyan). Large display font: *"Build Products, Not Just Code"*. Single unified prompt input field (simulate MVP request).
    *   **Features Grid**: 4 pillars (Context precise selector, Task Planner graph, Resilience Simulator, Quality Verification proof).
    *   **Interactive Demo**: Mock terminal output showing multi-agent workspace coordination in real time.
*   **Actions & Transitions**:
    *   Clicking **"Get Started for Free"** or submitting the hero prompt redirects the user to the Signup/Login Screen.

---

### Screen 2: Login & Signup Screen
*   **Purpose**: Secure registration and entry.
*   **Visual Layout**:
    *   Clean glassmorphism auth card on a minimalist dark background.
    *   OAuth options (GitHub, Google) + Email/Password fields.
*   **Actions & Transitions**:
    *   Upon successful auth, redirects to the **Dashboard Screen**.

---

### Screen 3: Dashboard (Workspaces & Projects)
*   **Purpose**: Manage teams (workspaces) and active generation pipelines (projects).
*   **Visual Layout**:
    *   **Sidebar**: Workspace Selector, Projects list, Billing status, API Keys manager, User profile.
    *   **Main Workspace Grid**:
        *   Workspace selector (switch between Personal, Enterprise).
        *   **"Create New Project"** CTA card.
        *   Active projects list with status badges (`active`, `building`, `failed`), live subdomain URL, and credit consumption analytics.
*   **Actions & Transitions**:
    *   Clicking **"Create New Project"** opens the **AI Chat / Generation Interface**.
    *   Clicking an existing project opens the **AI Builder / Workspace**.

---

### Screen 4: AI Chat & Builder Workspace (The Workspace Hub)
*   **Purpose**: The central control center combining Chat, File Browser, Code Editor, and Live Preview.
*   **Visual Layout (3-Column Layout)**:
    *   **Left Column (AI Assistant)**:
        *   Chat message stream with markdown formatting and syntax highlighting.
        *   Integrated prompt context chip selector (attach Git logs, Database schema, API docs).
        *   Provider selector (Model Router auto-selection badge showing which model is currently active/cheapest).
        *   Session recording timeline ("Replay execution history" button).
    *   **Center Column (File Browser & Code Editor)**:
        *   Collapsible tree selector showing project directory structure.
        *   Tabbed text editor (monaco-like interface) showing actual synthesized source files.
    *   **Right Column (Live Preview / Sandbox)**:
        *   Active viewport rendering HTML/CSS page templates.
        *   Log stream terminal displaying Formal Verification violations (if any), Quality checks, and deployment logs.
*   **Actions & Transitions**:
    *   Clicking **"Deploy"** triggers the Deployment Engine, assigning a preview URL and creating an immutable rollback snapshot.
    *   Clicking **"Undo/Redo"** restores file tree versions.
