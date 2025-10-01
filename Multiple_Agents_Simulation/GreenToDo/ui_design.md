UI Design Document - GreenToDo
Generated: 2025-09-30T10:29:07.724207Z

1) Overview
GreenToDo is a lightweight, mobile-first personal task manager. This UI design is a modular, component-driven React + Vite + TypeScript prototype. It focuses on rapid task capture, a clear task list, task details, and simple settings.

2) Key screens / pages (from PRD & spec)
- Dashboard (Task list + quick add + filters + empty state)
- Task Detail (view/edit task details, notes, due date)
- Settings (simple preferences)
- Shared UI: Header, Sidebar (optional for larger screens), Empty/Error/Loading states

3) Component hierarchy (atoms -> molecules -> organisms -> pages)
atoms:
  - Button (props: variant, disabled, onClick, ariaLabel)
  - Icon (svg wrapper)
  - Input (text input, onChange, value, placeholder, ariaLabel)
  - Checkbox (checked, onChange, ariaLabel)
  - Badge (label)
molecules:
  - FormField (label, input element, hint, error)
  - QuickAdd (Input + Add Button)
  - SearchBar (Input + clear action)
  - TaskCard (title, dueDate, checkbox, small actions)
organisms:
  - TaskList (list of TaskCard, empty state, loading state, pagination placeholder)
  - TaskDetailPanel (title, description, due date editor, action buttons)
  - Header (app title, search, settings)
pages:
  - DashboardPage (QuickAdd + TaskList + lightweight stats)
  - TaskDetailPage (TaskDetailPanel)
  - SettingsPage (simple preference form)

4) Props & Types (TypeScript interfaces)
- Task:
  interface Task {
    id: string;
    title: string;
    notes?: string;
    dueDate?: string; // ISO date string
    completed: boolean;
    createdAt: string;
  }

- ButtonProps:
  interface ButtonProps {
    children: React.ReactNode;
    variant?: 'primary' | 'secondary' | 'ghost';
    onClick?: () => void;
    disabled?: boolean;
    ariaLabel?: string;
  }

- InputProps:
  interface InputProps {
    value: string;
    onChange: (val: string) => void;
    placeholder?: string;
    ariaLabel?: string;
    type?: string;
  }

(Full props details are included in component source files under ui/src/components and ui/src/types.ts)

5) Routing map (high-level)
- /             -> DashboardPage
- /task/:id     -> TaskDetailPage
- /settings     -> SettingsPage
Routing is client-side; the scaffold uses a minimal approach without adding dependencies.

6) UI states
- Empty state: friendly prompt with CTA "Add your first task"
- Loading: neutral skeleton / spinner placeholder text
- Error: plain-language message with retry CTA

7) Accessibility notes
- All interactive elements receive focus styles and keyboard operability.
- Inputs have associated labels and aria-labels where visible labels are omitted.
- Buttons include aria-label when icon-only.
- Color contrast: use conservative color palette with high contrast text on background (CSS variables).
- Logical focus order: header -> quick add -> task list; modals trap focus (modal scaffolding only).

8) Styling strategy
- Reuse the template's styling approach (vanilla CSS or CSS modules). No new dependencies added.
- Provide a small global CSS variables file (ui/src/styles/global.css) for colors, spacing, and typography.
- Component-level styles use classNames matching component names to avoid conflicts.
- Mobile-first responsive layout; simple breakpoint for wide screens to show a left sidebar.

9) Assumptions
- Offline-first sync and persistence are out of scope for UI prototype: UI demonstrates placeholders for "sync status".
- No auth is required initially.
- The template is a simple React + Vite TypeScript SPA without heavy CSS frameworks. We will avoid adding new dependencies.

10) User journeys (summary)
- New user: lands on Dashboard -> sees empty state -> uses Quick Add to create first task -> sees it in list -> taps to view details -> edits notes -> returns to list.
- Returning user: sees list ordered by due date/uncompleted -> marks tasks complete via checkbox -> uses search/filter to find tasks.

11) Template analysis (scanned files)
Template path: C:\Users\cbz\Desktop\VibeCoder\VibeCoder\Multiple_Agents_Simulation\GreenToDo\ui
Observations:
  - App entry files inspected: App.tsx present: False (len=0); main.tsx present: False (len=0)
  - package.json present: False (len=0)
  - The template is a React + Vite SPA and appears to support TypeScript and Tailwind. Styling scaffolding uses plain CSS in this prototype to avoid altering dependencies.

12) Implementation plan
- Create a small component library in ui/src/components (atoms/molecules/organisms).
- Create pages under ui/src/pages and wire a minimal App under ui/src/App.tsx.
- Add ui/src/types.ts for shared type definitions.
- Add ui/src/styles/global.css and per-component classes in simple CSS.
- Provide placeholder data in page components to demonstrate layout.

13) How to change assumptions later
- All design decisions are stored in UI memory keys (component_hierarchy, design_decisions, template_analysis). They can be updated via set_ui_memory.

End of design doc.
