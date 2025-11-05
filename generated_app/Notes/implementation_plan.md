
# Implementation Plan for Notes App

This document outlines the implementation plan for the Notes app, a fast, minimal, offline-first notes application.

## 1. Technical Architecture

### 1.1. State Management
- A single global `state` object will be defined in `js/main.js` to manage the application's state.
- The `state` object will have the following structure:
  ```javascript
  {
    notes: [], // Array of note objects
    currentView: 'home', // The currently active view ('home', 'detail', 'settings')
    selectedNoteId: null // The ID of the note being edited
  }
  ```

### 1.2. Data Persistence
- Data will be persisted in the browser's `localStorage`.
- All notes will be stored as a single JSON string under the key `"Notes.items"`.
- Helper functions will be created to handle reading from and writing to `localStorage`.

### 1.3. HTML Structure
- The application will be a single-page application (SPA) with three main views contained within a single `index.html` file.
- The views are:
  - `home-view`: Displays the list of notes, search bar, and filter options.
  - `detail-view`: A form for creating and editing notes.
  - `settings-view`: Contains options for importing, exporting, and clearing data.
- View switching will be handled by manipulating the `display` CSS property of the view containers.

### 1.4. Error Handling
- `try...catch` blocks will be used for `localStorage` operations and JSON parsing to handle potential errors gracefully.
- User feedback for confirmations and errors will be provided using `alert()` and `confirm()` dialogs.

## 2. Implementation Phases

### Phase 1: Core Infrastructure
1.  **Initialize `js/main.js`**: Set up the basic structure, including the `state` object and the `init` function.
2.  **Implement Data Persistence**: Create the `storage.js` module with `getNotes`, `saveNotes`, and `clearNotes` functions.
3.  **Utility Functions**: Create utility functions for generating UUIDs and getting ISO timestamps.

### Phase 2: HTML Logic & Views
1.  **View Management**: Implement the `showView(viewId)` function to switch between views.
2.  **Render Notes**: Create the `renderNotes()` function to display the notes in the `home-view`.
3.  **CRUD Operations**:
    - **Create**: Implement the logic to show the `detail-view` with a blank form.
    - **Read**: Implement the logic to populate the `detail-view` with the data of a selected note.
    - **Update**: Implement the logic to save the changes made in the `detail-view` form.
    - **Delete**: Implement the logic to delete a note.

### Phase 3: Features
1.  **Search & Filter**: Implement search functionality to filter notes by title and content.
2.  **Tagging**: Implement the ability to add and filter by tags.
3.  **Pinning**: Implement the functionality to pin and unpin notes.
4.  **Data Portability**:
    - **Export**: Implement the "Export Data" feature to download all notes as a JSON file.
    - **Import**: Implement the "Import Data" feature to import notes from a JSON file.
5.  **Clear Data**: Implement the "Clear All Data" feature with a confirmation dialog.

### Phase 4: Integration & Polish
1.  **Event Listeners**: Connect all UI elements (buttons, inputs, etc.) to their respective JavaScript functions.
2.  **Confirmations**: Add `confirm()` dialogs for all destructive actions (delete note, clear all data).
3.  **User Feedback**: Provide clear feedback to the user for actions like saving, importing, and exporting.
4.  **Final Testing**: Thoroughly test all features and user flows.

## 3. File Structure Plan

- **`ui/index.html`**: Will be modified to include the HTML for the three views and all necessary UI elements.
- **`ui/css/style.css`**: Will be modified to style the application, including the different views and UI components.
- **`ui/js/main.js`**: This file will contain all the JavaScript logic for the application. No new JavaScript files will be created.

## 4. Implementation Details

### `js/main.js`

- **`state`**: The global state object as described in section 1.1.
- **`init()`**:
  - Called on `DOMContentLoaded`.
  - Loads notes from `localStorage`.
  - Renders the initial home view.
- **`showView(viewId)`**:
  - Takes a `viewId` as an argument.
  - Hides all main view sections.
  - Shows the section with the corresponding `id`.
- **`renderNotes()`**:
  - Clears the current notes list in the DOM.
  - Iterates over `state.notes` and creates the HTML for each note.
  - Appends the note HTML to the notes list container.
- **CRUD Functions**:
  - `addNote(note)`
  - `updateNote(note)`
  - `deleteNote(noteId)`
- **Feature Functions**:
  - `searchNotes(query)`
  - `filterNotesByTag(tag)`
  - `togglePin(noteId)`
  - `importNotes(file)`
  - `exportNotes()`
  - `clearAllNotes()`
- **Event Handlers**:
  - Event listeners for clicks on buttons (`new-note-btn`, `cancel-btn`, `delete-note-btn`, etc.).
  - Event listener for the search input.
  - Event listener for the note form submission.

### `index.html`

- A `<main>` element will wrap the three view sections.
- **`<section id="home-view">`**:
  - Contains the "New Note" button, search input, and the notes list container.
- **`<section id="detail-view" style="display: none;">`**:
  - Contains the note form with fields for title, description, tags, and a pinned checkbox.
  - Includes "Save" and "Cancel" buttons.
- **`<section id="settings-view" style="display: none;">`**:
  - Contains buttons for "Import Data", "Export Data", and "Clear All Data".
  - An `<input type="file">` for importing notes.
