"""
UI Agent for generating runnable React prototypes from PRD, spec, and template inputs.

This agent takes:
- PRD.md: Product Requirements Document
- spec.json: Technical specification  
- Local React template folder (includes multiple files)

And outputs:
- A runnable React prototype in <App>/ui/ (template source remains unchanged)
"""

from smolagents import CodeAgent, OpenAIServerModel
from am_tools import (
    mkdir, list_files, read_file, write_file, ensure_dir, 
    copy_from_template, render_placeholders, write_files, 
    apply_patches, write_manifest, basic_check, save_ui_file
)
from pathlib import Path
import json
from typing import Optional, Dict, Any


class UIAgent:
    """
    UI Agent that generates runnable React prototypes from PRD, spec, and template inputs.
    
    Inputs:
    - PRD.md: Product Requirements Document with user needs and features
    - spec.json: Technical specification with detailed UI requirements  
    - Template folder: Local React template (includes multiple files, remains unchanged)
    
    Outputs:
    - Runnable React prototype in <App>/ui/ directory
    - Template source directory remains unchanged
    """
    
    def __init__(self, model_name: str = 'gpt-5-mini'):
        """Initialize the UI Agent with specified model."""
        self.model = OpenAIServerModel(model_name)
        self.agent = CodeAgent(
            tools=[
                mkdir, list_files, read_file, write_file, ensure_dir,
                copy_from_template, render_placeholders, write_files,
                apply_patches, write_manifest, basic_check, save_ui_file
            ],
            model=self.model
        )
    
    def generate_ui_prototype(
        self, 
        app_folder_path: str, 
        template_path: str,
        app_name: str = None
    ) -> Dict[str, Any]:
        """
        Generate a runnable React prototype from PRD.md and spec files in an app folder.
        
        Args:
            app_folder_path: Path to the app folder containing PRD.md and app_spec.json
            template_path: Path to React template directory
            app_name: Name of the application (optional, will be read from spec if not provided)
            
        Returns:
            Dictionary with generation results and status
        """
        
        # Determine file paths within the app folder
        prd_path = Path(app_folder_path) / "PRD.md"
        spec_path = Path(app_folder_path) / "app_spec.json"
        spec_md_path = Path(app_folder_path) / "spec.md"
        
        # Check which spec file exists
        if spec_md_path.exists():
            spec_file_path = str(spec_md_path)
        elif spec_path.exists():
            spec_file_path = str(spec_path)
        else:
            return {
                'success': False,
                'error': f"No spec file found in {app_folder_path}. Expected app_spec.json or spec.md",
                'app_folder_path': app_folder_path,
                'message': f"Failed to find spec file in {app_folder_path}"
            }
        
        # Set output path to ui/ folder within the app directory
        output_path = str(Path(app_folder_path) / "ui")
        
        # Read app name from spec if not provided
        if not app_name:
            try:
                with open(spec_file_path, 'r', encoding='utf-8') as f:
                    spec_data = json.load(f)
                    app_name = spec_data.get('app_name', spec_data.get('display_name', 'UnknownApp'))
            except Exception as e:
                app_name = Path(app_folder_path).name
        
        return self._generate_ui_from_files(
            prd_path=str(prd_path),
            spec_path=spec_file_path,
            template_path=template_path,
            output_path=output_path,
            app_name=app_name
        )
    
    def _generate_ui_from_files(
        self, 
        prd_path: str, 
        spec_path: str, 
        template_path: str, 
        output_path: str,
        app_name: str
    ) -> Dict[str, Any]:
        """
        Generate a runnable React prototype from the given input files.
        
        Args:
            prd_path: Path to PRD.md file
            spec_path: Path to spec file (app_spec.json or spec.md)
            template_path: Path to React template directory
            output_path: Path where UI prototype should be generated
            app_name: Name of the application
            
        Returns:
            Dictionary with generation results and status
        """
        
        # Create the UI generation task
        ui_task = f"""
You are the **UI Designer Agent**.
Your mission: Generate a runnable React prototype in {output_path} based on PRD.md, spec file, and a local React template folder.

## Input Requirements:
- **PRD.md**: Product Requirements Document at {prd_path}
- **Spec file**: Technical specification at {spec_path}  
- **Template folder**: Local React template at {template_path}

## Output Requirements:
- **Runnable React prototype** in {output_path} directory
- **Template source directory remains unchanged**

## 1) Template Analysis (Read-First Approach)
Before generating anything, thoroughly analyze the template at {template_path}:
- Read `README.md`, `package.json` (scripts, dependencies), `eslint.config.*`, `tsconfig*.json`, `components.json`
- Examine existing code under `src/` to understand:
  - **Component conventions** (naming, export patterns, folder structure)
  - **Styling approach** (Tailwind/CSS Modules/vanilla CSS)
  - **TypeScript patterns** and lint rules
  - **Import/export patterns** and file organization

## 2) Requirements Analysis
- Read the PRD at {prd_path} to understand user needs
- Read the spec file at {spec_path} to extract:
  - Screens/pages, forms, lists/tables, detail views
  - Navigation flow and UI states (empty/loading/error)
  - Reusable elements (buttons, inputs, cards, modals, badges, etc.)
  - Data models and validation requirements

## 3) UI Design Planning
Create a comprehensive `ui_design.md` plan in {output_path} including:
- **Component hierarchy** (atoms → molecules → organisms/pages)
- **TypeScript interfaces** for all component props
- **Routing structure** and navigation patterns
- **State management** approach (local state, props drilling)
- **Accessibility considerations** (ARIA, keyboard navigation, contrast)
- **Responsive design** strategy (mobile-first approach)
- **Styling strategy** aligned with template (no new dependencies)

## 4) Template Processing and File Generation
- Use `ensure_dir()` to create the target UI directory structure at {output_path}
- Use `copy_from_template()` to copy base template files from {template_path} to {output_path}
- Use `render_placeholders()` to replace template placeholders with app-specific values
- Use `write_files()` to generate multiple component files efficiently
- Use `apply_patches()` for targeted modifications to existing files

## 5) Component Implementation
Generate **presentational, prop-driven components** that:
- Follow the template's coding style and conventions
- Are **small, cohesive, and reusable**
- Use **TypeScript interfaces** for all props
- Include **placeholder data** for layout demonstration
- Handle **empty/loading/error states** appropriately
- Are **responsive and accessible**

## 6) Quality Assurance
- Use `basic_check()` to validate the generated UI at {output_path}
- Ensure all components follow TypeScript and ESLint rules
- Verify responsive design works across different screen sizes
- Test keyboard navigation and accessibility features

## 7) File Organization
Structure the generated files in {output_path} as:
```
{output_path}/
├── package.json (copied from template)
├── src/
│   ├── components/
│   │   ├── ui/ (base UI components)
│   │   ├── atoms/ (smallest components)
│   │   ├── molecules/ (composed components)
│   │   └── organisms/ (complex components)
│   ├── pages/ (main page components)
│   ├── types/ (TypeScript interfaces)
│   ├── App.tsx (main app component)
│   └── main.tsx (entry point)
├── public/ (static assets)
└── ui_design.md (design documentation)
```

## 8) Constraints and Guidelines
- **DO NOT** modify build configs, lint configs, or package dependencies
- **DO NOT** implement business logic or data fetching
- **DO NOT** add new dependencies beyond what's in the template
- **DO** respect the template's existing patterns and conventions
- **DO** create modular, reusable components
- **DO** ensure the prototype is runnable with `npm run dev`

## 9) Deliverables Checklist
- [ ] `ui_design.md` with comprehensive design plan
- [ ] Runnable React prototype in {output_path}
- [ ] All components are TypeScript-typed and prop-driven
- [ ] Responsive design works on mobile and desktop
- [ ] Accessibility features implemented
- [ ] Template source directory remains unchanged
- [ ] No new dependencies added
- [ ] Code passes TypeScript and ESLint checks

## 10) App-Specific Configuration
- App Name: {app_name}
- Replace all template placeholders with {app_name} where appropriate
- Ensure the generated app reflects the specific requirements from the PRD and spec
- Make the UI prototype immediately runnable and testable
"""
        
        try:
            # Run the UI generation task
            result = self.agent.run(ui_task)
            
            # Perform basic validation
            validation_result = self._validate_generated_ui(output_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'app_name': app_name,
                'validation': validation_result,
                'message': f"Successfully generated UI prototype for {app_name} at {output_path}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output_path': output_path,
                'app_name': app_name,
                'message': f"Failed to generate UI prototype for {app_name}: {str(e)}"
            }
    
    def _validate_generated_ui(self, output_path: str) -> Dict[str, Any]:
        """
        Validate the generated UI prototype.
        
        Args:
            output_path: Path to the generated UI directory
            
        Returns:
            Validation results dictionary
        """
        try:
            # Use the basic_check tool to validate the UI
            check_result = basic_check(output_path)
            validation_data = json.loads(check_result)
            
            return {
                'valid': len(validation_data.get('errors', [])) == 0,
                'errors': validation_data.get('errors', []),
                'warnings': validation_data.get('warnings', []),
                'checks': validation_data.get('checks', {}),
                'timestamp': validation_data.get('timestamp')
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Validation failed: {str(e)}",
                'errors': [str(e)],
                'warnings': [],
                'checks': {}
            }
    
    def discover_app_folders(self, base_path: str = "Multiple_Agents_Simulation") -> list:
        """
        Discover app folders that contain PRD.md and spec files.
        
        Args:
            base_path: Base directory to search for app folders
            
        Returns:
            List of app folder paths that have both PRD.md and spec files
        """
        try:
            base_dir = Path(base_path)
            if not base_dir.exists():
                return []
            
            app_folders = []
            for item in base_dir.iterdir():
                if item.is_dir():
                    prd_file = item / "PRD.md"
                    spec_json = item / "app_spec.json"
                    spec_md = item / "spec.md"
                    
                    # Check if PRD.md exists and at least one spec file exists
                    if prd_file.exists() and (spec_json.exists() or spec_md.exists()):
                        app_folders.append(str(item))
            
            return sorted(app_folders)
            
        except Exception as e:
            print(f"Error discovering app folders: {e}")
            return []
    
    def get_app_info(self, app_folder_path: str) -> Dict[str, Any]:
        """
        Get information about an app folder including PRD and spec details.
        
        Args:
            app_folder_path: Path to the app folder
            
        Returns:
            Dictionary with app information
        """
        try:
            app_dir = Path(app_folder_path)
            prd_path = app_dir / "PRD.md"
            spec_json_path = app_dir / "app_spec.json"
            spec_md_path = app_dir / "spec.md"
            
            # Determine which spec file to use
            spec_path = None
            spec_type = None
            if spec_md_path.exists():
                spec_path = spec_md_path
                spec_type = "markdown"
            elif spec_json_path.exists():
                spec_path = spec_json_path
                spec_type = "json"
            
            # Read PRD content
            prd_content = ""
            if prd_path.exists():
                with open(prd_path, 'r', encoding='utf-8') as f:
                    prd_content = f.read()
            
            # Read spec content
            spec_content = ""
            spec_data = {}
            if spec_path and spec_path.exists():
                with open(spec_path, 'r', encoding='utf-8') as f:
                    spec_content = f.read()
                
                if spec_type == "json":
                    try:
                        spec_data = json.loads(spec_content)
                    except json.JSONDecodeError:
                        spec_data = {}
            
            # Extract app name
            app_name = app_dir.name
            if spec_data:
                app_name = spec_data.get('app_name', spec_data.get('display_name', app_name))
            
            return {
                'app_folder_path': str(app_dir),
                'app_name': app_name,
                'prd_path': str(prd_path),
                'spec_path': str(spec_path) if spec_path else None,
                'spec_type': spec_type,
                'prd_exists': prd_path.exists(),
                'spec_exists': spec_path is not None and spec_path.exists(),
                'ui_output_path': str(app_dir / "ui"),
                'prd_content': prd_content,
                'spec_content': spec_content,
                'spec_data': spec_data
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get app info: {str(e)}",
                'app_folder_path': app_folder_path
            }
    
    def list_available_templates(self, templates_dir: str = "templates") -> list:
        """
        List available React templates.
        
        Args:
            templates_dir: Directory containing templates
            
        Returns:
            List of available template names
        """
        try:
            templates_path = Path(templates_dir)
            if not templates_path.exists():
                return []
            
            templates = []
            for item in templates_path.iterdir():
                if item.is_dir() and (item / "package.json").exists():
                    templates.append(item.name)
            
            return sorted(templates)
            
        except Exception as e:
            print(f"Error listing templates: {e}")
            return []
    
    def get_template_info(self, template_path: str) -> Dict[str, Any]:
        """
        Get information about a specific template.
        
        Args:
            template_path: Path to the template directory
            
        Returns:
            Template information dictionary
        """
        try:
            template_dir = Path(template_path)
            
            # Read package.json
            package_json_path = template_dir / "package.json"
            if package_json_path.exists():
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
            else:
                package_data = {}
            
            # Read README.md
            readme_path = template_dir / "README.md"
            readme_content = ""
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
            
            # List source files
            src_dir = template_dir / "src"
            source_files = []
            if src_dir.exists():
                for file_path in src_dir.rglob("*.tsx"):
                    source_files.append(str(file_path.relative_to(template_dir)))
                for file_path in src_dir.rglob("*.ts"):
                    source_files.append(str(file_path.relative_to(template_dir)))
            
            return {
                'name': package_data.get('name', template_dir.name),
                'version': package_data.get('version', 'unknown'),
                'description': package_data.get('description', ''),
                'dependencies': package_data.get('dependencies', {}),
                'dev_dependencies': package_data.get('devDependencies', {}),
                'scripts': package_data.get('scripts', {}),
                'readme': readme_content,
                'source_files': sorted(source_files),
                'template_path': str(template_dir)
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get template info: {str(e)}",
                'template_path': template_path
            }


def main():
    """Example usage of the UI Agent."""
    # Initialize the UI Agent
    ui_agent = UIAgent()
    
    print("UI Agent initialized successfully!")
    print("Available templates:", ui_agent.list_available_templates())
    
    # Discover available app folders
    print("\nDiscovering app folders...")
    app_folders = ui_agent.discover_app_folders()
    print(f"Found {len(app_folders)} app folders:")
    for folder in app_folders:
        print(f"  - {folder}")
    
    # Show detailed info for each app
    print("\nApp details:")
    for app_folder in app_folders:
        app_info = ui_agent.get_app_info(app_folder)
        if 'error' not in app_info:
            print(f"\nApp: {app_info['app_name']}")
            print(f"  Folder: {app_info['app_folder_path']}")
            print(f"  PRD exists: {app_info['prd_exists']}")
            print(f"  Spec exists: {app_info['spec_exists']} ({app_info['spec_type']})")
            print(f"  UI output path: {app_info['ui_output_path']}")
        else:
            print(f"Error for {app_folder}: {app_info['error']}")
    
    # Example of generating a UI prototype for the first available app
    if app_folders:
        print(f"\nExample: Generating UI for {app_folders[0]}")
        result = ui_agent.generate_ui_prototype(
            app_folder_path=app_folders[0],
            template_path="templates/react-simple-spa"
        )
        print("Generation result:", result)
    else:
        print("\nNo app folders found with both PRD.md and spec files.")
        print("Make sure you have app folders in Multiple_Agents_Simulation/ with:")
        print("  - PRD.md file")
        print("  - app_spec.json or spec.md file")


if __name__ == "__main__":
    main()
