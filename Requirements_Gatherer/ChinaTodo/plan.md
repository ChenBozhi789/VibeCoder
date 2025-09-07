## ChinaTodo — Development Plan

### Overview
ChinaTodo is a minimal, local-first personal to-do list web app for desktop users. The app focuses on quick creation, editing, and deletion of single-line tasks. It runs entirely in the browser; no server or cloud storage is used. The goal is a fast, accessible, offline-capable single-page application (SPA) that stores user tasks locally.

### Functional Requirements
- Users can create tasks with a required Title.
- Users can edit an existing task's Title.
- Users can delete tasks.
- Tasks are shown in a single-column list (compact view) with most-recently-created or user-chosen sort.
- The app persists tasks locally so they remain between browser sessions.

User stories (MVP):
1. As a user, I want to add a task so I can remember what I need to do.
   - Acceptance: Enter a non-empty title, click Save or press Enter. Task appears in the list.
2. As a user, I want to edit a task so I can correct or refine the title.
   - Acceptance: Edit control is available; changes persist and updated timestamp is recorded.
3. As a user, I want to delete a task so I can remove completed/irrelevant items.
   - Acceptance: Delete action removes the task and it no longer appears after refresh.

### Non-Functional Requirements
- Performance: App loads and is interactive within 300–500ms on a typical desktop browser; list operations (add/edit/delete) update UI instantly.
- Offline-first: Fully usable without network access; all data remains on the device.
- Accessibility: Meet WCAG 2.1 AA where practical: keyboard focus order, meaningful ARIA labels, sufficient color contrast, and screen-reader friendly semantics.
- Privacy & Security: No data leaves the device. No third-party analytics by default.
- Size: Keep the initial bundle small (prefer <200KB gzipped) for snappy startup.

### UI/UX Design
- Layout: Single-column list with an input area at the top for quick capture.
- Primary components:
  - Header with app name "ChinaTodo" and a small info/help button.
  - New-task input bar: single-line text box + Add button (Enter key should add).
  - Task list: each row shows Title and inline actions: Edit, Delete.
  - Edit mode: inline editable text field replacing the title, with Save/Cancel actions.
  - Empty state: friendly message and hint for adding the first task (e.g., "No tasks yet — type one above and press Enter").
- Desktop considerations: layout optimized for mouse and keyboard, wider content area and comfortable spacing.

User flow:
1. Open app → see list or empty state.
2. Type title in input → press Enter or click Add → task appears at top of list.
3. Click Edit on a task → modify title → Save or Cancel.
4. Click Delete → confirmation (optional confirm step configurable).

### Data Model
- Storage: Use IndexedDB for reliable local persistence and future growth; provide a simple wrapper to keep code clean. For very small scale, localStorage could be used, but IndexedDB is recommended.

Data schema (object store: "tasks"):

| Field        | Type    | Required | Notes |
|--------------|---------|----------|-------|
| id           | string  | yes      | UUID or timestamp-based unique id (primary key)
| title        | string  | yes      | max 200 chars
| completed    | boolean | no       | default: false (internal, not part of user request but useful)
| createdAt    | string  | yes      | ISO timestamp
| updatedAt    | string  | yes      | ISO timestamp

Implementation note: The UI shows only title by default; completed field may be hidden or used later.

### Validation & Edge Cases
- Title validation: required, trimmed, max length 200. If validation fails, show inline error message and prevent save.
- Empty list: show helpful empty state and CTA to add tasks.
- Duplicate titles: allowed (no uniqueness constraint) but could warn optionally.
- Large number of tasks: lazy rendering or simple virtualization if list grows very large (>500 items) to maintain performance.
- Storage full: catch storage errors and show user-friendly message suggesting export and clear.

### Storage & Persistence
- Local-first: data stored locally via IndexedDB. No backend required or used.
- Offline caching: include a Service Worker to cache the app shell (HTML/CSS/JS) for offline startup.
- Backup/export: although the user did not request it, the plan includes an optional menu command to export/import JSON (download/upload) so users can save or restore their data.

### Implementation Plan
- Tech choices: Vanilla ES Modules (no heavy framework) to keep size small and simple. Use a tiny bundler (esbuild) only if a build is needed.
- PWA-ready: include manifest.json and Service Worker, but do not force install. PWA installability can be enabled later.

Suggested folder structure:

```
ChinaTodo/
├─ public/
│  ├─ index.html
│  ├─ manifest.json
│  └─ icons/ (optional)
├─ src/
│  ├─ main.js          # app entry, routing (if any)
│  ├─ ui.js            # UI helpers, rendering
│  ├─ db.js            # IndexedDB wrapper and schema
│  ├─ store.js         # state management (simple pub/sub)
│  ├─ styles.css
│  └─ sw.js            # service worker for offline caching
├─ tests/              # unit / integration test files
└─ package.json (optional)
```

Key implementation notes:
- Keep UI state and persistence logic separated. Use a small state store (observer pattern) to update UI on DB changes.
- Use semantic HTML elements and ARIA attributes for accessibility.
- Provide keyboard shortcuts: Enter to add, Esc to cancel edit, Arrow keys to navigate tasks.

### Validation & Edge Cases (Developer-focused)
- Ensure database migrations are handled if schema changes in future versions.
- Gracefully handle IndexedDB errors and provide fallback (e.g., localStorage) with a clear warning to the user.
- Ensure Service Worker updates are smooth and do not clear user data.

### Quality Assurance Checklist
- [ ] Add task creates a persistent record and appears in the list after reload.
- [ ] Edit task updates title and updatedAt timestamp.
- [ ] Delete removes the task and it does not reappear after reload.
- [ ] Required validation prevents empty titles.
- [ ] Keyboard interactions: Enter to add, Esc to cancel, tab order correct.
- [ ] Accessibility: ARIA labels, screen reader reads controls, contrast complies.
- [ ] Offline: App loads and functions after network is disconnected.
- [ ] Service Worker caches assets correctly and updates are handled.
- [ ] Export/import JSON (if enabled) correctly serializes and restores tasks.
- [ ] Performance: List operations remain snappy with 100+ items.

### Success Criteria ✅
- The MVP allows creating, editing, and deleting tasks on Desktop and persists data locally.
- The app works offline and starts quickly (<500ms on target hardware).
- All QA checklist items are passing; no major accessibility or data-loss bugs.

### Future Enhancements 💡
- Add due dates, reminders, and priority levels.
- Tags/categories and simple filtering/search.
- Subtasks and checklists.
- Optional cloud sync or multi-device sync as an opt-in feature.
- Mobile-optimized layout and PWA install optimization.

> ⚠️ Note: The user explicitly requested a very minimal MVP (create/edit/delete of Title only). Other features are suggested as future improvements and are not part of the current scope.

_Last updated: Generated by the multi-agent team._