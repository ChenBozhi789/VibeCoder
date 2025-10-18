# Product Requirement Document

**App Name:** EasyBook  
**Goal/Purpose:** Provide a lightweight, offline-ready app to create, view, edit, reschedule, and cancel simple bookings/appointments. It helps solo providers, small teams, and households keep track of upcoming bookings without spreadsheets, logins, or internet, with fast search and clear visibility of the schedule.

**Target Users:** Service providers (e.g., tutors, barbers, consultants), small office admins, and families who need a simple, local booking tracker to manage name/date/time slots and keep an organized list of upcoming and past bookings.

## Core Features
- Booking Management (Create/Edit/Delete/Cancel): Users can add a booking with name (title), date, time, optional notes, and status; edit any field; delete bookings; and cancel (mark as cancelled) with confirmation.
- List & Preview: A central list shows all bookings with key info (name, date, time, status, and a short notes preview). Default view highlights upcoming bookings.
- Search & Filter: Instant search by name and description; filters by date range (e.g., today, this week), status (scheduled, cancelled, completed), and optional tags.
- Reschedule: Quickly change date/time for an existing booking with a single action and auto-update timestamps.
- Conflict Warning: Warn the user if another booking exists at the same date and time when creating or editing, with an option to proceed or adjust.
- Data Portability: Export all bookings to a JSON file for backup and import them back (merge or replace) to restore data.

## Data Model
- **Main Entity:** Booking
  - `id`: string (UUID, unique identifier)
  - `title`: string (required; booking name, e.g., customer or purpose)
  - `description`: string (optional; notes/details)
  - `date`: string (ISO date, e.g., YYYY-MM-DD)
  - `time`: string (24h HH:mm)
  - `status`: string enum: `scheduled` | `cancelled` | `completed` (default: `scheduled`)
  - `tags` (optional): array of strings (for filtering and organization)
  - `createdAt`: ISO8601 timestamp (when the booking was created)
  - `updatedAt`: ISO8601 timestamp (when the booking was last modified)

(Secondary entities are not required.)

## User Interface (Views)
- **Home / List View:**
  - Displays a chronological list (upcoming first) of all bookings, with quick access to past bookings via a filter.
  - Key elements: Prominent "New Booking" button, search bar, and filter/sort controls (date range, status, A–Z/date sort).
  - Each row shows title, date, time, status badge, and a notes snippet, plus a quick cancel/delete action with confirmation.

- **Detail / Form View:**
  - Clean form for creating or editing a booking.
  - Fields: Title (required), Date (date picker), Time (time picker), Notes/Description, Tags (comma-separated), Status.
  - Actions: Primary "Save" button; "Cancel"/Back; and "Delete" (with confirmation) for existing bookings.
  - Reschedule affordance: date/time fields are prominent and easy to adjust; show conflict warning if applicable.

- **Settings View:**
  - App-level actions for data management.
  - Import Data: From JSON file; user chooses Merge (add/update by id) or Replace (clear then import). Clear explanation and confirmation.
  - Export Data: To a JSON file containing all bookings.
  - Clear All Data: Wipes all local data (with confirmation dialog and irreversible warning).

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration.
- **UI/UX:** Clean, minimal, responsive design with basic accessibility (keyboard navigation, labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI remains responsive with 1,000+ bookings; initial load under 1 second on a modern browser.
- **Reliability:** Destructive actions (delete, clear all) require confirmation. Handle storage quota limits gracefully with user-friendly messages.
- **Data Safety:** Import/export serves as the primary backup. Data format is simple JSON, documented, and stable.
- **Time/Date Handling:** Use local timezone consistently; avoid ambiguous parsing; validation for date/time inputs.

## Implementation Notes / Developer Hints
- **Data Storage:** Store all bookings as a single array in one `localStorage` key (e.g., `EasyBook.bookings`). Persist a small `EasyBook.settings` object for UI preferences (e.g., default filters).
- **State Management:** Prefer vanilla JS or a lightweight library (Preact, Vue, or Svelte). Keep dependencies minimal.
- **Search/Filter Logic:** Perform client-side filtering by iterating the in-memory array. For date range filters, compare combined date+time values.
- **Conflict Warning:** When saving, check if any other booking shares the same `date` and `time` (and is not cancelled). If conflict, show warning with proceed/cancel options.
- **Timestamps:** Set `createdAt` on first save; update `updatedAt` on every edit.
- **Accessibility:** Ensure form fields have labels, buttons have accessible names, and focus order is logical.
