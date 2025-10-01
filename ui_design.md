UI Design for DailyTasks (prototype)

Overview
- App: DailyTasks — simple task manager (presentational prototype).
- Goal: Provide a modular, configurable UI prototype (no business logic). Components are prop-driven and typed in TypeScript, aligned with existing React + Vite + TS template and the project's CSS approach (vanilla CSS with design tokens in src/styles.css).

Component hierarchy
- atoms/
  - Button (Button.tsx) - accessible button with variants (primary/ghost), supports disabled and aria-label.
  - Input (Input.tsx) - labeled input with validation hint UI only.
- molecules/
  - Card (Card.tsx) - generic surface for content.
  - TaskCard (TaskCard.tsx) - presentational row/card for a Task with actions (view, complete UI only).
- organisms/
  - TaskList (TaskList.tsx) - list of TaskCard items, renders empty state and pagination placeholder.
- pages/
  - ListPage (pages/list-page.tsx) - search/filter row, "Add" button, TaskList usage and empty state.
  - DetailPage (pages/detail-page.tsx) - task detail view with back link and edit button (UI only).

Props & Types (TypeScript interfaces)
- interface Task {
    id: string;
    title: string;
    description?: string;
    dueDate?: string; // ISO date string or human text
    completed?: boolean;
  }

- ButtonProps
  - children: React.ReactNode
  - variant?: 'primary' | 'ghost'
  - onClick?: () => void
  - disabled?: boolean
  - ariaLabel?: string

- InputProps
  - id: string
  - label?: string
  - value?: string
  - placeholder?: string
  - onChange?: (v: string) => void
  - hint?: string
  - type?: string

- CardProps
  - title?: string
  - subtitle?: string
  - children: React.ReactNode

- TaskCardProps
  - task: Task
  - onView?: (id: string) => void
  - onToggleComplete?: (id: string) => void

- TaskListProps
  - tasks: Task[]
  - onView?: (id: string) => void
  - onToggleComplete?: (id: string) => void

Routing map (high-level)
- "/" -> ListPage (main list, search, add)
- "/tasks/:id" -> DetailPage (shows task detail)
Navigation pattern:
- Header with site title and simple nav (App.tsx already present). Pages are self-contained and exported as default.
- Router placeholder in App.tsx — host app to replace with react-router if needed.

UI states
- Empty: card-like empty-state UI with action hint to "Add".
- Loading: skeleton placeholders (simple grey boxes via CSS).
- Error: visible card with error message (UI-only).
- Input validation: show hint text and aria-invalid attribute if a value is missing (UI-only).

Accessibility notes
- Buttons: use <button> with aria-label when text not descriptive.
- Inputs: always include a <label> associated with input id.
- Keyboard: focus styles kept visible (existing CSS outline used).
- Semantic markup: use main, header, nav, section, button, ul/li for lists.
- Contrast: use existing CSS variables ensuring sufficient contrast for primary text and primary buttons.

Styling strategy
- Use existing src/styles.css variables and conventions. No new dependencies.
- Add a small set of component classes appended to src/styles.css to keep styling local (no Tailwind).
- Follow responsive mobile-first breakpoints used in styles.css.

Assumptions
- No router currently used — App.tsx uses a view selector. Pages are exported as default and will be imported by host router later.
- No global state library present. Components remain purely presentational.
- Dates are strings (ISO or friendly); formatting outside scope.
- Placeholder actions call provided callback props; if absent, they are no-op.

How to change assumptions later
- Add router: replace App's view with react-router Routes.
- Connect to business logic: pass handlers from host or add context/Redux if needed.
- Styling: migrate to CSS modules or Tailwind by refactoring classnames and build config if desired.

Files added
- ui_design.md
- src/components/button.tsx
- src/components/input.tsx
- src/components/card.tsx
- src/components/task-card.tsx
- src/components/task-list.tsx
- src/pages/list-page.tsx
- src/pages/detail-page.tsx
- (appended) src/styles.css - component styling portion

Acceptance checklist (self-check)
- Matches app_spec.json screens (List + Detail) and responsive behavior.
- Components are prop-driven, typed, and reusable.
- No new dependencies added.
- Accessibility and responsive behaviors included in notes.
- Assumptions documented and easy to change.

End of design doc.
