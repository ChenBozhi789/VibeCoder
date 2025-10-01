# RedToDo — Product Requirements Document

## App Name
RedToDo

## Purpose & Users
- Purpose: A simple personal to-do and habit tracker focused on helping individuals manage daily tasks.
- Primary users: Individuals looking for a minimal, fast way to add tasks and receive reminders.

## Features (as chosen)
1. Set due dates and reminders (user selected)

Note: The user selected only "Set due dates and reminders" as the main feature. To operate, the app will minimally need the ability to add tasks (create a task entry) — included in the MVP scope.

## UI / Look & Feel
1. Simple list view (clean, minimal) — user selected

Notes:
- Mobile-friendly simple list layout that prioritizes speed and clarity.
- Minimal UI chrome: task rows with title, status (done/undone), and reminder indicator.

## Data Model (what's saved for each task)
1. Title (short name) — required (user selected)

Assumption to confirm:
- Because reminders and due dates were chosen as a feature, the app will likely need these fields (due date, reminder time). The user explicitly selected only Title as saved data. Please confirm whether to add:
  - Due date (datetime)
  - Reminder time/notification

## Validation Rules
1. Title required (user selected)

Recommended (to support reminders & sane data):
- If a due date field is added: due date must be in the future when creating a reminder.
- Reminders should not be allowed after the due date (or should warn/auto-adjust).

## Non-functional Requirements
1. Works offline with local storage and background sync (user selected)
- Local-first storage so tasks are available offline and sync when online.
- Background synchronization to avoid data loss and provide near-real-time updates.

## Extras
1. Backup/export (CSV/JSON export or export to file) — user selected

## Success Criteria / Done Definition
1. Core features done, stable and bug-free: add tasks, due dates/reminders, and reliable basic task management (user selected)
- App can add tasks quickly from the list view.
- Reminders fire on time (when online/offline as per platform limits).
- Export of tasks to CSV/JSON works and can be triggered manually.

## Handling Empty Lists and Mistakes
- Empty list UX: show a friendly illustration and a clear CTA to add the first task.
- Mistake handling: provide undo for deletes and a trash/restore flow (recommendation — not explicitly selected but best practice).

## Open Questions / Next Steps (to confirm with the user)
1. Should due date and reminder fields be added to the saved data model (they are required to support the selected feature of reminders)?
2. Do you want recurrence/recurring reminders later (not selected yet)?
3. Confirm desired platforms (mobile apps, web PWA, desktop) — user selected simple list UI but not target platforms.

---

Prepared from the interview responses. Please review and confirm the assumptions (especially around due date/reminder fields) so I can finalize the PRD.
