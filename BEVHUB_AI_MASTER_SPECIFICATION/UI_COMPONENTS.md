# UI COMPONENT SPECIFICATION
## FRONTEND COMPONENT LIBRARY & DESIGN SYSTEM

This document outlines the standard UI components, props, design tokens, and interactions for the BevHub AI Next.js frontend application.

---

### 1. Typography & Styling Tokens (CSS variables)
*   **Colors**:
    *   `--background`: `#0b0f19` (sleek deep space dark blue)
    *   `--card`: `#131926` (semi-transparent glass card)
    *   `--primary`: `#8b5cf6` (electric purple)
    *   `--accent`: `#06b6d4` (neon cyan)
    *   `--text-primary`: `#f3f4f6` (off-white)
    *   `--text-muted`: `#9ca3af` (cool gray)
*   **Font family**: `Inter`, system-ui, sans-serif.

---

### 2. Base Input & Form Components

#### Button Component (`<Button />`)
*   **Props**: `variant` (`'primary' | 'secondary' | 'danger'`), `loading` (`boolean`), `disabled` (`boolean`), `icon` (`ReactNode`).
*   **Behavior**: Highlighting hover effects with CSS scale transforms. Shows loading spinner when `loading=true`.

#### Text Input Component (`<Input />`)
*   **Props**: `placeholder` (`string`), `value` (`string`), `onChange` (`(val: string) => void`), `error` (`string`).
*   **Behavior**: Glassmorphism borders. Shifts border color to `--primary` on focus and `--danger` on input validation error.

---

### 3. Navigation & Sidebars

#### Sidebar Navigation (`<Sidebar />`)
*   **Visual Layout**:
    *   Sleek vertical sidebar. Contains Workspace selector dropdown, link list (Projects, Billing, Analytics, Settings), and profile info widget.

---

### 4. Interactive AI Workspace Components

#### File Tree Explorer (`<FileTree />`)
*   **Props**: `files` (`string[]`), `activePath` (`string`), `onFileSelect` (`(path: string) => void`).
*   **Behavior**: Collapsible folders, path icons. Click selects file and opens in code editor pane.

#### Code Workspace Editor (`<CodeEditor />`)
*   **Props**: `filePath` (`string`), `content` (`string`), `onChange` (`(val: string) => void`), `readOnly` (`boolean`).
*   **Behavior**: Integrates Monaco Editor wrapper. Configured with dark VSCode theme mapping, line numbers, autocomplete, and syntax highlighting.

#### Sandbox Viewport (`<SandboxPreview />`)
*   **Props**: `htmlContent` (`string`), `subdomain` (`string`).
*   **Behavior**: Mounts inside a isolated `<iframe>` element. Captures errors and displays load progress indicator during redeployment cycles.

---

### 5. AI Session Replay Console (`<SessionReplayConsole />`)
*   **Props**: `session` (`SessionRecord`), `onRewind` (`(stepName: string) => void`).
*   **Behavior**: Shows step-by-step progress timeline of AI task. If step is `failed`, displays error payload. Users can click any step node to rewind the workspace files history to that specific moment.
