# SuperTodo - User Requirements

Overview:
This document captures the user's answers and the core requirements for SuperTodo, a single-page app (SPA).

Collected Answers (from the interview):
- App name: SuperTodo
- App type: Personal task/to-do list with reminders (single-page app)
- Main users: Just me (personal use)
- Key features requested: Due dates & reminders
- Reminder delivery: Simple in-app alerts only (no external notifications)
- Subtasks & checklists: Simple checklist items under a task — you can tick them off, but they have no own due dates or reminders.

Goals:
- Let a single user quickly add, edit, and remove tasks.
- Allow setting due dates and receiving simple in-app alerts for upcoming or overdue tasks.
- Support simple checklists inside tasks (no separate due dates for checklist items).
- Keep the app fast and easy to use, with a clean single-page interface.

Must-haves (MVP):
- Add, edit, delete tasks.
- Set a due date/time for each task.
- Mark tasks completed/incomplete.
- Simple checklist items under each task that can be added and ticked off.
- In-app alerts: visible notifications inside the app (banners, modal, or toast) when a task is due or overdue.
- Data stored locally in the browser (no account/sync required) so the app works offline in basic form.

Nice-to-have (future iterations):
- Subtasks as full tasks with their own due dates & reminders (if requested later)
- Categories/tags & filters
- Recurring tasks
- Simple notes & attachments
- Sync across devices

Constraints and decisions from user choices:
- No push notifications or emails — only in-app alerts.
- Designed for a single user (no multi-user/team features).
- Checklists are simple items attached to a parent task; they do not have separate reminder behavior.

Acceptance criteria:
- A user can create a task with a title and optional description.
- A user can add checklist items to a task and tick them off.
- A user can set a due date/time on the task.
- When a task reaches its due time (or is overdue), the app shows an in-app alert that the user can dismiss.
- Tasks and their checklist items persist between browser sessions (using localStorage or equivalent).
- The app is a single-page web app with a minimal, mobile-friendly UI.

Open questions to confirm before development (one at a time):
1) Do you want offline capability where the app fully works without internet? (Yes/No)
2) Do you want tasks to support reminders at specific times or just a date? (date only / date + time)
3) Would you like a quick way to see 'Due today' and 'Overdue' lists? (Yes/No)

