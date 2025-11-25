# Product Requirement Document

**App Name:** BookNook  
**Goal/Purpose:** Help readers maintain a simple personal log of books they’ve read. The app makes it fast to add a book by Title and Author, browse a clean list of entries, and remove items when needed — all offline and without accounts.  
**Target Users:** Avid readers, students, and book club members who want an easy, distraction-free way to track books they’ve finished and keep light notes.

## Core Features
- Quick Add Book: Users can rapidly add a book with Title (required) and Author (required). Optional notes and tags can be added when editing.
- List & Preview: A central list shows all saved books with title, author, and date added. Items are sorted by most recent first.
- **Create/Edit/Delete:** Users can create new book entries, view details, update fields (title, author, notes, tags), and delete entries with confirmation.
- **Search & Filter:** Instant search by title and author; optional filters by tag and sort by date or title.
- **Data Portability:** Export the full book list to a JSON file and import it back for restore or migration.

## Data Model
- **Main Entity:** Book
  - `id`: string (UUID, unique identifier)
  - `title`: string (required)
  - `author`: string (required)
  - `description`: string (optional notes about the book)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)
  - `tags` (optional): array of strings (for filtering and organization)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all books.
  - Key elements: Prominent "New Book" button, search bar, and filter/sort controls.
  - Each list item shows the title, author, creation date, an optional snippet of notes, and a quick delete action (with confirmation).
- **Detail / Form View:**
  - A clean form for creating or editing a book entry.
  - Fields: Title (required), Author (required), Notes (Description), Tags.
  - Actions: Primary "Save" button, "Cancel"/back navigation, and a "Delete" button (with confirmation) for existing items.
- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file (option to merge with or replace existing data).
  - **Export Data:** To a JSON file.
  - **Clear All Data:** A button to wipe all local data, protected by a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** The application must be fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with a focus on usability and basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI must remain responsive and fast, even with 1,000+ items. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion) must require user confirmation. The app should handle storage quota limits gracefully by notifying the user.
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).

## Implementation Notes / Developer Hints
- **Data Storage:** Store all books as a single array of objects in one `localStorage` key (e.g., `BookNook.books`).
- **State Management:** For a simple app, vanilla JS or a lightweight library (like Preact, Vue, or Svelte) is preferred over a heavy framework.
- **Search/Filter Logic:** Implement search and filtering on the client-side by iterating through the main data array and matching against title, author, and tags.
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability.
