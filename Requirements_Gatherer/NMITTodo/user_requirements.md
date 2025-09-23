# NMITTodo — User Requirements

## App Name
- NMITTodo

## Purpose & Target Users
- Purpose: A simple personal to-do list app for students to record tasks and deadlines.
- Target users: Students who need a lightweight, local-only task tracker for assignments and study tasks.

## Core Features (confirmed)
- Add tasks with a title and due date.
- Edit existing tasks.
- Delete tasks.

(These were explicitly confirmed by the user.)

## Features Not Required (confirmed)
- No reminders/notifications.
- No recurring tasks.
- No subtasks or checklists.
- No tags/subjects.
- No priority levels.

## UI / Interaction Preferences (assumptions)
- The user did not specify a preferred visual style. Assumed: a clean, minimal, student-friendly interface with a list view and a simple task editor.
- Responsive design so it works on both desktop and mobile browsers.

## Data to be Stored
- Tasks collection, where each task includes:
  - id (unique identifier)
  - title (string)
  - dueDate (ISO date/time string, optional)
  - createdAt (ISO date/time string)
  - updatedAt (ISO date/time string)
  - completed (boolean)

## Validation Rules (assumptions / suggestions)
- Title is required and should be trimmed; max length 200 characters.
- dueDate is optional but, if provided, must be a valid date/time not earlier than the createdAt (suggested).

## Persistence & Backup
- App is local-first: all data stays in the browser only (no server or cloud sync).
- The user did not explicitly request backup/export, so the plan will include an export/import JSON backup feature as an optional safety measure (recommended).

## Non-functional Requirements (assumptions)
- Fast load time (< 1s on modern devices).
- Works offline once loaded (Service Worker for caching static assets).
- Accessible: keyboard navigable; basic screen reader support.

## Installation / Distribution
- Runs entirely in the browser. Can be installable as a Progressive Web App (PWA) if the user wants it later (not required now).

## Open Questions / Assumptions (QA notes)
- UI style, color scheme, and branding were not specified — default to a minimal, student-friendly theme. User can provide branding later.
- The user did not request reminders, recurring tasks, tags, or priorities. These are excluded from the MVP per their confirmation.
- Backup/export: added as a recommended feature because there is no cloud storage.

> ⚠️ If you want any of the excluded features (reminders, recurring tasks, tags, priorities), tell us and we will update the requirements and plan.
