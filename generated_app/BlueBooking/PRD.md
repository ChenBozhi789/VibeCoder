# Product Requirement Document

**App Name:** BlueBooking  
**Goal/Purpose:** Provide a simple, offline-capable reservation manager that lets users create, view, edit, and cancel bookings while preventing time conflicts. Designed for solo operators and small teams who need an easy way to manage appointments without a backend.

**Target Users:** Independent service providers (e.g., tutors, consultants, personal trainers) and small shops that need a lightweight, private booking tool to track reservations locally on a single device.

## Core Features
- Reservation management with date/time pickers: Users can create, view, edit, and cancel reservations with start and end times.
- Availability checks: The app prevents overlapping reservations (for active bookings) and clearly indicates conflicts before saving.
- Calendar and List views: A calendar view (month/week) to visualize bookings and a sortable list view for quick scanning.
- Create/Edit/Delete: Users can create, view, update, and delete reservations.
- Search & Filter: Quick text search plus filters by date range and status (booked, cancelled, completed).
- Data Portability: Export/import all reservations as JSON for backup/restore.
- Basic Form Validation: Required fields (title, start/end times), validation of time ranges (end after start), and friendly error messages.

## Data Model
- **Main Entity:** Reservation
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text; e.g., client name or booking title)
  - `description`: string (longer notes)
  - `startDateTime`: ISO8601 timestamp (required)
  - `endDateTime`: ISO8601 timestamp (required; must be after start)
  - `status`: string enum (`booked` | `cancelled` | `completed`), default `booked`
  - `tags` (optional): array of strings (for filtering and organization)
  - `createdAt`: ISO8601 timestamp (creation time)
  - `updatedAt`: ISO8601 timestamp (last modification)
  - `contactEmail` (optional): string
  - `contactPhone` (optional): string
  - `partySize` (optional): number

## User Interface (Views)
- **Home / List View:**
  - Displays reservations in reverse-chronological order by start date/time.
  - Key elements: Prominent "New Reservation" button, a search bar, and filter/sort controls (date range, status, tag).
  - Toggle to switch between List and Calendar views (week/month). Calendar shows bookings by time slot.
  - Each list item shows title, start–end times, status, and quick actions (view/edit, quick cancel/delete with confirmation).
- **Detail / Form View:**
  - A clean form for creating or editing a reservation.
  - Fields: Title, Description, Tags, Start Date/Time, End Date/Time, Status (for existing items).
  - Actions: Primary "Save" button, "Cancel"/back navigation, and a "Delete" button (with confirmation) for existing reservations.
  - Validation/Conflicts: Prevent saving if end time is before start, and if the time range overlaps another active reservation. Show a clear inline error.
- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - Import Data: From a JSON file. Clarify whether the import merges with or replaces existing data (provide both options with a confirmation dialog).
  - Export Data: To a JSON file of all reservations and settings.
  - Clear All Data: Wipes all local data with a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage (key: `BlueBooking.reservations`). No backend or cloud sync is required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration.
- **UI/UX:** Clean, minimal, and responsive with basic accessibility (keyboard navigation, labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI remains responsive with 1,000+ reservations. Initial load under 1 second on a modern browser.
- **Reliability:** Destructive actions (delete/clear) require confirmation. Handle storage quota limits gracefully with informative messages.
- **Data Safety:** Import/export is the primary backup. Use a simple, well-documented JSON format.

## Implementation Notes / Developer Hints
- **Data Storage:** Store all reservations as a single array of objects under one `localStorage` key (e.g., `BlueBooking.reservations`). Optionally store UI preferences (e.g., last selected view) under `BlueBooking.settings`.
- **State Management:** Prefer vanilla JS or a lightweight library (Preact, Vue, Svelte). Keep dependencies minimal for speed and maintainability.
- **Calendar:** Use a simple in-app calendar rendering (no heavy libraries). Support week and month views; allow clicking a slot to start a new reservation.
- **Search/Filter Logic:** Implement client-side filtering by iterating the main array. For text search, check title/description/tags fields.
- **Availability Checks:** To detect conflicts, compare the new reservation range `[start, end)` against all existing active reservations and block save if any overlap.
- **Date/Time Inputs:** Use native `datetime-local` inputs for broad browser support. Normalize to ISO strings when storing.
- **Sorting:** Default sort by `startDateTime` descending in list view; provide an option to sort ascending.
