# BevHub AI Subsystem Specification — Website Builder

This document provides the technical blueprint for the **Website Builder** layout and styling engine in BevHub AI.

---

## 1. Overview & Objective
The **Website Builder** translates design system tokens and copy into semantic, responsive HTML/CSS structures.
- **Design Token Injection**: Colors, typography, borders, and margins are defined inside a JSON object (`design_system`) and mapped directly into styling blocks.
- **Responsive Layout Grid**: Structured with modern CSS Grid and flex layouts to guarantee clean mobile responsiveness.
- **Modular Components**: Auto-injects common navigation headers and custom footers across all project subpages to avoid duplicate structures.

---

## 2. Database Models & Schema

### `Page`
- `id` (UUID, PK)
- `project` (ForeignKey to `Project`, CASCADE)
- `slug` (SlugField, unique per project)
- `title` (CharField, limit 255)
- `layout_ast` (JSONField representing layouts, sections, and widgets)
- `raw_content` (TextField, final generated HTML)

### Layout AST Structure (JSON Example):
```json
{
  "sections": [
    {
      "id": "hero_section",
      "type": "hero",
      "style": { "padding": "80px 24px" },
      "elements": [
        { "tag": "h1", "text": "Curated Premium Coffee", "class": "title" },
        { "tag": "p", "text": "Artisanal beans roasted weekly.", "class": "lead" }
      ]
    }
  ]
}
```

---

## 3. Styling Engine & Token Definitions

Styles are applied using custom CSS blocks defined inside `<style>` tags at the top of generated pages.

### Design System Tokens mapping:
- `--primary`: Project `design_system.primary_color` (e.g. `#8b5cf6`)
- `--secondary`: Project `design_system.secondary_color` (e.g. `#d946ef`)
- `--background`: Project `design_system.background_color` (e.g. `#0b0f19`)
- `--font`: Project `design_system.font_family` (e.g. `Outfit, sans-serif`)
- `--radius`: Project `design_system.border_radius` (e.g. `12px`)

---

## 4. Components Assembly

- **Header Component**:
  - Dynamically displays the generated project title.
  - Links to `/index` and `/products` (curated offerings).
- **Footer Component**:
  - Implements standard copyright parameters.
  - Dynamically displays SEO optimizations and description tokens.
