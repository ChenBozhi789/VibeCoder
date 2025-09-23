# PRD: MiracleBooking

## 1. Purpose & Users
- Purpose: Let customers book appointments with small businesses.
- Primary users:
  - Customers who want to find and book appointment slots.
  - Small business owners/staff who view and manage their appointments (basic dashboard).

## 2. Key Features (minimum viable)
- Book an appointment (create a new booking).
- View a simple list of appointments (today/upcoming/past).
- Edit or cancel an existing appointment.
- Local offline storage so the app works without network connectivity.
- Basic validations and feedback (required fields, sensible error messages).

Notes: Additional features to consider later: reminders, payments, staff availability, and reviews.

## 3. Look & Feel (UI/UX)
- Layout: Simple list view of appointments as the primary interface.
- Platform: Single-page app (SPA) optimized for local/offline use; mobile-first but usable on desktop.
- Interaction:
  - Clear “Add appointment” button.
  - Tap an item to view/edit details or swipe/delete (mobile friendly).
  - Empty state: a friendly “No appointments yet” screen with a clear call-to-action to add one.
  - Confirmations and an undo option for deletes (short toast with Undo).
- Accessibility: Use readable font sizes, high-contrast colors, and basic keyboard navigation.

## 4. Information to Save (data model)
- Appointment (primary record):
  - id (string/UUID)
  - customer_name (string) — required
  - customer_contact (string) — optional; phone or email
  - service (string) — optional (e.g., haircut, consultation)
  - date_time (ISO datetime) — required
  - duration_minutes (integer) — optional
  - status (enum) — e.g., booked, confirmed, cancelled
  - notes (string) — optional
  - created_at, updated_at (timestamps)

Notes: Keep the model small and flexible. Fields like staff, price, and payment_status can be added later as optional fields.

## 5. Rules & Validation
- customer_name is required.
- date_time must be provided and (by default) should be in the present or future. Warn if a past date is entered; disallow if clearly invalid.
- Basic format checks for contact info (simple email/phone patterns) — non-blocking but helpful.
- Prevent obvious double-booking in the same slot if a business/staff model is later introduced (recommended enhancement).
- Provide clear, user-friendly error messages next to fields.

## 6. Non-functional Requirements
- Offline-first: works fully offline using local storage (IndexedDB or similar). User can create/edit/cancel while offline and changes persist locally.
- Performance: load quickly on mobile devices; primary screen should appear within 1s on typical mobile hardware.
- Small footprint: minimal external dependencies.
- Accessibility: support screen readers and adjustable font sizes.

## 7. Extras / Nice-to-haves
- Single local offline SPA (as requested) — no backend required for MVP.
- Export/backup: allow manual export of appointments as CSV or JSON (local file download) for backups.
- Installable PWA (optional later) so users can install the app to their device/home screen.
- Simple branding options: app name, primary color, and logo upload (for small-business owners).

## 8. Success Criteria (what “done” looks like)
- End-to-end booking flow works: add, view (list), edit, and cancel an appointment.
- App functions fully offline: data created/edited while offline is persisted locally and visible when offline.
- The main screen loads quickly and shows a clear list or a friendly empty state.
- Validations in place: required name, valid date/time, and helpful error messages.
- Deletion has a short undo window (toast) to correct mistakes.
- Basic export (CSV/JSON) available for backups.

## 9. Implementation Notes / Next Steps
- MVP scope: local-only SPA with local persistence and the features above.
- Consider a future sync feature (optional) to add server-based backups or multi-device sync.
- Design simple UI mocks for the list, add/edit form, empty state, and delete confirmation/undo.

---
Generated from interview responses collected:
- App name: MiracleBooking
- Purpose: Let customers book appointments with small businesses
- Core feature chosen by user: Book appointments
- UI preference: Simple list of appointments
- Data: customer basic info
- Rule specified by user: customer name required
- Non-functional: work offline
- Extras specified by user: single local offline SPA

If you'd like any item expanded, changed, or have additional requirements (payments, staff scheduling, reminders), tell me and I will update this PRD.md accordingly.
