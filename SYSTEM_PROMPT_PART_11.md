# SYSTEM_PROMPT_PART_11.md
# NEXT.JS • REACT • TYPESCRIPT BIBLE

==================================================
MISSION
==================================================

The frontend must feel invisible.

Users should focus on building businesses,
not learning the interface.

Every interaction must be predictable.

Every screen must feel premium.

==================================================
FRAMEWORK
==================================================

Use:

Next.js App Router

React

TypeScript

TailwindCSS

Shadcn/UI

Framer Motion

TanStack Query

React Hook Form

Zod

==================================================
PROJECT STRUCTURE
==================================================

src/

app/

components/

features/

hooks/

providers/

services/

store/

types/

constants/

utils/

styles/

config/

==================================================
ROUTING
==================================================

Use App Router only.

Group routes logically.

Protect authenticated routes.

Use layouts.

Use loading.tsx.

Use error.tsx.

Use not-found.tsx.

==================================================
COMPONENT RULES
==================================================

Every component has one purpose.

Never create huge files.

Split large components.

Prefer composition.

Never duplicate UI.

==================================================
COMPONENT SIZE
==================================================

Ideal

50-150 lines

Acceptable

300 lines

Maximum

500 lines

If larger

Split immediately.

==================================================
STATE MANAGEMENT
==================================================

Server State

↓

TanStack Query

UI State

↓

React State

Global State

↓

Zustand

Never abuse global state.

==================================================
FORMS
==================================================

React Hook Form

+

Zod

Always validate.

Never trust frontend validation alone.

==================================================
API
==================================================

Never call fetch directly inside components.

Always create services.

Example

AuthService

ProjectService

BillingService

AIService

==================================================
ERROR HANDLING
==================================================

Every request supports

Loading

Success

Empty

Retry

Failure

Offline

==================================================
THEME
==================================================

Dark

Light

System

Save preference.

==================================================
RESPONSIVE
==================================================

Support

320px

375px

768px

1024px

1440px

1920px

==================================================
ACCESSIBILITY
==================================================

Keyboard

ARIA

Labels

Focus

Contrast

Screen Readers

==================================================
IMAGES
==================================================

Use next/image

Lazy Load

Optimize

Responsive

==================================================
TYPOGRAPHY
==================================================

Readable.

Consistent.

Accessible.

==================================================
ANIMATIONS
==================================================

Fast.

Natural.

Purposeful.

Never distract users.

==================================================
FINAL RULE
==================================================

Every page should feel as polished as the OpenAI dashboard.

==================================================
END OF PART 11
