# Product Requirement Document

**App Name:** Local Booking Manager  
**Goal/Purpose:** A simple, offline-first reservation manager for solo providers and small teams to create, view, edit, and cancel bookings with clear availability checks. It helps prevent double-booking, provides both calendar and list views, and keeps all data stored locally for privacy and speed.

**Target Users:** Independent service providers (e.g., tutors, coaches, stylists, consultants) and small studios that need a lightweight, no-login booking tracker they can run locally in a browser.

## Core Features
- Calendar & List Views: Users can toggle between a calendar (Month/Week/Day) and a compact list view to see upcoming and past reservations at a glance.
- Date/Time Picker & Validation: Friendly date/time selection with validation (start before end, required fields, sensible default durations).
- Availability/Conflict Checks: On create/edit, the system detects overlapping reservations and prevents or warns about conflicts before saving.
- Cancellation Flow: Users can cancel a reservation (status change) with confirmation; canceled items remain visible (and filterable) for history.
- **Create/Edit/Delete:** Users can create, view, update, and delete the main items (reservations).
- **List & Preview:** A central view lists all items, showing key info like title, date, and a content preview.
- **Search & Filter:** Users can instantly search all content and apply simple filters (e.g., by date or tags).
- **Data Portability:** Users can export their entire dataset to a JSON file for backup and import it back.

## Data Model
- **Main Entity:** Reservation
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text; e.g., "Client Name – Session")
  - `description`: string (longer text content / notes)
  - `startDateTime`: ISO8601 timestamp (required)
  - `endDateTime`: ISO8601 timestamp (required; must be after `startDateTime`)
  - `status`: string enum ("scheduled", "cancelled", "completed"; default "scheduled")
  - `tags` (optional): array of strings (for filtering and organization)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)

(Only one main entity is used. No secondary entities like resources or rooms are included by default.)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all reservations with a toggle to switch to Calendar view (Month/Week/Day).
  - Key elements: Prominent "New Reservation" button, a search bar, and filter/sort controls (by date range, status, tags).
  - Each list item shows: title, start–end time, status badge, and a quick cancel action (with confirmation). Deleted items require confirmation.
  - Calendar view highlights reservations, shows conflicts visually (overlaps), and supports clicking a slot or event to create/edit.

- **Detail / Form View:**
  - A clean form for creating or editing a reservation.
  - Fields: Title (required), Description, Tags, Start Date/Time, End Date/Time, Status.
  - Actions: Primary "Save" button (disabled until valid), "Cancel" or back navigation, and a "Delete" button (with confirmation) for existing items. Provide a dedicated "Cancel Reservation" action that sets status to "cancelled" with confirmation.
  - Validation & Conflict UX: Inline validation messages and a clear conflict warning banner when overlaps are detected, with options to adjust times.

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
- Time zone: Use the user's local browser time zone for display and storage (ISO with offset). No cross-timezone scheduling is required.

## Non-Functional Requirements
- **Performance:** The UI must remain responsive and fast, even with 1,000+ items. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion, clear all) must require user confirmation. Handle storage quota limits gracefully (surface clear error messages and next steps).
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).
- **Validation:** All required fields must be validated on the client; conflicts must be checked before save.

## Implementation Notes / Developer Hints
- **Data Storage:** Store all reservations as a single array of objects in one `localStorage` key (e.g., `localBookingManager.reservations`). Maintain a separate key for app settings if needed (e.g., `localBookingManager.settings`).
- **State Management:** Prefer vanilla JS or a lightweight library (Preact, Vue, or Svelte). Avoid heavy frameworks to keep load times low.
- **Calendar:** For a minimal footprint, implement a simple calendar grid, or use a lightweight dependency only if necessary. Month/Week/Day can be simple tabs that render different time scales.
- **Search/Filter Logic:** Implement client-side filtering by iterating the reservations array. Index by lowercase `title`, `tags`, and date range checks.
- **Conflict Detection:** Before save, check for overlaps with other reservations where `status !== 'cancelled'` by comparing intervals (`[startDateTime, endDateTime)`). Use ISO strings and compare via Date objects.
- **Validation Rules:** Require `title`, `startDateTime`, and `endDateTime`. Enforce `end > start`. Show inline errors.
- **Dependencies:** Minimize dependencies. If needed for dates, prefer a small library (e.g., date-fns or dayjs) over moment.js.
- **Accessibility:** Ensure keyboard navigation for calendar cells, proper ARIA labels for date/time controls, and sufficient color contrast for status badges.
