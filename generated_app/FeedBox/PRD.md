# Product Requirement Document

**App Name:** FeedBox  
**Goal/Purpose:** FeedBox is a lightweight web app for collecting and reviewing user feedback. It allows users to submit concise feedback with a title, message, and rating, and provides a simple dashboard to browse, search, and understand feedback at a glance. It’s ideal for teams or individuals who need a fast, offline-ready way to gather and organize feedback without a backend.

**Target Users:** Product teams, website owners, indie developers, and support teams who need a simple, private, and offline-capable way to capture and review user feedback.

## Core Features
- Feedback Submission: A clean form to submit feedback with a title, detailed message, and a 1–5 rating (star or number input), plus optional tags.
- Create/Edit/Delete: Users can create, view, update, and delete feedback entries.
- List & Preview: A central dashboard lists all feedback items showing title, rating, date, and a short message preview.
- Search & Filter: Instant client-side search across titles and messages, with filters for rating, tags, and date range; basic sort by date or rating.
- Dashboard Summary: A simple summary bar showing total feedback count and average rating.
- Data Portability: Export all feedback to a JSON file and import it back (choose merge or replace).

## Data Model
- **Main Entity:** Feedback
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `description`: string (longer text content; the feedback message)
  - `rating`: integer (required; 1–5)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)
  - `tags` (optional): array of strings (for filtering and organization)

## User Interface (Views)
- **Home / List View (Dashboard):**
  - Displays a reverse-chronological list of all feedback.
  - Key elements: Prominent "New Feedback" button, a search bar, filter/sort controls (rating, date, tags), and a compact summary bar (total count, average rating).
  - Each list item shows the title, rating (stars or number), creation date, a snippet of the message, and a quick delete action.
- **Detail / Form View:**
  - A clean form for creating or editing a feedback item.
  - Fields: Title (required), Message, Rating (1–5, required), Tags (optional).
  - Actions: Primary "Save" button, "Cancel"/back navigation, and a "Delete" button (with confirmation) for existing items.
- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file. Clarify if the import will merge with or replace existing data.
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
- **Data Storage:** Store all feedback items as a single array of objects in one `localStorage` key (e.g., `feedbox.feedback`).
- **State Management:** Use vanilla JS or a lightweight library (Preact, Vue, or Svelte). Avoid heavy frameworks.
- **Search/Filter Logic:** Implement search and filtering on the client-side by iterating through the main data array; precompute basic summary stats (count, average rating) on load and after mutations.
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability.
- **Validation:** Require title and rating; ensure rating is an integer between 1 and 5; trim inputs; guard against empty or excessively long values.
