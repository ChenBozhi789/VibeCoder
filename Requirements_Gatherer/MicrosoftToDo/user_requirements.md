# MicrosoftToDo — User Requirements

## Summary
A local-first personal task manager (single-user) named "MicrosoftToDo" that runs entirely in the browser on desktop. The app focuses on simple task creation, inline editing, and a completed status. Data remains on the device (no backups or cloud sync by user choice).

## Purpose and Target Users
- Purpose: Keep and manage personal tasks quickly and simply on a desktop browser.
- Target users: Individuals who want a lightweight, local-only to-do list on desktop.

## Core Features (as requested)
- Create tasks (quick add).
- Edit tasks (inline edit by clicking/double-clicking the title).
- Delete tasks.
- Mark tasks completed (checkbox to check/uncheck).
- Single list only (no sidebar or multiple lists).
- Tasks remain in creation order (no reordering or sorting options).
- Completed tasks move to a "Completed" section at the bottom.

## UI / Layout
- Layout chosen: Single list view (no sidebar). A simple header with app title, theme toggle, and an add-task input above the list.
- Inline edit: click or double-click the task title to edit inline.
- Desktop-focused design (not mobile-first).
- Theme: Light and dark modes, switchable.

## Data to be Stored
- Each task stores:
  - Title (required, maximum 100 characters)
  - Completed status (Yes — stored as boolean)  

Note: To preserve creation order, the implementation will store an internal creation timestamp for each task (internal metadata). This was added by the team to ensure stable ordering.

## Validation Rules
- Title: required (cannot be empty), max length 100 characters.
- No other fields required.

## Persistence and Backups
- Data stays local in the browser only (local-first).  
- User chose: No backup/export features for MVP (data only in browser).  
- App will not include automatic backups or cloud sync in MVP.

## Non-functional Requirements
- Desktop browsers only.
- No special accessibility or performance requirements were requested.

## Behavior Details / Edge Cases
- Completed tasks: when checked, the task is moved to a "Completed" section at the bottom. Users can uncheck to move it back to active list.
- Empty list: app should show a friendly message like "No tasks — add your first task".

## Outstanding / Assumed Items (team clarifications)
- The user was not able to confirm whether the completed state should be stored; the team assumed "Yes" since the user chose the completed option earlier.
- Default single list name: team will use "Inbox" as the list name internally (UI will show just the list title). If you prefer a different default name, please tell us.
- Created timestamp is included as internal metadata to maintain creation order (not editable by the user).

> ⚠️ If any of these assumptions are incorrect, please tell us which ones to change (e.g., enable backups, allow multiple lists, change default list name).

*End of requirements summary.*
