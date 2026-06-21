# Implementation Plan — Super Mine Sweeper

## 1) Scope & Requirements (from PRD.md + app_spec.json)
### Core gameplay
- Click to reveal cells.
- Reveal mine => lose.
- Reveal safe => show adjacent mine count; flood-reveal contiguous zero regions.
- Win when all non-mine cells are revealed.

### Difficulty levels
- Beginner: 9x9, 10 mines
- Intermediate: 16x16, 40 mines
- Expert: 30x16, 99 mines

### Flagging
- Right-click (context menu) or long-press (mobile) to toggle flag.
- Flagged cells cannot be revealed by left click.

### Timer
- Starts on first reveal.
- Stops on win/lose.
- Reset on new game.

### Scoreboard (persistence)
- Store best (shortest) time per difficulty in `localStorage`.
- Show best time and current time.

### UI requirements
- Clear indicators; color-coded numbers 1-8.
- Responsive grid sizing for mobile/desktop.
- Keyboard accessibility where practical.

## 2) Technical Architecture
### State management (vanilla JS, single file)
Maintain a single `state` object in `js/main.js`:
- `difficulty`, `rows`, `cols`, `mineCount`
- `board` (array of cell objects)
- `revealedCount`, `flagCount`
- `gameStatus`: 'ready' | 'playing' | 'won' | 'lost'
- `startTimeMs`, `timerId`, `elapsedMs`

Render is derived from state:
- `renderHeader()` updates score/timer/best, mine counter, status message.
- `renderGrid()` creates grid buttons and sets classes/text.

### Data persistence (localStorage)
Keys:
- `sms.bestTimes` => JSON: `{ beginner: number|null, intermediate: number|null, expert: number|null }`
- (Optional) `sms.settings` => last difficulty

Persist on win and on difficulty change.

### Validation / Safety
- Clamp mines to `< rows*cols`.
- Avoid first-click mine: on first reveal, ensure clicked cell is safe (generate mines after first click or regenerate if hit).
- Prevent timer duplication, clear interval on stop/reset.
- Block reveal when flagged or game ended.
- Flood fill uses iterative stack to avoid recursion depth.

## 3) Files to Modify / Create
### Create
- `css/style.css` (new; referenced by index.html)
- `js/main.js` (new; referenced by index.html)

### Modify
- `index.html`
  - Add difficulty selector
  - Add timer + best time display
  - Add mine counter, flag hint, status text
  - Ensure grid container uses CSS grid.

## 4) Implementation Phases
1. **Core infrastructure**
   - Implement localStorage helpers: `loadBestTimes()`, `saveBestTimes()`
   - Timer helpers: `startTimer()`, `stopTimer()`, `resetTimer()`, `formatTime(ms)`
2. **Board generation**
   - Cell structure: `{ r,c, isMine, adjacent, revealed, flagged }`
   - Place mines randomly excluding first-click cell
   - Compute adjacent counts
3. **Gameplay interactions**
   - Left click => reveal logic + win/lose evaluation
   - Right click / long press => flag toggle
   - Reset button => `newGame(difficulty)`
4. **Rendering**
   - Render header elements
   - Render grid cells (buttons for accessibility)
   - Apply number colors with CSS classes
5. **Validation & edge cases**
   - Flood reveal, bounds checks
   - Mobile long press
   - Prevent context menu on grid
6. **Testing & QA**
   - Run `validate_implementation()`
   - Fix missing files / broken selectors
   - Manual acceptance checks

## 5) DOM Contract (IDs/classes)
- Existing:
  - `#grid-container`, `#reset-button`, `#score`
- Add:
  - `#difficulty`
  - `#timer`
  - `#best-time`
  - `#mines-left`
  - `#status`

## 6) Acceptance Checklist Mapping
- Multiple grid sizes ✅ (selector)
- Flagging ✅ (right click / long press)
- Timer ✅ (starts first click)
- Scoreboard ✅ (best time per difficulty persisted)
- Responsive UI ✅ (CSS grid, scalable cells)
