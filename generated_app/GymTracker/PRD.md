# Product Requirement Document

**App Name:** GymTracker  
**Goal/Purpose:** Help gym-goers quickly log each exercise they perform during a workout, capturing the number of sets and the reps for each set. This enables simple progress tracking over time without friction, fully offline and privacy-friendly.

**Target Users:** Individuals who lift weights or do resistance training and want a lightweight way to record their exercises. Suitable for beginners and experienced lifters who prefer a simple, fast, offline tracker.

## Core Features
- Exercise logging with per-set reps: Users can add a log entry for a single exercise and record the reps for each set (e.g., 12, 10, 8). They can add or remove set rows easily.
- Create/Edit/Delete: Users can create new exercise logs, view details, update, and delete entries.
- List & Preview: A central list shows each exercise log with exercise name, workout date, number of sets, and a compact preview of reps (e.g., "12/10/8").
- Search & Filter: Instant search by exercise name and optional filters by date (e.g., today, this week) or tags.
- Data Portability: Export all logs as a JSON file and import them back to restore or move data.

## Data Model
- **Main Entity:** ExerciseLog
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, exercise name)
  - `description`: string (optional notes)
  - `createdAt`: ISO8601 timestamp (when the log was created)
  - `updatedAt`: ISO8601 timestamp (when the log was last modified)
  - `workoutDate`: ISO8601 date or datetime (the date the exercise was performed)
  - `repsPerSet`: array<number> (required; each entry is the reps performed in one set)
  - `tags` (optional): array<string> (for filtering/organization, like muscle group)

(Only one main entity is required. A separate Workout entity is not necessary; each ExerciseLog represents one exercise performed on a given date.)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of exercise logs.
  - Key elements: prominent "New Log" button, a search bar (by exercise name), and filter/sort controls (by date, sets count).
  - Each list item shows: exercise name (title), workout date, sets count, and a preview of reps (e.g., "12/10/8"). Include a quick delete action with confirmation.
- **Detail / Form View:**
  - A clean form for creating or editing an ExerciseLog.
  - Fields: Exercise Name (Title), Workout Date, Notes (Description), and a dynamic list of Set inputs (reps per set). Provide buttons to add/remove set rows. Validate reps as positive integers.
  - Actions: primary "Save" button; "Cancel"/Back; and a "Delete" button (with confirmation) for existing entries.
- **Settings View:**
  - A simple page or modal with app-level actions.
  - **Import Data:** From a JSON file; allow user to choose merge vs. replace existing data.
  - **Export Data:** Download all data as JSON.
  - **Clear All Data:** Wipes local data with a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync.
- **Offline First:** Fully functional offline.
- **Single-User:** No authentication or collaboration.
- **UI/UX:** Clean, minimal, responsive; basic accessibility (labels, keyboard navigation, contrast).

## Non-Functional Requirements
- **Performance:** UI remains responsive with 1,000+ logs; initial load under 1 second on modern browsers.
- **Reliability:** Deletions require confirmation. Handle storage quota limits gracefully with user-friendly messages.
- **Data Safety:** JSON import/export is the primary backup. Keep the JSON format simple and documented.

## Implementation Notes / Developer Hints
- **Data Storage:** Store all `ExerciseLog` items as a single array under one `localStorage` key, e.g., `GymTracker.items`.
- **State Management:** Prefer vanilla JS or a lightweight framework (Preact, Vue, or Svelte) for simplicity and speed.
- **Search/Filter Logic:** Implement client-side filtering by iterating the in-memory array. Precompute sets count from `repsPerSet.length` and preview string by joining reps with "/".
- **Validation:** Require `title` and at least one set in `repsPerSet`. Ensure reps are positive integers.
- **Dependencies:** Minimize external libraries to ensure fast load times and maintainability.
