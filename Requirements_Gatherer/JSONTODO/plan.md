# JSONTODO — Development Plan

## Overview

JSONTODO is a small, local-first single-page to-do application that runs entirely in the browser and stores all data on the user's device. The goal is a minimal, fast task list for users who want offline-first, private task management with simple add/edit/delete functionality.

> "local first to-do"

## Functional Requirements

### Core features (MVP)
- Add task
  - User can enter a task title and save it.
  - Acceptance criteria: New task appears in the list with timestamp and unchecked status.
- Edit task
  - User can edit the task title or mark it complete/incomplete.
  - Acceptance criteria: Changes persist locally and reflect immediately in UI.
- Delete task
  - User can remove a task.
  - Acceptance criteria: Task is removed and will not reappear after reload.

### User stories

| ID | User story | Acceptance criteria |
|---:|---|---|
| US-1 | As a user, I want to add a quick task so I can remember something to do. | Task saves locally, has title, timestamp, shows in list. |
| US-2 | As a user, I want to edit or mark tasks complete so I can track progress. | Edits persist and complete flags update UI. |
| US-3 | As a user, I want to delete tasks I no longer need. | Task is removed and not shown after reload. |
| US-4 | As a user, I want to export my tasks to a file so I can back them up. | Export produces a JSON file with current data. |

## Non-Functional Requirements

- Performance: Load under 1s on modern desktop browsers; UI actions (add/edit/delete) should be instant (<50ms perceived latency).
- Size: Keep bundle small (preferably <300KB gzipped for MVP) so it installs and loads fast.
- Accessibility: Aim for WCAG 2.1 AA where practical. Keyboard-only navigation and semantic HTML must work for core flows.
- Offline-first: App must function fully offline after initial load (assets cached via Service Worker).
- Privacy/Security: All user data remains local to the device. No telemetry or remote sync in MVP.

## UI/UX Design

### Layout
- Single-page layout with two main areas:
  - Top: Task entry area (input + Add button)
  - Main: Task list showing tasks in reverse-chronological order (newest on top)
- Each task row: checkbox (complete), title text (editable inline or via small edit form), timestamp, delete button (trash icon).

### Interactions
- Quick-add: pressing Enter after typing a title adds the task.
- Inline edit: double-click or an edit icon switches the title to an input field.
- Clear visual states for completed vs active tasks (e.g., strike-through + subdued color).
- Empty state: show a friendly message and a short tip on how to add the first task.

### Responsive behavior
- Desktop-first but responsive: input and list stack vertically on narrow screens. Buttons and touch targets sized appropriately on mobile.

## Data Model

Data will be persisted to the browser's storage. For simplicity and reliability, use IndexedDB or a small abstraction that falls back to localStorage if needed (implementation notes below).

### Task schema

| Field | Type | Description |
|---|---|---|
| id | string (UUID or timestamp-based) | Unique identifier for the task |
| title | string | Task text (required, max 200 chars) |
| completed | boolean | Whether the task is done |
| created_at | string (ISO 8601) | Creation timestamp |
| updated_at | string (ISO 8601) | Last update timestamp |

Storage keys / structure:
- DB name: json_todo_db
- Store name: tasks

## Validation & Edge Cases

- title: required; show inline validation message if empty. Enforce max length of 200 characters.
- Duplicate titles: allowed (no strict uniqueness needed).
- Large number of tasks: implement pagination/virtual scrolling if users exceed ~1000 tasks (note: optimistic default is small lists).
- Corrupt data on import: validate JSON structure and alert user with helpful error messages; do not overwrite existing data unless user confirms.
- Storage full: show a friendly warning if local storage quota is exceeded and provide guidance to export/delete tasks.

## Storage & Persistence

- Data: stored locally in the browser (IndexedDB preferred). No server-side components.
- Offline caching: Use a Service Worker to cache application shell and assets for offline usage. Provide a simple install prompt for PWA where supported.
- Backup / Export / Import:
  - Export: user downloads a JSON file containing all tasks and metadata.
  - Import: user can upload a JSON file to restore tasks; app validates the file before merging or replacing data.

## Implementation Plan

### Tech choices (MVP)
- Framework: Vanilla JavaScript + small UI library (optional) OR a lightweight framework like Svelte or Preact for smaller bundles. Recommendation: Vanilla JS or Preact to keep the bundle small and simple.
- Styling: CSS variables + simple responsive layout (mobile-first or desktop-first per earlier note). Keep design minimal.
- Storage: IndexedDB via a small wrapper (e.g., idb) or a simple custom wrapper. Provide export/import as JSON.
- Build: Vite or simple static build for bundling and dev server.

### Folder structure

```
jsontodo/
├─ public/                # static assets (icons, manifest)
├─ src/
│  ├─ index.html
│  ├─ main.js             # app entry
│  ├─ ui/                 # UI components
│  ├─ store/              # storage wrapper (IndexedDB)
│  ├─ views/              # page/view logic
│  ├─ styles/             # CSS
│  └─ sw.js               # Service Worker
├─ package.json
└─ README.md
```

### Key files
- main.js: bootstraps UI, registers Service Worker, loads tasks from storage.
- store/index.js: small API: getAllTasks(), addTask(task), updateTask(id, changes), deleteTask(id), exportJSON(), importJSON(file).
- ui/taskList.js: renders list and handles interactions.
- ui/taskEditor.js: input area for new/edit task.

## Quality Assurance Checklist

- [ ] Add task: create, persist, and display new task.
- [ ] Edit task: update title and completed state persists.
- [ ] Delete task: remove task and persist removal.
- [ ] Export: produces valid JSON of current data.
- [ ] Import: accepts valid JSON and restores tasks (with validation).
- [ ] Offline: app loads and performs core actions while offline (Service Worker cached).
- [ ] Accessibility: keyboard navigation works (add/edit/delete), screen reader reads task list items.
- [ ] Performance: main interactions complete with no perceptible lag; initial load under 1s on modern desktop.
- [ ] Error handling: importing invalid JSON or storage errors show user-friendly messages.

## Success Criteria

- ✅ Core features (add/edit/delete) fully functional and persist locally.
- ✅ Export/import works and is robust to invalid input.
- ✅ App loads and functions offline after initial visit.
- ✅ Basic accessibility and responsive layout verified.
- ✅ No critical bugs in core flows.

## Future Enhancements (not in MVP)

- Optional cloud sync for cross-device syncing (user opt-in).
- Tags, projects, priorities, due dates, and reminders.
- Recurring tasks and subtasks.
- Attachments and rich text notes.
- Optional user accounts and encryption for sync.

## Notes from QA

- The user's responses were minimal: they chose only the simple task list (add/edit/delete). The QA review confirms the plan addresses that requirement and leaves room for extensions. If the user later requests additional features, revise the plan and data model accordingly.


