# VibeCoder: Smolagent Template-Based App Generator Implementation Plan

*Created: August 21, 2025*

## Executive Summary

Simple template-to-app generator using smolagents that:
1. Copies template from `templates/` to `result/` directory
2. Parameterizes template files with user specifications  
3. Uses editing tools from `/plans/2025_08_21_smolagent_edit_tools.md` for modifications

**Focus**: Elegant simplicity - copy template, set parameters, use editing tools for customization.

## 1. App Specification Model

### Pydantic Model Definition
```python
from pydantic import BaseModel
from typing import Optional, List

class AppSpec(BaseModel):
    """Specification for generating React app from template."""
    
    # Basic app information
    app_name: str                    # "my-todo-app" (kebab-case, used for directory/package name)
    display_name: str               # "My Todo App" (human-readable title)
    description: str                # "A simple todo management application"
    
    # Optional metadata
    author: Optional[str] = None    # "John Doe"
    version: Optional[str] = "0.1.0"
    
    # Template selection
    template_name: str = "react-simple-spa"  # Template to use from templates/ directory
    
    # Output configuration
    output_dir: str = "result"      # Where to generate the app
    
    # Custom content (used by editing tools)
    custom_content: Optional[str] = None     # Custom JSX content for App.tsx
    features: List[str] = []                 # ["localStorage", "dark-mode"] - for future use

    class Config:
        # Example for documentation
        schema_extra = {
            "example": {
                "app_name": "task-manager",
                "display_name": "Task Manager",
                "description": "A modern task management application with localStorage",
                "author": "Developer",
                "template_name": "react-simple-spa",
                "output_dir": "result",
                "custom_content": "<h1>Welcome to Task Manager</h1>",
                "features": ["localStorage"]
            }
        }
```

### Template Files to Parameterize
Only these files need variable replacement:
- `package.json` → `app_name`, `description`, `author`, `version`
- `index.html` → `display_name` (title tag)
- `src/App.tsx` → `custom_content` (if provided)
- Any `README.md` → `display_name`, `description`

## 2. Simple Template Generator

### Core Tool Definition

```python
# template_generator.py

import shutil
import os
from pathlib import Path
from smolagents import tool

@tool
def generate_app_from_template(app_spec: AppSpec) -> str:
    """
    Generate complete React app by copying template and setting parameters.
    
    Args:
        app_spec: AppSpec model with all configuration
    
    Returns:
        Success message with generated app location
    """
    # 1. Copy template to output directory
    template_path = Path("templates") / app_spec.template_name
    output_path = Path(app_spec.output_dir) / app_spec.app_name
    
    if not template_path.exists():
        return f"❌ Template not found: {template_path}"
    
    if output_path.exists():
        shutil.rmtree(output_path)  # Clean existing
    
    shutil.copytree(template_path, output_path)
    
    # 2. Parameterize key files
    _parameterize_package_json(output_path, app_spec)
    _parameterize_index_html(output_path, app_spec)
    
    if app_spec.custom_content:
        _parameterize_app_tsx(output_path, app_spec)
    
    return f"✅ Generated app '{app_spec.app_name}' in {output_path}"

# Helper functions (not tools)
def _parameterize_package_json(output_path: Path, spec: AppSpec):
    """Replace variables in package.json"""
    package_json_path = output_path / "package.json"
    with open(package_json_path, 'r') as f:
        content = f.read()
    
    # Simple string replacement (could use json.loads/dumps for robustness)
    content = content.replace('"react-simple-spa"', f'"{spec.app_name}"')
    content = content.replace('"0.0.0"', f'"{spec.version}"')
    
    # Add description if not exists
    if '"description":' not in content:
        content = content.replace(
            '"version":',
            f'"description": "{spec.description}",\n  "version":'
        )
    
    with open(package_json_path, 'w') as f:
        f.write(content)

def _parameterize_index_html(output_path: Path, spec: AppSpec):
    """Replace title in index.html"""
    html_path = output_path / "index.html"
    with open(html_path, 'r') as f:
        content = f.read()
    
    content = content.replace('<title>Vite + React + TS</title>', 
                            f'<title>{spec.display_name}</title>')
    
    with open(html_path, 'w') as f:
        f.write(content)

def _parameterize_app_tsx(output_path: Path, spec: AppSpec):
    """Replace content in App.tsx if custom_content provided"""
    app_tsx_path = output_path / "src" / "App.tsx"
    with open(app_tsx_path, 'r') as f:
        content = f.read()
    
    # Replace the content inside the div
    old_content = '''<div className="flex min-h-svh flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">Hello World</h1>
      <Button>Click me</Button>
    </div>'''
    
    new_content = f'''<div className="flex min-h-svh flex-col items-center justify-center">
      {spec.custom_content}
    </div>'''
    
    content = content.replace(old_content, new_content)
    
    with open(app_tsx_path, 'w') as f:
        f.write(content)
```

#### C. Development Feedback Tools

```python
@tool
def run_linter() -> str:
    """Run ESLint and return issues with file locations."""
    
@tool
def run_type_check() -> str:
    """Run TypeScript compiler and return type errors."""
    
@tool
def build_app() -> str:
    """Build the app and return build status + errors."""
    
@tool
def run_tests() -> str:
    """Run test suite and return failures."""
    
@tool
def preview_app() -> str:
    """Start development server and return access URL."""
```

#### D. Advanced Development Tools

```python
@tool
def watch_files(pattern: str, callback_action: str) -> str:
    """Watch files for changes and trigger actions."""
    
@tool
def analyze_bundle_size() -> str:
    """Analyze build bundle size and suggest optimizations."""
    
@tool
def extract_component(file_path: str, selection: str, new_component_name: str) -> str:
    """Extract JSX into new reusable component."""
    
@tool
def add_localStorage_integration(component_path: str, state_variables: list) -> str:
    """Add localStorage persistence to component state."""
```

## 3. Usage Examples

### Basic App Generation
```python
# Create simple app spec
app_spec = AppSpec(
    app_name="todo-app",
    display_name="Todo App", 
    description="A simple todo management application",
    author="Developer"
)

# Generate the app
result = generate_app_from_template(app_spec)
print(result)
# Output: ✅ Generated app 'todo-app' in result/todo-app
```

### With Custom Content
```python
# App with custom JSX content
app_spec = AppSpec(
    app_name="task-manager",
    display_name="Task Manager",
    description="Advanced task management with categories", 
    custom_content='''
      <h1 className="text-4xl font-bold">Task Manager</h1>
      <p className="text-gray-600">Organize your tasks efficiently</p>
      <Button>Get Started</Button>
    '''
)

result = generate_app_from_template(app_spec)
```

### Natural Language Parsing (Agent Handles This)
```python
# No composite tool - agent parses requirements into AppSpec internally
# Agent workflow would be:

user_request = "Create a todo app called TaskMaster"

# Agent internally:
# 1. Parses "TaskMaster" as app name
# 2. Infers "Task Master" as display name  
# 3. Creates AppSpec with parsed values
# 4. Calls generate_app_from_template(app_spec)
# 5. Uses additional editing tools if needed

# This keeps the agent flexible and avoids rigid parsing logic
```

## 4. Integration with Editing Tools

### Post-Generation Customization
After generating the base app, use editing tools for further customization:

```python
# 1. Generate base app
app_spec = AppSpec(
    app_name="todo-app",
    display_name="Todo App",
    description="A todo management application"
)
generate_app_from_template(app_spec)

# 2. Use editing tools for customization
from editing_tools import add_import_statement, replace_exact_text

# Add useState import
add_import_statement("result/todo-app/src/App.tsx", "import { useState } from 'react'")

# Add state to App component  
old_text = """function App() {
  return ("""

new_text = """function App() {
  const [todos, setTodos] = useState([]);
  return ("""

replace_exact_text("result/todo-app/src/App.tsx", old_text, new_text)

# 3. Validate changes
from quality_tools import check_typescript_syntax, build_react_app

check_typescript_syntax("result/todo-app/src/App.tsx")
build_react_app("result/todo-app")
```

### Agent Workflow Pattern
```python
# Agent decides each step independently - no composite tools

# 1. Agent generates base app
app_spec = AppSpec(app_name="todo-app", display_name="Todo App")
result = generate_app_from_template(app_spec)

# 2. Agent chooses to add imports (atomic operation)
add_import_statement("result/todo-app/src/App.tsx", "import { useState } from 'react'")

# 3. Agent chooses to modify content (atomic operation)  
old_text = """function App() {
  return ("""
new_text = """function App() {
  const [todos, setTodos] = useState([]);
  return ("""
replace_exact_text("result/todo-app/src/App.tsx", old_text, new_text)

# 4. Agent chooses to validate (atomic operation)
check_typescript_syntax("result/todo-app/src/App.tsx")

# 5. Agent chooses to build (atomic operation)
build_react_app("result/todo-app")
```

## 5. Agent Setup

### Simple Agent Configuration

```python
# agent_setup.py

from smolagents import CodeAgent, OpenAIServerModel
from template_generator import generate_app_from_template
from editing_tools import replace_exact_text, add_import_statement, read_file_section
from quality_tools import check_typescript_syntax, build_react_app
from am_tools import read_file, write_file, list_files, mkdir

template_agent = CodeAgent(
    tools=[
        # Template generation (atomic)
        generate_app_from_template,
        
        # File editing (atomic operations from editing tools plan)
        replace_exact_text,
        add_import_statement, 
        read_file_section,
        
        # Quality checks (atomic operations)
        check_typescript_syntax,
        build_react_app,
        
        # File system operations (atomic)
        read_file,
        write_file,
        list_files,
        mkdir
    ],
    model=OpenAIServerModel("gpt-5"),
    additional_authorized_imports=["shutil", "pathlib", "subprocess"],
    system_prompt="""You are a React app generator. You create React SPAs using atomic operations:
    1. Parse user requirements into AppSpec model
    2. Call generate_app_from_template() to create base app
    3. Use individual editing tools as needed for customization
    4. Use individual validation tools to check quality
    
    Make independent decisions about when to use each tool. Keep it simple and focused on working applications."""
)
```

### Usage Pattern
```python
# Agent workflow
user_request = "Create a todo app called TaskMaster with a clean interface"

# Agent would:
# 1. Parse request into AppSpec
# 2. Call generate_app_from_template(spec)
# 3. Use editing tools for any customization
# 4. Validate with quality tools
# 5. Return success/failure message

result = template_agent.run(user_request)
```

## 6. Implementation Phases

### Phase 1: Core Template Generator (Week 1)
- ✅ Define AppSpec Pydantic model
- ✅ Implement `generate_app_from_template()` tool
- ✅ Basic template copying with shutil
- ✅ Simple parameterization for package.json, index.html
- ✅ Integration with existing am_tools.py

### Phase 2: Enhanced Parameterization (Week 2)  
- ⚠️ Robust file parameterization (App.tsx custom content)
- ⚠️ Integration with editing tools from other plan
- ⚠️ Agent workflow with atomic tool decisions
- ⚠️ Error handling and validation
- ⚠️ Agent setup and testing

### Phase 3: Quality & Validation (Week 3)
- ⚠️ Integration with TypeScript/ESLint checking tools
- ⚠️ Build validation after generation
- ⚠️ Natural language to AppSpec parsing
- ⚠️ Comprehensive error messages
- ⚠️ Template validation and testing

### Phase 4: Polish & Documentation (Week 4)
- ⚠️ Agent workflow examples and documentation
- ⚠️ Template expansion capabilities
- ⚠️ Performance optimization
- ⚠️ Integration testing with full workflow

## 7. File Structure

### Project Layout
```
VibeCoder/
├── templates/
│   └── react-simple-spa/          # Source template
│       ├── package.json           # Parameterized: name, description, version
│       ├── index.html            # Parameterized: title
│       ├── src/App.tsx           # Parameterized: custom_content (optional)
│       └── ...                   # All other files copied as-is
├── result/
│   └── {app_name}/               # Generated apps appear here
│       ├── package.json          # After parameterization
│       ├── index.html           # After parameterization
│       ├── src/App.tsx          # After parameterization
│       └── ...                  # Copied template files
├── template_generator.py         # Core implementation
├── am_tools.py                   # Existing file system tools
└── generate_app.py              # Updated to use new approach
```

### Template Variables
Templates use simple string replacement (no Jinja2 complexity):

**package.json**:
```json
{
  "name": "{{APP_NAME}}",
  "description": "{{DESCRIPTION}}",
  "version": "{{VERSION}}",
  "author": "{{AUTHOR}}"
}
```

**index.html**:
```html
<title>{{DISPLAY_NAME}}</title>
```

**App.tsx** (only if custom_content provided):
```tsx
// Replace default content div with custom content
```

## 8. Success Metrics

### Core Metrics
- **Template Copy Success**: 100% (simple file copying)
- **Parameterization Success**: >95% (string replacement)
- **Build Success**: 100% (generated apps must build)
- **TypeScript Validation**: 100% (no type errors)

### Performance
- **Generation Time**: <10 seconds (copy + parameterize)
- **File Size**: Identical to template (no bloat)
- **Memory Usage**: Minimal (no complex processing)

### Quality
- **Runnable Apps**: 100% (must start with `pnpm dev`)
- **Clean Code**: Generated code matches template quality
- **No Errors**: All generated apps pass lint and build

## 9. Future Enhancements

### Additional Templates
- 🔮 `react-dashboard` - Admin dashboard template
- 🔮 `react-blog` - Blog/content template  
- 🔮 `react-ecommerce` - Shopping cart template
- 🔮 Template auto-selection based on requirements

### Enhanced Parameterization  
- 🔮 Component-level customization
- 🔮 Theme/styling options in AppSpec
- 🔮 Package dependency selection
- 🔮 Environment configuration generation

### Workflow Improvements
- 🔮 Better natural language parsing to AppSpec
- 🔮 Template validation and testing
- 🔮 Generated app preview/screenshot
- 🔮 Automatic dependency updates

---

**Key Principle**: Keep template generation simple - copy files and replace variables. Use editing tools from the other plan for complex modifications.

**Integration**: This plan focuses purely on template→app generation. The `/plans/2025_08_21_smolagent_edit_tools.md` plan handles all post-generation editing and customization.

---

**Legend:**
- ✅ Completed
- ⚠️ In Progress/Planned
- 🔮 Future Enhancement

This implementation plan provides a roadmap for building a sophisticated, token-efficient AI-powered React application generator using smolagents, with strong emphasis on iterative development and quality assurance.