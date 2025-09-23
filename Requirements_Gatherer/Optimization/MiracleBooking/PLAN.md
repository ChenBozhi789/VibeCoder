# PLAN: MiracleBooking

## Overview
MiracleBooking is a local-first single-page app (SPA) that lets customers book appointments with small businesses and lets business owners/staff view and manage appointments. Mobile-first, offline-capable, small footprint, accessible, and focused on a simple list-first UX.

> Important: MVP is local-only (no backend). Data persists locally (IndexedDB). Manual export (CSV/JSON) is included per PRD success criteria.


## Functional Requirements (User Stories)
Each story includes acceptance criteria. Items marked **MVP** are required for v1; others are optional.

1) Add / Book an appointment (MVP)
- As a customer, I want to create a new appointment so I can reserve a time slot.
- Acceptance criteria:
  - Form available from a prominent “Add appointment” button on the primary screen.
  - Required fields: customer_name, date_time. Optional: customer_contact, service, duration_minutes, notes.
  - On save, appointment is persisted locally and visible in the list immediately.
  - Validation: name required; date_time present and not clearly invalid; simple helper messages for contact format.

2) View appointments list (today/upcoming/past) (MVP)
- As a user, I want to see appointments grouped by timeframe so I can understand schedule at a glance.
- Acceptance criteria:
  - Primary screen is a list of appointments.
  - Default group/tabs: Today, Upcoming, Past.
  - Each item shows: customer_name, service (if present), date_time, duration (if present), status.
  - Empty state: friendly message + CTA to add appointment.

3) Edit an appointment (MVP)
- As a user, I want to edit an appointment to correct or change details.
- Acceptance criteria:
  - Tap an item to open details/edit view.
  - Edits persist locally; updated_at is set.
  - Validations applied same as on create.

4) Cancel / Delete appointment with undo (MVP)
- As a user, I want to cancel or delete an appointment and be able to undo accidental deletions.
- Acceptance criteria:
  - Delete action available via swipe (mobile) and explicit button in details.
  - Deletion shows short toast with Undo for 6–8 seconds.
  - If not undone, record is marked status=cancelled (soft-delete) or removed from list (implementation detail). Prefer soft-delete with status 'cancelled' to allow recovery.

5) Local offline persistence (IndexedDB) (MVP)
- As a user, I want the app to function fully offline so I can manage appointments without network.
- Acceptance criteria:
  - All CRUD operations persisted locally using IndexedDB.
  - App loads and shows appointments when offline; all actions work without network.

6) Basic validations & user-friendly feedback (MVP)
- As a user, I want clear validation messages and inline error hints.
- Acceptance criteria:
  - customer_name required error shown inline.
  - date_time required and result validated (warn for past, disallow invalid formats).
  - Contact helpers show non-blocking format suggestions.

7) Export appointments for backup (CSV/JSON) (MVP per PRD Success Criteria)
- As a user, I want to export my appointments to a local file so I can back them up.
- Acceptance criteria:
  - Manual export available from settings/menu.
  - Export formats: JSON (full data) and CSV (flat table).
  - Files are downloaded to device (no server involved).

Optional / Future (not required for MVP)
- PWA installability (install to home screen).
- Branding: app name, primary color, logo upload.
- Staff, payment, reminders, sync/multi-device.


## Traceability Table
Maps PRD items to PLAN sections.

| PRD Section | Requirement | Plan Section (in this doc) |
|---|---:|---|
| 1. Purpose & Users | App purpose & primary users | Overview; Functional Requirements intro |
| 2. Key Features | Create/view/edit/cancel; offline; validation | Functional Requirements 1–6; Storage & Persistence; Validation |
| 3. Look & Feel | List-first SPA, mobile-first, CTA, empty state, undo | UI/UX Design; Functional Requirements 1–4 |
| 4. Data Model | Appointment fields | Data Model section |
| 5. Rules & Validation | customer_name required; date_time checks; contact patterns | Validation & Edge Cases |
| 6. Non-functional | Offline-first, performance, small footprint, accessibility | Non-Functional Requirements; Implementation Plan |
| 7. Extras | Export/backup, PWA, branding | Functional Requirements export; Future Enhancements for PWA/branding |
| 8. Success Criteria | End-to-end booking flow, offline, quick load, validation, undo, export | Success Criteria section; QA Checklist |


## Non-Functional Requirements
- Offline-first: full CRUD works without network using IndexedDB.
- Performance:
  - First meaningful paint (list screen) <= 1s on typical mobile hardware.
  - App bundle minimized; lazy-load non-critical code (export, settings) if needed.
- Small footprint: avoid heavy frameworks; prefer lightweight stack and minimal dependencies.
- Accessibility:
  - Semantic HTML, ARIA labels for interactive elements.
  - High contrast colors, readable font sizes, adjustable font scaling.
  - Keyboard navigation for desktop.
- Security & privacy:
  - Data stored locally; no analytics or remote calls in MVP.


## UI / UX Design
Follow PRD strictly: simple list-first mobile-friendly SPA.

Screens & Flows:
1) Main List Screen (primary)
- Header: App name, overflow menu (Export, Settings, About).
- Prominent floating action button (FAB) or top button: “Add appointment”.
- Tabs or segmented control: Today | Upcoming | Past.
- List items:
  - Row shows customer_name (bold), service (small), date_time (human-friendly), duration, status pill.
  - Tap row -> opens detail/edit sheet.
  - Swipe left/right -> reveal Delete/Cancel quick action (mobile).
- Empty state:
  - Friendly illustration/text: “No appointments yet”, short CTA button “Add appointment”.

2) Add / Edit Appointment (modal or full-screen sheet)
- Fields (order): customer_name* (text), customer_contact (text), service (text), date_time* (datetime picker), duration_minutes (number), notes (textarea).
- Primary action: Save; Secondary: Cancel.
- Inline validation messages under fields.
- Save shows success toast.

3) Appointment Detail (sheet or page)
- Show full data + Edit and Delete buttons.
- Delete triggers toast undo.

4) Toast system
- Short messages for success, error, and undo with action.
- Undo for deletes lasts 6–8s.

Accessibility & Interaction
- Use large tappable areas, high-contrast buttons.
- Keyboard-accessible focus order for desktop.
- Screen-reader labels for list items (announce name, time, status).


## Data Model (IndexedDB primary; localStorage for tiny flags)
Store in an IndexedDB database named `miraclebooking-db`, object store `appointments`.

Appointments table (object store):

| Field | Type | Notes |
|---|---|---|
| id | string (UUID) | Primary key
| customer_name | string | required
| customer_contact | string | optional; phone or email
| service | string | optional
| date_time | string (ISO 8601) | required
| duration_minutes | integer | optional
| status | string (enum: 'booked'|'confirmed'|'cancelled') | default 'booked'
| notes | string | optional
| created_at | string (ISO) | auto-set
| updated_at | string (ISO) | auto-set
| deleted_at | string (ISO) nullable | optional; used for soft-delete

Indexes:
- date_time index (for queries by time range)
- status index (for filtering by status)

Local flags (localStorage or small store)
- ui: { last_active_tab }
- settings: { export_preference }

Storage size: Small; include basic migration strategy (versioned DB schema with upgrade handlers).


## Validation & Edge Cases
Rules:
- customer_name: required, non-empty, trim whitespace.
- date_time: required, must parse as ISO datetime. If date_time < now, show warning ("You're choosing a past date"). Allow saving but require explicit confirmation if truly in past? PRD says warn if past, disallow if clearly invalid — implement: disallow invalid formats; allow past dates with explicit confirm toggle.
- customer_contact: non-blocking validation for simple email regex and phone pattern; show helper text.
- duration_minutes: positive integer; default empty/null.

Edge Cases & Handling:
- Duplicate entries: allow same name but warn user if identical date_time and customer_name (soft warning). Prevent strict deduping.
- Clock changes / timezone: store date_time as ISO with timezone offset. Display relative to device local timezone.
- DB corruption/unavailable: fallback to in-memory session with error message; ask user to export (if possible) and restart.
- Undo: deletion sets status='cancelled' and deleted_at timestamp; Undo clears cancelled status if within window.
- Concurrency: single-device local app. If future sync added, handle conflict resolution later.

UI Empty states:
- No appointments -> show friendly CTA to add.
- No network -> show "Offline" indicator but allow full functionality.

Error messages:
- Show inline field errors; toast for operation-level errors (save failed, DB error).


## Storage & Persistence
Local-first strategy:
- Primary persistence: IndexedDB (`miraclebooking-db`, store `appointments`).
- Small UI flags/settings: localStorage.
- Export: manual export to JSON/CSV to device file per user action.

Offline behavior:
- App shell and assets cached (service worker optional for PWA later). For MVP, ensure app loads as static files from disk without network; include fallback offline banner.
- All CRUD operations recorded to IndexedDB synchronously; UI updates immediately.

Backup & Export (per PRD):
- Export button in menu -> offers JSON (complete export) and CSV (flat table) downloads.
- Import is NOT in MVP unless explicitly requested. (PRD only requested export.)


## Implementation Plan
Tech choices (recommended for small footprint):
- Framework: Preact with Vite (small bundle), or Svelte if team prefers. Use vanilla JS only if team wants zero-framework.
- Build tool: Vite.
- State management: local reactive stores (minimal) or context; keep simple.
- IndexedDB wrapper: use `idb` (tiny, well-tested) or implement a minimal thin wrapper around IndexedDB.
- UI: lightweight CSS framework or custom CSS. Avoid heavy UI libraries.

Suggested folder structure:

src/
- main.tsx (app entry)
- App.tsx
- routes/
  - ListView.tsx
  - AppointmentDetail.tsx
  - AppointmentForm.tsx
  - Settings.tsx
- components/
  - AppointmentRow.tsx
  - Tabs.tsx
  - Toast.tsx
  - Modal.tsx
- stores/
  - appointmentsStore.ts (CRUD + sync with IndexedDB)
  - uiStore.ts
- db/
  - indexeddb.ts (DB open, migrations, object-store helpers)
- utils/
  - datetime.ts
  - export.ts (CSV/JSON builders)
  - validators.ts
- styles/
  - variables.css
  - layout.css
- assets/
- tests/
  - unit/ (validators, utils)

Key implementation notes:
- App initializes by opening DB and loading recent items for the default tab.
- appointmentsStore exposes: list(filter), get(id), create(obj), update(id, delta), softDelete(id), undoDelete(id).
- All methods return Promise and update reactive store for UI updates.
- DB upgrades handled by versioned migration scripts.

Estimated implementation effort (rough):
- 1 week: scaffolding, basic list UI, add/edit form, DB layer.
- 1 week: validations, delete/undo, toasts, tabs, empty states.
- 1 week: export CSV/JSON, accessibility adjustments, performance tuning.
- 3–5 days: QA and bug fixes, final polish.


## QA Checklist
- [ ] Add appointment: form validates and saves locally (customer_name, date_time required).
- [ ] View appointments: Today/Upcoming/Past tabs show correct items.
- [ ] Edit appointment: changes persist and updated_at changes.
- [ ] Delete/Cancel: delete shows toast with Undo; undo restores appointment.
- [ ] Offline: app loads and all CRUD operations work offline.
- [ ] Export: JSON and CSV export files download and contain expected data.
- [ ] Empty state: clear CTA visible when no appointments.
- [ ] Validation messages: inline helpful messages for invalid inputs.
- [ ] Accessibility: screen reader labels, keyboard nav, focus states.
- [ ] Performance: main screen renders within target (~1s on typical mobile device emulation).
- [ ] Data integrity: date_time stored as ISO and sorted correctly.
- [ ] Error handling: DB errors present helpful message and fallback.


## Success Criteria (MVP Done)
- User can add, view (list), edit, and cancel an appointment locally.
- App works fully offline with data persisted in IndexedDB and visible while offline.
- Main list screen loads quickly and shows list or a friendly empty state.
- Validations enforced: customer_name required; date_time validated with user-friendly messages.
- Deletion has undo window (6–8s) and functions correctly.
- Basic export (CSV & JSON) available and produces valid files.


## Future Enhancements
(Do not implement in MVP; for roadmap)
- Optional: import feature to restore backups.
- PWA service worker + installable app.
- Optional server sync for multi-device backups and conflict-resolution.
- Staff and resource availability model to prevent double-booking.
- Reminders/notifications (local notifications for installed PWA).
- Payments and price fields.
- Branding options: color and logo upload for business owners.


---

If you want, I can also produce minimal UI mock screenshots or a component-level task breakdown (tickets) from this plan. ✅
