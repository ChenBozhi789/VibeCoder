# JSONTODO — User Requirements

> "local first to-do"

## App name
- JSONTODO

## Purpose
- A simple, local-first to-do list app that runs entirely in the browser and stores data on the user's device. The user described it as: "local first to-do".

## Target users
- Individuals who want a small, fast, offline-capable task list (e.g., developers, students, and anyone wanting local-only task management).

## Core features (explicitly requested)
- Simple task list with the ability to add, edit, and delete tasks.
  - Add task (title required)
  - Edit task title and mark complete/incomplete
  - Delete task

## Features not requested / assumed minimal defaults
- No due dates, reminders, tags, priorities, recurring tasks, or attachments unless the user later requests them.

## UI preferences (user did not specify details)
- Single-page layout with a concise task entry area and a list view of tasks. Minimal, distraction-free interface.

## Data to be stored
Each task will store the following fields (minimal set):
- id (string, generated)
- title (string)
- completed (boolean)
- created_at (ISO timestamp)
- updated_at (ISO timestamp)

## Validation rules
- title: required, max length 200 characters
- No other required fields

## Persistence and backup
- Data will be stored locally in the browser (no server). The app will provide a manual export/import (JSON) feature so users can back up and restore their data if they wish.

## Offline behavior
- The app must work fully offline and load quickly from cached assets.

## Platform / accessibility
- Desktop-first design but should be usable on mobile screens.
- Basic accessibility: keyboard operable, semantic HTML for screen readers.

## Installability & extras
- Installable as a Progressive Web App (PWA) is optional; included in the plan as an easy enhancement.

## Notes / Open questions
- The user selected only the basic task list feature and indicated they were fine with defaults for subsequent questions. If the user later wants reminders, tags, or syncing, those will be added in a future version.

