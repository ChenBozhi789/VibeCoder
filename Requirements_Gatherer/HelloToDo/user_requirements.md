# HelloToDo - User Requirements

## App Name
- HelloToDo

## Purpose and Target Users
- Purpose: A simple, personal to-do list app that runs entirely in the user's browser (local-first).
- Target users: A single user who wants an easy, private way to add, edit, and delete personal tasks.

## Core Features (explicitly requested)
- Add tasks (title + optional details).
- Edit tasks.
- Delete tasks.

## Backup / Export
- Include an explicit backup/export feature: user can download their data to a file and later upload it to restore tasks. (User answered: Yes.)

## Items Not Explicitly Specified (open or default choices)
> The following items were not specified by the user and are left as open questions or reasonable defaults for the MVP.

- Due dates & reminders: Not requested.
- Tags/labels and filtering: Not requested.
- Priority levels: Not requested.
- Recurring tasks: Not requested.
- Subtasks/checklists: Not requested.
- Search and sort: Not requested.
- Installable as PWA: Not explicitly requested.
- Simple statistics: Not requested.

## Basic Data to Store (minimum, based on requested features)
- Task ID (unique)
- Title (required)
- Description / notes (optional)
- Created timestamp
- Updated timestamp
- Completed flag (boolean)

## Validation Rules (minimum)
- Title: required, non-empty, max length (suggested 250 chars).
- Description: optional, max length (suggested 2000 chars).

## Non-Functional Expectations (assumed/asked)
- Local-first: The app runs entirely in the browser and does not send user data to any server.
- Offline-capable: The user will be able to use the app without an internet connection.
- Performance: Fast load, small bundle size (MVP should be lightweight).

## Accessibility & Platforms
- Platform: Not explicitly specified. Default: Desktop-first with responsive layout for mobile.
- Accessibility: Not explicitly specified. Recommend basic accessibility (keyboard navigation, readable contrast).

## Branding and UI Preferences
- Not specified by the user. Default: Clean, minimal, low-friction UI focused on quickly adding and completing tasks.

## Follow-ups / Open Questions (QA notes)
- Do you want a simple Installable app (PWA "Add to Home Screen")?
- Do you want the ability to mark tasks as completed? (This is assumed but not explicitly stated.)
- Any preference for task fields beyond title and description (e.g., due date, priority, tags)?
- Any platform preference (mobile-only, desktop-only, or both)?

> QA note: The user provided a minimal set of requirements (task CRUD + backup). Several typical task app features were not specified — the plan will treat them as out-of-scope for the MVP but propose sensible defaults and extension points.

## Summary (in the user's words)
- "HelloToDo is a simple personal to-do list app to add, edit, and delete tasks, with the ability to export and import data for backup. It will run entirely in the browser and keep data local."