# Product Requirement Document

**App Name:** TaskProMax  
**Goal/Purpose:** TaskProMax is a local-first, offline-capable task manager that helps individuals quickly capture, organize, and complete tasks without relying on cloud services. It delivers smart views, fast search, reminders, and optional recurrence in a clean, accessible UI, with a modular architecture ready for future sync/export.

**Target Users:** Individuals, students, freelancers, and professionals who prefer a private, distraction-free, and fast task manager that works entirely in the browser—even without internet access—while remaining simple and accessible.

## Core Features
- Smart Task Management: Create, view, edit, and delete tasks with quick status toggles (done/undone) and optional due dates.
- List & Preview: A central list of tasks with title, key dates, status, and a short description preview; quick actions for complete/delete.
- Search & Filter: Instant search across titles and descriptions; filters by status (active/done), tags, due date ranges (today, upcoming, overdue), and recurrence.
- Smart Views: Predefined and user-adjustable views like Today, Upcoming (next 7 days), Overdue, Completed, and Recurring; each is a saved filter with sort settings.
- Reminders & Recurrence (optional): In-app reminders that trigger while the app is open; optional browser notifications (with permission). Simple recurrence patterns (daily/weekly/monthly or custom) with automatic next occurrence generation when completing a task.
- Data Portability: Export and import all data (tasks, settings, views) as JSON files for backup and restore.
- Accessibility & Keyboard Support: Keyboard shortcuts for quick add/save/toggle; semantic structure, proper labels, and focus states.

## Data Model
- **Main Entity:** Task
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `description`: string (longer text content)
  - `createdAt`: ISO8601 timestamp (when the task was created)
  - `updatedAt`: ISO8601 timestamp (when the task was last modified)
  - `status`: string enum (`"todo" | "done"`)
  - `tags` (optional): array of strings (for filtering and organization)
  - `dueDate` (optional): ISO8601 timestamp (task due date/time)
  - `remindAt` (optional): ISO8601 timestamp (reminder time)
  - `recurrence` (optional): object
    - `type`: string enum (`none | daily | weekly | monthly | custom`)
    - `interval` (optional): number (e.g., every 2 days)
    - `byWeekday` (optional): array<number 0-6> (for weekly patterns)
    - `count` (optional): number of occurrences
    - `until` (optional): ISO8601 date limit

(Secondary entities are not required; smart views are stored as settings.)

## User Interface (Views)
- **Home / List View:**
  - Displays a list of tasks with sort options (created date, due date, title) and filters (status, tags, smart ranges like Today/Overdue).
  - Key elements: Prominent "New Task" button, a search bar, filter/sort controls, and a Smart Views sidebar (Today, Upcoming, Overdue, Completed, Recurring).
  - Each list item shows title, status, due date indicator, and a snippet of the description; quick actions for toggle complete and delete.
- **Detail / Form View:**
  - A clean form to create or edit a task.
  - Fields: Title, Description, Tags, Status, Due Date, Reminder, Recurrence.
  - Actions: Primary "Save", "Cancel"/back navigation, and "Delete" with confirmation for existing tasks.
- **Settings View:**
  - App-level actions and preferences.
  - Import Data (JSON): Option to merge or replace existing data; clear messaging about effects.
  - Export Data (JSON): Full dataset export.
  - Clear All Data: Wipes local data with a confirmation dialog.
  - Notifications: Request/Manage permission for browser notifications (if enabled by the user).
  - Smart Views: Optional simple configuration (enable/disable default views).

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** UI remains responsive with 1,000+ tasks; initial load under 1 second on modern browsers.
- **Reliability:** Destructive actions (delete/clear) require confirmation. Gracefully handle storage quota limits (surface clear guidance and export option).
- **Data Safety:** Import/export is the primary backup mechanism. The data format is straightforward and documented (JSON); imports validate schema.

## Implementation Notes / Developer Hints
- **Data Storage:**
  - Store all tasks as an array in one key (e.g., `taskpromax.tasks`).
  - Store settings and smart view configs separately (e.g., `taskpromax.settings`, `taskpromax.views`).
- **State Management:** Vanilla JS or a lightweight framework (Preact, Vue, or Svelte). Keep dependencies minimal.
- **Search/Filter Logic:** Client-side search through the in-memory array. Cache derived lists (e.g., Today/Overdue) for quick rendering.
- **Reminders:**
  - Use an interval timer (e.g., every 60 seconds) while the app is open to check `remindAt` against current time and `status`.
  - Optionally request Notification API permission and show notifications if allowed; otherwise, use in-app toasts/banners.
  - Note: Background notifications when the app is closed are not guaranteed without a service worker + server; keep in-app reminders as the baseline.
- **Recurrence:** When a recurring task is marked done, generate the next occurrence based on `recurrence` rules (e.g., same time next day/week/month). Avoid retroactive changes to completed instances.
- **Accessibility:** Include ARIA labels where appropriate, maintain focus order, and ensure keyboard access for all actions.
- **Dependencies:** Prefer zero or minimal dependencies; consider a small date library (e.g., Day.js) for reliable date math if needed.
