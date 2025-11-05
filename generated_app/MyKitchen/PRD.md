# Product Requirement Document

**App Name:** MyKitchen  
**Goal/Purpose:** Help home cooks quickly save, organize, and retrieve their personal recipes offline. The app makes it easy to capture a recipe with structured ingredients and clear instructions, browse all saved recipes by title, and view full details on demand.

**Target Users:** Home cooks, meal preppers, and food enthusiasts who want a simple, private, offline-friendly place to store personal recipes without the complexity of accounts or cloud sync.

## Core Features
- Recipe detail and editing with structured fields for Title, Ingredients, and Instructions. Optionally support tags and a favorite flag for lightweight organization.
- A simple, clutter-free experience focused on speed, reliability, and offline access.
- **Create/Edit/Delete:** Users can create, view, update, and delete recipes.
- **List & Preview:** A central view lists all recipes. Per the requirement, the list displays recipe titles primarily; a minimal subtitle (e.g., tag or date) is optional.
- **Search & Filter:** Users can instantly search titles and optionally filter by tags or ingredient text matches.
- **Data Portability:** Users can export their entire recipe collection to a JSON file for backup and import it back.
- Structured Ingredients: Add multiple ingredients with name, quantity, unit, and optional notes; reorder ingredients via drag-and-drop or simple up/down controls.
- Print-friendly view (optional): Generate a clean, print-ready layout from a recipe’s detail page.

## Data Model
- **Main Entity:** Recipe
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `description`: string (optional notes about the recipe)
  - `ingredients`: array of objects
    - `name`: string (required)
    - `quantity`: string (optional, e.g., "2", "1/2")
    - `unit`: string (optional, e.g., "cups", "tsp")
    - `note`: string (optional, e.g., "chopped", "room temp")
  - `instructions`: string (long-form text, required)
  - `tags` (optional): array of strings (for filtering and organization)
  - `favorite` (optional): boolean (defaults to false)
  - `createdAt`: ISO8601 timestamp (when the recipe was created)
  - `updatedAt`: ISO8601 timestamp (when the recipe was last modified)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all recipes.
  - Key elements: Prominent "New Recipe" button, a search bar, and optional filter controls (e.g., tags).
  - Per user requirement, each list item shows the recipe title. A small subtitle (like tag or date) is optional; no content preview is required.
  - Quick actions: select to view, and a discreet delete icon with confirmation.

- **Detail / Form View:**
  - A clean form for creating or editing a recipe.
  - Fields: Title (text), Ingredients (dynamic list: name, quantity, unit, note; add/remove/reorder), Instructions (multiline text), Tags (chips input, optional), Favorite (toggle, optional).
  - Actions: Primary "Save" button, "Cancel"/back navigation, and "Delete" (with confirmation) for existing recipes.
  - Read mode vs. Edit mode: Open in read mode by default with a clear "Edit" button; editing reveals the form controls.

- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file. The UI clarifies whether import will merge with or replace existing data; provide both options.
  - **Export Data:** To a JSON file.
  - **Clear All Data:** A button to wipe all local data, protected by a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** The application must be fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with a focus on usability and basic accessibility standards (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** The UI must remain responsive and fast, even with 1,000+ recipes. Initial load time should be under 1 second on a modern browser.
- **Reliability:** Destructive actions (e.g., deletion) must require user confirmation. The app should handle storage quota limits gracefully by notifying the user.
- **Data Safety:** The import/export functionality serves as the primary backup mechanism. The data format should be simple and well-documented (JSON).

## Implementation Notes / Developer Hints
- **Data Storage:** Store all recipes as a single array of objects in one `localStorage` key (e.g., `MyKitchen.recipes`). Consider a separate key for app settings (e.g., `MyKitchen.settings`).
- **State Management:** For a simple app, vanilla JS or a lightweight library (like Preact, Vue, or Svelte) is preferred over a heavy framework.
- **Search/Filter Logic:** Implement search and filtering on the client-side by iterating through the main data array. For ingredient search, match against ingredient `name` and `note` fields; for tags, match exact strings.
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability.
- **Validation:** Require `title` and `instructions`; allow empty `ingredients` for quick draft saves but encourage structured input.
