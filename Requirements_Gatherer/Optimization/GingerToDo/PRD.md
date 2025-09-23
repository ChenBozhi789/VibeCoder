# PRD — GingerToDo

## Purpose & Users
- Purpose: Help the single user (you) track personal tasks.
- Users: Personal single-user app — no multi-user or team support required.

## Features (as requested)
- Add tasks (primary feature requested).
- View tasks in a simple list.
- Basic task actions expected for core functionality: mark complete, edit, delete, and reorder (minimal inferred features to make the app usable).

## Look & Feel (UI/UX)
- Simple list interface (clean, minimal). 
- Single-screen or primary list view; mobile-friendly layout is optional but not required unless specified later.

## Information to Save (Data Model)
- Tasks (minimum fields):
  - id (unique identifier)
  - title (string)
  - notes (optional string)
  - created_at (timestamp)
  - completed (boolean)
- Note: user requested "basic necessary info" — primary required field is title; other fields are optional.

## Rules & Validation
- The user specified "nothing else" for checks. No strict validations beyond minimal sensible defaults.
  - Recommended minimal rule: allow empty or non-empty notes; titles can be required or optional per later preference (no strict validation requested).

## Non-functional Requirements
- Must work offline (offline-first behavior / local persistence).
- Load quickly and remain responsive (implicit priority for a small personal app).

## Extras
- No need for backups or export (CSV/JSON) as per user request.
- Offline installability (PWA or local install) is acceptable if desired, since offline capability was requested.

## Success Criteria (When it's done)
- Core features implemented to a usable standard (add/view/edit/complete/delete tasks in a simple list, offline storage working).
- The user indicated the single success criterion: "core features implemented." Additional UX polish (empty-list messaging, undo for delete) can be added later if desired.

## Open Questions / Assumptions
- "Basic necessary info" was left vague; PRD assumes title is primary and notes are optional. Confirm if you want due dates, reminders, or priorities later.
- Validation rules were not requested; confirm if you want title required or other checks.

---
Generated from a short interview. If you want any fields changed (e.g., require title, add due dates, enable reminders, or include backups), say which and I will update the PRD.
