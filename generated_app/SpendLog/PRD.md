# Product Requirement Document

**App Name:** SpendLog  
**Goal/Purpose:** Help individuals quickly capture daily expenses with minimal friction and provide instant visibility into a running list and totals over time. SpendLog focuses on fast entry (description + amount), clear summaries, and simple review to encourage consistent tracking and spending awareness.

**Target Users:** Individuals who want a lightweight, offline-ready expense tracker without accounts or complexity—students, professionals, or anyone looking to log spending quickly and see totals at a glance.

## Core Features
- **Quick Add Expense:** A single, prominent form to enter a description and amount; date defaults to “now.” Hitting Enter saves immediately. Optional tags can be added for organization.
- **Running Totals & Summaries:** Display the total for the currently selected period (e.g., Today by default) and support quick ranges like Today, This Week, This Month, and Custom Date Range.
- **Create/Edit/Delete:** Users can create, view, update, and delete expenses.
- **List & Preview:** A central view lists all expenses in reverse chronological order, showing description, date/time, amount (formatted by currency), and optional tags.
- **Search & Filter:** Users can search by text (matches description and tags) and filter by date range and tags. Sorting by date (newest first) and by amount is supported.
- **Data Portability:** Users can export all expenses and settings to JSON for backup and import them back (merge or replace).

## Data Model
- **Main Entity:** Expense
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text; the expense description)
  - `amountInCents`: integer (required, non-negative; store amounts as integer cents to avoid floating-point errors)
  - `currency`: string (ISO code, e.g., "USD"; default from Settings)
  - `occurredAt`: ISO8601 timestamp (when the expense happened; defaults to now)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)
  - `tags` (optional): array of strings (for filtering and organization)
- (No secondary entities required.)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all expenses (default filter: Today).
  - Summary bar shows the total for the current filter (e.g., Today’s total) and quick range selectors (Today, Week, Month, Custom).
  - Key elements: Prominent "New Expense" or inline quick-add form, a search bar, filter controls (date range, tags), and sort options.
  - Each list item shows description (title), occurred date/time, amount (currency formatted), and a quick delete action.
- **Detail / Form View:**
  - A clean form for creating or editing an expense.
  - Fields: Description (Title), Amount, Date/Time (OccurredAt), Tags. Amount input supports currency formatting; internally saved as integer cents.
  - Actions: Primary "Save" button, "Cancel"/back navigation, and a "Delete" button (with confirmation) for existing items.
- **Settings View:**
  - A dedicated page or modal for app-level actions and preferences.
  - **Currency:** Choose a default currency (ISO code, used for formatting new entries).
  - **Import Data:** From a JSON file; user chooses merge or replace behavior.
  - **Export Data:** To a JSON file.
  - **Clear All Data:** A button to wipe all local data, protected by a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** The application must be fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with a focus on usability and basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI must remain responsive and fast, even with 1,000+ expenses. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion) must require user confirmation. The app should handle storage quota limits gracefully by notifying the user.
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).

## Implementation Notes / Developer Hints
- **Data Storage:**
  - Store all expenses as a single array of objects in one `localStorage` key, e.g., `SpendLog.expenses`.
  - Store settings (e.g., default currency) in `SpendLog.settings`.
- **Amount Handling:** Use `amountInCents` (integer) for storage and calculations; format for display using the selected currency and locale.
- **State Management:** Vanilla JS or a lightweight library (Preact, Vue, or Svelte) is preferred over a heavy framework.
- **Search/Filter Logic:** Implement client-side search and filtering by iterating through the main data array; date range filters should operate on `occurredAt`.
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability.