# UI Design Document — RedToDo

Overview:
A minimal, mobile-first todo list UI focused on speed and clarity. Presentational, prop-driven React + TypeScript components. No business logic or network calls—only typed props and small in-file mocks for layout.

Template analysis:
- template_path: templates\react-simple-spa
- NOTE: The template copy step may have failed; scaffolded minimal ui/src files are provided to continue UI design without changing build configs.

Component hierarchy (summary):
- Atoms: Button, TextInput, Checkbox, Icon
- Molecules: TaskRow (title, status, due badge), EmptyState, ConfirmDialog
- Organisms/Pages: TaskList, TaskEditorModal (presentational), Settings, Home page

Props & Types:
- Task: { id: string; title: string; done: boolean; dueDate?: string; reminder?: string }
- TaskRowProps: { task: Task; onToggle?: (id:string)=>void; onEdit?: (t:Task)=>void }
- TaskListProps: { tasks: Task[] }

Routing map:
- / -> TaskList (Home)
- /settings -> Settings (static)
(If template provides routing, we'll wire; scaffold uses simple App -> Home render.)

Accessibility notes:
- Use semantic buttons and inputs with labels and aria-labels.
- Modal focus management (documented in UI design) and visible focus outlines.
- High-contrast text and sufficient hit area for mobile.

Assumptions:
- dueDate and reminder fields are optional (UI presents them).
- Offline persistence and export are out of scope for UI scaffolding; UI shows export button.

Implementation files added:
- src/components/... presentational components and pages (no business logic).
