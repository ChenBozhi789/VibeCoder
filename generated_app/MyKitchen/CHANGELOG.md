# CHANGELOG

## 0.1.0 - Implementation of PRD-aligned MyKitchen app
- Implemented full recipe manager:
  - Data model: { id, title, ingredients[], instructions, tags[], createdAt, updatedAt }
  - CRUD: create, edit, delete recipes
  - Search: title and ingredients
  - Filter: by tag (auto-derived from recipes)
  - Sort: updatedAt desc, title A–Z, title Z–A
  - Settings: show/hide instructions preview in list
  - Data portability: export JSON; import JSON with replace or merge mode
  - Quick action: copy ingredients to clipboard (with fallback)
- Persistence via localStorage (MyKitchen:state:v1)
- Validation: title required; at least one ingredient; reasonable lengths
- Accessibility: aria-live error messages; labeled inputs; focus management
- UI files replaced: ui/index.html, ui/css/style.css, ui/js/main.js
- Documentation: implementation_plan.md created/updated
