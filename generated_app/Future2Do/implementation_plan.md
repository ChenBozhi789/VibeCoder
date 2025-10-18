
# Implementation Plan for FutureToDo

This document outlines the implementation plan for the FutureToDo application, based on the PRD, app_spec.json, and UI_STRUCTURE.json.

## A. Technical Architecture

- **State Management:** A global `tasks` array will be used to manage the state of the to-do items. A `filters` object will store the current state of the search, filter, and sort controls. All state will be managed within the `js/main.js` file using vanilla JavaScript.
- **Data Persistence:** `localStorage` will be used for data persistence. The `tasks` array will be serialized to JSON and stored under the key `'tasks'`. This ensures that the user's to-do list is saved between sessions.
- **HTML Structure:** The application will use a single `index.html` file. The task list will be dynamically rendered into the `<ul id="task-list">` element using JavaScript.
- **Error Handling & Validation:** Basic validation will be implemented for the task title to ensure it's not empty. User feedback for errors will be provided using the browser's `alert()` function.

## B. Implementation Phases

1.  **Core Infrastructure (js/main.js):**
    -   Define global state variables: `tasks` and `filters`.
    -   Implement `saveTasks()` to write the `tasks` array to `localStorage`.
    -   Implement `loadTasks()` to read tasks from `localStorage`.

2.  **HTML Logic & DOM Manipulation (js/main.js):**
    -   Implement `renderTasks()` to clear and re-populate the task list in the DOM based on the current `tasks` array, applying any active filters and sorting.
    -   Implement `addTask(event)` to handle the add-task form submission. This function will create a new task object, add it to the `tasks` array, save the updated array, and trigger a re-render.
    -   Implement `deleteTask(id)` to remove a task from the `tasks` array by its ID, save, and re-render.
    -   Implement `toggleTaskStatus(id)` to toggle the `completed` property of a task, save, and re-render.

3.  **Filtering, Sorting, and Search (js/main.js):**
    -   Implement a single handler function that updates the `filters` state object based on user input from the search field, status dropdown, and sort dropdown.
    -   This handler will then call `renderTasks()` to reflect the changes.

4.  **Integration (js/main.js):**
    -   Create an `init()` function or use a `DOMContentLoaded` event listener.
    -   This entry point will:
        -   Get references to all necessary DOM elements.
        -   Load tasks from `localStorage`.
        -   Set up event listeners for the form, search input, filter dropdown, and sort dropdown.
        -   Perform an initial render of the tasks.

## C. File Structure Plan

The project will use the existing file structure provided by the `bare-bones-vanilla-main` template. No new files will be created.

-   **`ui/index.html`**: The main HTML file. Its content will be updated to match the application's structure.
-   **`ui/css/style.css`**: The stylesheet. Its content will be replaced with custom styles for the FutureToDo app.
-   **`ui/js/main.js`**: The main JavaScript file. This file will be completely replaced with the application's logic, including state management, DOM manipulation, and event handling.

## D. Implementation Details (per file)

### `ui/js/main.js`

-   **Global Variables:**
    -   `tasks`: An array to hold task objects.
    -   `filters`: An object `{ searchTerm: '', status: 'all', sortBy: 'priority' }`.
    -   DOM element variables (e.g., `taskForm`, `taskList`).

-   **Functions:**
    -   `loadTasks()`: Reads and parses the 'tasks' item from `localStorage`.
    -   `saveTasks()`: Stringifies and saves the `tasks` array to `localStorage`.
    -   `renderTasks()`:
        1.  Filters tasks based on `filters.status` (`active`/`completed`).
        2.  Filters tasks based on `filters.searchTerm` (case-insensitive search on title and description).
        3.  Sorts the filtered list based on `filters.sortBy` (`due-date` or `priority`).
        4.  Generates an HTML string for the final list of tasks.
        5.  Updates the `innerHTML` of the task list element.
        6.  Attaches event listeners to the delete and toggle buttons of the newly rendered tasks.
    -   `addTask(event)`:
        1.  Prevents default form submission.
        2.  Gets values from the form inputs (`title`, `description`, `dueDate`, `priority`).
        3.  Validates that `title` is not empty.
        4.  Creates a new task object with a unique `id` (e.g., `Date.now()`), the input values, and `completed: false`.
        5.  Adds the new task to the `tasks` array.
        6.  Calls `saveTasks()` and `renderTasks()`.
        7.  Resets the form fields.
    -   `handleTaskListClick(event)`: An event handler on the `<ul>` element to delegate clicks for delete and toggle actions. It checks `event.target` to see if a delete or toggle button was clicked and calls the appropriate function (`deleteTask` or `toggleTaskStatus`) with the task ID.
    -   `init()` / `DOMContentLoaded` listener:
        1.  Assigns DOM elements to variables.
        2.  Sets up event listeners for:
            -   `#add-task-form` -> `submit` event -> `addTask`.
            -   `#search` -> `input` event -> update `filters.searchTerm` and call `renderTasks`.
            -   `#filter-status` -> `change` event -> update `filters.status` and call `renderTasks`.
            -   `#sort-by` -> `change` event -> update `filters.sortBy` and call `renderTasks`.
            -   `#task-list` -> `click` event -> `handleTaskListClick`.
        3.  Calls `loadTasks()` to initialize the `tasks` array.
        4.  Calls `renderTasks()` for the initial display.

### `ui/css/style.css`

-   Styles for the main container, form elements, filter controls, and task list.
-   Visual distinction for completed tasks (e.g., line-through text, different color).
-   Priority indicators (e.g., color-coded borders).
-   Basic responsive design for smaller screens.

### `ui/index.html`

- The structure provided by the UI agent is sufficient. No major changes are needed, but the final version will be written to ensure it's in sync with the CSS and JS. It will include the main container, heading, form, filter/sort controls, and the empty task list `<ul>`.
