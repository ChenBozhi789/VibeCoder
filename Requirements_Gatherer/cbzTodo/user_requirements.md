# cbzTodo — User Requirements

## App name
cbzTodo

## One-line description
Shopping list app for families.

## Purpose and target users
- Purpose: Help family members create and manage shopping lists locally on a shared device (no cloud sync).
- Target users: Families or household members who share a single device (phone/tablet) to coordinate shopping.

## Core features (explicitly requested)
- Create, edit, and delete shopping lists.

## Features not confirmed (assumptions & suggestions)
> The user ended the session early. The items below were not explicitly confirmed and require clarification. The development plan will assume reasonable defaults where noted, but these should be reviewed with the user.

- Item fields: Not specified. Suggested default fields to support common needs:
  - Item name (required)
  - Quantity (optional)
  - Unit (optional, e.g., kg, pack)
  - Bought flag / checked state (optional)
  - Notes (optional)
  - Category (optional)

- Multiple lists: Not confirmed. Suggested default: support multiple separate lists (e.g., weekly, pantry, event) because that matches common family workflows.

- Export/import / backup: Not confirmed. Suggested default: provide an export/import JSON feature so families can back up or share lists via file transfer.

- UI preferences: Not provided. Suggested default: simple, accessible list-focused UI with clear Add/Edit controls and checkboxes for bought items.

- Reminders/notifications, barcode scanning, cloud sync, and multi-device sync were NOT requested and will NOT be included in the MVP.

## Data to be stored (high level)
- Lists: name, optional description, created/updated timestamps, and collection of items.
- Items: name, quantity, unit, category, notes, bought flag, created/updated timestamps.

## Validation rules (suggested / to confirm)
- Item name: required, non-empty, max length 200 characters.
- Quantity: optional, if provided must be a positive number (or a short free-text field if units are complex).
- List name: required, non-empty, max length 100 characters.

## Non-functional needs (stated or inferred)
- Local-first: app must run entirely in the browser with no server; data stays on the device.
- Offline-capable: app should work without network connectivity.
- Small and fast: quick load and responsive interactions on mobile devices.

## Security & Privacy
- All data remains on the user's device. No data leaves the browser unless the user explicitly exports it.

## Open questions / items needing user confirmation
1. Do you want support for multiple lists (weekly, pantry, event) or a single list? (We suggest multiple.)
2. Which item fields do you want exactly? (We suggest: name, quantity, unit, bought flag, notes, category.)
3. Do you want an export/import backup feature? (Recommended: yes, JSON file.)
4. Any UI style or color/branding preferences?
5. Should the app be installable as a PWA (add to home screen)?

---

> Notes from QA: The user provided only the app name and a one-line description and explicitly ended the session. Several important choices were not specified. The plan will use sensible defaults but these Open Questions should be answered to finalize the specification.
