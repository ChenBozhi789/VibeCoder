# BlueBooking Implementation Plan

This document outlines the complete plan to transform the HTML/CSS/JS prototype into a fully functional BlueBooking application.

## 1. Summary of Requirements (from PRD and app_spec)
- App: BlueBooking – offline-capable reservation manager.
- Users: Solo operators / small teams; manage appointments without backend.
- Core Features:
  - CRUD bookings (create, view, edit, delete/cancel).
  - Conflict prevention: No overlapping bookings (same date and overlapping times).
  - Date/time pickers, today navigation, calendar/day view list.
  - Search by client/title/notes; filter by status; sort by time.
  - Local persistence via localStorage.
  - Import/export JSON.
  - Accessibility and basic responsive design.

## 2. Technical Architecture
- Stack: Vanilla HTML/CSS/JS (bare-bones-vanilla-main template).
- State Management: In-memory JS object with persistence sync to localStorage.
- Persistence: localStorage key `bluebooking.bookings` and `bluebooking.state`.
- HTML Structure: Single-page layout with:
  - Header actions (Today, New Booking, Import/Export).
  - Search/filter bar.
  - Date selector (day view) and booking list.
  - Modal form for add/edit.
- Error handling & validation:
  - Required fields: title/client, date, start time, end time.
  - start < end enforced.
  - Conflict detection with existing bookings (same date overlapping time).
  - Inline error messages and non-blocking toasts.

## 3. Implementation Phases
1) Core Infrastructure:
   - State bootstrapping, load/save from localStorage, id generation, utils.
2) HTML Logic:
   - Implement DOM bindings, render functions for list and form, interactions.
3) Data Validation:
   - Validate on submit; show errors; block invalid/overlapping saves.
4) Integration:
   - Connect actions (search/filter/sort/day navigation/import/export).
5) Polish:
   - Empty states, keyboard navigation, accessible labels, basic responsiveness.

## 4. File Structure Plan
- Modify in place, do not add new files beyond documentation:
  - ui/index.html: full layout, modal, and controls.
  - ui/css/style.css: styles for layout, modal, list, forms, toasts.
  - ui/js/main.js: all application logic (state, persistence, UI, validation).
  - implementation_plan.md (this document).

## 5. Detailed Feature Implementation
- Booking data model:
  { id, title, client, date (YYYY-MM-DD), start (HH:MM), end (HH:MM), status ('confirmed'|'tentative'|'cancelled'), notes }

- State:
  state = { bookings: [], selectedDate: today, search: '', statusFilter: 'all', sortKey: 'time', sortDir: 'asc' }

- Persistence:
  - loadState(): read JSON from localStorage; fallback to defaults.
  - saveState(): stringify and save after each mutation.

- Conflict Detection:
  - Same date; time windows overlap if startA < endB and startB < endA.
  - Ignore the booking itself when editing (by id).

- UI Components and Interactions:
  - Header: Today button sets selectedDate = today; New Booking opens form prefilled; Export downloads JSON; Import parses JSON, merges safely.
  - Search/filter: Instant re-render on input/change.
  - Day selector: date input controls selectedDate; list shows bookings for that date.
  - List: Shows title/client/time/status; edit/delete buttons; toggle status via select.
  - Modal form: Create and edit; validation and errors; cancel closes modal without changes.

- Validation & Errors:
  - Missing required fields: inline messages.
  - Invalid time order or conflicts: inline plus toast.

- Accessibility:
  - Labels, aria-* for modal/dialog and toasts, focus management on open/close.
  - Keyboard: ESC to close modal, Enter on form fields submits.

- Import/Export:
  - Export: Blob or data URL; file name includes date.
  - Import: JSON parse; validate records; skip invalid; show results.

## 6. Debugging & Traceability
- All mutations pass through helper functions that also call saveState().
- Console logs prefixed with [BlueBooking] where helpful in dev.
- This plan acts as the single source of truth for implementation steps.

## 7. Acceptance Criteria
- Can add/edit/delete bookings; persists after reload.
- Cannot create overlapping bookings on same date.
- Can view bookings for a selected date; sort by time.
- Can search and filter by status.
- Import/export JSON works; invalid records handled gracefully.
- Accessibility basics: labels, modal roles, keyboard navigation.


## 8. Actual Implementation Details

### 8.1 Files Modified

- ui/index.html: Replaced with accessible, single-page layout using a dialog for the booking form, search/filter controls, sort controls, and list rendering.

- ui/css/style.css: Replaced with responsive styles for header, controls, list items, modal dialog, form, and toast notifications.

- ui/js/main.js: Replaced with full application logic (state, persistence via localStorage, CRUD, validation, conflict detection, filtering, sorting, search, and import/export JSON).

### 8.2 Data Model

- Booking: { id, title, client, date (YYYY-MM-DD), start (HH:MM), end (HH:MM), status ('confirmed'|'tentative'|'cancelled'), notes }

- State key: bluebooking.state.v1 in localStorage with structure:

  { bookings: [], selectedDate, search, statusFilter, sortKey, sortDir }

### 8.3 Key Functions (main.js)

- loadState/saveState: Sync state with localStorage.

- filteredSortedDayBookings: Applies date scoping, search, status filter, and sorting (time/title/client/status) with asc/desc.

- validateBooking: Required fields, start<end, and same-date overlap detection using minute math and interval overlap check.

- addBooking/updateBooking/deleteBooking/getBooking: Core CRUD with render + saveState.

- openNew/openEdit: Prefill and open dialog for create or edit.

- importJsonFromFile/exportJson: Import with validation & deduplication, export with timestamped filename.

- renderControls/renderList/render: DOM updates for controls and booking list.

### 8.4 Validation Rules

- Required: title, date, start, end.

- Time order: end > start.

- No overlaps on the same date: aStart < bEnd and bStart < aEnd (self excluded when editing).

### 8.5 Accessibility

- Dialog used for the form; aria labels on toast and sections; keyboard ESC closes dialog; focus is placed on title on open.

- Labels associated with inputs; aria-live region for list updates.

### 8.6 Known Limitations & Future Enhancements

- Single-day list view (no month grid). Could add week/month calendar.

- No time zone normalization; relies on browser locale for date/time.

- Simple toast system; could add more granular error banners and focus management improvements on validation errors.

### 8.7 Testing Notes

- Manually tested: add/edit/delete; conflict prevention; search/filter/sort; import valid/invalid JSON; persistence across reload.

- If a validation tool is available, see validation section below for results.


## 9. File Modification History

- Replaced ui/index.html, ui/css/style.css, ui/js/main.js in this implementation.

- Created implementation_plan.md (this document).


## 10. Troubleshooting

- If dialog does not open, ensure the browser supports <dialog>; fallback sets the 'open' attribute.

- If import fails, verify the JSON file structure matches { state: { bookings: [...] } }.

- If data is not persisting, check localStorage availability and quotas.
