# Product Requirement Document

**App Name:** MyRecipeBox  
**Goal/Purpose:** Help home cooks easily capture, organize, and retrieve their personal recipes offline. The app focuses on quick entry of ingredients and instructions, simple browsing, and reliable local storage with backup via JSON export/import.

**Target Users:** Home cooks, food enthusiasts, and hobby chefs who want a lightweight, private recipe manager to store their personal collection without accounts or cloud sync.

## Core Features
- Recipe Management: Users can add recipes with a title, structured ingredients list, and step-by-step instructions.
- **Create/Edit/Delete:** Users can create, view, update, and delete recipes.
- **List & Preview:** A central list shows all recipes with title, creation date, and a short preview (first line of instructions or notes). Quick delete action available.
- **Search & Filter:** Instant search over titles, ingredients, and instructions. Simple filters (e.g., by tag when tags are used) and sort by newest/oldest/title.
- **Data Portability:** Export all recipes to a JSON file for backup and import them back (merge or replace).
- Optional Tags for Organization: Users can add simple tags to group recipes (e.g., "dessert", "vegetarian").

## Data Model
- **Main Entity:** Recipe
  - `id`: string (UUID, unique identifier)
  - `title`: string (required)
  - `description`: string (optional notes)
  - `ingredients`: array of Ingredient objects
    - `name`: string (required)
    - `quantity`: string (optional; allows fractions like "1/2")
    - `unit`: string (optional; e.g., "cup", "tsp")
  - `instructions`: array of strings (each entry is a step)
  - `tags` (optional): array of strings
  - `createdAt`: ISO8601 timestamp
  - `updatedAt`: ISO8601 timestamp

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of all recipes.
  - Key elements: Prominent "New Recipe" button, a search bar, and filter/sort controls.
  - Each list item shows the title, creation date, and a snippet (first instruction or note) plus a quick delete icon with confirmation.
- **Detail / Form View:**
  - A clean form for creating or editing a recipe.
  - Fields: Title (required), Description/Notes (optional), Ingredients (dynamic list with name, quantity, unit), Instructions (editable list of steps).
  - Actions: Primary "Save" button, "Cancel"/back navigation, and "Delete" (with confirmation) for existing recipes.
- **Settings View:**
  - **Import Data:** From a JSON file; user chooses merge or replace.
  - **Export Data:** Download all recipes as JSON.
  - **Clear All Data:** Wipes all local data, protected by a confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, user accounts, or collaboration features.
- **UI/UX:** Clean, minimal, and responsive design with basic accessibility (keyboard navigation, proper labels, sufficient contrast).

## Non-Functional Requirements
- **Performance:** UI remains fast with 1,000+ recipes. Initial load under 1 second on modern browsers.
- **Reliability:** Destructive actions (e.g., delete, clear all) require confirmation. Handle storage quota limits by notifying the user.
- **Data Safety:** Import/export is the primary backup mechanism. Data format is simple and well-documented (JSON).

## Implementation Notes / Developer Hints
- **Data Storage:** Store all recipes as a single array of objects in one `localStorage` key, e.g., `MyRecipeBox.recipes`.
- **State Management:** Prefer vanilla JS or a lightweight library (Preact, Vue, or Svelte) over heavy frameworks.
- **Search/Filter Logic:** Client-side search over `title`, `ingredients.name`, and `instructions` strings. Provide sort by `createdAt` and `title`.
- **Dependencies:** Minimize external dependencies for fast loads and maintainability.
