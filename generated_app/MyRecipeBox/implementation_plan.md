
# Implementation Plan: MyRecipeBox

This document outlines the comprehensive plan for implementing the MyRecipeBox application, a lightweight, offline-first recipe manager. It covers technical architecture, implementation phases, file structure, and detailed feature implementation based on the requirements from PRD.md, app_spec.json, and UI_STRUCTURE.json.

## 1. Technical Architecture

The application will follow a simple yet robust architecture using vanilla JavaScript, leveraging the browser's built-in capabilities for storage and rendering.

- **State Management:**
  - A single global `state` object will manage the application's data and UI state.
  - This object will include `recipes` (the core data), `currentView` (e.g., 'list', 'form', 'settings'), `filterCriteria`, `sortOrder`, and any other dynamic data.
  - All rendering functions will use this `state` object as the single source of truth.

- **Data Persistence:**
  - **`localStorage`** will be used for all data storage.
  - All recipes will be stored as a JSON string under a single key: `MyRecipeBox.recipes`.
  - Helper functions `storage.load()` and `storage.save()` will be created to abstract the serialization and deserialization of data.

- **HTML Structure & Rendering:**
  - The application will be a single-page application (SPA) contained within `index.html`.
  - Different "views" (List, Form, Settings) will be managed by toggling the `display` CSS property of their respective container elements.
  - The recipe list and form fields will be rendered dynamically using JavaScript DOM manipulation.

- **Error Handling & Validation:**
  - **Input Validation:** The recipe `title` will be a required field. Validation will be performed on form submission.
  - **User Feedback:** A dedicated status bar element will provide feedback on successful actions (e.g., "Recipe saved") or errors.
  - **Confirmation Modals:** A reusable modal will be implemented to confirm destructive actions like deleting a recipe or clearing all data.

## 2. Implementation Phases

The implementation will be broken down into logical phases to ensure a structured and testable development process.

**Phase 1: Core Infrastructure (Foundation)**
1.  **Data Persistence (`storage.js`):** Create `storage.load()` and `storage.save()` utilities to handle `localStorage` interactions.
2.  **State Management:** Initialize the global `state` object with default values.
3.  **Utilities (`utils.js`):** Implement a `uid()` function for generating unique recipe IDs.

**Phase 2: View Implementation (UI & Logic)**
1.  **List View:**
    - Render the list of recipes from the `state`.
    - Implement search functionality to filter recipes by title, ingredients, and instructions.
    - Implement sorting by creation date and title.
    - Implement filtering by tags.
2.  **Form View:**
    - Implement logic to create a new recipe or edit an existing one.
    - Dynamically add/remove ingredient and instruction fields.
    - Handle form submission, validation, and saving data.
3.  **Settings View:**
    - Implement the "Export Data" functionality to download all recipes as a JSON file.
    - Implement the "Import Data" functionality to load recipes from a JSON file.
    - Implement the "Clear All Data" functionality with a confirmation modal.

**Phase 3: Integration & Polish**
1.  **Navigation:** Connect all views so that the user can navigate seamlessly between them.
2.  **Modals:** Implement the confirmation modal and integrate it with all destructive actions.
3.  **Empty States:** Add user-friendly messages for empty states (e.g., "No recipes found").
4.  **Styling:** Apply the final CSS styles to ensure a clean and responsive user interface.

## 3. File Structure Plan

The project will use the existing files from the `bare-bones-vanilla-main` template. No new files will be created.

- **`ui/index.html`:**
  - Will be modified to include the HTML structure for all three views: List, Form, and Settings.
  - Will contain the necessary containers, forms, inputs, and buttons for all features.

- **`ui/js/main.js`:**
  - **This will be the primary file containing all application logic.**
  - The existing content will be completely replaced with the MyRecipeBox implementation.
  - It will include:
    - The global `state` object.
    - Data persistence functions.
    - View rendering and management functions.
    - All event handlers for user interactions.

- **`ui/css/style.css`:**
  - The existing content will be replaced with the custom styles for MyRecipeBox.
  - Will include styles for the overall layout, recipe list, forms, modals, and responsive design.

## 4. Implementation Details

### `js/main.js` - Key Functions & Logic

- **Initialization:**
  - `document.addEventListener('DOMContentLoaded', () => { ... });` will be the main entry point.
  - Inside, it will load recipes from `localStorage`, initialize the `state`, and render the initial view.

- **State Management:**
  - `const state = { recipes: [], currentView: 'list', ... };`
  - `function setState(newState) { ... }` to update the state and re-render the UI.

- **Routing / View Management:**
  - `function showView(viewId)`: Hides all main views and shows only the one with the specified ID.

- **List View Functions:**
  - `renderListView()`: Clears and re-renders the recipe list based on the current `state`.
  - `applyFiltersAndSort()`: Filters and sorts the `state.recipes` array before rendering.

- **Form View Functions:**
  - `openRecipe(recipeId)`: Populates the form with data from an existing recipe.
  - `startNewRecipe()`: Clears the form for a new entry.
  - `handleFormSubmit(event)`: Collects form data, validates it, and saves it.

- **Settings View Functions:**
  - `exportData()`: Creates and triggers a download of the `recipes.json` file.
  - `importData(event)`: Reads a JSON file and updates the `state.recipes`.

- **Event Handlers:**
  - All event listeners will be attached in the main `DOMContentLoaded` callback.
  - They will call the appropriate functions to update the state and UI.

## 5. Final Implementation Details & Changelog

This section documents the final implementation and the changes made to the project files.

- **`ui/index.html`:**
  - Replaced the placeholder content with the full HTML structure for the MyRecipeBox application.
  - Includes three main views: List, Form, and Settings.
  - All necessary forms, inputs, and buttons have been added to support the application's features.

- **`ui/js/main.js`:**
  - Replaced the template's JavaScript with the complete application logic for MyRecipeBox.
  - Implemented a global state management system.
  - Added data persistence using `localStorage`.
  - Implemented all view rendering, event handling, and business logic for managing recipes.

- **`ui/css/style.css`:**
  - Replaced the template's styles with custom CSS for the MyRecipeBox application.
  - Includes styles for all components, ensuring a clean and responsive user interface.

### Changelog

- **v1.0.0 (Initial Release):**
  - Implemented all core features of the MyRecipeBox application.
  - Replaced the `bare-bones-vanilla-main` template with the full application.
