import shutil
import os
import json
from pathlib import Path
from smolagents import tool
from app_spec import AppSpec


@tool
def generate_app_from_template(
    app_name: str,
    display_name: str,
    description: str,
    author: str = "Developer",
    version: str = "0.1.0",
    template_name: str = "react-simple-spa",
    output_dir: str = "result",
    custom_content: str = None
) -> str:
    """
    Generate complete React app by copying template and setting parameters.
    
    Args:
        app_name: Name of the app (kebab-case, used for directory/package name)
        display_name: Human-readable title for the app
        description: Description of what the app does
        author: Author name (default: "Developer")
        version: App version (default: "0.1.0")
        template_name: Template to use (default: "react-simple-spa")
        output_dir: Where to generate the app (default: "result")
        custom_content: Custom JSX content for App.tsx (optional)
    
    Returns:
        Success message with generated app location
    """
    # Create AppSpec object from parameters
    app_spec = AppSpec(
        app_name=app_name,
        display_name=display_name,
        description=description,
        author=author,
        version=version,
        template_name=template_name,
        output_dir=output_dir,
        custom_content=custom_content
    )
    
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
    
    if not package_json_path.exists():
        return
    
    with open(package_json_path, 'r') as f:
        content = f.read()
    
    # Simple string replacement for package name
    content = content.replace('"react-simple-spa"', f'"{spec.app_name}"')
    content = content.replace('"0.0.0"', f'"{spec.version}"')
    
    # Add description if not exists or update existing
    try:
        # Try to parse as JSON to be more robust
        data = json.loads(content)
        data["description"] = spec.description
        if spec.author:
            data["author"] = spec.author
        
        content = json.dumps(data, indent=2)
    except json.JSONDecodeError:
        # Fallback to string replacement if JSON parsing fails
        if '"description":' not in content:
            content = content.replace(
                '"version":',
                f'"description": "{spec.description}",\n  "version":'
            )
        else:
            # Replace existing description
            import re
            content = re.sub(
                r'"description":\s*"[^"]*"',
                f'"description": "{spec.description}"',
                content
            )
    
    with open(package_json_path, 'w') as f:
        f.write(content)


def _parameterize_index_html(output_path: Path, spec: AppSpec):
    """Replace title in index.html"""
    html_path = output_path / "index.html"
    
    if not html_path.exists():
        return
    
    with open(html_path, 'r') as f:
        content = f.read()
    
    # Replace common title patterns
    title_patterns = [
        '<title>Vite + React + TS</title>',
        '<title>React App</title>',
        '<title>Vite App</title>',
        '<title>React</title>',
    ]
    
    new_title = f'<title>{spec.display_name}</title>'
    
    for pattern in title_patterns:
        if pattern in content:
            content = content.replace(pattern, new_title)
            break
    else:
        # If no pattern found, try to replace any title tag
        import re
        content = re.sub(
            r'<title>[^<]*</title>',
            new_title,
            content
        )
    
    with open(html_path, 'w') as f:
        f.write(content)


def _parameterize_app_tsx(output_path: Path, spec: AppSpec):
    """Replace content in App.tsx if custom_content provided"""
    app_tsx_path = output_path / "src" / "App.tsx"
    
    if not app_tsx_path.exists():
        return
    
    with open(app_tsx_path, 'r') as f:
        content = f.read()
    
    # Look for the main content div and replace it
    old_content_patterns = [
        # Current template pattern
        '''<div className="flex min-h-svh flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">Hello World</h1>
      <Button>Click me</Button>
    </div>''',
        # Alternative patterns
        '''<div className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">Hello World</h1>
      <Button>Click me</Button>
    </div>''',
    ]
    
    new_content = f'''<div className="flex min-h-svh flex-col items-center justify-center">
      {spec.custom_content}
    </div>'''
    
    for old_pattern in old_content_patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_content)
            break
    else:
        # If no exact pattern found, try to find and replace the main div
        import re
        # Look for a div with min-h- class that contains content
        pattern = r'<div className="[^"]*min-h-[^"]*"[^>]*>.*?</div>'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content.replace(match.group(0), new_content)
    
    with open(app_tsx_path, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    # Example usage
    app_spec = AppSpec(
        app_name="test-todo-app",
        display_name="Test Todo App",
        description="A test todo management application",
        author="Developer",
        custom_content='''<h1 className="text-4xl font-bold">Todo App</h1>
      <p className="text-gray-600">Manage your tasks efficiently</p>
      <Button>Get Started</Button>'''
    )
    
    result = generate_app_from_template(app_spec)
    print(result)