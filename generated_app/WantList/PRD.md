# Product Requirement Document

**App Name:** WantList  
**Goal/Purpose:** Help individuals quickly capture and manage a personal list of things they want to buy, optionally track prices, and see a running total to support budgeting and purchasing decisions.  
**Target Users:** Shoppers and budget-conscious individuals who keep a wishlist of items to purchase and want a simple way to total estimated costs.

## Core Features
- Item management: Quickly add items with a required name and an optional price; view, edit, and delete items easily.
- Total price summary: Display the sum of all item prices (items without a price are ignored in the total). Show item count alongside the total.
- Create/Edit/Delete: Users can create, view, update, and delete items.
- List & Preview: A central list shows each item’s name, optional price, and creation date.
- Search & Filter: Instant search by item name. Simple filters (e.g., items with price vs. without price).
- Data Portability: Export all data to a JSON file and import it back to restore or merge data.

## Data Model
- **Main Entity:** Item
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, the item name)
  - `description`: string (optional, notes such as store, link, or details)
  - `price`: number (optional, currency amount; store as a number and display formatted to two decimals)
  - `createdAt`: ISO8601 timestamp (when the item was created)
  - `updatedAt`: ISO8601 timestamp (when the item was last modified)
  - `tags` (optional): array of strings (e.g., category like “electronics”, “books”)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all items.
  - Key elements: Prominent "New Item" button, search bar, and filter/sort controls.
  - Each list row shows: item name (title), optional price (formatted), creation date snippet, and a quick delete action with confirmation.
  - A summary section (top or bottom) shows: total number of items and the total price (sum of items that have a numeric price).

- **Detail / Form View:**
  - A clean form for creating or editing an item.
  - Fields: Title (required), Price (number input, optional), Description (multiline), Tags (tokenized input).
  - Actions: Primary "Save" button, "Cancel"/back navigation, and "Delete" (with confirmation) for existing items.
  - Validation: Title required and trimmed; Price must be a valid non-negative number if provided.

- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - Import Data: From a JSON file. Clearly indicate if import will merge with or replace existing data (offer both options).
  - Export Data: To a JSON file.
  - Clear All Data: A button to wipe all local data, protected by a confirmation dialog.

## Assumptions
- Platform: Single-page web application running entirely in the browser.
- Persistence: Uses browser `localStorage` for data storage (key: `WantList.items`). No backend or cloud sync required.
- Offline First: Fully functional without internet connectivity.
- Single-User: No authentication, user accounts, or collaboration features.
- UI/UX: Clean, minimal, and responsive design with basic accessibility (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- Performance: UI remains responsive with 1,000+ items; initial load under 1 second on modern browsers.
- Reliability: Destructive actions (e.g., deletion, clear all) require explicit confirmation. Handle storage quota limits gracefully with user notifications.
- Data Safety: Import/export is the primary backup mechanism. Use a simple, well-documented JSON format.
- Formatting: Prices display with two decimal places; items without a price display a placeholder (e.g., “—”).

## Implementation Notes / Developer Hints
- Data Storage: Store all items as a single array in one `localStorage` key (e.g., `WantList.items`).
- State Management: Prefer vanilla JS or a lightweight library (Preact, Vue, or Svelte) for simplicity and speed.
- Search/Filter Logic: Implement client-side search (case-insensitive substring match on `title`) and simple filters (has price / no price).
- Total Computation: Compute total via client-side `reduce` over items with a numeric `price`. Recompute on data changes. Display to two decimals.
- Validation & Parsing: Parse price input to a number; reject invalid input; store as a number. Avoid floating-point surprises by formatting on display (toFixed(2)).
- Dependencies: Minimize external libraries to ensure fast load and maintainability.
