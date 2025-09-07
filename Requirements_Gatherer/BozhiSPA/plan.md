BozhiSPA - Plan

1) App summary
- Name: BozhiSPA
- Type: Habit tracker / recurring tasks (To-do / Task manager focused on habits)
- Target users: Individuals managing personal habits
- Storage: Local-only (data stored in the browser)

2) Collected requirements (from interview)
- Main purpose: Habit tracker with recurring tasks and daily check-ins
- Target users: Individuals managing personal habits
- Key features: Daily habit check-ins with streaks
- Account model: Local-only storage (no sign-in)

3) Prioritized feature list (MVP)
- Core: Create/edit/delete habits
- Core: Daily check-in UI (mark habit done for today)
- Core: Streak tracking (current streak, longest streak)
- Core: History view (past check-ins by date)
- Core: Local persistence via localStorage
- Nice-to-have later: Export/import backup, reminders via browser notifications, simple analytics (progress chart), gamification (points/badges)

4) User stories
- As a user, I want to add a new habit (name + frequency) so I can track it daily.
- As a user, I want to mark a habit as done today so my streak updates.
- As a user, I want to see my current and longest streak for each habit.
- As a user, I want to view my recent history of check-ins to review progress.
- As a user, I want my data to persist in the browser so I don't lose progress.

5) UI / UX plan (simple, single-page)
- Header with app name and quick add
- Left / top area: list of habits with status, streaks, and quick check button
- Main area: selected habit details and history calendar/list
- Footer: simple links (export, settings)
- Mobile-first responsive design, clear large checkboxes/buttons for daily use

6) Data model (localStorage JSON)
- habits: array of habit objects {
    id: string,
    name: string,
    createdAt: ISO date string,
    schedule: { type: "daily" | "weekly" | "custom", details?: any },
    history: array of date strings (ISO) for check-ins,
    currentStreak: number,
    longestStreak: number
  }

7) Suggested tech stack
- Framework: React (Vite) or Vue (Vite) — default: React + Vite for wide familiarity
- Styling: simple CSS or Tailwind for quick UI
- Persistence: localStorage (sync on change)
- Build: single-page app, no backend

8) Milestones & timeline (suggested)
- Milestone 1 (0-1 day): Scaffold the SPA, basic layout, localStorage helper
- Milestone 2 (1-2 days): Habit CRUD, check-in flow, streak calculation
- Milestone 3 (2-3 days): History view, mobile responsive UI
- Milestone 4 (3-4 days): Export/import backup, optional notifications

9) Next steps
- Confirm any additional features (export, notifications, analytics)
- Choose whether to generate the initial scaffold now and which framework to use
- After scaffold: iterate on UI and add optional features based on feedback

Notes:
- Because storage is local-only, switching devices will not sync data unless export/import is used.
- Browser notifications require permission; reminders can be added later as an opt-in feature.
