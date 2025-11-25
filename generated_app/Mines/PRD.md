# Product Requirement Document

**App Name:** Mines  
**Goal/Purpose:** Deliver a fast, clean, offline-capable Minesweeper game that lets players enjoy quick logic puzzles on any device. Players uncover safe cells on a grid while avoiding hidden mines, using numeric hints to deduce safe moves. The app emphasizes smooth play, configurable difficulty, and lightweight persistence for settings and best times.

**Target Users:** Casual gamers and puzzle enthusiasts who want a quick mental challenge during short breaks. Ideal for users who value classic gameplay, responsiveness, and minimal distractions.

## Core Features
- New Game & Difficulty Selection: Presets for Beginner, Intermediate, Expert, plus Custom (width, height, mine count). Optional “first click is always safe.”
- Grid Interaction & Rules: Reveal cells; auto-flood reveal of contiguous empty cells; numbers show adjacent mine counts; game reveals all mines on loss; win is detected when all non-mine cells are revealed.
- Flagging & Question Marks: Right-click (or long-press on touch) to cycle hidden → flagged → question; mine counter updates based on flags.
- Timer & Counters: Timer starts on first reveal; shows elapsed time and remaining mines; optional move counter.
- Stats & Best Times: Track best times per difficulty, total games played/won, win rate; allow reset of stats.
- Accessibility & Controls: Keyboard navigation (arrow keys), Reveal (Enter/Space), Flag (F), and high-contrast color scheme option for color-blind accessibility.
- Data Portability: Export/import JSON for settings and stats so users can back up or migrate their data.

## Data Model
- **Main Entity:** Game
  - `id`: string (UUID, unique identifier)
  - `title`: string (e.g., "Expert Game – 2025-11-05 14:03")
  - `description`: string (optional, free text)
  - `createdAt`: ISO8601 timestamp
  - `updatedAt`: ISO8601 timestamp
  - `tags` (optional): array of strings (e.g., ["expert", "win"])  
  - `difficulty`: string enum ("beginner" | "intermediate" | "expert" | "custom")
  - `width`: number (grid columns)
  - `height`: number (grid rows)
  - `mines`: number (mine count)
  - `seed` (optional): string (for reproducible board generation)
  - `status`: string enum ("idle" | "inProgress" | "won" | "lost")
  - `elapsedMs`: number (milliseconds; timer starts on first reveal)
  - `moves`: number (incremented on reveals/flags)
  - `firstClickSafe`: boolean
  - `grid`: 2D array of cell objects with fields:
    - `hasMine`: boolean
    - `adjacent`: number (0–8)
    - `state`: string enum ("hidden" | "revealed" | "flagged" | "questioned")

(Note: Settings and stats are persisted separately but are not separate primary entities.)

- **Settings (stored in localStorage):**
  - `difficultyDefault`: string enum
  - `custom`: { `width`: number, `height`: number, `mines`: number }
  - `firstClickSafe`: boolean
  - `highContrast`: boolean
  - `soundEnabled`: boolean (optional)

- **Stats (stored in localStorage):**
  - `bestTimes`: { `beginner`?: number, `intermediate`?: number, `expert`?: number, `custom`?: number }
  - `gamesPlayed`: number
  - `gamesWon`: number

## User Interface (Views)
- **Home / List View (Game History):**
  - Displays recent games with difficulty, result (win/loss), time, date.
  - Controls: "New Game" button, filter by difficulty, sort by date/time, quick delete of a history entry.
  - Each item shows difficulty badge, elapsed time, and status.

- **Detail / Form View (New Game / Board):**
  - For creating a new game or resuming the current one.
  - Form fields (when starting a new game): Difficulty preset, or custom Width, Height, Mines; First-click-safe toggle.
  - Board UI: Grid with left-click/tap to reveal, right-click/long-press to flag/question; header with timer and remaining mines; Reset button; Pause overlay.

- **Settings View:**
  - Preferences: High-contrast mode, first-click-safe default, sound on/off.
  - Data Portability: Import JSON (merge or replace) and Export JSON.
  - Clear All Data: Wipes settings, stats, and history with confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for settings, stats, and optional game history. No backend required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, accounts, or collaboration.
- **UI/UX:** Clean, minimal, responsive design with keyboard navigation, proper labels, and sufficient contrast.

## Non-Functional Requirements
- **Performance:** Maintain smooth interactions on grids up to 50x50 with 500+ mines. Initial load under 1 second in modern browsers. Flood-reveal should complete within 50ms for typical boards.
- **Reliability:** Destructive actions (clear data, delete history) require confirmation. Enforce safe-first-click if enabled. Handle storage quota gracefully with user-friendly error messages.
- **Data Safety:** JSON import/export for settings and stats. Document the JSON structure in help or comments.

## Implementation Notes / Developer Hints
- **Data Storage:**
  - `localStorage` keys, e.g., `mines.settings`, `mines.stats`, `mines.history`, `mines.currentGame`.
  - Store history as an array of `Game` objects without the full `grid` for completed games to save space (keep summary fields only).
- **Board Generation:**
  - Defer mine placement until the first reveal to guarantee a safe initial click; then place mines using RNG (seeded if `seed` provided) and compute adjacency counts.
  - Implement flood-reveal via BFS/DFS when `adjacent === 0`.
  - Support chording: if a revealed number’s adjacent flags equal its number, reveal remaining adjacent hidden cells.
- **Input & Accessibility:**
  - Desktop: Left click reveal; Right click flag/question; Middle click chording (optional).
  - Touch: Tap reveal; Long-press to flag/question; Provide on-screen toggles for devices without right-click.
  - Keyboard: Arrow keys move focus; Space/Enter reveal; F flags; Q toggles question.
- **Rendering:** Use semantic HTML + CSS Grid for the board; prefer lightweight JS (vanilla, Preact, Svelte). Avoid heavy dependencies for fast load and maintainability.
- **Testing:** Include unit tests for board generation and flood-reveal; simulate edge cases (all mines on edges, near corners, etc.).