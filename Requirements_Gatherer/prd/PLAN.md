# PLAN.md — HopeTodo

## Overview
HopeTodo is a lightweight, local-first to‑do list web app for general users (students, professionals, homemakers). It provides a minimal, list-focused UI with core task lifecycle features: create, edit, delete, set due dates and reminder times, and mark tasks completed. The app is a single-page web app that runs entirely in the browser and persists data locally.

> Important: This plan strictly follows the PRD. No extras (export/import, sync, branding) are included in MVP. Any additional ideas are listed under Future Enhancements.


## Functional Requirements (User Stories)
All stories below are scoped to the PRD and marked where applicable as MVP.

1) Add Task
- MVP: Yes
- User story: As a user, I want to add a task so I can capture a to‑do item.
- Acceptance Criteria:
  - User can open an Add Task input/form.
  - Fields: Title (required), Description (optional), Due Date (optional), Reminder Time (optional).
  - On submit, task is saved locally with created_at and updated_at timestamps and appears in the list.
  - Validation: if Title is empty, the app shows an inline error and prevents save.

2) Edit Task
- MVP: Yes
- User story: As a user, I want to edit an existing task so I can update its details.
- Acceptance Criteria:
  - Each task row has an edit affordance (icon or click-to-edit).
  - On edit, user can change Title, Description, Due Date, Reminder Time, Completed.
  - After saving, updated_at is updated and UI reflects changes immediately.
  - Validation: Title required.

3) Delete Task
- MVP: Yes
- User story: As a user, I want to delete a task so I can remove completed or unwanted items.
- Acceptance Criteria:
  - Each task row has a delete affordance.
  - Deletion prompts a minimal confirmation to prevent accidental deletes.
  - On confirm, task is removed from storage and UI updates.

4) Mark Completed
- MVP: Yes
- User story: As a user, I want to mark a task completed so I can track progress.
- Acceptance Criteria:
  - Each task has a checkbox/toggle to mark completed.
  - Toggling updates the `completed` flag and updated_at and re-renders the list.

5) View Metadata
- MVP: Yes
- User story: As a user, I want to view task metadata (created/updated) so I know when items were changed.
- Acceptance Criteria:
  - Each task shows created_at and updated_at in a short or relative format.

6) Minimal List Layout
- MVP: Yes
- Acceptance Criteria:
  - Single vertical list, clean white background, minimal chrome. No extra panes or complex navigation.


## Traceability Table
Maps PRD items to plan sections.

| PRD Item | Plan Section(s) |
|---|---|
| Add tasks | Functional Requirements (Add Task), UI/UX Design, Implementation Plan |
| Edit tasks | Functional Requirements (Edit Task), UI/UX Design, Implementation Plan |
| Delete tasks | Functional Requirements (Delete Task), UI/UX Design, Implementation Plan |
| Minimal list-focused UI | UI/UX Design, Non-Functional Requirements |
| Data fields (title, description, due_date, reminder_time, completed, created_at, updated_at) | Data Model, Functional Requirements |
| Validation: title required | Validation & Edge Cases, Functional Requirements |
| No extras | Scope Discipline, Future Enhancements |


## Non-Functional Requirements
- Local-first: fully client-side persistence (IndexedDB primary, localStorage fallback).
- Fast load: keep initial bundle minimal; aim for <=1s on modern mobile network.
- Accessibility: keyboard navigation, semantic HTML, labels for inputs, sufficient color contrast.
- Performance: smooth operations for up to ~200 tasks; UI updates immediately after actions.
- Responsiveness: single-column layout adapting to mobile widths.


## UI/UX Design
Respect PRD: minimal, list-focused, clean white background. No additional UI patterns.

Screens & Flows

1) Main Screen (SPA)
- Header: small app title "HopeTodo" and a compact Add button.
- Add Task area: compact inline form at top or toggleable small panel. Fields: Title (required), Description (optional), Due Date (date/time picker optional), Reminder Time (time picker optional), Save/Cancel.
- Task List: vertical list; each row shows:
  - Checkbox for completed
  - Title (bold) and optional description preview
  - Small metadata: due date / reminder time when present
  - Edit and Delete icons (icons with accessible labels)
- Empty State: centered text "No tasks yet — add your first task" and Add affordance.

Interactions
- Add: opens inline form, autofocuses Title.
- Submit: validate Title, save, collapse form, update list.
- Edit: opens form pre-filled; save updates task in place.
- Delete: show confirmation (modal or native confirm); on confirm, remove and animate row removal.
- Mark Completed: toggling applies subtle visual (e.g., lighter text or strikethrough) and updates state.

Accessibility
- All controls keyboard-focusable; aria-labels on icon buttons; semantic form elements and list markup.


## Data Model
Primary storage: IndexedDB object store "tasks" (recommended). Fallback: localStorage key "hopetodo.tasks".

Task object (schema)

| Field | Type | Notes |
|---|---|---|
| id | string (UUID) | Primary key
| title | string | required, max 255 chars
| description | string|null | optional, max 2000 chars
| due_date | string|null | ISO 8601 datetime or null
| reminder_time | string|null | ISO 8601 time/datetime or null
| completed | boolean | default false
| created_at | string | ISO 8601 datetime
| updated_at | string | ISO 8601 datetime

Indexes
- Primary key: id
- Optional indexes: created_at (default ordering), due_date (future enhancement)

Storage considerations
- Keep payloads small; enforce UI limits on description length to avoid quota issues.


## Validation & Edge Cases
- Title: required, trim whitespace, max length 255. Inline error "Title is required." prevents save.
- Description: optional; limit to 2000 chars.
- Date/time: validate ISO format; do not auto-convert timezones beyond storing ISO strings.
- Prevent double-submit: disable Save while write in progress.
- Storage errors: detect quota/full and show "Unable to save task — storage full." with guidance.
- IndexedDB errors: surface an error toast and offer retry.
- Empty states: show friendly message and visible Add affordance.
- Concurrency: single-user, no sync; no conflict resolution required.


## Storage & Persistence
- Use IndexedDB via a small wrapper (idb or tiny custom module) for CRUD.
- Fallback to localStorage when IndexedDB is unavailable.
- App is fully functional offline (no server dependencies).
- Export/import backups: NOT in scope (Future Enhancements).


## Implementation Plan
Tech stack recommendations
- Option A (developer efficiency): React (17/18) + Vite for minimal bundle and fast dev cycle.
- Option B (minimal bundle): Vanilla JS with small modules (for smallest possible footprint).
- IndexedDB helper: idb (small) or custom wrapper.
- CSS: plain CSS (no heavy frameworks). Keep styles minimal and white background.

Project structure (example for React)

- public/
  - index.html
- src/
  - main.jsx
  - App.jsx
  - components/
    - Header.jsx
    - TaskList.jsx
    - TaskRow.jsx
    - TaskForm.jsx
    - EmptyState.jsx
    - ConfirmDialog.jsx
  - store/
    - db.js            // IndexedDB wrapper
    - taskService.js   // CRUD APIs used by components
  - utils/
    - date.js
    - validators.js
  - styles/
    - base.css
    - components.css
- package.json
- vite.config.js

Core APIs (taskService)
- createTask({title, description, due_date, reminder_time}) -> Promise<Task>
- getTasks() -> Promise<Task[]>
- updateTask(id, patch) -> Promise<Task>
- deleteTask(id) -> Promise<void>
- toggleComplete(id, boolean) -> Promise<Task>

Development tasks (MVP)
- Project scaffold and build tooling (0.5-1 day)
- IndexedDB wrapper + taskService (0.5-1 day)
- Core UI components (list, form, row) (2-3 days)
- Validation, accessibility, responsive styles (1 day)
- QA & bugfix (1 day)
Estimated total: ~5–7 developer-days for a single developer.


## QA Checklist
- [ ] Add task: Title required; task persists and appears with created_at/updated_at.
- [ ] Edit task: changes persist; updated_at changes.
- [ ] Delete task: confirmation shown; task removed from storage and UI.
- [ ] Mark completed: toggles completed and updates timestamp and UI.
- [ ] Empty state visible when no tasks.
- [ ] Validation: cannot save without Title; inline error displayed.
- [ ] Offline: app loads and full functionality works without network.
- [ ] Persistence: tasks remain after reload.
- [ ] Accessibility: keyboard navigation, aria labels, focus management.
- [ ] Performance: add/edit/delete within reasonable local write time (typ. <200ms).
- [ ] Error handling: storage full or write errors show user-friendly messages.


## Success Criteria (MVP Done)
- All MVP stories implemented and verified in QA checklist.
- Data persisted locally and survives page reloads.
- UI matches PRD style (single-column list, minimal chrome, white background).
- Title validation enforced and accessible UI controls present.
- App operates fully offline and basic accessibility checks pass.


## Future Enhancements (Out of Scope for MVP)
- Export/import JSON backups.
- Cloud sync across devices and user accounts.
- Filtering, sorting, search, and grouping by due date or completed state.
- Notifications/reminders via service workers and OS notifications.
- Bulk actions (delete completed, mark all complete).


---

If you want, I can also generate a minimal starter scaffold or initial code files from this plan.
