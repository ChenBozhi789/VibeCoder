# Product Requirement Document

**App Name:** NewTask  
**Goal/Purpose:** Help individuals quickly capture, view, and complete daily to-do items in a simple, fast, and distraction-free interface. The app focuses on making it easy to add tasks, see what’s pending, and mark tasks as done.

**Target Users:** Busy individuals, students, and professionals who need a lightweight, local, privacy-friendly task list for day-to-day planning and execution.

## Core Features
- Mark Complete/Incomplete: Each task can be toggled between active and completed states with a single click (checkbox). Completed tasks remain visible (with a subtle visual distinction) and can be reverted.
- **Create/Edit/Delete:** Users can create, view, update, and delete tasks.
- **List & Preview:** A central view lists all tasks, showing key info like title, created date, completion state, and a short description preview.
- **Search & Filter:** Users can instantly search by keyword and filter by status (All, Active, Completed) and optionally by tags.
- **Data Portability:** Users can export their entire dataset to a JSON file for backup and import it back (merge or replace mode).

## Data Model
- **Main Entity:** Task
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `description`: string (longer text content)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)
  - `tags` (optional): array of strings (for filtering and organization)
  - `completed`: boolean (default: false)
  - `completedAt` (optional): ISO8601 timestamp (when the item was completed)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all tasks.
  - Key elements: Prominent "New Task" button, a search bar, and filter/sort controls (Status: All/Active/Completed; Sort by latest/oldest).
  - Each list item shows: a completion checkbox (primary action), title, creation date, a snippet of the description, and a quick delete action.
  - Visual distinction for completed tasks (e.g., subdued color or strikethrough title).
- **Detail / Form View:**
  - A clean form for creating or editing a task.
  - Fields: Title, Description, Tags, and a Completed toggle (for existing tasks).
  - Actions: A primary "Save" button, a "Cancel" or back navigation, and a "Delete" button (with confirmation) for existing tasks.
- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file. Should clarify if the import will merge with or replace existing data.
  - **Export Data:** To a JSON file.
  - **Clear All Data:** A button to wipe all local data, protected by a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** The application must be fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with a focus on usability and basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI must remain responsive and fast, even with 1,000+ tasks. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion, clear all) must require user confirmation. The app should handle storage quota limits gracefully by notifying the user.
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).

## Implementation Notes / Developer Hints
- **Data Storage:** Store all tasks as a single array of objects in one `localStorage` key (e.g., `NewTask.tasks`). Consider a separate key for simple app settings (e.g., `NewTask.settings`).
- **State Management:** For a simple app, vanilla JS or a lightweight library (like Preact, Vue, or Svelte) is preferred over a heavy framework.
- **Search/Filter Logic:** Implement search and filtering on the client-side by iterating through the main data array. Debounce search input for better performance.
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability. Use a small UUID generator for `id` creation and basic CSS for styling.