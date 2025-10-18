
# Implementation Plan for SpendLog

## 1. UI Overview and HTML Structure

The UI is composed of a single HTML file (`index.html`) which includes:
- An input form for adding new expenses, with fields for expense name, amount, and category.
- A section to display the list of expenses.
- A summary section to show total expenses and a breakdown by category.

Key UI components identified from `UI_STRUCTURE.json`:
No specific components identified.

## 2. Technical Architecture

- **State Management:** A simple array in vanilla JavaScript will manage the state of expenses. The array will be stored in and retrieved from `localStorage` to persist data across sessions.
- **Data Persistence:** `localStorage` will be used to store the expenses array as a JSON string.
- **HTML Structure and Data Flow:** 
    - The user adds an expense through the form.
    - The JavaScript code captures the form submission, creates a new expense object, and adds it to the local expenses array.
    - The array is saved to `localStorage`.
    - The UI is then re-rendered to display the updated list of expenses and the summary.
- **Error Handling and Validation:** Basic validation will be implemented to ensure that the expense name is not empty and the amount is a positive number.

## 3. Implementation Phases

### Phase 1: Core Infrastructure
- Implement utility functions for interacting with `localStorage` (`getExpenses`, `saveExpenses`).
- Set up the main application state array (`expenses`).

### Phase 2: HTML Logic & Business Logic
- **Add Expense:** Implement the `addExpense` function to handle form submission. This will involve reading values from the input fields, creating an expense object, adding it to the `expenses` array, saving to `localStorage`, and re-rendering the UI.
- **Display Expenses:** Create a `renderExpenses` function that iterates through the `expenses` array and generates the HTML for the expense list.
- **Delete Expense:** Implement a `deleteExpense` function that removes an expense from the array (by its index or a unique ID), saves the updated array to `localStorage`, and re-renders the UI.
- **Update Summary:** Create an `updateSummary` function to calculate and display the total expenses and the category breakdown.

### Phase 3: Data Validation
- Add checks in the `addExpense` function to validate the input fields.
- Display simple alerts or error messages to the user if validation fails.

### Phase 4: Integration and Testing
- Connect all the functions via event listeners (`DOMContentLoaded`, form `submit`, list `click` for deletion).
- Manually test the application to ensure all features work as expected: adding, deleting, and persisting expenses.

## 4. File Structure Plan

- **`ui/index.html`**: Will be modified to include the necessary HTML structure for the form, expense list, and summary. Existing template HTML will be replaced.
- **`ui/css/style.css`**: Will be modified to add custom styles for the application. Existing template CSS will be replaced.
- **`ui/js/main.js`**: This will contain all the JavaScript logic. Existing template JS will be replaced. No other JavaScript files will be created.

## 5. Implementation Details

### `ui/js/main.js`

- **Global Variables:**
    - `expenses` (array): To hold the list of expense objects.
    - DOM element references for the form, inputs, expense list, and summary sections.

- **Functions:**
    - `init()`: Runs on `DOMContentLoaded`. Fetches expenses from `localStorage` and calls the initial render functions.
    - `addExpense(e)`: Event handler for form submission.
    - `renderExpenses()`: Renders the `expenses` array to the DOM.
    - `deleteExpense(index)`: Deletes an expense at a given index.
    - `updateSummary()`: Calculates and displays summary data.
    - `getExpenses()`: Retrieves expenses from `localStorage`.
    - `saveExpenses()`: Saves the `expenses` array to `localStorage`.

- **Event Listeners:**
    - `DOMContentLoaded`: To initialize the application.
    - `submit` on the expense form: To add a new expense.
    - `click` on the expense list (event delegation): To handle delete actions.

## 6. Data Validation Rules

- **Expense Name:** Must not be empty.
- **Expense Amount:** Must be a valid, positive number.
- **Category:** Must be selected.

This plan provides a clear path forward for implementing the SpendLog application.
