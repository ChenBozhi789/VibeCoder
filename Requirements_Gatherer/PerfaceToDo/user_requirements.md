# PerfaceToDo — User Requirements

> "PerfaceToDo is a simple personal to-do list for a single user, running entirely in the browser."

## Basic Info

- App name: PerfaceToDo
- Intended users: Single user (personal use)
- Platform: Desktop browsers only
- Installable / PWA: No (not required)
- Data location: Stored locally in the browser only (no server, no cloud)

## Purpose

- Provide a simple personal to-do list and daily planner for a single user to quickly create, edit, and delete tasks.

## Core Features (explicitly requested)

- Create tasks (Title only)
- Edit tasks (modify Title)
- Delete tasks

> Note: The user explicitly requested create/edit/delete as the core feature set and did not request completed/checkbox states or archiving.

## Visual / UI Preferences

- Simple list view (vertical list of tasks). Tasks can be clicked to edit in-place.
- Desktop-first layout (not optimized for mobile).

## Task Data Fields

- Title (required)
  - Maximum length: 100 characters
  - No other fields are required (no description, no dates, no priority, etc.)

## Persistence & Backup

- Data is local-only in the browser.
- The user opted NOT to include export/import or automatic backups. (No backup/export feature requested.)

## Saving Behavior

- Auto-save after each change (no Save button). Changes persist immediately to browser storage.

## Completed / Done Behavior

- The user prefers "Delete only" for finished tasks (no completed checkbox or archive).

## Non-Functional Requirements

- Fast startup and snappy UI: load under 2 seconds on a normal desktop.
- Expected number of tasks: Small — under 500 tasks.

## QA / Clarifications

- The QA agent noted an earlier clarification was needed about completed states; the user confirmed "Delete only" behavior.
- No other ambiguous items remain. If you later want reminders, tags, or export, these will require additional planning.

## Summary (short)

- PerfaceToDo: desktop-only, local-only, very simple to-do app.
- Tasks: Title only, required, max 100 chars.
- Core actions: create, edit, delete.
- Auto-save, no backup/export, delete-only completion.
- Performance target: fast startup (<2s), expected <500 tasks.

