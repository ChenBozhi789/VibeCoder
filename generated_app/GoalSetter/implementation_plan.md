
# GoalSetter: Implementation Plan

This document outlines the technical plan for implementing the GoalSetter application based on the PRD, app_spec.json, and UI_STRUCTURE.json.

## 1. Technical Architecture

### A. State Management
- **Strategy:** A single global `state` object will be managed within `js/main.js`. This is a simple and effective approach for a vanilla JavaScript application of this scale.
- **State Object Structure:**
  ```javascript
  let state = {
    goals: [], // Array of goal objects from localStorage
    editingGoalId: null, // The ID of the goal being edited, or null for new goals
    filterBy: {
      status: 'all', // 'all', 'active', 'achieved'
      dueState: 'all' // 'all', 'overdue', 'due-soon'
    },
    sortBy: 'updatedAt-desc' // e.g., 'updatedAt-desc', 'progress-asc'
  };
  ```

### B. Data Persistence
- **Strategy:** Browser `localStorage` will be used for all data persistence.
- **Key:** All goals will be stored under a single key: `GoalSetter.goals`.
- **Functions:**
  - `loadState()`: Reads the goals array from `localStorage` into `state.goals` on app start.
  - `saveState()`: Writes the current `state.goals` array to `localStorage` after any modification (create, update, delete).

### C. Application Flow & UI
- **Structure:** The application will be a Single Page Application (SPA) contained within `index.html`.
- **Views:** Different sections of the HTML (`<main id="list-view">`, `<main id="form-view">`) will act as "views." Their visibility will be controlled by adding/removing a `.hidden` CSS class.
- **Modals:** Settings and confirmation dialogs will also be implemented as modals hidden by default.

### D. Error Handling & Validation
- **Validation:** Basic client-side validation will be implemented for the goal form. The `title` field will be required.
- **Confirmation:** Destructive actions (delete goal, clear all data) will require user confirmation using a dedicated modal dialog.

## 2. Implementation Phases

### Phase 1: Core Infrastructure (in `js/main.js`)
1.  **DOMContentLoaded Listener:** Set up the main entry point to initialize the app.
2.  **DOM Element References:** Get and store references to all necessary DOM elements (views, forms, buttons, inputs, etc.).
3.  **State Management:** Implement the global `state` object.
4.  **Persistence Functions:** Create `saveState()` and `loadState()` to interact with `localStorage`.
5.  **Utility Functions:** Create a `generateUUID()` function for new goal IDs.
6.  **Initial Render:** Call `loadState()` and `render()` to display the initial UI.

### Phase 2: CRUD Functionality
1.  **Render Function:** Create a master `render()` function that calls sub-renderers. Its primary job is to render the goal list based on the current state (filters and sorting).
2.  **Goal List Rendering:** Implement `renderGoalList()` to generate the HTML for each goal item and display it. This function will handle overdue and due-soon highlighting.
3.  **View Switching:** Implement `showListView()` and `showFormView(goalId)` to manage which view is visible.
4.  **Form Handling:**
    - Wire up the "New Goal" button to call `showFormView(null)`.
    - Wire up "Edit" actions on list items to call `showFormView(goalId)`.
    - Implement `handleFormSubmit()` to either create a new goal or update an existing one based on `state.editingGoalId`.
5.  **Delete Logic:** Implement `handleDeleteGoal(goalId)` which shows a confirmation modal before deleting the goal and re-rendering.

### Phase 3: Features (Search, Filter, Sort)
1.  **Event Listeners:** Add `input` and `change` event listeners to the search bar, filter dropdowns, and sort controls.
2.  **Filtering Logic:** In the `renderGoalList()` function, apply filters from `state.filterBy` to the `state.goals` array *before* rendering.
3.  **Search Logic:** Apply the search term to filter goals by title and description.
4.  **Sorting Logic:** Apply the sorting rule from `state.sortBy` to the `state.goals` array *before* rendering.
5.  **State Updates:** The event listeners will update the corresponding properties in the `state` object and then call `render()` to reflect the changes.

### Phase 4: Settings & Data Portability
1.  **Settings Modal:** Implement logic to show/hide the settings modal.
2.  **Export Data:** Implement `exportData()` to stringify `state.goals` and trigger a file download.
3.  **Import Data:** Implement `importData()` using a file input. Parse the JSON file, validate its structure, and replace `state.goals` with the imported data (after confirmation).
4.  **Clear All Data:** Implement `clearAllData()` which, after confirmation, clears `state.goals` and `localStorage`, then re-renders the empty state.

## 3. File Modification Plan

- **`ui/js/main.js`**: **Complete Overwrite.** The existing template file will be replaced with the full application logic, including all phases described above. It will be a single, non-modular script.
- **`ui/css/style.css`**: **Complete Overwrite.** The template styles will be replaced with custom styles for GoalSetter, including the `.hidden` class for view management, and styles for goal items, forms, modals, and responsive design.
- **`ui/index.html`**: **Minor Modifications.** The HTML structure is largely in place. I will ensure all elements have the correct IDs and `data-*` attributes required by `js/main.js`. I will also connect all event-handling attributes if necessary.

