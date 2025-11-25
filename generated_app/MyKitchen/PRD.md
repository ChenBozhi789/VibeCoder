# Product Requirement Document

**App Name:** MyKitchen  
**Goal/Purpose:** Help home cooks save, organize, and quickly retrieve their personal recipes. The app provides a fast, offline-friendly place to capture ingredients and instructions, browse saved recipes, and prepare meals without distraction.

**Target Users:** Home cooks, food enthusiasts, and anyone who wants a simple, private, and reliable way to store personal recipes and access them later while cooking.

## Core Features
- Recipe Management: Create, view, edit, and delete recipes with a clean, distraction-free interface.
- List & Preview: The home screen lists all recipe titles. Optionally, a short preview (first line of instructions) can be toggled in Settings.
- Search & Filter: Instant search across recipe titles and ingredients; filter by tags to narrow down results.
- Data Portability: Export all recipes to a JSON file for backup and import them back later. Import can merge or replace data.
- Quick Actions: From the list or detail view, copy the ingredients list to the clipboard to streamline shopping or prep.

## Data Model
- **Main Entity:** Recipe
  - `id`: string (UUID, unique identifier)
  - `title`: string (required, short text)
  - `ingredients`: array of strings (required; each entry is a single ingredient such as "2 cups flour")
  - `instructions`: string (longer text content with step-by-step directions)
  - `tags` (optional): array of strings (e.g., ["vegan", "dessert"]) for filtering and organization
  - `createdAt`: ISO8601 timestamp (when the recipe was created)
  - `updatedAt`: ISO8601 timestamp (when the recipe was last modified)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all recipes by title (default shows titles only, per user request).
  - Key elements: Prominent "New Recipe" button, a search bar (searches titles and ingredients), and simple filter/sort controls (e.g., by tag or date).
  - Each list item shows the recipe title and a quick delete action (with confirmation). Optionally, a preview snippet can be enabled in Settings.

- **Detail / Form View:**
  - A clean form for creating or editing a recipe.
  - Fields: Title (text), Ingredients (dynamic list where users can add/remove lines; support pasting multiline text to split into items), Instructions (multiline text area), Tags (optional, comma-separated or chips).
  - Actions: Primary "Save" button, "Cancel"/back navigation, and a "Delete" button (with confirmation) for existing recipes.

- **Settings View:**
  - A dedicated page or modal for app-level actions.
  - **Import Data:** From a JSON file. User chooses whether to merge with or replace existing data.
  - **Export Data:** To a JSON file containing all recipes.
  - **Clear All Data:** A button to wipe all local data, protected by a confirmation dialog.
  - **Display Options:** Toggle to show/hide instruction preview in the list view.

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
- **Data Storage:** Store all recipes as a single array of objects in one `localStorage` key (e.g., `MyKitchen.recipes`). Also store minimal app settings in a separate key (e.g., `MyKitchen.settings`).
- **Example Schema:**
  ```json
  {
    "recipes": [
      {
        "id": "uuid-123",
        "title": "Chocolate Chip Cookies",
        "ingredients": ["2 cups flour", "1 cup sugar", "1 cup chocolate chips"],
        "instructions": "Preheat oven to 350°F...",
        "tags": ["dessert"],
        "createdAt": "2025-01-01T12:00:00.000Z",
        "updatedAt": "2025-01-01T12:00:00.000Z"
      }
    ],
    "settings": {"showPreview": false}
  }
  ```
- **State Management:** Use vanilla JS or a lightweight library (Preact, Vue, or Svelte). Keep logic simple and local to components.
- **Search/Filter Logic:** Normalize strings to lowercase; search title and ingredients fields. Implement client-side filtering by tags and simple sorts (date/title).
- **Dependencies:** Minimize external dependencies to ensure fast load times and long-term maintainability.
