# Product Requirement Document

**App Name:** GreenTodo  
**Goal/Purpose:** Provide a fast, simple, and offline-ready personal task manager that lets users capture, organize, prioritize, and complete tasks without accounts or cloud dependencies. The app emphasizes quick entry, clear prioritization, and effortless filtering to help individuals stay focused and productive.

**Target Users:** Individuals (students, professionals, freelancers) who want a lightweight, distraction-free to-do app for personal task tracking with due dates and priorities, running entirely in the browser.

## Core Features
- Task Management: Add, edit, delete, and mark tasks as completed. Include due dates and priority levels for clear planning.
- Status Filters: One-click tabs to view All, Active, or Completed tasks; badges show counts for each.
- Sorting & Prioritization: Sort by due date (soonest first), priority (High > Medium > Low), and recently updated.
- Quick Actions: From the list, toggle complete via checkbox and delete a task with a single click (with confirmation).
- **Create/Edit/Delete:** Users can create, view, update, and delete tasks.
- **List & Preview:** A central view lists all tasks with title, due date, priority badge, completion status, and a snippet of notes.
- **Search & Filter:** Instant search across titles and descriptions; filters by status (All/Active/Completed), due date (e.g., Today, This Week, Overdue), and priority.
- **Data Portability:** Export all tasks to JSON for backup and import JSON back into the app (merge or replace options).

## Data Model
- **Main Entity:** Task
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `description`: string (optional, longer text content)
  - `createdAt`: ISO8601 timestamp (when the task was created)
  - `updatedAt`: ISO8601 timestamp (when the task was last modified)
  - `dueDate` (optional): ISO8601 date (deadline for the task)
  - `priority` (optional): string enum ("low" | "medium" | "high"), default "medium"
  - `completed`: boolean (default false)
  - `completedAt` (optional): ISO8601 timestamp (when the task was completed)
  - `tags` (optional): array of strings (for filtering and organization)
- No secondary entities are required.

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of tasks (by updatedAt), with options to switch sorting to due date or priority.
  - Key elements: prominent "New Task" button, search bar, filter chips/tabs (All, Active, Completed), sort control.
  - Each row shows: checkbox (complete), title, due date (with overdue indicator), priority badge (color-coded), optional description snippet, quick delete (with confirm).
  - Sticky toolbar for filters/search/sort on small screens; responsive layout for mobile and desktop.
- **Detail / Form View:**
  - Clean form for creating or editing a task.
  - Fields: Title (required), Description, Due Date (date picker), Priority (Low/Medium/High), Tags (comma-separated or token input), Completed toggle (only when editing).
  - Actions: Primary "Save" button, "Cancel"/back navigation, and "Delete" (with confirmation) for existing tasks.
- **Settings View:**
  - App-level actions and preferences.
  - **Import Data:** From a JSON file; user chooses merge with or replace existing tasks.
  - **Export Data:** Download tasks as a JSON file.
  - **Clear All Data:** Wipes all local data with a clear confirmation dialog.
  - Optional preferences: default sort (due date/priority/recent), show completed at bottom.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration.
- **UI/UX:** Clean, minimal, responsive design with basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** UI remains responsive with 1,000+ tasks; initial load under 1 second on modern browsers.
- **Reliability:** Destructive actions (delete, clear all, replace-on-import) require confirmation. Handle storage quota limits gracefully with user-friendly notices and guidance to export/clean up.
- **Data Safety:** Import/export (JSON) is the primary backup mechanism; data format is simple and documented.
- **Accessibility:** Ensure keyboard operability for all actions; use ARIA labels for controls and maintain sufficient color contrast.

## Implementation Notes / Developer Hints
- **Data Storage:** Store all tasks as a single array in one `localStorage` key, e.g., `GreenTodo.tasks`. Consider a separate key for app preferences, e.g., `GreenTodo.settings`.
- **State Management:** Prefer vanilla JS or a lightweight library (Preact/Vue/Svelte). Keep dependencies minimal.
- **Search/Filter Logic:** Implement client-side search and filters (status, due windows like Today/This Week/Overdue, priority) by iterating the tasks array.
- **Sorting:** Provide stable sorting; when sorting by priority, secondary sort by due date, then updatedAt.
- **Overdue Badge:** Compute `overdue` as `!completed && dueDate < today`.
- **ID Generation:** Use `crypto.randomUUID()` where available; fallback to a small UUID utility.
- **Validation:** Require title; normalize and trim inputs; prevent setting `completed` without setting `completedAt` timestamp.
- **Import/Export:** JSON structure `{ version: 1, tasks: Task[] }`. On import, validate schema; for merge, match by `id` and update/insert; for replace, overwrite.
- **UI Polish:** Color-coded priority (High=red, Medium=amber, Low=green), subtle badges for overdue, and empty state with a helpful prompt.
