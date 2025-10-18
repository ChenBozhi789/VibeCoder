# Product Requirement Document

**App Name:** GoalSetter  
**Goal/Purpose:** Help individuals plan, track, and complete personal goals by setting clear targets, visualizing progress, and marking achievements. The app provides a simple, offline-first workspace to keep goals organized and actionable.

**Target Users:** Individuals focused on personal development and productivity (students, professionals, and self-improvement enthusiasts) who want a lightweight tool to define goals, track progress over time, and celebrate completion.

## Core Features
- Goal planning workspace with target dates: Create goals with titles, descriptions, tags, and a target date, and visualize time remaining.
- Progress tracking: Update progress (0–100%) via a slider or number input; show a progress bar in the list and detail views.
- Achievements and status: Mark goals as achieved/unachieved; auto-stamp the achieved date and freeze progress at 100% when achieved.
- Sorting and organization: Sort by target date, creation date, last updated, or progress; optional tags for grouping.
- Quick actions: Inline actions to mark achieved, adjust progress, and delete with confirmation from the list.
- **Create/Edit/Delete:** Users can create, view, update, and delete goals.
- **List & Preview:** A central view lists all goals, showing key info like title, target date, progress bar, and status (Active/Achieved).
- **Search & Filter:** Users can instantly search goal titles and descriptions, and apply filters by status (Active/Achieved), due state (Overdue/Due Soon/All), and tags.
- **Data Portability:** Users can export their entire dataset to a JSON file for backup and import it back.

## Data Model
- **Main Entity:** Goal
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `description`: string (longer text content)
  - `createdAt`: ISO8601 timestamp (when the goal was created)
  - `updatedAt`: ISO8601 timestamp (when the goal was last modified)
  - `targetDate`: ISO8601 date (the intended completion date)
  - `progress`: number (0–100, percentage complete)
  - `achieved`: boolean (true if the goal is completed)
  - `achievedAt` (optional): ISO8601 timestamp (when it was marked achieved)
  - `tags` (optional): array of strings (for filtering and organization)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list (by updatedAt) of all goals.
  - Key elements: Prominent "New Goal" button, a search bar, and filter/sort controls.
  - Each list item shows: title, target date (with days remaining), a progress bar, status (Active/Achieved), and a quick delete action.
  - Optional visual cues: Overdue goals highlighted; goals nearing due date indicated (e.g., within 7 days).
- **Detail / Form View:**
  - A clean form for creating or editing a goal.
  - Fields: Title, Description, Tags, Target Date, Progress (slider or numeric input), Achieved toggle.
  - Actions: Primary "Save" button, "Cancel"/back navigation, and a "Delete" button (with confirmation) for existing goals.
  - Behavior: When marking Achieved = true, set `progress` to 100 and set `achievedAt` if not already set.
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
- **Performance:** The UI must remain responsive and fast, even with 1,000+ goals. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion, clear all) must require user confirmation. The app should handle storage quota limits gracefully by notifying the user.
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).

## Implementation Notes / Developer Hints
- **Data Storage:** Store all goals as a single array of objects in one `localStorage` key (e.g., `GoalSetter.goals`). Consider a secondary key for settings (e.g., `GoalSetter.settings`).
- **State Management:** For a simple app, vanilla JS or a lightweight library (like Preact, Vue, or Svelte) is preferred over a heavy framework.
- **Search/Filter Logic:** Implement search and filtering on the client-side by iterating through the main data array. Precompute derived flags like `isOverdue` based on `targetDate`.
- **Date Handling:** Use native Date and Intl APIs or a tiny helper for formatting and day-difference calculations to avoid heavy dependencies.
- **UI Components:** Progress bar component, goal list item with quick actions, confirmation modal.
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability.