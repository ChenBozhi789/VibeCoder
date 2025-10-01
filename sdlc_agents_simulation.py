from smolagents import PlanningStep, CodeAgent, ToolCallingAgent, OpenAIServerModel, tool
from am_tools import list_files, write_file, mkdir, read_file, build_app_spec_from_docs 
from pathlib import Path
from datetime import datetime
import json, os

# Shared state manager for agent communication
class AgentState:
    def __init__(self):
        self.current_project = None
        self.projects = {}  # Dictionary to store multiple projects
        self.base_path = Path("Multiple_Agents_Simulation").resolve()
        self.ui_memory = {}  # Memory for UI agent across sessions
        
    def set_current_project(self, project_name: str):
        """Set the current active project"""
        self.current_project = project_name
        if project_name not in self.projects:
            self.projects[project_name] = {
                'app_name': project_name,
                'app_folder_path': self.base_path / project_name,
                'prd_path': self.base_path / project_name / "PRD.md",
                'spec_path': self.base_path / project_name / "app_spec.json",
                'template_path': Path("templates/react-simple-spa"),
                'ui_design_path': self.base_path / project_name / "ui_design.md"
            }
        
    def get_current_project(self) -> str:
        return self.current_project
        
    def get_app_name(self) -> str:
        if self.current_project and self.current_project in self.projects:
            return self.projects[self.current_project]['app_name']
        return None
        
    def get_app_folder_path(self) -> Path:
        if self.current_project and self.current_project in self.projects:
            return self.projects[self.current_project]['app_folder_path']
        return None
        
    def get_prd_path(self) -> Path:
        if self.current_project and self.current_project in self.projects:
            return self.projects[self.current_project]['prd_path']
        return None
        
    def get_spec_path(self) -> Path:
        if self.current_project and self.current_project in self.projects:
            return self.projects[self.current_project]['spec_path']
        return None
        
    def get_template_path(self) -> Path:
        if self.current_project and self.current_project in self.projects:
            return self.projects[self.current_project]['template_path']
        return Path("templates/react-simple-spa")
        
    def list_projects(self) -> list:
        """List all available projects"""
        return list(self.projects.keys())
        
    def project_exists(self, project_name: str) -> bool:
        """Check if a project exists"""
        return project_name in self.projects
        
    def get_ui_design_path(self) -> Path:
        """Get the UI design file path for the current project"""
        if self.current_project and self.current_project in self.projects:
            return self.projects[self.current_project]['ui_design_path']
        return None
        
    def set_ui_memory(self, key: str, value: any) -> None:
        """Set a value in UI memory"""
        if self.current_project:
            if self.current_project not in self.ui_memory:
                self.ui_memory[self.current_project] = {}
            self.ui_memory[self.current_project][key] = value
            
    def get_ui_memory(self, key: str) -> any:
        """Get a value from UI memory"""
        if self.current_project and self.current_project in self.ui_memory:
            return self.ui_memory[self.current_project].get(key)
        return None
        
    def get_all_ui_memory(self) -> dict:
        """Get all UI memory for current project"""
        if self.current_project and self.current_project in self.ui_memory:
            return self.ui_memory[self.current_project]
        return {}

# Global state instance
agent_state = AgentState()

@tool
def get_user_requirements(question_for_user: str) -> str:
    """
    Get user requirements on the app.

    Args:
        question_for_user: The question to ask the user

    Returns:
        The user's requirements as a string
    """
    print(question_for_user)
    response = input("Enter your response: ")
    return response

# set_app_name = create or select + ensure folder exists.
@tool
def set_app_name(app_name: str) -> str:
    """
    Set the app name in the global state and create the app folder structure.
    
    Args:
        app_name: The name of the app
        
    Returns:
        Confirmation message with the created paths
    """
    global agent_state
    
    # Set the current project
    agent_state.set_current_project(app_name)
    
    # Create the app folder if it doesn't exist
    app_folder = agent_state.get_app_folder_path()
    if app_folder and not app_folder.exists():
        mkdir(str(app_folder))
    
    return f"Project '{app_name}' set as current project. Created folder at: {app_folder}"

# set_current_project = select only (requires folder to already exist).
@tool
def set_current_project(project_name: str) -> str:
    """
    Set the current active project.
    
    Args:
        project_name: The name of the project to set as current
        
    Returns:
        Confirmation message
    """
    global agent_state
    
    # Check if project exists in the file system
    project_path = agent_state.base_path / project_name
    if not project_path.exists():
        return f"Project '{project_name}' does not exist. Available projects: {list_existing_projects()}"
    
    # Set the current project
    agent_state.set_current_project(project_name)
    
    return f"Current project set to '{project_name}'"

@tool
def list_existing_projects() -> str:
    """
    List all existing projects in the Multiple_Agents_Simulation folder.
    
    Returns:
        List of existing project names
    """
    global agent_state
    
    if not agent_state.base_path.exists():
        return "No projects found. Base directory does not exist."
    
    projects = []
    for item in agent_state.base_path.iterdir():
        if item.is_dir():
            projects.append(item.name)
    
    if not projects:
        return "No projects found."
    
    return f"Existing projects: {', '.join(projects)}"

@tool
def get_current_project() -> str:
    """
    Get the current active project name.
    
    Returns:
        The current project name or "No project selected"
    """
    global agent_state
    current = agent_state.get_current_project()
    return current if current else "No project selected"

@tool
def get_app_name() -> str:
    """
    Get the current app name from the global state.
    
    Returns:
        The current app name
    """
    global agent_state
    return agent_state.get_app_name() or "No app name set"

@tool
def get_prd_path() -> str:
    """
    Get the PRD file path from the global state.
    
    Returns:
        The PRD file path
    """
    global agent_state
    return str(agent_state.get_prd_path())

@tool
def get_spec_path() -> str:
    """
    Get the app spec file path from the global state.
    
    Returns:
        The app spec file path
    """
    global agent_state
    return str(agent_state.get_spec_path())

@tool
def get_template_path() -> str:
    """
    Get the template path from the global state.
    
    Returns:
        The template path
    """
    global agent_state
    return str(agent_state.get_template_path())

@tool
def get_ui_design_path() -> str:
    """
    Get the UI design file path from the global state.
    
    Returns:
        The UI design file path
    """
    global agent_state
    return str(agent_state.get_ui_design_path())

@tool
def set_ui_memory(key: str, value: str) -> str:
    """
    Set a value in UI memory for the current project.
    
    Args:
        key: The memory key
        value: The value to store (will be converted to string)
        
    Returns:
        Confirmation message
    """
    global agent_state
    agent_state.set_ui_memory(key, value)
    return f"UI memory set: {key} = {value}"

@tool
def get_ui_memory(key: str) -> str:
    """
    Get a value from UI memory for the current project.
    
    Args:
        key: The memory key
        
    Returns:
        The stored value or "Not found"
    """
    global agent_state
    value = agent_state.get_ui_memory(key)
    return str(value) if value is not None else "Not found"

@tool
def get_all_ui_memory() -> str:
    """
    Get all UI memory for the current project.
    
    Returns:
        JSON string of all UI memory
    """
    global agent_state
    memory = agent_state.get_all_ui_memory()
    return json.dumps(memory, indent=2)

@tool
def copy_template_to_ui_folder() -> str:
    """
    Copy the React template to the ui/ folder within the current app directory.
    This creates a working React app structure that can be modified for the UI design.
    
    Returns:
        Confirmation message with the destination path
    """
    global agent_state
    import shutil
    
    if not agent_state.current_project:
        return "Error: No current project selected. Use set_current_project() first."
    
    # Get paths
    app_folder = agent_state.get_app_folder_path()
    template_path = agent_state.get_template_path()
    ui_folder = app_folder / "ui"
    
    if not app_folder or not template_path:
        return "Error: Could not get app folder or template path."
    
    try:
        # Create ui folder if it doesn't exist
        if not ui_folder.exists():
            mkdir(str(ui_folder))
        
        # Copy template contents to ui folder
        if template_path.exists():
            # Copy all contents from template to ui folder
            for item in template_path.iterdir():
                dest = ui_folder / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            
            return f"Template successfully copied to: {ui_folder}"
        else:
            return f"Error: Template path does not exist: {template_path}"
            
    except Exception as e:
        return f"Error copying template: {str(e)}"


# 1. PRD Agent
prd_agent = ToolCallingAgent(
   tools=[
      mkdir,
      get_user_requirements,
      write_file,
      set_app_name,
      get_app_name,
      get_prd_path,
   ],
   model=OpenAIServerModel('gpt-5-mini'),
   # step_callbacks={PlanningStep: print},
)

# Can optimize this path to be more dynamic
storage_folder = "Multiple_Agents_Simulation"
# Final path: C:\Users\cbz\Desktop\VibeCoder\VibeCoder\Multiple_Agents_Simulation
final_path = Path(storage_folder).resolve()

# Example task + human feedback loop
prd_task = f"""
## 📝 PRD Task
You are a helpful Product Manager.  
Your mission is to guide the user through a short interview to gather app requirements, then save them to **PRD.md**.

---

## 📋 Requirement Rules
- **FIRST**: Ask for the **app name** and use `set_app_name(app_name)` to store it in the system.
- Ask **one question at a time** in plain, everyday language.  
- **ALWAYS present options as numbered lists** (1, 2, 3...) or lettered lists (A, B, C...) for easy selection.
- Follow this order of questions:

1. **App Name** → What should we call this app? (Use `set_app_name()` after getting the answer)
2. **Purpose & users** → What problem should the app solve, and who will use it?  
3. **Features** → What main things should people be able to do? (e.g., add tasks, set reminders, organize, etc.)  
4. **Look & feel** → How should it look and work? (simple list, mobile-friendly, desktop, or both)  
5. **Information to save** → What details do you want to keep for each item? (title, notes, due date, reminder, etc.)  
6. **Rules** → Any checks needed when people enter info? (title required, dates must make sense)  
7. **Other needs** → Should it work offline, load quickly, or be easy for everyone to use?  
8. **Extras** → Do you want backup/export, the app to be installable offline, or special branding?  
9. **When it's done** → What would make you feel the app is complete? How should it handle empty lists or mistakes?  

---

## 📋 Questioning Principles
- **One Step at a Time** → Keep questions simple and clear.  
- **Everyday Language** → Avoid jargon; focus on what the app does and who uses it.  
- **Numbered/Lettered Options** → ALWAYS present multiple choice options as numbered (1, 2, 3...) or lettered (A, B, C...) lists.
- **Easy Selection** → Users can simply type the number/letter of their choice, or type their own answer.
- **Logical Flow** → Start with the big picture, then go into details.  
- **Friendly and Helpful** → Make it easy for users to choose by providing clear, numbered options.

**Example Format:**
```
What type of app are you building?

1. Task Management (to-do lists, reminders)
2. Note Taking (personal notes, documents)
3. Data Collection (forms, surveys)
4. Social/Communication (chat, forums)
5. E-commerce (shopping, payments)
6. Other (please describe)

Please enter the number of your choice (1-6) or describe your own idea:
```

---

## ✅ Final PRD Summary
At the end of the interview, summarize all answers clearly in **PRD.md**.  
Include: purpose, features, UI/UX notes, data model, rules, non-functional needs, extras, and success criteria.  
Format the output in clean Markdown with headings and bullet points.  

---

## 📂 File Handling Rules
1. **Set App Name First**  
- Use `set_app_name(app_name)` to store the app name and create the folder structure.
2. **Get File Paths**  
- Use `get_prd_path()` to get the correct PRD file path.
3. **Write Files**  
- Save the PRD file using:  
   ```python
   write_file(get_prd_path(), content)
   ```
4. **Restriction**  
- ❌ Do not write anywhere else.
"""

print("🚀 Start running PRD agent")
prd_agent.run(prd_task)

# 2. Spec agent
spec_agent = ToolCallingAgent(
   tools=[
      read_file,
      write_file,
      get_app_name,
      get_prd_path,
      get_spec_path,
      build_app_spec_from_docs,
      set_current_project,
      list_existing_projects,
      get_current_project
   ],
   model=OpenAIServerModel('gpt-5-mini'),
   # step_callbacks={PlanningStep: print},
)

spec_task = f"""
You are the Spec Agent.  
Your mission is to review `PRD.md` and build `app_spec.json`.  

---

## Spec Tasks
1. **Check current project status**:
   - Use `get_current_project()` to see if a project is already selected
   - If no project is selected, use `list_existing_projects()` to see available projects
   - If multiple projects exist, ask the user which project to work on, then use `set_current_project(project_name)`

2. **Get the app name and file paths**:
   - Use `get_app_name()` to get the current app name
   - Use `get_prd_path()` to get the PRD file path
   - Use `get_spec_path()` to get the target spec file path

3. **Read the PRD file**:
   - Use `read_file(get_prd_path())` to read the PRD content

4. **Verify every requirement** from `PRD.md` is covered in `app_spec.json`.  

5. **Ensure terminology consistency** (same feature names in both files).  

6. **Check that `app_spec.json` includes all sections**:  
   - Overview  
   - Functional Requirements  
   - Non-Functional Requirements  
   - UI/UX Design  
   - Data Model  
   - Validation & Edge Cases  
   - Storage & Persistence  
   - Implementation Plan  
   - QA Checklist  
   - Success Criteria  
   - Future Enhancements  

7. **Build AppSpec from PRD**:
   ```python
   build_app_spec_from_docs(get_prd_path(), get_spec_path())
   ```

8. **Save the spec file**:
   - The file will be automatically saved to the correct path using `get_spec_path()`

---

## INSTRUCTIONS
1. **First, check project status** - ensure you're working on the correct project
2. Get the app name and file paths using the provided tools
3. Read the PRD file using `read_file(get_prd_path())`
4. Build the app spec using `build_app_spec_from_docs(get_prd_path(), get_spec_path())`
5. The spec will be automatically saved to the correct location

## Multi-Project Handling
- If multiple projects exist, you must select which project to work on
- Always confirm the current project before proceeding
- If the user wants to work on a different project, use `set_current_project(project_name)`
"""

print("🚀 Start running Spec agent")
spec_agent.run(spec_task)

# Need to specify the template path and spec path
# template_path = Path("templates/react-simple-spa")
# Final path: C:\Users\cbz\Desktop\VibeCoder\VibeCoder\Multiple_Agents_Simulation\<app_name>\app_spec.json
# spec_path = Path(f"{final_path}/<app_name>/app_spec.json")
template_path = agent_state.get_template_path()
spec_path = agent_state.get_spec_path()

# 3. UI agent - CodeAgent
ui_agent = CodeAgent(
   tools=[
      mkdir,
      list_files,
      read_file,
      write_file,
      get_app_name,
      get_prd_path,
      get_spec_path,
      get_template_path,
      get_ui_design_path,
      copy_template_to_ui_folder,
      set_ui_memory,
      get_ui_memory,
      get_all_ui_memory,
      set_current_project,
      list_existing_projects,
      get_current_project
   ],
   model=OpenAIServerModel('gpt-5-mini'),
   # step_callbacks={PlanningStep: print},
)

ui_task = f"""
You are the **UI Designer Agent**.
Your job: create a **modular, configurable UI prototype** that fits naturally into the existing **React + Vite + TypeScript** template.
Do not implement business logic or backend; stay strictly in the UI layer.

## 1) Check project status and get app information
- Use `get_current_project()` to see if a project is already selected
- If no project is selected, use `list_existing_projects()` to see available projects
- If multiple projects exist, ask the user which project to work on, then use `set_current_project(project_name)`
- Use `get_app_name()` to get the current app name
- Use `get_prd_path()` to get the PRD file path
- Use `get_spec_path()` to get the app spec file path
- Use `get_template_path()` to get the template path
- Use `get_ui_design_path()` to get the UI design file path

## 2) Check and use memory
- Use `get_all_ui_memory()` to check if there's existing UI design work for this project
- If memory exists, review previous decisions and continue from where you left off
- Use `set_ui_memory(key, value)` to store important design decisions and findings
- Store key information like: component_hierarchy, design_decisions, user_requirements_summary, etc.

## 3) Read and understand requirements
**MANDATORY**: Read both requirement documents to understand the full scope:
- Read the PRD using `read_file(get_prd_path())` to understand the business requirements and user needs
- Read the app spec using `read_file(get_spec_path())` to understand the technical specifications
- Extract from both documents and store in memory:
  - Screens/pages, forms, lists/tables, detail views
  - Navigation flow and UI states (empty/loading/error)
  - Reusable elements (buttons, inputs, cards, modals, badges, pagination, search/filter, etc.)
  - User personas and use cases from PRD
  - Technical constraints and requirements from spec

## 3) Copy React template to ui/ folder
- Use `copy_template_to_ui_folder()` to copy the entire React template into the app's ui/ folder
- This creates a working React app structure that you can modify for the UI design
- The template will be copied from the template_path to `<app>/ui/`

## 4) Discover the template (read-first mindset)
After copying, read and learn from the template in the ui/ folder:
- Project docs & configs: `ui/README.md`, `ui/package.json` (scripts, deps), `ui/eslint.config.*`, `ui/tsconfig*.json`, `ui/components.json` (if present).
- Existing code under `ui/src/` to infer coding style (functional components, hooks, routing, styling approach).
From this, infer:
- **Component conventions** (naming, export patterns, folder conventions).
- **Routing/navigation approach** (if any).
- **Styling approach** (Tailwind/CSS Modules/vanilla CSS) and lint/type rules to respect.

## 5) Plan (write-first design doc)
**MANDATORY**: Create `ui_design.md` file using `write_file(get_ui_design_path(), content)` with a comprehensive design plan that includes:
- **Component hierarchy** (atoms → molecules → organisms/pages) and rationale.
- **Props & types** for each component (TypeScript interfaces).
- **Routing map** (high-level), navigation patterns, and empty/error/loading states.
- **Accessibility** notes (ARIA, keyboard focus order, labels, contrast).
- **Assumptions** made where the spec is silent, and how to change them later.
- **Styling strategy** aligned with the template (no new dependencies).
- **User journey mapping** based on PRD requirements.
- **Template analysis** findings from the copied React template.

**IMPORTANT**: You MUST use `write_file(get_ui_design_path(), content)` to create this file. This is a required deliverable.

## 6) Implement the prototype (scaffold, not logic)
- Generate **presentational, prop-driven components** that reflect the plan.
- Modify the copied template files in the `ui/` folder to implement your design
- Keep components **small, cohesive, and reusable**; avoid global state unless the template already prescribes it.
- Provide **placeholder data via typed props** or minimal in-file mocks purely for layout demo (no network calls).
- Follow the template's import/exports, lint rules, and file-naming conventions.
- **IMPORTANT**: Do not modify `ui/package.json`, `ui/package-lock.json`, or any build configuration files
- If a richer UI element is needed (table, modal), first look for existing patterns in the template; if absent, implement a lightweight, dependency-free version.
- Focus on modifying `ui/src/` files to implement your UI design

## 6.5) Create UI Design Documentation
**BEFORE FINISHING**: Ensure you have created the `ui_design.md` file using `write_file(get_ui_design_path(), content)`.
This file should document your design decisions, component structure, and implementation approach.

## 7) UX quality bar
- Responsive (mobile-first) and keyboard-accessible.
- Clear empty states, input validation hints (UI only), and error placeholders.
- Consistent spacing, typography, and interactive states (hover/focus/disabled).

## 8) What NOT to do
- Do not add or change dependencies or configs.
- Do not implement real data fetching or business logic.
- Do not rely on global singletons or app-wide state unless the template mandates it.
- Do not introduce ad-hoc CSS frameworks outside the template's documented approach.

## 9) Deliverables
**REQUIRED FILES TO CREATE**:
1. **`ui_design.md`** - Use `write_file(get_ui_design_path(), content)` to create this file in the same app folder as PRD.md
   - Must include: plan + rationale + assumptions + user journey mapping + template analysis
2. **`ui/` folder** - Complete, working React app with your UI design implemented
3. **Memory storage** - Use `set_ui_memory()` to store key design decisions for future reference

**CRITICAL**: The `ui_design.md` file creation is MANDATORY and must be completed before finishing.

## 10) Memory Management
- Use `set_ui_memory()` to store important design decisions, component hierarchy, and findings
- Use `get_ui_memory()` to retrieve specific information when needed
- Use `get_all_ui_memory()` to review all stored information
- Store information like:
  - component_hierarchy: The planned component structure
  - design_decisions: Key UI/UX decisions made
  - user_requirements_summary: Summary of requirements from PRD and spec
  - template_analysis: Key findings about the template structure
  - accessibility_notes: Important accessibility considerations

## 11) Acceptance checklist (self-check)
- Matches both `PRD.md` and `app_spec.json` screens and flows.
- `ui_design.md` is saved in the same app folder as PRD.md and app_spec.json
- React template is successfully copied to `ui/` folder
- UI design is implemented in the copied template files (focus on `ui/src/`)
- No build configuration files (`package.json`, `package-lock.json`, etc.) are modified
- Key design decisions are stored in memory for future reference
- Design document includes component hierarchy, props & types, routing map, accessibility notes
- Assumptions are documented and easy to change later
- Memory is used effectively to maintain context across sessions
"""

print("🚀 Start running UI agent")
ui_agent.run(ui_task)

# 4. Code agent - CodeAgent
code_agent = CodeAgent(
   tools=[
      read_file,
      write_file,
      list_files,
      get_all_ui_memory,
   ],
   model=OpenAIServerModel('gpt-5-mini'),
   # step_callbacks={PlanningStep: print},
)

code_task = f"""
You are the **Code Generation Agent**.  
Your mission is to turn `app_spec.json` and `ui_prototype.html` into a working application.

### ⚙️ Tasks
1. Generate the application code structure:
   - Frontend (React/Tailwind OR vanilla HTML/JS depending on spec).
   - Backend (Node/Express, Django, or local-first approach).
   - Data model files.
2. Implement all functional requirements listed in `app_spec.json`.
3. Save files under `{final_path}/<app_name>/src`.
4. Ensure:
   - Code runs without syntax errors.
   - Comments explain major functions.
   - Config files (e.g., `package.json`, `requirements.txt`) are included.

Deliver a **minimal but functional** app matching the spec.
"""

print("🚀 Start running Code agent")
code_agent.run(code_task)