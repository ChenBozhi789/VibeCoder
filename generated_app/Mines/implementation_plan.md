# Implementation Plan - Mines (Minesweeper)

## Technical Architecture
- State management: Vanilla JS with global appState and pure functions; no modules.
- Data persistence: localStorage for settings, best times per difficulty, and basic stats (games, wins).
- HTML structure: Header with difficulty select and controls, counters (mines left, timer), grid container, footer with stats section.
- Error handling: Guard event handlers; validate custom inputs if present; safe JSON parse.

## Implementation Phases
1) Core Infrastructure: localStorage helpers, state container, timer utility.
2) Grid/HTML Logic: generate board, attach events (left click, right-click), flood-reveal, win/lose.
3) Validation: difficulty bounds, custom inputs (if any), prevent invalid flags/moves; keyboard support.
4) Integration: counters, timer, difficulty switching, persistence of best times and last difficulty.
5) Polish: accessibility (roles, labels), responsive grid, edge cases (first click safe, restart).

## File Structure Plan
- Modify ui/index.html: ensure containers for controls and board; ARIA roles; link js/main.js and css/style.css.
- Replace ui/css/style.css: responsive grid, cells states, controls layout.
- Replace ui/js/main.js: all game logic, state, persistence, event wiring.

## Detailed Features
- Difficulties: Beginner(9x9,10), Intermediate(16x16,40), Expert(30x16,99). Persist last selection.
- Grid and Rules: 2D board, numbers adjacency, zero flood-fill, first click never a mine.
- Flagging & Question: Right-click toggles Flag -> Question -> Clear. 'F' key to flag, Space/Enter to reveal.
- Timer & Counters: Start on first reveal; stop on win/lose; mines left = total mines - flags.
- Stats & Best Times: Track games played, won; best time per difficulty; persisted.
- Accessibility: role=grid and gridcell; tabbable cells; aria-label with cell state.

## Data Model
- appState: { rows, cols, mines, board[][], status, flags, revealedCount, startTime, elapsed, timerId, firstClick, difficulty }
- board cell: { mine:boolean, adj:int, revealed:boolean, flagged:boolean, question:boolean }
- storage keys: mines:lastDifficulty, mines:bestTimes, mines:stats

## Validation Rules
- Difficulty values must be in safe ranges (rows 5-30, cols 5-30, mines < rows*cols).
- Ignore actions after game ended; ignore flagging revealed cells; bounds check on all coords.

## Testing & Validation
- Validate no JS errors, grid builds correctly for each difficulty, timer works, counters update, win/lose conditions correct, persistence saved/restored.


## Implementation Notes
- Core infrastructure and full game logic implemented in js/main.js.
- UI and styles replaced to support Minesweeper gameplay, counters, timer, stats and best times persistence.
- Accessibility: role=grid/gridcell, keyboard navigation with arrows, Space/Enter, and F for flag.
- Persistence keys: mines:lastDifficulty, mines:bestTimes, mines:stats.

## Additions Implemented
- Custom difficulty: rows, cols, mines with validation and persistence (min 5, max 30; mines < rows*cols).
- First-click-safe toggle: persisted; influences mine placement safety zone.
- Data Portability: Export to mines-data.json; Import from JSON with validation; updates stats, best times, settings.
- Clear Stats: Resets played/won counts and best times.
- Touch support: Long-press to flag; tap to reveal.
- Error handling: Inline error banner for invalid custom inputs and import failures.

## Final Validation and Documentation
- Validated UI interactions: reveal, flag/question cycle, first-click-safe behavior, win/lose states, counters.
- Stats and best times persist via localStorage and update correctly after games.
- Custom difficulty validated with bounds; errors shown inline; persisted last custom settings.
- Data portability works: Export JSON and Import with schema validation and UI refresh.
- Accessibility: role=grid/gridcell, keyboard navigation (arrows), Space/Enter reveal, F to flag, ARIA labels.
- Touch support: long-press to flag, tap to reveal.
- Responsive design: grid and controls adapt to smaller screens.

## Acceptance Checklist
- [x] All required documents read and understood (PRD.md, app_spec.json, UI_STRUCTURE.json).
- [x] implementation_plan.md created and updated.
- [x] Core infrastructure implemented (vanilla JS state, localStorage persistence).
- [x] All HTML logic implemented in ui/index.html and js/main.js.
- [x] Data flow working across controls, board, and stats.
- [x] Validation and error handling in place for custom inputs and imports.
- [x] PRD/app_spec features implemented: difficulties (incl. custom), grid interaction, flagging & questions, timer & counters, stats & best times, accessibility & controls, data portability.
- [x] Documentation updated (implementation_plan.md).
