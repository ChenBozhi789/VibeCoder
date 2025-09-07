# cbzTodo — Development Plan

## Overview
cbzTodo is a local-first, single-page shopping list app designed for families who share a single device (phone or tablet). The app focuses on simplicity: creating, editing, and deleting multiple shopping lists and managing items within those lists. All data stays on the user’s device; no cloud sync is included in the MVP.

> Purpose: Help family members coordinate shopping using one shared device with fast, offline-capable access to shopping lists. 📱

## Functional Requirements

### Core features (user stories)

1. Create/Edit/Delete shopping lists
   - As a family member, I can create a named shopping list (e.g., "Weekly Groceries") so I can collect items for a trip to the store.
   - Acceptance criteria:
     - [ ] User can add a new list with a name (required) and optional description.
     - [ ] User can rename a list.
     - [ ] User can delete a list with a confirmation prompt.

2. Add/Edit/Delete items inside a list
   - As a user, I can add items to a list with common fields so I can track what to buy.
   - Item fields (defaults for MVP): name (required), quantity (optional), unit (optional), category (optional), notes (optional), bought flag (checkbox).
   - Acceptance criteria:
     - [ ] Users can add items with at least a name.
     - [ ] Users can edit item fields.
     - [ ] Users can delete items.
     - [ ] Users can mark items as bought/unbought (toggle checkbox).

3. Multiple lists support
   - As a user, I can manage multiple separate lists (e.g., weekly, pantry, event) and switch between them.
   - Acceptance criteria:
     - [ ] User can create multiple lists and switch between them in the UI.

4. Export/Import (backup & sharing)
   - As a user, I can export my lists to a JSON file and import JSON to restore or transfer lists between devices.
   - Acceptance criteria:
     - [ ] Export creates a downloadable JSON file with all lists and items.
     - [ ] Import accepts the exported JSON format and merges or replaces data (user chooses).

5. PWA Installable & Offline-capable
   - As a user, I can install the app to my device (add to home screen) and use it without network access.
   - Acceptance criteria:
     - [ ] App installs as a PWA and launches offline.
     - [ ] Static assets are cached by a Service Worker.

### Not included in MVP
- Cloud sync across devices, barcode scanning, automatic reminders/notifications, multi-device real-time sharing.

## Non-Functional Requirements

- Performance: Fast initial load (under 1.5s on modern mobile), list interactions should be instantaneous (no perceptible delay).
- Size: Minimal dependencies; keep bundle < 300 KB gzipped if possible.
- Accessibility: Aim for WCAG 2.1 AA where reasonable (keyboard focus, color contrast, screen reader labels).
- Offline-first: Full read/write functionality with no network required.
- Privacy: All user data stays on device; data only leaves device when user exports.

## UI/UX Design

### High-level layout
- Single-page layout with three main areas:
  1. Sidebar / top dropdown: list of shopping lists (Create / Rename / Delete actions) — shows list names and counts.
  2. Main panel: items for the selected list, with Add Item input at top and item rows beneath.
  3. Footer / toolbar: actions like Export, Import, Settings, and PWA install prompt.

### Components
- List Sidebar (or dropdown on small screens)
  - Shows lists with quick add button (+)
  - Long-press or context menu for rename/delete on mobile
- Item Row
  - Checkbox (bought)
  - Item name (primary)
  - Quantity + Unit (secondary)
  - Category tag (small pill)
  - Edit button (pencil) and delete button (trash)
- Add/Edit Item Modal or Inline Form
  - Fields: Name (text), Quantity (number or text), Unit (select/short text), Category (select or free text), Notes (optional multiline)
- Empty States
  - Friendly messages when there are no lists or no items in a list (e.g., “No items yet — tap + to add your first item”).

### Behavior & Interactions
- Tapping an item checkbox toggles bought state with a brief visual change (strike-through and dim).
- Swipe-to-delete on mobile for item rows (optional) with an undo toast.
- Confirm on list delete to prevent accidental loss.

## Data Model

We will use IndexedDB for structured, reliable storage of list and item data. For a small app, a lightweight wrapper (e.g., idb) is recommended but plain IndexedDB APIs may be used.

Data schema (MVP):

| Store / Table | Key | Fields | Notes |
|---|---:|---|---|
| lists | listId (UUID) | name (string), description (string), createdAt (ISO), updatedAt (ISO) | Each shopping list record. |
| items | itemId (UUID) | listId (FK), name (string), quantity (string), unit (string), category (string), notes (string), bought (boolean), createdAt (ISO), updatedAt (ISO) | Items reference parent list via listId. |

Indexes:
- items: index on listId to query items by list quickly.

Local export format (JSON):
{
  "version": 1,
  "lists": [ { list object } ],
  "items": [ { item object } ]
}

## Validation & Edge Cases

- Required fields:
  - List name: required, trimmed, max 100 chars.
  - Item name: required, trimmed, max 200 chars.
- Quantity: optional. Accepts either a positive numeric value or short free text (e.g., "2", "a bunch").
- Units and categories: optional free text with suggestions based on recent entries.
- Deleting a list deletes related items (confirmation required).
- Importing JSON with incompatible version: show an error and refuse import or offer a best-effort conversion.
- Storage limits: if the device storage quota is reached, show a clear error and suggest export & delete.

## Storage & Persistence

- Local-first: Use IndexedDB for data and Cache API + Service Worker to cache static assets.
- Data never sent to a remote server by default.
- Backup/export: Add explicit Export and Import actions in Settings.
  - Export: download JSON file named cbzTodo-backup-YYYYMMDD.json
  - Import: allow user to choose whether to merge with existing data or replace it.

## Implementation Plan

### Tech choices
- Framework: Vanilla JavaScript + small utilities (recommended) to keep size small and avoid build complexity.
- Optional: Use a tiny UI helper (e.g., lit or Svelte) if the developer prefers faster componentization; otherwise plain DOM with modules.
- Storage: IndexedDB (using idb library optional).
- Build: Optional simple bundler (Vite/Rollup) for dev; production can be a single static bundle.
- PWA: Service Worker with precache of core assets and runtime caching of others.

### Folder / File Structure (suggested)

- src/
  - index.html
  - main.js
  - app.js (entry for SPA routing & state)
  - components/
    - listSidebar.js
    - itemRow.js
    - itemForm.js
    - modal.js
  - db/
    - db.js (IndexedDB wrapper)
  - styles/
    - main.css
  - sw.js (Service Worker)
  - manifest.json
- dist/ (build output)
- tests/ (manual and automated test scripts)

### Key implementation notes
- Use a single global state object that is persisted to IndexedDB after changes.
- Keep UI updates reactive but minimal (update only changed rows).
- Provide undo for delete via a short-lived toast.

## Quality Assurance Checklist

- Functionality
  - [ ] Create, rename, delete list
  - [ ] Add, edit, delete item
  - [ ] Toggle bought state
  - [ ] Export and import JSON (merge and replace options)
  - [ ] Data persistence across app restarts
- Offline & PWA
  - [ ] App loads and functions offline after initial load
  - [ ] App shows install prompt and can be added to home screen
- Performance
  - [ ] App loads in < 1.5s on modern mobile (cold cache)
  - [ ] UI interactions respond within 100 ms
- Accessibility
  - [ ] All interactive elements reachable by keyboard
  - [ ] Proper ARIA labels for main controls
  - [ ] Contrast ratios meet WCAG 2.1 AA where possible
- Edge cases & Errors
  - [ ] Import invalid JSON displays helpful error
  - [ ] Storage quota errors handled gracefully
  - [ ] Deleting list asks for confirmation

## Success Criteria ✅
- The MVP allows users to create, edit, delete multiple shopping lists and items, with data stored locally and export/import working reliably.
- The app is installable as a PWA and works offline with cached assets and persisted data.
- No critical bugs; basic accessibility and performance targets met.

## Future Enhancements (not in MVP) 💡
- Optional cloud sync for cross-device collaboration (user opt-in).
- Barcode scanning to add products quickly.
- Shared lists between family members via optional file-based exchange or QR code transfer.
- Smart suggestions and frequently used items / templates.


> ⚠️ Notes / Assumptions: The user ended the session early and only explicitly requested list create/edit/delete. The plan assumes sensible defaults (multiple lists, item fields, export/import, PWA). These assumptions should be confirmed before development.
