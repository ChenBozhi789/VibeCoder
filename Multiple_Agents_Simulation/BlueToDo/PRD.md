# PRD — BlueToDo

## App name
BlueToDo

## Purpose & Users
- Purpose: A simple personal to‑do / productivity app to help individuals keep track of tasks quickly and easily.
- Primary users: Individual users who want a lightweight, fast todo list for day-to-day tasks.

## Key Features (as chosen)
1. Add and edit simple tasks (title, notes)

Note: The feature choice focused on simple task creation/editing. The data model chosen (see below) is minimal to match a lightweight first release.

## UI / UX Notes
- Interface: Simple list view, very minimal and fast.
- Interaction: Quick add input at top or bottom, swipe/delete on touch devices, single-tap to edit.
- Focus on speed: reduce taps needed to add or complete a task, minimal animations.
- Empty state: show a friendly message with a clear CTA button to add the first task.

## Data Model (what the app will save for each task)
- Task
  - id: string/UUID
  - title: string (required)
  - notes: string (optional / planned — feature list included notes but initial saved fields prioritized title)
  - created_at: timestamp
  - updated_at: timestamp

Rationale: You selected to save the Title only (required). Notes are acknowledged in the features selection and listed here as optional/planned so the app remains flexible without adding complexity to the initial implementation.

## Validation Rules
1. Title required (must not be empty).
2. (Optional) Title length limit recommended (e.g., 100 chars) — keep this soft for v1 if needed.

## Non-functional Requirements
1. Offline support: users can create and edit tasks without internet; data is stored locally and persisted between sessions.
2. Fast loading and snappy interactions (goal for minimal perceived latency).

## Extras
1. Backup / Export: manual export to CSV/JSON and option for scheduled backups (user-configurable) so users can preserve or move their data.

## Success Criteria (definition of done)
- Minimal complete release:
  1. Users can create, edit, and delete tasks.
  2. Tasks are saved locally (persisted on device/storage) and available after restart.
  3. Basic validation: title is required.
  4. Empty lists show a friendly empty state with a clear CTA to add tasks.
  5. Mistakes: provide an undo action for deletes (allow quick recovery).

Notes on reminders: The selected success criteria description mentioned "reminders fire," however reminders were not chosen explicitly in the features or saved fields. If reminders are desired, we should add: a) a due date/time and b) reminder settings to the data model and feature list. For the initial minimal release, reminders are optional — clarify if you want them in v1.

## Next steps / Questions
1. Confirm whether you want Notes to be saved in v1 (we listed it as optional/planned). Reply: 1) Keep Notes optional (later); 2) Include Notes in v1. Please answer with 1 or 2.
2. Confirm whether reminders (due date/time + notifications) should be included in the first release. Reply: 1) Not in v1; 2) Include reminders in v1.

---

(This PRD was created from the answers you provided in the interview flow.)
