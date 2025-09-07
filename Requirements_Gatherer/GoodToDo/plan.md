# GoodToDo — Development Plan

## Overview
GoodToDo is a local-first, single-page web app that provides a simple personal to-do list. It runs entirely in the browser with no backend. All user data stays on the device and users can export/import their tasks as JSON for backup or migration.

## Functional Requirements
### Key features (MVP)
- Add a new task with title (required) and optional description, due date, priority, and tags.
- Edit existing tasks.
- Delete tasks.
- Mark tasks complete/incomplete.
- Filter and sort tasks (by due date, priority, completed status).
- Persist all data locally in the browser.
- Export tasks to a JSON file and import from a JSON file.
- Offline-first behavior and ability to install as a Progressive Web App (optional, see notes).

### User stories (with acceptance criteria)
| ID | User story | Acceptance criteria |
|---|---|---|
| US-01 | As a user, I can add a task with a title so I can record something to do. | When I enter a non-empty title and save, the task appears in the list with timestamp. |
| US-02 | As a user, I can edit a task so I can correct or change details. | Changes persist and updatedAt is modified; UI reflects changes immediately. |
| US-03 | As a user, I can mark a task complete/incomplete so I know what is done. | Completed tasks show a visual indicator and can be toggled. |
| US-04 | As a user, I can export my tasks to JSON so I can back them up. | Export downloads a .json file with the full data structure. |
| US-05 | As a user, I can import tasks from a JSON file so I can restore data. | Import validates file schema and merges or replaces tasks as chosen. |

## Non-Functional Requirements
- Performance: Load and be interactive in under 1s on modern desktop browsers; handle 5,000 tasks with acceptable responsiveness (UI operations <200ms).
- Accessibility: Target WCAG 2.1 AA where practical (keyboard navigation, labels for screen readers, contrast ratios).
- Offline-first: App must work when offline; use a Service Worker to cache assets and shell for reliable offline start.
- Privacy/Security: Data never leaves the device unless user explicitly exports it. No external analytics by default.
- Size: Keep initial bundle small (< 200 KB minified for vanilla/lean frameworks) to speed load.

## UI/UX Design
### High-level layout
- Single-page layout with a left/top toolbar and primary task list view.
- Components:
  - Header with app name and actions (Export, Import, Settings).
  - Quick-add input for creating a task (title + expand for details).
  - Task list: each row/card shows title, due date, priority, tags, and completion checkbox.
  - Filters bar: search, sort (dueDate, priority), toggle show/hide completed.
  - Detail panel / modal to edit full task details.

### Screens / Dialogs
- Main screen (task list + quick-add + filters) — one primary view.
- Edit task modal / slide-over panel.
- Import dialog with file picker and import options (merge vs replace).
- Settings dialog for preferences (theme, PWA install prompt, accessibility options).

### Design notes
- Keep design clean and minimal (focus on quick task entry and scanning the list).
- Use a light and dark theme toggle (simple CSS variables).
- Responsive layout: single-column on narrow screens (mobile), wider list on desktop.

## Data Model
- Storage: Use IndexedDB (via a small wrapper) for reliable structured storage and better performance for larger datasets. Use localStorage only for small UI preferences and caching pointers.

### Schema (Task record)
| Field | Type | Notes |
|---|---|---|
| taskId | string (UUID) | Primary key |
| title | string | required, max 200 |
| description | string | optional |
| createdAt | string (ISO datetime) | auto-filled |
| updatedAt | string (ISO datetime) | updated on edits |
| dueDate | string (ISO date) | optional |
| completed | boolean | default: false |
| priority | string enum | one of [low, medium, high], default: medium |
| tags | array of strings | optional, each max 50 chars |

## Validation & Edge Cases
- Input validation:
  - Title required; show inline error if empty.
  - Due date must be a valid date.
  - Tag lengths and count enforced.
- Import validation:
  - Validate JSON schema before applying. If schema mismatch, show a clear error and refuse import.
  - Offer user choice: merge (skip duplicates by taskId), replace (clear existing then import), or cancel.
- Edge cases:
  - Empty list: show friendly empty state with tips to add first task.
  - Large dataset: paginate or virtualize list (use windowing) to keep UI responsive.
  - Corrupted IndexedDB: detect and offer export (best-effort) then reset DB after user confirmation.

## Storage & Persistence
- Local-first: all data stored client-side in IndexedDB.
- Service Worker: cache app shell and assets to enable offline usage and fast reloads. Use workbox or simple service worker strategies.
- Backup/Export: user can download a JSON file containing all tasks and metadata (timestamped filename). The import flow validates and applies data.

> Note: Data never sent to any server unless the user explicitly exports and uploads it elsewhere.

## Implementation Plan
### Tech choices (recommendation)
- Framework: Vanilla JavaScript with small libraries OR a lightweight framework like Svelte or Preact for a small bundle. (Svelte preferred for small apps if familiarity exists.)
- Storage: IndexedDB via idb (small wrapper) for simplicity.
- Build: Vite for fast builds and dev server.
- Styling: CSS variables + small utility (Tailwind optional) — but lean CSS recommended for small size.

### Project structure (example)

GoodToDo/
- index.html
- src/
  - main.js (app bootstrap)
  - App.js / App.svelte
  - components/
    - TaskList.js
    - TaskItem.js
    - TaskEditor.js
    - Toolbar.js
    - ImportExport.js
  - db/
    - index.js (IndexedDB wrapper)
    - migrations.js
  - sw/
    - service-worker.js
  - styles/
    - variables.css
    - layout.css
- public/
  - manifest.json
- package.json
- vite.config.js

### Important implementation notes
- Use feature detection for IndexedDB and fall back to an in-memory store with a clear warning if unavailable.
- Keep export/import operations safe and provide confirmation dialogs for destructive actions.

## Quality Assurance Checklist
- [ ] Core CRUD operations: add/edit/delete tasks work correctly.
- [ ] Mark complete/incomplete toggles persist and reflect immediately.
- [ ] Export to JSON produces a downloadable file with the expected schema.
- [ ] Import from JSON validates schema and supports merge/replace.
- [ ] App loads and works offline (Service Worker caches assets).
- [ ] Data persists across reloads and browser restarts.
- [ ] Handles large task lists without UI freeze (virtualization/pagination tested).
- [ ] Accessibility checks: keyboard-only navigation, ARIA labels, screen reader verification.
- [ ] Responsive layout: usable on mobile and desktop screen sizes.
- [ ] Error handling: corrupted DB, failed import, invalid input.

## Success Criteria ✅
- The app runs entirely in the browser and all features work without a network connection.
- User can export and import tasks in JSON reliably.
- CRUD operations are stable and tested across common browsers (Chrome, Firefox, Edge).
- No critical accessibility blockers; keyboard navigation and screen reader basics work.

## Future Enhancements
- Optional cloud sync (user opt-in) for cross-device sync.
- Reminders/notifications and calendar integration.
- Recurring tasks and smart suggestions.
- Themes and advanced filtering/boards (kanban).

## QA Review (from QA Agent)
- The plan covers the explicit user inputs: personal to-do list and JSON backup.
- Several UI/behaviour details were not provided; the plan uses reasonable defaults and marks those as assumptions to confirm with the user.
- Action: Before implementation, confirm the open questions listed in the user requirements to avoid rework.

> 💡 Tip: If you want, we can run a short follow-up Q&A to lock down UI choices (compact vs. card list, whether reminders are needed, and PWA install preference).