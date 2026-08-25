# BEVHUB AI Master Specification
## Section 01: Product Vision & Competitor Mapping
Version: 1.0.0
Status: ACTIVE

================================================================================
EXECUTIVE VISION
================================================================================
BevHubAI is not a simple website builder. It is an **Autonomous Software Development Enterprise** packaged as a SaaS. It empowers non-technical users, developers, and agencies to transform plain-text business models into fully functional, production-ready, edge-deployed software systems without manual coding.

The system achieves this by orchestrating a specialized network of 20 AI roles that work asynchronously to write backend APIs, database schemas, premium glassmorphism user interfaces, SEO content, and security controls.

================================================================================
COMPETITOR ANALYSIS & DIFFERENTIATORS
================================================================================
To deliver a world-class system, BevHubAI directly targets the capabilities of leading market platforms:

1.  **Cursor & Replit Agent (Code Assistants)**
    *   *Competitor Limit*: Require continuous manual interaction, terminal commands approval, and context management by the developer.
    *   *BevHubAI Differentiator*: Fully autonomous execution. The user defines the prompt once, and the multi-agent system runs background tasks (orchestrated via Django/Celery) to generate, build, test, and host the code autonomously.

2.  **Lovable & Bolt.new (Frontend App Builders)**
    *   *Competitor Limit*: Excellent frontend generation, but limited to static site hosting or simple client-side mock databases.
    *   *BevHubAI Differentiator*: Deep backend generation. The system generates actual database models, SQL schemas, API routes, and schedules workers while keeping them persistent in a virtual file system.

3.  **Vercel AI & Netlify (Hosting & Previews)**
    *   *Competitor Limit*: Purely host-based, leaving development to local tools.
    *   *BevHubAI Differentiator*: Vertical slice compilation. BevHubAI acts as the developer, code editor, visual designer, and host under a single platform, with a hot-reloaded visual interface.

================================================================================
CORE CAPABILITY TARGETS
================================================================================
- **Zero-Latency Visual Building**: Users can switch between a visual interactive drag-and-drop editor and direct file tree code editing.
- **Persistent Sandboxes**: Every tenant has their own isolated sandbox (Workspaces) with dedicated database configurations.
- **Credit-Driven Economics**: Real-time credit calculation per agent step ensures a sustainable API billing model.
- **Hot-Reload Hotfixes**: Code changes to virtual files are instantaneously compiled and visible in the preview iframe.
