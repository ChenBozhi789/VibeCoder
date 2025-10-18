# Product Requirement Document

**App Name:** ContactVault  
**Goal/Purpose:** A lightweight, offline-capable personal contact manager that lets individuals quickly store, search, and update contact details without cloud dependencies. It focuses on fast lookup and simple editing for everyday use.

**Target Users:** Individuals who want a simple, private address book for personal use on their own device, including students, freelancers, and everyday users who prefer local data over cloud services.

## Core Features
- Contact Management: Create, view, edit, and delete contacts with essential fields (name, phone, email). Support quick edits to reduce friction.
- List & Preview: Display a clean, scrollable list of contacts showing name plus primary phone or email for quick scanning.
- Search & Filter: Instant, case-insensitive search across name, phone, and email. Optional filters like “has phone,” “has email,” and by tag.
- Data Portability: Export all contacts to a JSON file and import them back. Import flow should let users choose merge vs. replace.
- Basic Validation & Deduplication: Validate phone and email formats and warn of potential duplicates based on normalized phone or email.
- Minimal Tagging (optional): Allow tagging contacts (e.g., “Family,” “Work”) to help with simple organization and filtering.

## Data Model
- **Main Entity:** Contact
  - `id`: string (UUID, unique identifier)
  - `name`: string (required, short text)
  - `phone`: string (optional but recommended)
  - `email`: string (optional but recommended)
  - `notes`: string (optional, longer freeform text)
  - `tags` (optional): array of strings (for filtering and organization)
  - `createdAt`: ISO8601 timestamp (when the contact was created)
  - `updatedAt`: ISO8601 timestamp (when the contact was last modified)

## User Interface (Views)
- **Home / List View:**
  - Displays an alphabetical list of contacts by name with quick access to search.
  - Key elements: "New Contact" button, a search bar, and simple filter/sort controls (A–Z, Z–A, recently updated).
  - Each list item shows the name and a primary detail (phone or email if available), plus quick actions for edit and delete (with confirmation).
- **Detail / Form View:**
  - A clean form for creating or editing a contact.
  - Fields: Name, Phone, Email, Tags, Notes.
  - Actions: Primary "Save" button, "Cancel"/back navigation, and a "Delete" button (with confirmation) for existing contacts.
- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file. Let the user choose to merge with or replace existing data.
  - **Export Data:** To a JSON file.
  - **Clear All Data:** Wipes all local data with a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** The application must be fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with a focus on usability and basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI must remain responsive and fast, even with 1,000+ contacts. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion) must require user confirmation. The app should handle storage quota limits gracefully by notifying the user.
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).
- **Validation:** Use lightweight validation for email (simple pattern) and phone (digits and common symbols), with non-blocking warnings.

## Implementation Notes / Developer Hints
- **Data Storage:** Store all contacts as a single array of objects in one `localStorage` key (e.g., `ContactVault.contacts`).
- **State Management:** Prefer vanilla JS or a lightweight library (Preact, Vue, or Svelte). Keep dependencies minimal.
- **Search/Filter Logic:** Perform client-side search by normalizing strings (lowercase, strip spaces/dashes for phone). Support simple tag-based filtering.
- **Deduplication Heuristics:** Normalize phone (strip non-digits) and email (lowercase) to detect likely duplicates and prompt the user when adding/saving.
- **Form UX:** Support quick edit from the list (inline or via fast modal), keyboard shortcuts (e.g., Enter to save, Esc to cancel), and auto-focus on the Name field.
- **Accessibility:** Ensure labels are associated with inputs, focus states are visible, and all actions are keyboard accessible.
