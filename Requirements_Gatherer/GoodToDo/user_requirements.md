# GoodToDo — User Requirements

## App Name
- GoodToDo

## Collected Answers (in the user's words)
- Primary purpose: "Personal to-do list / daily tasks for one person." (Selected option 1)
- Target user: A single user who wants a simple, local to-do list stored in their browser.
- Backup/Import: Yes — user requested an export/import feature and prefers JSON format.
- Local-first: The app must run entirely in the browser and keep all data on the user\'s device (no server storage).

## Basic implied requirements (clarified or assumed due to limited input)
- Core tasks the user will want to accomplish:
  - Create, view, edit, and delete tasks.
  - Mark tasks as complete/incomplete.
  - Optionally set a due date for tasks.
  - Optionally add a short description for tasks.
  - Optionally use simple labels/tags and/or priority (assumed helpful).
- Data export/import:
  - Export tasks to a JSON file.
  - Import tasks from a JSON file (restore or migrate data).

## Data fields (assumed minimal useful schema)
- taskId (string, unique)
- title (string, required)
- description (string, optional)
- createdAt (ISO datetime)
- updatedAt (ISO datetime)
- dueDate (ISO date, optional)
- completed (boolean)
- priority (enum: low, medium, high) — optional
- tags (array of strings) — optional

## Validation rules (assumptions / recommended defaults)
- title: required, max length 200 characters.
- dueDate: if provided, must be a valid date (not a text string).
- tags: each tag max length 50 characters, max 10 tags per task.

## Non-functional expectations (from conversation and common defaults)
- Runs entirely in the browser (local-first, offline-capable).
- Export/import via JSON file.
- Reasonable performance for up to several thousand tasks.
- No cloud sync (user opted local-only).

## Unanswered / Open Questions (QA flagged)
> ⚠️ The user provided minimal input. The QA agent flags these as items that need clarification if the project scope increases:
- Preferred UI layout or style (compact list, kanban, calendar view?) — not specified.
- Need for recurring tasks or reminders/notifications — not specified.
- Platform focus: desktop-first, mobile-first, or both — not specified.
- Accessibility requirements (e.g., screen reader support) — not specified.
- Installable as a PWA/app on device? — not specified.

## Next steps (recommended)
- Confirm UI preferences (list layout, filters, sort options).
- Confirm whether reminders/notifications or recurring tasks are needed.
- Confirm whether PWA/installability is desired.
- Confirm accessibility targets (WCAG level) and target platforms (desktop/mobile).

> Note: We captured the core items you explicitly provided (personal to-do list and JSON backup). The planning document will include reasonable defaults and clearly mark any assumptions so you can review and revise them later.