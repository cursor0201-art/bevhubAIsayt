# SYSTEM_PROMPT_PART_03.md
# FRONTEND ENGINEERING BIBLE

==================================================
MISSION
==================================================

The frontend of BevHub AI must feel like a premium product.

Target quality:

OpenAI
Linear
Notion
Stripe
Apple

Every interaction should feel smooth.

Every animation should have a purpose.

Every page should load instantly.

==================================================
TECH STACK
==================================================

Next.js (App Router)

TypeScript

TailwindCSS

Shadcn UI

Framer Motion

TanStack Query

React Hook Form

Zod

Lucide Icons

==================================================
FOLDER STRUCTURE
==================================================

src/

app/

components/

features/

hooks/

services/

store/

lib/

types/

utils/

styles/

providers/

constants/

config/

==================================================
RULES
==================================================

Never place business logic inside pages.

Pages only compose components.

Business logic belongs inside features.

API logic belongs inside services.

Validation belongs inside schemas.

State belongs inside store.

Utility functions belong inside utils.

==================================================
COMPONENT RULES
==================================================

Every component must have one responsibility.

Every component must be reusable.

Never duplicate UI.

Never create huge components.

Split when larger than necessary.

Props must be typed.

No any.

==================================================
DESIGN SYSTEM
==================================================

Border Radius

Consistent.

Spacing

Based on 4px grid.

Typography

Modern.

Readable.

Large headings.

Comfortable line-height.

Icons

Lucide only.

Buttons

Primary

Secondary

Outline

Ghost

Danger

Success

Cards

Minimal.

No unnecessary borders.

Shadows only when needed.

==================================================
COLORS
==================================================

Dark Theme First.

Light Theme supported.

Primary

Modern Blue

Accent

Purple

Success

Green

Danger

Red

Warning

Orange

Neutral

Gray Scale

==================================================
RESPONSIVE DESIGN
==================================================

Support

Mobile

Tablet

Laptop

Desktop

UltraWide

4K

Never create horizontal scrolling.

==================================================
LOADING STATES
==================================================

Every async action has

Skeleton

Spinner

Progress

Retry

Timeout

==================================================
ERROR HANDLING
==================================================

Never expose server errors.

Show friendly messages.

Always provide retry.

Always log internally.

==================================================
FORMS
==================================================

Every form

Client validation

Server validation

Loading state

Success state

Error state

Accessible labels

Keyboard navigation

==================================================
PERFORMANCE
==================================================

Lazy loading

Dynamic imports

Code splitting

Optimized fonts

Optimized images

Prefetch routes

Memoization only when beneficial

==================================================
ANIMATIONS
==================================================

Framer Motion only.

Animations must be fast.

Never block interaction.

Avoid excessive movement.

Respect reduced-motion settings.

==================================================
ACCESSIBILITY
==================================================

Keyboard navigation

Visible focus

ARIA labels

Semantic HTML

Color contrast

Screen reader support

==================================================
SEO
==================================================

Unique titles

Meta description

OpenGraph

Twitter Card

Structured Data

Canonical URLs

Sitemap

Robots.txt

==================================================
QUALITY CHECKLIST
==================================================

Before shipping:

✓ Responsive

✓ Accessible

✓ Fast

✓ Typed

✓ Tested

✓ No console errors

✓ No warnings

✓ Lighthouse optimized

==================================================
FINAL RULE
==================================================

Every screen should feel like it belongs to the same premium product.

Do not chase visual complexity.

Prioritize clarity, speed and consistency.

==================================================
END OF PART 03
