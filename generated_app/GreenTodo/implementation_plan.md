# GreenTodo - Implementation Plan

## Overview
GreenTodo is a lightweight, offline-ready personal task manager built on the bare-bones-vanilla-main template. This plan details the technical architecture, features, data model, validation, and the implementation steps to transform the UI prototype into a fully functional app.

## Technical Architecture
- State management: Simple global state object in vanilla JavaScript; render functions re-draw UI based on state. No modules or imports.
- Persistence: localStorage with stable keys (greentodo.tasks, greentodo.settings). All CRUD operations persist immediately.
- HTML structure: Single-page app with sections for Home, Tasks (list), Details/Edit modal, Search. Routes via hash navigation; primary work happens in Tasks section.
- Error handling: Inline validation messages; try/catch around storage and JSON ops; defensive checks on DOM.
- Accessibility: ARIA labels, keyboard navigation, focus management for modals/forms, skip link maintained.

## Data Model
- Task:
  - id: string (UUID-like)
  - title: string (required, 1-200 chars)
  - description: string (0-2000 chars)
  - priority: 'low' | 'medium' | 'high' (default 'medium')
  - dueDate: string (YYYY-MM-DD) or ''
  - completed: boolean (default false)
  - createdAt: number (epoch ms)
  - updatedAt: number (epoch ms)

## Features (from PRD/spec)
- Create, Read, Update, Delete tasks
- Toggle completed status
- Filters: status (All/Active/Completed), priority, due (overdue/today/this week/all)
- Search: by title/description
- Sorting: by due date, priority, createdAt; ascending/descending
- Bulk: clear completed
- Data portability: export JSON, import JSON
- Offline: all logic local; persists via localStorage

## Implementation Phases
1) Core Infrastructure
   - Global state structure: state = { tasks: [], filters: {...}, sort: {...}, ui: {...} }
   - Storage helpers: loadTasks(), saveTasks(), exportJSON(), importJSON()
2) HTML Logic
   - Tasks section: input form for create/edit; list rendering; item actions (edit/delete/toggle)
   - Filters/search/sort controls and their event handlers
   - Details modal: reuse form for editing with focus trapping and ESC close
3) Validation
   - Title required; max lengths; dueDate format check
   - Inline error display next to fields; aria-invalid
4) Integration
   - Connect hash routes; default to #tasks
   - Wire events; re-render on state changes
5) Polish
   - Keyboard navigation; button aria-labels
   - Empty states; loading states (basic)

## File Structure Plan
- ui/index.html: Replace with accessible structure containing nav, sections, and the tasks UI controls
- ui/css/style.css: Replace with styles for layout, form, list, modal, responsiveness
- ui/js/main.js: Replace with full business logic (state, storage, rendering, events, validation)

## UI Sections and Logic
- Home: brief intro
- Tasks (primary):
  - Controls: search input, status filter tabs, priority filter, due filter, sort select, export/import, clear completed
  - Form: Add/Edit task form (title, description, priority, dueDate)
  - List: Task items with title, badges (priority, due), actions (toggle, edit, delete)
- Details: Modal used for edit (optional route)
- Search: Mirrors controls; route preserved but Tasks handles rendering

## Validation Rules
- Title: required, trim(), 1-200 chars
- Description: optional, <= 2000 chars
- Priority: one of low|medium|high
- Due date: optional; if provided must be valid YYYY-MM-DD

## Error Handling
- Storage failures: try/catch with user feedback (alert banner)
- Import failures: parse errors communicated to user
- Defensive DOM selection; null checks; noop on missing elements

## State Flow
- Any mutation (create/update/delete/toggle/import/clear) -> save -> render()
- Filters/search/sort update -> render()
- Modal open for edit sets ui.editingId and pre-fills form

## Testing Checklist
- Create/Edit/Delete works; persistence survives refresh
- Toggle completed; status filters reflect counts
- Search finds by title/description
- Priority and due filters combine with search and status
- Sorting asc/desc works for chosen field
- Export downloads JSON; Import merges or replaces (replace option chosen here)
- Clear completed removes all completed tasks

## Notes
- No modules; script loaded via js/main.js; file:// friendly
- Keep IDs stable; avoid fragmenting into multiple files

## Manual Validation Report
- Index/JS/CSS present and replaced.
- Missing elements: None
- Section/Asset checks:
  - Has section #home: OK
  - Has section #tasks: OK
  - Has section #search: OK
  - Links js/main.js: OK
  - Links css/style.css: OK
- JS logic checks:
  - Uses localStorage key greentodo.tasks: OK
  - Defines render(): OK
  - Handles form submit: OK
  - Implements export/import: OK
  - Routing via hashchange: OK
## Finalization

- Manual validation passed:
  - All required UI elements exist and match JS references.
  - Sections and asset links are correct.
  - Core JS logic present: render(), localStorage, routing, form submit, import/export.
- Deliverables:
  - implementation_plan.md (created and updated with manual validation)
  - Modified ui/index.html, ui/css/style.css, ui/js/main.js
  - CHANGELOG.md (created)
- Next steps for testing:
  - Open ui/index.html in a browser.
  - Create/Edit/Delete tasks; toggle complete; apply filters; search; change sorting.
  - Export JSON and re-import to verify data portability.
  - Clear completed tasks and verify persistence across reloads.
