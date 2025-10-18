# Product Requirement Document

**App Name:** BookTrackr  
**Goal/Purpose:** Help readers effortlessly track what they are reading, how far along they are, and when they finish. The app keeps a simple personal library with progress and status so users can stay motivated and organized without the friction of complex tools.  
**Target Users:** Avid readers, students, and book club members who want a lightweight, offline-friendly way to record books, monitor current page progress, and mark completion.

## Core Features
- Reading Progress Tracking: Add total pages (optional) and update current page; show a progress bar/percentage; quick increment buttons for common updates (e.g., +1, +5 pages).
- Finish & Status Management: Mark books as finished; automatically set finishedAt and (if provided) snap currentPage to totalPages.
- **Create/Edit/Delete:** Users can create, view, update, and delete books.
- **List & Preview:** A central view lists all books, showing key info like title, author, status, and a progress preview.
- **Search & Filter:** Users can instantly search all books and apply simple filters (e.g., by status: Reading/Finished, by author, or tags).
- **Data Portability:** Users can export their entire dataset to a JSON file for backup and import it back.

## Data Model
- **Main Entity:** Book
  - `id`: string (UUID, unique identifier)
  - `title`: string (required)
  - `author`: string (required)
  - `description`: string (optional notes about the book)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)
  - `tags` (optional): array of strings (for filtering and organization)
  - `totalPages` (optional): number (total number of pages)
  - `currentPage`: number (defaults to 0; cannot exceed `totalPages` if provided)
  - `status`: string enum ("reading" | "finished"); derived from actions and progress
  - `finishedAt` (optional): ISO8601 timestamp (when the book was marked finished)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all books (by updatedAt), optionally grouped or filterable by status.
  - Key elements: Prominent "New Book" button, a search bar, and filter/sort controls (Status, Author, Tags; Sort by Updated/Created/Title).
  - Each list item shows: Title, Author, Status (Reading/Finished), progress indicator (currentPage/totalPages with a bar or percentage), and last updated date.
  - Quick actions per item: +1 page, +5 pages (disabled when finished), Mark Finished, and Delete (with confirmation).

- **Detail / Form View:**
  - A clean form for creating or editing a book.
  - Fields: Title (required), Author (required), Total Pages (optional), Current Page (number), Description/Notes (multiline), Tags (chips or comma-separated).
  - Validation: Current Page must be >= 0 and <= Total Pages (if set). Title/Author required.
  - Actions: Primary "Save" button; "Cancel" or back navigation; "Delete" (with confirmation) for existing books; "Mark Finished" toggle/action that sets status and finishedAt and aligns currentPage to totalPages when present.

- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file. Should clarify if the import will merge with or replace existing data (provide a choice with default = merge).
  - **Export Data:** To a JSON file.
  - **Clear All Data:** A button to wipe all local data, protected by a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** The application must be fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with a focus on usability and basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI must remain responsive and fast, even with 1,000+ books. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion, Clear All) must require user confirmation. The app should handle storage quota limits gracefully by notifying the user.
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).
- **Validation & Safety:** Prevent invalid page updates (e.g., negative numbers or currentPage > totalPages). When finishing a book without totalPages, allow finishing and set currentPage unchanged.

## Implementation Notes / Developer Hints
- **Data Storage:** Store all books as a single array of objects in one `localStorage` key (e.g., `BookTrackr.books`). Consider a separate key for app-level settings (e.g., `BookTrackr.settings`).
- **State Management:** Use vanilla JS or a lightweight library (Preact, Vue, or Svelte). Keep state in memory, persist on each change.
- **Search/Filter Logic:** Implement client-side search across title, author, and tags. Provide status filters (Reading/Finished). Use debounced input for search.
- **Progress Logic:** Derive percentage as `currentPage / totalPages` when totalPages exists; handle division-by-zero by hiding percentage or showing page-only progress.
- **Status Logic:** If `currentPage >= totalPages` (and totalPages set) or user taps "Mark Finished", set `status = "finished"` and `finishedAt = now`. Otherwise `status = "reading"`.
- **Sorting:** Default sort by `updatedAt` desc; allow user to switch to Title or Created date.
- **UX Details:** Inline toasts/snackbars for Save/Delete/Import actions. Keyboard-accessible controls. Confirmation dialogs for Delete and Clear All.
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability.