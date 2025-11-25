# BookNook Implementation Plan

App: BookNook (bare-bones-vanilla-main)

1. Requirements Summary (from PRD/app_spec)
- Goal: Personal log of books; offline; fast add; manage list.
- Core features: Quick Add; List; Create/Edit/Delete; Search & Filter; Sort; Persistence; Validation; Accessibility.
- Spec features snippet: "features": [
    "Quick Add Book",
    "List & Preview",
    "Create/Edit/Delete",
    "Search & Filter",
    "Data Portability"
  ]

2. Technical Architecture
- State management: Global singleton object in js/main.js; event-driven updates; render() functions per view.
- Persistence: localStorage under key 'booknook.books' and 'booknook.state'.
- HTML: Use existing index.html structure; hook into form inputs, list containers, filters, and modals if present.
- Error handling: Inline validation messages; ARIA-live region for announcements.
- Accessibility: Labels, keyboard navigation on list; focus management after operations.

3. Implementation Phases
3.1 Core Infrastructure
- Storage helpers: loadBooks(), saveBooks(), loadState(), saveState().
- ID generator: simple timestamp + counter.
- Pub/sub or simple re-render triggers on state changes.
3.2 HTML Logic
- Wire up Add Book form: title (required), author (required), optional fields (status, category, rating, notes, date read).
- Render list with controls (edit, delete, toggle status).
- Search box filters by title/author; dropdown filter by status; sort by date added/title/author.
3.3 Validation
- Required: title, author (trim, length 1-200).
- Optional: rating integer 1-5; date in YYYY-MM-DD; notes length <= 1000.
- Show inline error text; prevent submission if invalid.
3.4 Integration
- Ensure all handlers bound after DOMContentLoaded; persist all changes; re-render on changes.
3.5 Polish
- Empty state messages; clear completed; import/export JSON; keyboard shortcuts (Enter to add).

4. File Structure Plan
- Modify ui/index.html, ui/css/style.css, ui/js/main.js only; no new files/modules.
- Add ARIA live region and error containers in HTML if missing.

5. Detailed Feature Mapping to UI
- Add Form: #book-form with inputs #title, #author, #category, #status, #rating, #dateRead, #notes; submit -> addBook().
- List: container #book-list; items show title, author, status; actions [Edit, Delete, Toggle].
- Filters: #searchInput, #statusFilter, #sortSelect; on input/change -> update state and re-render.
- Edit Modal or Inline: If modal exists, bind; else inline editing using a simple editor row.
- Bulk: Clear All or Clear Read; confirm dialog.
- Export/Import: Buttons #exportBtn, #importBtn; export JSON file; import via file input #importFile.

6. Data Model
{ id, title, author, category?, status: 'read'|'unread'|'reading', rating?:1-5, notes?, dateAdded, dateRead? }

7. Validation Rules
- title: required, 1-200; author: required, 1-200; rating: null or 1-5; dateRead: ISO date; notes <= 1000.

8. Testing & Validation
- Manual: Add, edit, delete, search, filter status, sort; persistence across reloads; import/export; edge cases.
- Use validate_implementation(ui) if available.


9. Implementation Summary (executed)
- main.js replaced with full CRUD, search/filter/sort, localStorage persistence, import/export, inline edit support, accessibility announcements.
- style.css augmented with styles for form, list, badges, buttons, and error states.
- index.html left as-is; runtime scaffolding ensures #book-form, filters, and #book-list exist if missing.
- Data persistence: localStorage keys booknook.books.v1 and booknook.ui.v1.
- Validation: required title/author; rating 1-5; date YYYY-MM-DD; notes <= 1000.
- Bulk: clear read; export/import JSON.

10. Validation Status
- validate_implementation initial result: N/A

11. Troubleshooting & Notes
- If the UI form or list is not visible, ensure the <main id="main"> element exists. The script injects scaffolding at runtime.
- localStorage keys used: booknook.books.v1 and booknook.ui.v1. Clearing browser storage will reset data.
- Import expects an array of book objects with at least title and author strings.
- If sorting or filters do not seem to work, type into Search or change the dropdowns; state persists automatically.

12. Acceptance Checklist (self-check)
- [x] Read PRD.md, app_spec.json, UI_STRUCTURE.json
- [x] implementation_plan.md created and updated
- [x] Core infrastructure implemented (localStorage, in-file state management)
- [x] HTML logic implemented: Add/Edit/Delete, Toggle status, Render list
- [x] Search, Filter (status), Sort (added/title/author/rating)
- [x] Import/Export JSON; Bulk: Clear Read
- [x] Validation with inline errors and ARIA live announcements
- [~] Final automated validation: Not available in this environment; manual test recommended

13. How to Test Manually
- Open ui/index.html in a browser.
- Add a few books using Title and Author; verify they appear and persist after reload.
- Use Edit to modify, Toggle to change status, and Delete to remove.
- Try Search, Filter by status, and Sort options; verify results update.
- Export JSON; clear storage; Import JSON back; verify entries restored.
- Attempt invalid inputs (empty title/author, bad date) and verify inline errors.