# NMITTodo — Development Plan

## Overview
NMITTodo is a lightweight, local-first single-page application (SPA) designed for students to capture and manage personal tasks and deadlines. The app runs entirely in the browser (no server). It focuses on a fast, minimal interface for adding, editing, completing, and deleting tasks with optional due dates.

> Users: students who need a simple way to track assignments and study tasks without relying on cloud services.

## Functional Requirements
### Core features
- Add a task with a title and optional due date.
- Edit a task's title and due date.
- Mark a task completed/uncompleted.
- Delete a task.
- List view of tasks sorted by due date and creation time.
- Export/import (backup and restore) tasks as a JSON file (recommended safety feature since data is local-only).

### User stories & acceptance criteria
| ID | User story | Acceptance criteria |
|---|---|---|
| FR-1 | As a student, I can add a task so I remember a to-do item. | A task with a title (required) and optional due date is saved and appears in the list with createdAt timestamp. |
| FR-2 | As a student, I can edit a task so I can update details. | Editing updates the task fields and updatedAt timestamp; changes persist after reload. |
| FR-3 | As a student, I can mark tasks as completed. | Completed tasks toggle state and visually indicate completion; state persists. |
| FR-4 | As a student, I can delete a task. | Deleting removes the task after a confirmation and it no longer appears after reload. |
| FR-5 | As a student, I can export my tasks to a file and import them later. | Export downloads a JSON file; import accepts a valid JSON file and merges or replaces tasks per user's choice. |

## Non-Functional Requirements
- Performance: App should load quickly (< 1s on modern devices) and handle at least several thousand tasks with acceptable UI performance (virtualized list if needed).
- Offline-first: Fully usable offline after the first load (Service Worker to cache static assets and app shell).
- Accessibility: Aim for WCAG 2.1 AA where practical — keyboard navigation, meaningful ARIA labels, focus management, and readable color contrast.
- Privacy & Security: All user data stays on the device. No external network requests for user data. Exports are user-initiated files.
- Size: Keep the production bundle small (ideally < 200 KB gzipped) for fast load on mobile.

## UI/UX Design
### High level
- Single-page layout with a left/top header and main content area showing the task list.
- Simple controls to add a task (title + due date) at the top of the list or in a floating dialog.
- Each task shows title, due date (if present), createdAt/updatedAt metadata (small), and actions: Edit, Toggle Complete, Delete.
- Filtering/sorting controls: sort by due date, created date, or completed state.
- Empty state: friendly message guiding user to add their first task.

### Screens / Components
- App Shell / Header
  - App title, Export button, Import button, PWA install prompt (if supported).
- Task Entry Area
  - Input for title (required), optional date/time picker, Add button.
- Task List
  - List item with checkbox (complete), title, due date, edit button, delete button.
- Task Edit Dialog / Inline Editor
  - Same fields as Task Entry Area plus Save/Cancel.
- Confirmation Dialog
  - For deletes (simple modal).

### Interaction notes
- Keyboard-first: allow adding tasks with Enter, navigate with Tab, use Space/Enter to toggle completion.
- Visual affordances: completed tasks dim or show strikethrough.
- Minimal animations for clarity.

## Data Model
Data will be stored in the browser. For reliability and scalability, use IndexedDB for structured storage, with a small sync to an in-memory store for UI performance. Provide a fallback to localStorage if IndexedDB is unavailable (graceful degradation).

### Schema: tasks store
| Field | Type | Description |
|---|---:|---|
| id | string (UUID) | Primary key, unique identifier for the task |
| title | string | Required. User-provided title (max 200 chars). |
| dueDate | string (ISO 8601) or null | Optional due date/time for the task |
| completed | boolean | Task completion state (default: false) |
| createdAt | string (ISO 8601) | Timestamp when task was created |
| updatedAt | string (ISO 8601) | Timestamp when task was last updated |

Storage strategy:
- Use an IndexedDB database named `nmit_todo_db` with an object store `tasks` keyed by `id`.
- Maintain an in-memory array for rendering; write-through or write-back strategy to persist changes.

## Validation & Edge Cases
- Title validation
  - Required, trimmed; must be non-empty after trimming; max length 200 characters.
  - Show inline error message if missing.
- dueDate validation
  - If provided, must be a valid date/time string. Accepts local date/time input and stored in ISO 8601.
  - No reminders will be scheduled; dueDate is informational only.
- Editing edge cases
  - If a task being edited is deleted in another tab/window, show an informative error and refresh UI.
- Import edge cases
  - Validate JSON structure before importing. If file invalid, show an error and do not import.
  - Provide option to merge (skip duplicates by id) or replace data store.
- Storage full / quota
  - Detect quota errors and show guidance to export tasks and free space.

## Storage & Persistence (Local-first)
- All data stays on the device; no server communication for user data.
- Use a Service Worker to cache app shell and assets so the app loads offline after first visit.
- Provide explicit Export (download JSON) and Import (upload JSON) functions for user-managed backups.

> ⚠️ Important: Because data is local, users should be encouraged to export backups if they need portability between devices.

## Implementation Plan
### Technology choices
- Frontend: Vanilla modern JavaScript (ES2020+), no heavy framework to keep bundle size small. Use small helper libs if needed (e.g., date-fns for date parsing).
- Build: Optional simple toolchain (esbuild) for production build; can be done without a build system for pure static files.
- Storage: IndexedDB via a small wrapper (idb-keyval or a tiny custom wrapper) and fallback to localStorage.
- Service Worker: Workbox or a small custom SW to cache assets.

### Folder / file structure

```
Requirements_Gatherer/NMITTodo/
├─ index.html
├─ manifest.json
├─ sw.js
├─ src/
│  ├─ main.js         # app initialization, routing
│  ├─ ui.js           # UI components and rendering
│  ├─ store.js        # IndexedDB wrapper + in-memory store
│  ├─ api.js          # persistence API (export/import)
│  ├─ validators.js   # validation utilities
│  └─ styles.css
├─ assets/
└─ tests/
   └─ manual_test_plan.md
```

### Key implementation notes
- Keep components modular: UI rendering separated from storage logic.
- Use event-driven updates (CustomEvent or simple pub/sub) to notify UI of store changes.
- Provide graceful IndexedDB initialization and migration strategy.

## Quality Assurance Checklist
- [ ] Add a task with title only — persists after reload ✅
- [ ] Add a task with title + due date — displays correctly ✅
- [ ] Edit task fields and confirm updatedAt changes ✅
- [ ] Toggle completion and verify persistence after reload ✅
- [ ] Delete a task with confirmation — removed after reload ✅
- [ ] Export tasks to JSON — file downloads and is valid ✅
- [ ] Import tasks from a valid JSON — merges/replaces as expected ✅
- [ ] App loads and functions offline after initial visit (Service Worker) ✅
- [ ] Keyboard navigation: add, edit, toggle, delete via keyboard ✅
- [ ] Screen reader: verify labels and roles for main controls ✅
- [ ] Performance: app remains responsive with 1,000+ tasks ✅
- [ ] Error handling: invalid import, storage errors show user-friendly messages ✅

## Success Criteria
- ✅ All core features (add/edit/delete tasks, toggle complete) work and persist locally.
- ✅ App is fully usable offline after first load (assets cached).
- ✅ Export/import backup functions work and prevent accidental data loss.
- ✅ App meets basic accessibility checks (keyboard navigation, readable labels).
- ✅ No critical bugs; UI behaves consistently across modern desktop and mobile browsers.

## Future Enhancements (Out of scope for this MVP)
- Optional cloud sync or multi-device sync (user-enabled, encrypted).
- Reminders/notifications (browser notifications and scheduling).
- Recurring tasks and advanced recurrence rules.
- Tags/subjects, priority levels, calendar view, and analytics/usage stats.

---

> QA note: This plan was created to match the user's confirmed choices: only title + due date tasks, no reminders, no recurring items, no subtasks, no tags, no priority. If any of these preferences change, the plan should be updated accordingly.
