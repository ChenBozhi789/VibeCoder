# SuperTodo - Plan for First Version (MVP)

Summary:
Build a small, fast single-page app for one person to manage tasks with due dates, simple in-app alerts, and checklist items inside tasks. Data will be stored locally in the browser so the app stays private and works without a backend.

Initial prompt for an AI or developer to build the first version:
"Create a simple single-page web app called 'SuperTodo'. It should allow one user to add, edit, and delete tasks, set a due date/time, mark tasks complete, and show in-app alerts for tasks that are due or overdue. Each task can contain simple checklist items that can be added and ticked off (checklist items do not have their own due dates). Store tasks in browser localStorage. Use plain, modern HTML/CSS/JavaScript (or a small framework like React if preferred). Keep the UI minimal and mobile-friendly. No backend or external notifications needed."

MVP feature list:
- Task CRUD: create, read, update, delete.
- Title (required), description (optional), due date/time (optional), completed flag.
- Simple checklist items under each task (add item, check/uncheck, delete item). Checklist items do not have separate due dates.
- List view with simple filters: All, Due Today, Overdue, Completed.
- In-app alerts: a dismissible banner or toast when a task becomes due or is overdue.
- Local persistence: store tasks and checklist items in localStorage.
- Simple responsive layout for mobile and desktop.

Basic UI layout (single page):
- Header: App name "SuperTodo" and an Add Task button.
- Main area: Left/top - Task input form (title, description, due date/time) that can be toggled. The form allows adding checklist items inline. Right/below - Task list grouped by status (Due Today, Overdue, Upcoming, Completed).
- Footer or corner: Small settings button (optional) to clear all tasks or export/import JSON.
- In-app alert area: Top or bottom where toast messages appear for due tasks.

User flows (short):
1) Add a task: Click Add -> enter title (required) -> optional description -> choose due date/time -> add checklist items (optional) -> Save -> task appears in list.
2) Add checklist items: Within task form or task detail, click "Add item" -> enter text -> Save -> item appears under task and can be checked off.
3) Edit task or checklist items: Click task -> edit fields or manage checklist items -> Save.
4) Complete task: Click checkbox -> moves to Completed list.
5) In-app alert: When a task reaches its due time, show a toast/banner: "Task 'X' is due now." Allow Dismiss (snooze can be a future feature).

Data model (example):
- id: string (uuid or timestamp)
- title: string
- description: string
- dueAt: ISO datetime string or null
- completed: boolean
- checklist: array of { id: string, text: string, checked: boolean }
- createdAt: ISO datetime string

Technical suggestions:
- Tech stack: Plain HTML/CSS/JS for fastest MVP, or React + Vite for easier component structure.
- Storage: browser localStorage or IndexedDB for larger needs.
- Time handling: use native Date or a small library like dayjs for parsing/formatting.
- Alerts: in-app toasts implemented with JS timers and a check on app load to show overdue items.

Implementation steps (estimate):
1) Scaffold project (single index.html, styles.css, app.js) or React app.
2) Build task data layer (load/save to localStorage), including checklist items.
3) Build UI: task form with inline checklist item management and task list.
4) Implement filters (All, Due Today, Overdue, Completed).
5) Implement in-app alerts: check tasks every minute or use setTimeout to trigger toasts for upcoming dueAt times; also show overdue tasks on load.
6) Polish UI and responsive styles.
7) Test basic flows and persistence.

Testing checklist:
- Create, edit, delete tasks.
- Add, check/uncheck, and delete checklist items.
- Set a due date/time and confirm in-app alert triggers at the right time.
- Reload browser and confirm tasks & checklist items persist.
- Mark tasks complete and verify they move to Completed.

Suggested next features (guided choices):
1) Make subtasks full tasks with their own due dates & reminders.
2) Add categories/tags & filter bar.
3) Add recurring tasks.
4) Add sync across devices (requires backend).
5) Add push/email notifications.

Guided prompts you can pick (choose one next):
A) "Make subtasks into full tasks (each with due date & reminders)."
B) "Add categories/tags and a filter bar."
C) "Make the app a PWA so it can be installed and work offline fully."
D) "Generate the first version of the app as one HTML/CSS/JS file using localStorage."
E) "I want something else — I'll type my own idea."

Maintenance and iteration plan:
- After MVP is built, get user feedback and add 1-2 small features per sprint (1-2 weeks).
- Prioritize features that improve daily use: snooze, quick-add, due-today view.

