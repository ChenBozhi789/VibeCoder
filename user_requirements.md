# user_requirements.md

## Summary

- Purpose: Personal productivity app for simple to-dos (checklist items) for a single user on their desktop computer. The app runs entirely in the browser and stores data only on the device.

> "Personal productivity (to-dos, notes)." — user selected: simple to-dos only.

## Target users

- Individual users who want a minimal, desktop-focused to-do app for personal task tracking.

## Core features (what the user wants to accomplish)

- Create and edit simple to-do items (one-line tasks).
- Mark tasks as completed with a checkbox.
- Minimal feature set: no subtasks, no priorities, no tags, no reminders, no attachments, no notes — only a title per task.

## UI / Layout / Style

- Desktop-first design (keyboard & mouse primary).
- Visual style: support both light and dark themes with a toggle.
- Slightly larger default text for readability.
- Minimal, uncluttered interface. (User did not specify a detailed layout; developer will choose a simple, easy-to-use layout optimized for desktop.)

## Data to be stored

- Each to-do item stores:
  - Title (required, max 50 characters)
  - Completed status (boolean)

> Note: The user asked for only Title (required) as the visible field. Any additional metadata (created/modified timestamps, internal IDs) will be internal only and not requested by the user.

## Validation rules

- Title is required and cannot be empty or whitespace-only.
- Title max length: 50 characters. Longer input should be rejected with a clear message.

## Persistence / Backups

- App is local-only: data stays on the device and in the browser; no server or cloud sync.
- The user explicitly chose: no backups needed — user accepts the risk that data may be lost if the device is cleared or the browser data is removed.

## Installable / Offline

- The user requested the app be installable as a Progressive Web App (PWA) so it can be added to the desktop, open like a native app, work offline, and have an icon.

## Accessibility / Non-functional notes

- Desktop orientation prioritized.
- Slightly larger text for readability requested.
- No explicit accessibility requirements were provided by the user; developer should still follow basic accessibility best practices (keyboard focus, semantic markup).

## Anything else

- The user prefers a minimal feature set and explicitly selected "keep it minimal — no extras." They said that the information provided is sufficient and asked to generate the project files.

---

*Confirmed choices (as the user answered during Q&A):*

- Purpose: Personal productivity — simple to-dos
- Core features: A) Simple to-dos (checklist items)
- Extras: G) Keep it minimal — no extras
- Data fields: A) Title (required)
- Title max length: A) 50 characters
- Completion state: A) Yes — simple checkbox to mark complete
- Devices: A) Desktop (keyboard & mouse)
- Style: E) Dark/light theme toggle + slightly larger text
- Backups: C) No backup needed (user accepts risk)
- Installable: A) Yes — make it installable (PWA)
