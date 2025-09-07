# PerfaceToDo — Development Plan

> "PerfaceToDo is a simple personal to-do list for a single user, running entirely in the browser."

## Overview

PerfaceToDo is a small, local-first single-page application (SPA) for desktop browsers only. It provides a very simple, fast to-do list where a single user can quickly create, edit, and delete tasks. All data is stored in the user's browser; there is no server or cloud sync for the MVP.

Goals:
- Keep the app tiny and fast (load < 2s on a normal desktop) ✅
- Minimal UI: simple vertical list view for quick task entry and edits
- Strong privacy: user data never leaves their device ⚠️


## Functional Requirements

### Core features
- Create tasks (Title only)
- Edit tasks (modify Title inline)
- Delete tasks
- Auto-save after each change (no Save button)

### User stories and acceptance criteria

| ID | User story | Acceptance criteria |
|---|---|---|
| FR-1 | As a user, I want to add a new task so I can remember an item to do. | When I type a Title (<=100 chars) and press Enter or click Add, the task appears in the list and persists after reload. |
| FR-2 | As a user, I want to edit an existing task so I can correct or update it. | Clicking a task enables inline edit; changes are saved immediately and persist after reload. |
| FR-3 | As a user, I want to delete a task when it's no longer needed. | Deleting removes the task from the list and it does not reappear after reload. |
| FR-4 | As a user, I want the app to feel instant. | UI updates instantly on create/edit/delete, and the app loads under 2s on a typical desktop. |


## Non-Functional Requirements

- Performance: Initial load < 2s on a normal desktop, interactions (add/edit/delete) update UI instantly. ⚡
- Accessibility: Aim for keyboard-friendly interactions (add with Enter, edit with Enter/Esc) and support common screen readers. Target WCAG 2.1 AA where practical. ♿
- Capacity: Expect small dataset (under 500 tasks). No special scaling required for the MVP.
- Privacy & Security: Data stays on-device only; no external network calls for user data. Consider simple obfuscation/encryption only as a future option.
- Resilience: App should handle a full localStorage quota gracefully by showing an informative message.


## UI/UX Design

### Layout
- Single desktop screen with three main elements:
  1. Header with app name (left) and simple settings icon (right).
  2. Input bar at the top: text field for new task Title + Add button. Placeholder: "Add a task (max 100 chars)".
  3. Main area: vertical list of tasks. Each row shows Title and a small trash icon to delete.

### Interactions
- Add task: focus input, type title, press Enter or click Add → task created and appended to top or bottom (design choice: append to top recommended for visibility).
- Edit task: click a task Title → becomes inline editable input. Press Enter to save, Esc to cancel.
- Delete: click trash icon to delete; show a brief undo toast (5s) allowing one-step undo. (Undo is a lightweight UX safety — internal only, still auto-saved.)
- Empty state: when no tasks exist, show a friendly message and a big input to add the first task.

### Keyboard shortcuts (recommended)
- Enter in input: add task
- Ctrl+K / / to focus top input (optional)
- Up/Down to navigate tasks (optional enhancement)

### Visual style
- Clean, minimal, neutral color palette. Support a simple Light theme by default. Keep typography legible and sizes desktop-optimized. Use icons for delete and settings.


## Data Model

- Storage choice: localStorage (key-value) — suitable for this small, simple dataset and keeps implementation minimal.
  - Justification: small number of tasks (<500) and simple schema. If future needs grow (attachments, large lists), migrate to IndexedDB.

- Storage key: "perfacetodo.tasks" (JSON serialized array)

- Data schema (stored internally):

| Field | Type | Required | Notes |
|---|---:|---|---|
| id | string | yes | Internal UUID (v4) or monotonic id — used to identify tasks. Not shown to user. |
| title | string | yes | User-visible Title. Max 100 characters. Trim whitespace. |
| createdAt | string (ISO timestamp) | yes | Internal; used for ordering or debugging. |
| modifiedAt | string (ISO timestamp) | yes | Internal; updated on edits. |

> Note: The user-visible model is "Title only". createdAt/modifiedAt/id are internal metadata to support app behavior and do not add extra input fields for the user.


## Validation & Edge Cases

- Title validation:
  - Required. Empty or whitespace-only titles are rejected with inline validation message.
  - Maximum length: 100 characters. Prevent typing beyond the limit or show remaining chars.
  - Trim leading/trailing whitespace on save.
- Duplicate titles: no strict restriction. Consider showing a neutral hint but allow duplicates.
- Storage full (localStorage quota reached): show an informative error message suggesting the user delete tasks or clear browser storage.
- Undo delete: show a temporary toast with Undo (5s) after delete. If user does not undo, deletion is final.
- Data corruption/malformed JSON in storage: on startup, detect parse error, back up raw string to a fallback key (e.g., "perfacetodo.tasks_corrupt_<timestamp>") and reset to empty list, then show a one-time notice instructing user that data was reset. (This helps avoid app failure.)
- Empty list UX: show helpful guidance and focus input.


## Storage & Persistence (Local-First)

- All data is stored in browser localStorage under key "perfacetodo.tasks" as a JSON array.
- Auto-save: every create/edit/delete writes immediately to localStorage.
- Offline behavior: The app is purely client-side. Optionally, a small Service Worker may be registered to cache the app shell (HTML/CSS/JS) so the app loads fast and can open while offline. This does NOT sync data — it only caches static assets.

Important: The user requested NO export/import or backups for the MVP. Therefore, no Export/Import UI is included in the MVP. If desired later, a simple JSON download/upload can be added.


## Implementation Plan

### Technology choices
- Framework: Vanilla modern JavaScript (ES modules) to keep the app small and dependency-free. Alternative: a tiny framework (Preact/Svelte) if the team prefers component structure.
- Styling: CSS variables + small stylesheet; consider a micro CSS reset.
- Build: No build step required for MVP (deliver static files). Optionally use a simple bundler for minification.

### Folder / File structure

```
PerfaceToDo/
├─ index.html            # Single-page app shell
├─ src/
│  ├─ main.js            # App entry, router (if any), initialization
│  ├─ ui.js              # DOM helpers and UI components
│  ├─ storage.js         # localStorage wrapper and helpers (get/save/tasks)
│  ├─ model.js           # Task model, validation utilities
│  ├─ sw.js              # Optional Service Worker (caching static assets)
│  └─ styles.css         # Main styles
├─ assets/
│  └─ icons.svg
└─ README.md
```

### Key implementation notes
- storage.js exposes async getTasks() and saveTasks(tasks) wrappers around localStorage (use Promise API for uniformity).
- main.js wires up UI events (add/edit/delete) and subscribes to changes to call saveTasks.
- Use requestAnimationFrame/minor throttling for UI updates if needed.
- Add simple unit-tests (if desired) for model validation logic.


## Quality Assurance Checklist

- [ ] Functional: Can add a task and it appears in the list.
- [ ] Functional: Can edit a task inline and the new value persists after reload.
- [ ] Functional: Can delete a task and it is removed after reload.
- [ ] Persistence: Tasks persist across reloads and browser restarts.
- [ ] Performance: App loads in < 2s on a typical desktop (measured cold load).
- [ ] UX: Keyboard shortcuts (Enter adds) work reliably.
- [ ] UX: Empty state shows helpful guidance.
- [ ] Error handling: localStorage full shows clear message.
- [ ] Data integrity: Corrupt storage handled gracefully (backup/reset flow). ✅
- [ ] Accessibility: Basic keyboard navigation and screen-reader labels tested.
- [ ] Cross-browser: Works on modern desktop Chrome/Firefox/Edge.
- [ ] Security/Privacy: No external network calls related to user tasks.


## Success Criteria (MVP Done)

- ✅ All core features implemented and tested: add, edit, delete tasks.
- ✅ Auto-save works and data persists locally with no server involvement.
- ✅ App launches and responds under the performance target (initial load < 2s).
- ✅ No critical bugs in basic flows; graceful handling of storage errors.
- ✅ QA checklist items above are completed.


## Future Enhancements (Not in MVP)

- Export/Import (JSON) for backups and manual transfer. 💾
- Optional PWA installability and Home Screen support. 📱
- Completed/Archive state, or soft-delete with a Trash view.
- Tags, priorities, due dates, reminders, recurring tasks, and calendar view.
- Migrate storage to IndexedDB for large datasets or attachments.
- Optional encrypted storage for extra privacy.


## QA Agent Review & Consistency Notes

- The QA agent has compared this plan against the user requirements in user_requirements.md and confirms consistency:
  - App name: PerfaceToDo — present in both docs.
  - Platform: desktop-only — respected.
  - Core features: create/edit/delete tasks only — implemented in plan.
  - Task fields: Title only, required, max 100 chars — enforced by validation in the Data Model and Validation sections.
  - Auto-save behavior: included.
  - No export/import requested: MVP omits backup/export; mentioned in Future Enhancements.

> If you later decide you want export/import or a completed state, we can update the plan and add the additional UI and storage behavior.


---

Thank you — this plan is ready for developer implementation. If you want, I can now generate a minimal starter code scaffold for the project (index.html + main.js + storage.js + styles.css) to get you started.