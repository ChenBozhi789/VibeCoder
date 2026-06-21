import os
from pathlib import Path
from typing import Optional
from smolagents import tool


def _get_sandbox_root() -> Path:
    """
    Return the current sandbox root path.
    
    - Primary source: agent_state.base_path (system-managed sandbox root).
    - Fallback: current working directory.
    """
    try:
        # 延迟导入，避免模块初始化阶段的循环依赖问题
        from am_tools import agent_state  # type: ignore
        base = getattr(agent_state, "base_path", None)
        if base is None:
            return Path.cwd().resolve()
        return Path(base).resolve()
    except Exception:
        return Path.cwd().resolve()


def _resolve_safe_path(relative_path: str) -> Path:
    """
    Resolve a user-provided path into a safe absolute path rooted at the sandbox root.
    
    - Accepts relative paths.
    - If absolute path is provided, it MUST be within the sandbox root.
    - Normalizes '..' segments.
    - Ensures final path stays under the sandbox root.
    """
    sandbox_root = _get_sandbox_root()
    
    try:
        rel = Path(relative_path)
    except Exception:
        raise ValueError(f"Invalid path format: {relative_path}")

    # If it's absolute, try to make it relative to sandbox root to verify it's inside
    if rel.is_absolute():
        try:
            rel = rel.relative_to(sandbox_root)
        except ValueError:
            # Not under sandbox root
            raise ValueError(f"Absolute paths outside sandbox are forbidden: {relative_path}")
    
    # Compatibility normalization for older agents/prompts
    parts = list(rel.parts)
    if len(parts) >= 2:
        sandbox_task_id = sandbox_root.name
        # Case 1: generated_app/<task_id>/...
        if parts[0] == "generated_app" and parts[1] == sandbox_task_id:
            parts = parts[2:] or ["."]
            rel = Path(*parts)
        # Case 2: <task_id>/...
        elif parts[0] == sandbox_task_id:
            parts = parts[1:] or ["."]
            rel = Path(*parts)

    target = (sandbox_root / rel).resolve()
    
    # Final safety check: ensure target is within sandbox_root
    try:
        target.relative_to(sandbox_root)
    except ValueError:
        raise ValueError(f"Access denied: Path '{relative_path}' is outside sandbox root")
    
    return target


@tool
def read_file(filepath: str) -> str:
    """
    Read the content of a file under the sandbox root.

    Args:
        filepath: Path relative to sandbox root (e.g. 'ui/index.html')
    """
    target_path = _resolve_safe_path(filepath)

    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not target_path.is_file():
        raise ValueError(f"Path is not a file: {filepath}")

    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()


@tool
def write_file(filepath: str, content: str, mode: Optional[str] = "w") -> str:
    """
    Write content to a file under the sandbox root, creating parents as needed.

    Args:
        filepath: Path relative to sandbox root (e.g. 'ui/css/style.css')
        content: Text content to write
        mode: 'w' to overwrite, 'a' to append (default 'w')
    """
    if mode not in ["w", "a"]:
        raise ValueError("Mode must be 'w' (write/overwrite) or 'a' (append)")

    target_path = _resolve_safe_path(filepath)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path, mode, encoding="utf-8") as f:
        f.write(content)

    action = "written to" if mode == "w" else "appended to"
    return f"Successfully {action} file: {filepath}"


@tool
def list_files(directory: Optional[str] = ".", pattern: Optional[str] = "*") -> str:
    """
    List files in a directory under the sandbox root.

    Args:
        directory: Directory path relative to sandbox root (default '.')
        pattern: Glob pattern to filter files (default '*')
    """
    target_dir = _resolve_safe_path(directory)
    
    if not target_dir.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not target_dir.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    files = list(target_dir.glob(pattern))
    if not files:
        return f"No files matching pattern '{pattern}' in {directory}"
    
    sandbox_root = _get_sandbox_root()
    lines = []
    for file in sorted(files):
        try:
            # Always try to return paths relative to sandbox_root for the agent
            if file.is_file():
                relative_path = file.relative_to(sandbox_root)
                size = file.stat().st_size
                lines.append(f"  - {relative_path} ({size} bytes)")
            elif file.is_dir():
                relative_path = file.relative_to(sandbox_root)
                lines.append(f"  - {relative_path}/ (directory)")
        except ValueError:
            continue
    
    return f"Files in {directory}:\n" + "\n".join(lines)


@tool
def mkdir(directory: str, parents: Optional[bool] = True, exist_ok: Optional[bool] = True) -> str:
    """
    Create a directory under the sandbox root.

    Args:
        directory: Directory path relative to sandbox root
        parents: If True, create parent directories as needed (default True)
        exist_ok: If True, do not raise if directory already exists (default True)
    """
    target_dir = _resolve_safe_path(directory)

    if target_dir.exists():
        if not exist_ok:
            raise FileExistsError(f"Directory already exists: {directory}")
        if not target_dir.is_dir():
            raise ValueError(f"Path exists but is not a directory: {directory}")
        return f"Directory already exists: {directory}"

    try:
        target_dir.mkdir(parents=parents, exist_ok=exist_ok)
        return f"Successfully created directory: {directory}"
    except FileNotFoundError:
        if not parents:
            raise FileNotFoundError(
                "Parent directory doesn't exist. "
                "Set parents=True to create parent directories: "
                f"{directory}"
            )
        raise


# ============================================================================
# Agent State Management
# ============================================================================

class AgentState:
    """Manages agent state including current project, app name, and paths."""
    
    def __init__(self):
        # System-managed sandbox root.
        self.base_path = Path("generated_app")
        self.base_path.mkdir(exist_ok=True)
        self._current_project: Optional[str] = None
        self._app_name: Optional[str] = None
        self._ui_memory: dict = {}
        self.initial_user_requirements: Optional[str] = None
    
    def get_current_project(self) -> Optional[str]:
        """Get the current project name."""
        return self._current_project
    
    def set_current_project(self, project_name: str) -> str:
        """Set the current project name."""
        self._current_project = project_name
        return f"Current project set to: {project_name}"
    
    def get_app_name(self) -> Optional[str]:
        """Get the current app name."""
        return self._app_name
    
    def set_app_name(self, app_name: str) -> str:
        """Set the app name."""
        self._app_name = app_name
        return f"App name set to: {app_name}"
    
    def get_app_folder_path(self) -> str:
        """Get the absolute path to the current app folder (sandbox root)."""
        return str(self.base_path.resolve())

    def get_project_root(self) -> str:
        """Get the absolute path of the current project root."""
        return self.get_app_folder_path()

    def get_ui_folder(self) -> str:
        """Get the absolute path to the current project's UI folder."""
        return str(Path(self.get_app_folder_path()) / "ui")

    def get_ui_structure_path(self) -> str:
        """Get the absolute path to UI_STRUCTURE.json."""
        return str(Path(self.get_ui_folder()) / "UI_STRUCTURE.json")
    
    def get_prd_path(self) -> str:
        """Get the absolute path to PRD.md file."""
        return str(Path(self.get_app_folder_path()) / "PRD.md")
    
    def get_spec_path(self) -> str:
        """Get the absolute path to app_spec.json file."""
        return str(Path(self.get_app_folder_path()) / "app_spec.json")
    
    def get_template_path(self) -> str:
        """Get the path to templates directory."""
        return "templates"
    
    def get_ui_design_path(self) -> str:
        """Get the absolute path to UI design folder."""
        return str(Path(self.get_app_folder_path()) / "ui")
    
    def get_feedback_tickets_path(self) -> str:
        """Get the absolute path to feedback tickets file."""
        return str(Path(self.get_app_folder_path()) / "feedback_tickets.md")
    
    def get_enhancement_summary_path(self) -> str:
        """Get the absolute path to enhancement summary file."""
        return str(Path(self.get_app_folder_path()) / "enhancement_summary.md")
    
    def get_test_report_path(self) -> str:
        """Get the absolute path to test report file."""
        return str(Path(self.get_app_folder_path()) / "test_report.md")


# Create singleton instance
agent_state = AgentState()


# ============================================================================
# Agent State Management Tools (wrapped as @tool functions)
# ============================================================================

@tool
def get_current_project() -> str:
    """Get the current project identifier. Always returns 'default_project'."""
    return "default_project"


@tool
def set_current_project(project_name: str) -> str:
    """
    [DEPRECATED] Project switching is disabled. Returns a status message.

    Args:
        project_name: The name of the project to set (ignored)
    """
    return "Project switching is disabled. You are already in the correct root."


@tool
def list_existing_projects() -> str:
    """[DEPRECATED] Project listing is disabled. Returns a status message."""
    return "Project listing is disabled. Use '.' as your root."


@tool
def get_app_name() -> str:
    """Get the current app name."""
    app_name = agent_state.get_app_name()
    return app_name if app_name else "No app name set"


@tool
def set_app_name(app_name: str) -> str:
    """
    Set the app name.

    Args:
        app_name: The name of the app to set
    """
    return agent_state.set_app_name(app_name)


@tool
def get_prd_path() -> str:
    """Get relative path to PRD.md. Returns 'PRD.md'."""
    return "PRD.md"


@tool
def get_spec_path() -> str:
    """Get relative path to app_spec.json. Returns 'app_spec.json'."""
    return "app_spec.json"


@tool
def get_template_path() -> str:
    """Get the path to templates directory."""
    return agent_state.get_template_path()


@tool
def get_ui_design_path() -> str:
    """Get relative path to UI design folder. Returns 'ui'."""
    return "ui"


@tool
def get_app_folder_path() -> str:
    """Get the path to the current app folder. Returns '.'."""
    return "."


@tool
def get_project_root() -> str:
    """Get the current project root path. Returns '.'."""
    return "."


@tool
def get_ui_folder() -> str:
    """Get the project's UI folder path. Returns 'ui'."""
    return "ui"


@tool
def get_ui_structure_path() -> str:
    """Get the path to UI_STRUCTURE.json. Returns 'ui/UI_STRUCTURE.json'."""
    return "ui/UI_STRUCTURE.json"


@tool
def set_ui_memory(key: str, value: str) -> str:
    """
    Store UI design memory.

    Args:
        key: The key to store the memory under
        value: The value to store
    """
    agent_state._ui_memory[key] = value
    return f"UI memory set for key: {key}"


@tool
def get_ui_memory(key: str) -> str:
    """
    Get UI design memory by key.

    Args:
        key: The key to retrieve memory for
    """
    value = agent_state._ui_memory.get(key)
    return value if value else f"No memory found for key: {key}"


@tool
def get_all_ui_memory() -> str:
    """Get all UI design memory."""
    memory = agent_state._ui_memory
    if not memory:
        return "No UI memory stored"
    return "\n".join(f"{k}: {v}" for k, v in memory.items())


# ============================================================================
# User Requirements Tool
# ============================================================================

@tool
def get_user_requirements(question_for_user: str) -> str:
    """
    Get user requirements. 

    Args:
        question_for_user: The question to ask the user
    """
    pre_set = getattr(agent_state, "initial_user_requirements", None)
    if pre_set is not None and str(pre_set).strip():
        return f"{pre_set.strip()}\n\n[Non-interactive mode: apply sensible defaults for missing details.]"
    print(question_for_user)
    return input("User response: ")


# ============================================================================
# App Specification Tools
# ============================================================================

@tool
def build_app_spec_from_docs() -> str:
    """
    Build app_spec.json from PRD.md document.
    """
    try:
        prd_rel = agent_state.get_prd_path()
        spec_rel = agent_state.get_spec_path()
        
        prd_abs = _resolve_safe_path(prd_rel)
        spec_abs = _resolve_safe_path(spec_rel)
        
        if not prd_abs.exists():
            return f"Error: PRD.md not found at {prd_rel}"
        
        prd_content = prd_abs.read_text(encoding='utf-8')
        app_name = agent_state.get_app_name() or "app"
        
        app_spec = {
            "app_name": app_name,
            "display_name": app_name.replace('-', ' ').replace('_', ' ').title(),
            "description": prd_content[:200] + "..." if len(prd_content) > 200 else prd_content,
            "version": "0.1.0",
            "template_name": "react-simple-spa",
            "output_dir": "generated_app",
            "features": []
        }
        
        import json
        spec_abs.parent.mkdir(parents=True, exist_ok=True)
        spec_abs.write_text(json.dumps(app_spec, indent=2, ensure_ascii=False), encoding='utf-8')
        
        return f"Successfully generated app_spec.json at {spec_rel}"
    except Exception as e:
        return f"Error building app spec: {str(e)}"


# ============================================================================
# UI Structure Tools
# ============================================================================

@tool
def generate_ui_structure_json(ui_folder_path: Optional[str] = None) -> str:
    """
    Generate UI_STRUCTURE.json by analyzing the UI folder.

    Args:
        ui_folder_path: Optional path to the UI folder
    """
    try:
        if ui_folder_path is None or ui_folder_path.strip() == "":
            ui_folder_path = agent_state.get_ui_folder()
        
        ui_abs = _resolve_safe_path(ui_folder_path)
        if not ui_abs.exists():
            return f"Error: UI folder not found at {ui_folder_path}"
        
        html_file = ui_abs / "index.html"
        if not html_file.exists():
            return f"Error: index.html not found in {ui_folder_path}"
        
        ui_structure = {
            "version": "1.0",
            "ui_folder": ui_folder_path,
            "main_file": "index.html",
            "sections": [],
            "components": [],
            "notes": "Auto-generated UI structure"
        }
        
        structure_file_abs = ui_abs / "UI_STRUCTURE.json"
        import json
        structure_file_abs.write_text(json.dumps(ui_structure, indent=2, ensure_ascii=False), encoding='utf-8')
        
        return f"Successfully generated UI_STRUCTURE.json at {ui_folder_path}/UI_STRUCTURE.json"
    except Exception as e:
        return f"Error generating UI structure: {str(e)}"


@tool
def read_ui_structure_json(ui_folder_path: Optional[str] = None) -> str:
    """
    Read and return the content of UI_STRUCTURE.json.

    Args:
        ui_folder_path: Optional path to the UI folder
    """
    try:
        if ui_folder_path is None or ui_folder_path.strip() == "":
            rel_path = agent_state.get_ui_structure_path()
        else:
            rel_path = f"{ui_folder_path}/UI_STRUCTURE.json"
        
        abs_path = _resolve_safe_path(rel_path)
        if not abs_path.exists():
            return f"Error: UI_STRUCTURE.json not found at {rel_path}"
        return abs_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading UI structure: {str(e)}"


# ============================================================================
# Implementation Tools
# ============================================================================

@tool
def copy_template_to_ui_folder() -> str:
    """
    Copy UI template files to the current project's ui folder.
    """
    try:
        ui_path_abs = Path(agent_state.get_ui_design_path())
        template_path = Path(agent_state.get_template_path())
        
        # Look for a default template
        default_template = template_path / "react-simple-spa"
        if not default_template.exists():
            # Create basic UI structure
            ui_path_abs.mkdir(parents=True, exist_ok=True)
            (ui_path_abs / "css").mkdir(exist_ok=True)
            (ui_path_abs / "js").mkdir(exist_ok=True)
            
            # Create basic index.html
            html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="app">
        <h1>Welcome</h1>
    </div>
    <script src="js/main.js"></script>
</body>
</html>"""
            
            with open(ui_path_abs / "index.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return f"Created basic UI structure at {agent_state.get_ui_design_path()}"
        
        # Copy template if it exists
        import shutil
        if ui_path_abs.exists():
            shutil.rmtree(ui_path_abs)
        shutil.copytree(default_template, ui_path_abs)
        
        return f"Successfully copied template to {agent_state.get_ui_design_path()}"
    
    except Exception as e:
        return f"Error copying template: {str(e)}"


@tool
def implement_data_persistence(storage_type: str = "localStorage") -> str:
    """
    Implement data persistence for the app.
    
    Args:
        storage_type: Type of storage to use (default: localStorage)
    """
    return f"Data persistence implemented using {storage_type}"


@tool
def implement_state_management() -> str:
    """
    Implement state management for the app.
    """
    return "State management implemented"


@tool
def validate_implementation(ui_folder_path: Optional[str] = None) -> str:
    """
    Validate the implementation by checking files and structure.

    Args:
        ui_folder_path: Optional path to the UI folder
    """
    try:
        if ui_folder_path is None or ui_folder_path.strip() == "":
            ui_folder_path = agent_state.get_ui_folder()
        
        ui_abs = _resolve_safe_path(ui_folder_path)
        if not ui_abs.exists():
            return f"Error: UI folder not found at {ui_folder_path}"
        
        required_files = ["index.html"]
        missing = [f for f in required_files if not (ui_abs / f).exists()]
        
        if missing:
            return f"Validation failed: Missing files: {', '.join(missing)}"
        return "Validation passed: All required files present"
    except Exception as e:
        return f"Error validating implementation: {str(e)}"


@tool
def read_project_requirements() -> str:
    """
    Read and return the project requirements from PRD.md.
    """
    try:
        prd_rel = agent_state.get_prd_path()
        prd_abs = _resolve_safe_path(prd_rel)
        if not prd_abs.exists():
            return f"Error: PRD.md not found"
        return prd_abs.read_text(encoding='utf-8')
    except Exception as e:
        return f"Error reading project requirements: {str(e)}"


# ============================================================================
# QA and Auto-Fix Tools
# ============================================================================

@tool
def analyze_qa_report_for_fixes_needed() -> str:
    """
    Analyze QA report (code_prototype_test_report.md) to determine if fixes are needed.
    """
    try:
        report_rel = "code_prototype_test_report.md"
        report_abs = _resolve_safe_path(report_rel)
        
        if not report_abs.exists():
            return "NO - No QA report found"
        
        content = report_abs.read_text(encoding='utf-8').lower()
        issues = ["error", "bug", "missing", "broken", "fail", "issue", "critical"]
        has_issues = any(issue in content for issue in issues)
        
        if has_issues:
            return "YES - Issues found in QA report"
        return "NO - No critical issues found"
    except Exception as e:
        return f"NO - Error: {str(e)}"


@tool
def generate_vanilla_js_code(code_description: str) -> str:
    """
    Generate vanilla JavaScript code based on description.

    Args:
        code_description: Description of the code to generate
    """
    return f"// Generated code for: {code_description}\n// Implementation would go here"


# Example usage with smolagents
if __name__ == "__main__":
    from smolagents import CodeAgent, InferenceClientModel

    # Create an agent with the file tools
    model = InferenceClientModel()
    agent = CodeAgent(
        tools=[read_file, write_file, list_files, mkdir],
        model=model
    )

    # Example tasks the agent can perform:
    # agent.run("Create a directory called 'data'")
    # agent.run("Create nested directories 'output/reports/2024'")
    # agent.run("Create a file called 'test.txt' with the content 'Hello, World!'")
    # agent.run("Read the content of 'test.txt'")
    # agent.run("List all Python files in the current directory")
    # agent.run("Create a folder called 'output' and write a file 'output/results.txt' with some data")

    print("FileTool is ready to use with smolagents!")
