# Product Requirement Document

**App Name:** SuperTask  
**Goal/Purpose:** SuperTask is a fast, offline-capable to-do manager that lets people quickly capture, organize, and complete tasks without account setup or sync. It focuses on essential task management with powerful search, simple filters, and safe local data portability.

**Target Users:** Students, professionals, and makers who want a simple, distraction-free way to manage personal tasks in a web browser, working offline or online.

## Core Features
- Essential Task Management: Create tasks with a title and optional description; edit and delete as needed. Includes a quick-complete toggle and bulk delete with confirmation.
- **Create/Edit/Delete:** Users can create, view, update, and delete tasks.
- **List & Preview:** A central view lists all tasks with title, created date, a description snippet, and quick complete/delete actions.
- **Search & Filter:** Instant client-side search across title/description; filters by tags and status (Active/Completed). Sort by created date or title.
- **Data Portability:** Export all tasks to a JSON file for backup and import them back, with merge-or-replace options during import.

## Data Model
- **Main Entity:** Task
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `description`: string (longer text content)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)
  - `tags` (optional): array of strings (for filtering and organization)
  - `completed` (optional): boolean (default `false`, indicates if the task is done)
- (No secondary entities are required.)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all tasks (newest first).
  - Key elements: Prominent "New Task" button, search bar, filter chips (status: All/Active/Completed), tag filter, and sort control (Created date, Title).
  - Each list item shows: title, creation date, a snippet of description, a complete/undo toggle, and a quick delete (with confirmation).
- **Detail / Form View:**
  - A clean form for creating or editing a task.
  - Fields: Title (required), Description, Tags (comma-separated or tokenized), Completed (checkbox when editing).
  - Actions: Primary "Save" button, "Cancel"/Back navigation, and "Delete" (with confirmation) for existing tasks.
- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file. User selects Merge vs Replace behavior; show a preview count of items to be imported.
  - **Export Data:** To a JSON file.
  - **Clear All Data:** Wipes all local data with a typed or double-confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with basic accessibility (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** Remains responsive with 1,000+ tasks. Initial load under 1 second on modern browsers.
- **Reliability:** Destructive actions (e.g., deletion, clear all) require explicit confirmation. Handle storage quota limits gracefully with user-friendly messaging.
- **Data Safety:** Import/export is the primary backup mechanism. Data format is simple and well-documented (JSON).

## Implementation Notes / Developer Hints
- **Data Storage:** Store all tasks as a single array under one `localStorage` key, e.g., `SuperTask.tasks`.
- **State Management:** Prefer vanilla JS or a lightweight library (Preact, Vue, or Svelte) over heavy frameworks.
- **Search/Filter Logic:** Implement entirely on the client by iterating over the in-memory tasks array; debounce search input for smoother UX.
- **Dependencies:** Minimize external dependencies to ensure fast load times and maintainability.
