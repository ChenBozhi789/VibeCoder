# PRD — GreenToDo

## 1. App name
GreenToDo

## 2. Purpose and users
Purpose:
- A simple personal task / to-do manager to help individuals capture and complete daily tasks.

Primary users:
- Individuals who want a lightweight, mobile-first app to manage their daily tasks and reminders.

## 3. Core features
The app will provide the following main capabilities:
1. Add and edit tasks (title, notes)
2. Set a due date for tasks
3. Keep notes / detailed description for each task

Additional feature notes:
- Keep the initial scope intentionally small and focused on quick task entry and completion.

## 4. Look & feel (UI/UX)
1. Simple list view, mobile-first design
- Quick add input visible at top/bottom of list for rapid task capture
- Minimal controls; focus on speed and easy one-handed use
- Clear completed/uncompleted states with swipe to complete or delete (optional later)

Empty-state and error UX:
- Friendly empty-state screens that suggest actions (e.g., “Add your first task”) and clear, plain-language error messages.

## 5. Data model / Information to save for each task
Each task will store:
- Title (short name)
- Notes / detailed description
- Due date
- Metadata: creation date, last-modified date, completion status

(Attachments, tags, priorities, and other advanced fields are out of scope for MVP but can be added later.)

## 6. Validation rules
Rules enforced when creating or editing tasks:
1. Title is required (cannot be empty).
2. Basic sanitization: trim leading/trailing spaces from title and notes.

## 7. Non-functional requirements
1. Work offline and sync when back online — users must be able to add/edit tasks without network access; data syncs when possible.
2. Fast loading and lightweight app — mobile-first performance goals.

## 8. Extras / Nice-to-have
1. Backup/export (CSV, JSON) so users can export their tasks and restore if needed.

## 9. Success criteria / Definition of Done
GreenToDo will be considered complete when:
1. Core features are complete and stable: add/edit tasks, due dates, reminders (if implemented), and offline sync.
2. Polished mobile UX with fast performance and intuitive empty-state guidance.
3. Reliable data persistence with at least one export/backup option.

Handling empty lists and mistakes:
- Show helpful empty-state UI with a clear call-to-action (e.g., “Tap + to add your first task”).
- Provide undo for deletes/edits (toast with "Undo" for a short time) and confirmations for destructive actions where appropriate.

## 10. Next steps
1. Validate this PRD with stakeholders / product owner.
2. Draft simple wireframes for the mobile list view and quick-add flow.
3. Define an initial API and local storage schema for offline-first sync.
4. Plan an MVP development sprint focused on: task CRUD, local persistence, offline sync, and export.

---

Document created from user interview responses.
