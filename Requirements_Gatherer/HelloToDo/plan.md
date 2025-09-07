# HelloToDo - Development Plan

## Overview
HelloToDo is a lightweight, local-first single-page application (SPA) for one person to manage personal tasks. It runs entirely in the browser — no server — and offers basic task create/edit/delete operations plus a manual backup/export and import/restore capability.

> Goal: Deliver a tiny, fast app that works offline, keeps user data private on the device, and provides an easy way to back up and restore tasks.

## Functional Requirements

### User Stories

1. As a user, I want to add a new task so I can record what I need to do.
   - Acceptance criteria:
     - A visible input form lets me enter a task title (required) and optional details.
     - On save, the task appears in my list immediately.

2. As a user, I want to edit a task so I can update its title or details.
   - Acceptance criteria:
     - I can open an edit view for any task, change fields, and save updates.
     - Changes are persisted and shown in the list.

3. As a user, I want to delete a task so I can remove tasks I no longer need.
   - Acceptance criteria:
     - There is a clear delete action with a confirmation option (small prompt or undo toast).

4. As a user, I want to download my tasks to a file (backup) and later restore from that file.
   - Acceptance criteria:
     - There is an Export button that downloads a JSON file with all saved tasks.
     - There is an Import button that accepts a previously exported file and restores tasks (with a merge or replace option).

5. As a user, I want the app to work without internet connection.
   - Acceptance criteria:
     - The app shell and functionality load and run offline after the first successful load.

## Non-Functional Requirements
- Performance: App shell should load within 300–700ms on modern desktop (cold load); interactions should be instant for single-digit to-do lists.
- Bundle size: Keep initial JS under ~200 KB gzipped for speed (MVP aim).
- Accessibility: Target WCAG 2.1 AA basics — keyboard focus, readable contrast, semantic markup for screen readers.
- Offline-first: App fully functions offline after initial caching.
- Privacy/Security: All personal data stays on the device unless the user explicitly exports it. No outbound network calls containing user data.

## UI/UX Design

### High-level layout
- Single-page layout with these main areas:
  - Top header with app name (HelloToDo) and a compact menu (Export / Import / Settings).
  - Main content: task input at the top, then a vertical list of tasks.
  - Each task row contains: checkbox to mark complete, title, optional short description preview, and actions (edit, delete).
  - Empty state: friendly message and a CTA to add the first task.

### Screens / Dialogs
- Main screen (1) – add/edit inline or open a small modal for edit.
- Import dialog (modal or file picker) – confirm replace/merge behavior and show warnings on malformed files.
- Small confirmation or undo toast for delete.

### Interaction details
- Quick add: a single-line input with Enter to save.
- Edit: clicking the task title toggles to edit mode or opens an edit modal.
- Accessibility: ensure all actions are reachable by keyboard (Tab, Enter, Esc) and use ARIA labels where needed.

## Data Model
- Storage choice: IndexedDB (recommended) for structured data and future extensibility. localStorage could be used for very tiny prototypes, but IndexedDB is preferred.

### Object store: tasks

| Field | Type | Description |
|---|---:|---|
| id | string | unique id (UUID or timestamp-based) — primary key |
| title | string | required, max 250 chars |
| description | string | optional, max 2000 chars |
| completed | boolean | default false |
| created_at | ISO timestamp | when created |
| updated_at | ISO timestamp | when last updated |

### Metadata store (optional)
- Key-value store for app version, last export timestamp, UI preferences.

## Validation & Edge Cases
- Title required: do not allow empty titles. Trim whitespace.
- Max lengths: enforce reasonable field length limits and show inline validation messages.
- Empty list: show helpful empty-state UI with tips to add tasks.
- Import errors: detect invalid JSON, show an error message, and do not corrupt existing data. Provide options to replace or merge.
- Storage quota errors: detect and inform the user if the browser cannot store more data; advise export and clear.
- Duplicate IDs on import: resolve by generating new IDs or merging by ID based on chosen behavior.

## Storage & Persistence
- Data persistence: store tasks in IndexedDB.
- Offline caching: register a Service Worker to cache the app shell (HTML, CSS, JS, icons) for offline load.
- Backup/Export: implement Export → create a JSON blob of all tasks and trigger a download named hello-todo-backup-YYYYMMDD.json
- Restore/Import: allow user to select a backup JSON file. Validate schema, then either merge or replace.

> ⚠️ Important: No automatic cloud sync is included in the MVP. All data remains local unless the user exports it.

## Implementation Plan

### Tech choices (MVP)
- Framework: Vanilla JavaScript (ES modules) with small, focused helper utilities. (Reason: smallest footprint and easy to audit.)
- IndexedDB: use a small wrapper module for convenience (custom minimal wrapper, no heavy dependencies).
- Service Worker: small hand-written service worker to precache assets.
- Build/tools: optional bundler (esbuild/rollup) to create a small optimized bundle; could be plain script tags for simplest deployment.

### Project structure

```
HelloToDo/
├─ index.html
├─ manifest.json
├─ sw.js
├─ src/
│  ├─ main.js          # bootstraps app
│  ├─ app.js           # app logic and UI wiring
│  ├─ db.js            # IndexedDB wrapper and schema
│  ├─ ui/
│  │  ├─ taskList.js
│  │  ├─ taskItem.js
│  │  └─ dialogs.js
│  ├─ styles.css
│  └─ utils.js
├─ assets/
│  └─ icons/
└─ dist/ (optional build output)
```

### Key implementation notes
- Keep components simple and functional. Use progressive enhancement: app works without JS for static view only where possible, but main functionality requires JS.
- Provide unit-like tests (if a test runner is available) for critical logic such as import/merge and db operations.

## Quality Assurance Checklist
- [ ] Add / Edit / Delete tasks works and persists across reloads ✅
- [ ] Export creates a valid JSON backup file ✅
- [ ] Import restores tasks; validate merge/replace behavior ✅
- [ ] App runs offline after initial load (service worker caching) ✅
- [ ] Empty list UX is helpful and visible ✅
- [ ] Input validation: required title, length limits, error messages ✅
- [ ] Accessibility: all interactive elements keyboard reachable and labeled ✅
- [ ] Error handling: import errors, storage quota errors, and DB failures handled gracefully ✅
- [ ] Performance: initial load within target and responsive interactions ✅

## Success Criteria (MVP Done)
- ✅ Add, edit, delete tasks are fully functional and persisted locally.
- ✅ Export and Import (backup/restore) work without data loss.
- ✅ App loads and runs offline after first visit (cached assets).
- ✅ Basic accessibility and responsive layout implemented.
- ✅ No critical bugs in the core flows; app is stable for everyday single-user use.

## Future Enhancements (beyond MVP)
- Optional cloud sync (user opt-in) for cross-device sync.
- Due dates & reminders with local notifications.
- Tags / filters, search, and sorting.
- Recurring tasks and subtasks/checklists.
- Dark theme and extra UI customization.
- Publish as PWA to app stores if desired.

---
*QA review:* The plan above addresses the explicitly requested features (task CRUD and backup). The plan also highlights open questions where the user might want extra features later. If you want any of the omitted options (due dates, tags, priorities, or PWA installability) included in the MVP, tell us which and we will update both the requirements file and the plan accordingly.