import os
from pathlib import Path
from typing import Optional
from smolagents import tool
import subprocess
import json
from openai import OpenAI

@tool
# Reads and returns the content of a file in the current directory or subdirectories.
def read_file(filepath: str) -> str:
    """
    Reads the content of a file in the current directory or subdirectories.

    Args:
        filepath: Path to the file relative to current directory (e.g., 'data.txt' or 'folder/data.txt')

    Returns:
        The content of the file as a string
    """
    # Resolve the path and ensure it's within current directory
    # Get current working directory
    current_dir = Path.cwd()
    # Convert the filepath to an absolute path, normalizing it to prevent directory traversal attacks
    target_path = (current_dir / filepath).resolve()

    # 小提示（改进点）：用字符串的 startswith 有边界问题，比如："/home/me/project2" 会被认为以 "/home/me/project" 开头（其实并不在同一目录树下）。
    # Security check: ensure the resolved path is within current directory
    # Check if the resolved path starts with the current directory path, preventing access to files outside the current directory
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{filepath}' is outside current directory")

    # Existing check: Check if the file exists
    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Type check: check if the path is a file
    if not target_path.is_file():
        raise ValueError(f"Path is not a file: {filepath}")

    # Read the file content (Read only if the file exists and is a regular file)
    with open(target_path, 'r', encoding='utf-8') as f:
        return f.read()


@tool
# Writes or appends content to a file in the current directory or subdirectories.
def write_file(filepath: str, content: str, mode: Optional[str] = 'w') -> str:
    """
    Writes content to a file in the current directory or subdirectories.
    Creates parent directories if they don't exist.

    Args:
        filepath: Path to the file relative to current directory (e.g., 'output.txt' or 'results/output.txt')
        content: The content to write to the file
        mode: Write mode - 'w' for overwrite (default) or 'a' for append

    Returns:
        Success message with the file path
    """
    # Only allow 'w' (write/overwrite) or 'a' (append) modes
    if mode not in ['w', 'a']:
        raise ValueError("Mode must be 'w' (write/overwrite) or 'a' (append)")

    # Resolve the path and ensure it's within current directory
    current_dir = Path.cwd()
    target_path = (current_dir / filepath).resolve() # Absolute path

    # Security check: ensure the resolved path is within current directory
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{filepath}' is outside current directory")

    # Create parent directories if they don't exist
    # 在保存文件前，自动把存放它的各级文件夹都建好，而且不怕重复建。
    # 这行代码本身并不知道你要存放哪个文件。它是通过 target_path 变量知道了文件的最终绝对路径，然后通过 .parent 反向推导出这个文件需要被存放在哪个文件夹里，最后再执行创建文件夹的命令。
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the content to the file
    with open(target_path, mode, encoding='utf-8') as f:
        f.write(content)

    action = "written to" if mode == 'w' else "appended to"
    return f"Successfully {action} file: {filepath}"


@tool
# 列出某个目录下的文件，可以使用通配符模式筛选
def list_files(directory: Optional[str] = '.', pattern: Optional[str] = '*') -> str:
    """
    Lists files in the specified directory within the current working directory.

    Args:
        directory: Directory path relative to current directory (default: '.')
        pattern: Glob pattern for filtering files (default: '*' for all files)

    Returns:
        A formatted string listing all matching files
    """
    # Resolve the path and ensure it's within current directory
    current_dir = Path.cwd()
    target_dir = (current_dir / directory).resolve()

    # Security check: ensure the resolved path is within current directory
    if not str(target_dir).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{directory}' is outside current directory")

    # Existing check: Check if the directory exists
    if not target_dir.exists():
        # Special case for ui directory - provide helpful guidance
        if directory == "ui" or directory.endswith("/ui") or directory.endswith("\\ui"):
            raise FileNotFoundError(f"Directory not found: {directory}. If you're trying to access the ui/ folder, make sure to run copy_template_to_ui_folder() first to create it.")
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Type check: check if the path is a directory
    if not target_dir.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    # Find all matching files
    files = list(target_dir.glob(pattern))

    # If no files match the pattern, return a message
    if not files:
        return f"No files matching pattern '{pattern}' in {directory}"

    # Format the file list
    file_list = []
    for file in sorted(files):
        if file.is_file():
            relative_path = file.relative_to(current_dir)
            # stat stands for status, and st stands for struct
            size = file.stat().st_size
            # "  - data\file.txt (123 bytes)"
            # \n usage
            file_list.append(f"  - {relative_path} ({size} bytes)")

    return f"Files in {directory}:\n" + "\n".join(file_list)


@tool
# 创建目录，可选递归创建父目录
def mkdir(directory: str, parents: Optional[bool] = True, exist_ok: Optional[bool] = True) -> str:
    """
    Creates a directory within the current working directory.

    Args:
        directory: Directory path relative to current directory (e.g., 'data' or 'output/results')
        parents: If True, create parent directories as needed (default: True)
        exist_ok: If True, don't raise error if directory already exists (default: True)

    Returns:
        Success message with the created directory path
    """
    # Resolve the path and ensure it's within current directory
    current_dir = Path.cwd()
    target_dir = (current_dir / directory).resolve()

    # Security check: ensure the resolved path is within current directory
    if not str(target_dir).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{directory}' is outside current directory")

    # Check if directory already exists
    if target_dir.exists():
        if not exist_ok:
            raise FileExistsError(f"Directory already exists: {directory}")
        if not target_dir.is_dir():
            raise ValueError(f"Path exists but is not a directory: {directory}")
        return f"Directory already exists: {directory}"

    # Create the directory
    try:
        target_dir.mkdir(parents=parents, exist_ok=exist_ok)
        return f"Successfully created directory: {directory}"
    except FileNotFoundError:
        if not parents:
            raise FileNotFoundError(f"Parent directory doesn't exist. Set parents=True to create parent directories: {directory}")
        raise

@tool
# Generate AppSpec from user requirements
def build_app_spec_from_docs(user_req_path: str, out_path: str) -> str:
    """
    Build an AppSpec JSON from a markdown file.

    Args:
        user_req_path: Path (string) to Project Requirements Document (PRD.md)
        out_path: Path (string) to write spec/app_spec.json

    Returns:
        A message containing the absolute path to the written JSON file.
    """
    client = OpenAI()  # Use env variable 
    user_req = Path(user_req_path).read_text(encoding="utf-8")

    system = (
        "You convert the given user requirements into a valid AppSpec JSON. "
        "Be strict with types. If a field is missing, infer safe defaults. "
        "IMPORTANT: Generate ONLY the simple flat AppSpec format, NOT a complex nested structure. "
        "CRITICAL: Return ONLY valid JSON, no markdown formatting, no code blocks, no explanations."
    )
    user = f"""
        [PRD_MD]
        {user_req}

        [OUTPUT_SCHEMA]
        Produce an AppSpec with EXACTLY these fields (simple flat structure):
        - app_name (string, kebab-case, required)
        - display_name (string, human-readable title, required)  
        - description (string, brief description, required)
        - author (string, optional, can be null)
        - version (string, optional, default: "0.1.0")
        - template_name (string, default: "bare-bones-vanilla-main")
        - output_dir (string, default: "result")
        - custom_content (string, optional JSX content, can be null)
        - features (array of strings, extract key features from requirements)

        DO NOT include complex nested sections like "metadata", "overview", "functional_requirements", etc.
        Generate ONLY the simple flat structure shown above.
        
        IMPORTANT: Return ONLY the JSON object, no markdown, no code blocks, no explanations.
        Start with {{ and end with }}.
        """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=0.1
    )

    # Guard against None content
    raw_content = getattr(resp.choices[0].message, 'content', None)
    if raw_content is None:
        raise ValueError("Empty response from OpenAI API (no content)")

    spec_json = raw_content.strip()
    
    # Debug: Print the raw response to help identify issues
    print(f"DEBUG: Raw API response length: {len(spec_json)}")
    print(f"DEBUG: Raw API response content: {repr(spec_json[:200])}...")
    
    # Parse and validate the JSON
    try:
        spec_data = json.loads(spec_json)
    except json.JSONDecodeError as e:
        print(f"DEBUG: Failed to parse JSON. Raw content: {repr(spec_json)}")
        
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', spec_json, re.DOTALL)
        if json_match:
            try:
                spec_data = json.loads(json_match.group(1))
                print("DEBUG: Successfully extracted JSON from markdown code block")
            except json.JSONDecodeError as e2:
                print(f"DEBUG: Failed to parse extracted JSON: {e2}")
                raise ValueError(f"Failed to parse JSON response: {e}")
        else:
            raise ValueError(f"Failed to parse JSON response: {e}")
    
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(spec_data, indent=2), encoding="utf-8")
    return f"Successfully built AppSpec: {out_file}"


@tool
def get_user_feedback(question_for_user: str) -> str:
    """
    Get user feedback on the app.

    Args:
        question_for_user: The question to ask the user

    Returns:
        The user's feedback as a string
    """
    print(question_for_user)
    response = input("Enter your response: ")
    return response


# UI Agent Tools for template-based React UI generation

@tool
def ensure_dir(directory: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path relative to current directory
        
    Returns:
        Success message with the directory path
    """
    return mkdir(directory, parents=True, exist_ok=True)

@tool
def copy_from_template(template_path: str, target_path: str, source_file: str) -> str:
    """
    Copy a file from the template directory to the target location.
    
    Args:
        template_path: Path to the template directory
        target_path: Target directory path relative to current directory
        source_file: Source file path relative to template directory
        
    Returns:
        Success message with the copied file path
    """
    current_dir = Path.cwd()
    template_dir = (current_dir / template_path).resolve()
    target_dir = (current_dir / target_path).resolve()
    
    # Security check: ensure template path is within current directory
    if not str(template_dir).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Template path '{template_path}' is outside current directory")
    
    # Security check: ensure target path is within current directory
    if not str(target_dir).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Target path '{target_path}' is outside current directory")
    
    source_path = template_dir / source_file
    dest_path = target_dir / source_file
    
    if not source_path.exists():
        raise FileNotFoundError(f"Template file not found: {source_file}")
    
    # Create target directory if it doesn't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy the file
    import shutil
    shutil.copy2(source_path, dest_path)
    
    return f"Successfully copied {source_file} from template to {target_path}"

@tool
def render_placeholders(file_path: str, replacements: str) -> str:
    """
    Replace placeholders in a file with actual values.
    
    Args:
        file_path: Path to the file to modify
        replacements: JSON string containing placeholder replacements
        
    Returns:
        Success message
    """
    import json
    
    current_dir = Path.cwd()
    target_path = (current_dir / file_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{file_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Parse replacements
    try:
        replacements_dict = json.loads(replacements)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in replacements: {e}")
    
    # Read file content
    with open(target_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply replacements
    for placeholder, value in replacements_dict.items():
        content = content.replace(placeholder, str(value))
    
    # Write back to file
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return f"Successfully applied {len(replacements_dict)} placeholder replacements to {file_path}"

@tool
def write_files(files_data: str) -> str:
    """
    Write multiple files at once.
    
    Args:
        files_data: JSON string containing file paths and their contents
        
    Returns:
        Success message with count of files written
    """
    import json
    
    try:
        files_dict = json.loads(files_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in files_data: {e}")
    
    written_count = 0
    for file_path, content in files_dict.items():
        write_file(file_path, content)
        written_count += 1
    
    return f"Successfully wrote {written_count} files"

@tool
def apply_patches(file_path: str, patches: str) -> str:
    """
    Apply patches to a file using anchor-based insertions.
    
    Args:
        file_path: Path to the file to patch
        patches: JSON string containing patch operations
        
    Returns:
        Success message with patch results
    """
    import json
    
    current_dir = Path.cwd()
    target_path = (current_dir / file_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{file_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        patches_list = json.loads(patches)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in patches: {e}")
    
    # Read file content
    with open(target_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    applied_patches = 0
    failed_patches = []
    
    for patch in patches_list:
        try:
            anchor = patch.get('anchor')
            content = patch.get('content')
            operation = patch.get('operation', 'insert_after')  # insert_after, insert_before, replace
            
            if not anchor or content is None:
                failed_patches.append(f"Invalid patch: missing anchor or content")
                continue
            
            # Find anchor line
            anchor_found = False
            for i, line in enumerate(lines):
                if anchor in line:
                    anchor_found = True
                    if operation == 'insert_after':
                        lines.insert(i + 1, content + '\n')
                    elif operation == 'insert_before':
                        lines.insert(i, content + '\n')
                    elif operation == 'replace':
                        lines[i] = content + '\n'
                    applied_patches += 1
                    break
            
            if not anchor_found:
                failed_patches.append(f"Anchor '{anchor}' not found")
                
        except Exception as e:
            failed_patches.append(f"Patch failed: {str(e)}")
    
    # Write back to file
    with open(target_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    result = f"Applied {applied_patches} patches to {file_path}"
    if failed_patches:
        result += f". Failed patches: {'; '.join(failed_patches)}"
    
    return result

@tool
def write_manifest(manifest_path: str, manifest_data: str) -> str:
    """
    Write or update the UI manifest file.
    
    Args:
        manifest_path: Path to the manifest file
        manifest_data: JSON string containing manifest data
        
    Returns:
        Success message
    """
    import json
    from datetime import datetime
    
    try:
        manifest_dict = json.loads(manifest_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest_data: {e}")
    
    # Add timestamp
    manifest_dict['generated_at'] = datetime.now().isoformat()
    
    # Write manifest file
    write_file(manifest_path, json.dumps(manifest_dict, indent=2))
    
    return f"Successfully wrote manifest to {manifest_path}"

@tool
def basic_check(check_path: str) -> str:
    """
    Perform basic syntax/lint check on the generated UI.
    
    Args:
        check_path: Path to the UI directory to check
        
    Returns:
        Check report as JSON string
    """
    import json
    import subprocess
    from pathlib import Path
    
    current_dir = Path.cwd()
    target_path = (current_dir / check_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{check_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"Directory not found: {check_path}")
    
    from datetime import datetime
    report = {
        'timestamp': datetime.now().isoformat(),
        'directory': str(target_path),
        'checks': {},
        'errors': [],
        'warnings': []
    }
    
    # Check for package.json
    package_json = target_path / 'package.json'
    if package_json.exists():
        report['checks']['package_json'] = 'found'
    else:
        report['errors'].append('package.json not found')
    
    # Check for main entry files
    main_files = ['src/main.tsx', 'src/App.tsx', 'index.html']
    for file in main_files:
        file_path = target_path / file
        if file_path.exists():
            report['checks'][file] = 'found'
        else:
            report['warnings'].append(f'{file} not found')
    
    # Try to run TypeScript check if tsc is available
    try:
        result = subprocess.run(
            ['npx', 'tsc', '--noEmit'],
            cwd=target_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            report['checks']['typescript'] = 'passed'
        else:
            report['errors'].append(f'TypeScript errors: {result.stderr}')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        report['warnings'].append('TypeScript check skipped (tsc not available)')
    
    # Try to run ESLint if available
    try:
        result = subprocess.run(
            ['npx', 'eslint', 'src/'],
            cwd=target_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            report['checks']['eslint'] = 'passed'
        else:
            report['warnings'].append(f'ESLint warnings: {result.stdout}')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        report['warnings'].append('ESLint check skipped (eslint not available)')
    
    # Write check report
    check_report_path = target_path / 'check_report.json'
    with open(check_report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    return json.dumps(report, indent=2)

@tool
def save_ui_file(file_path: str, content: str) -> str:
    """
    Save a file in the UI directory, enforcing UI-only writes.
    
    Args:
        file_path: File path relative to UI directory
        content: File content
        
    Returns:
        Success message
    """
    # Ensure the file path is within a UI directory
    if not file_path.startswith('ui/'):
        raise ValueError("UI files must be saved under the 'ui/' directory")
    
    return write_file(file_path, content)

# Code Agent Tools for implementing functionality from UI prototypes

@tool
def analyze_ui_structure(ui_path: str) -> str:
    """
    Analyze the structure of a UI prototype to understand components and their relationships.
    
    Args:
        ui_path: Path to the UI directory (e.g., 'generated_app/BlueToDo/ui')
        
    Returns:
        JSON string containing UI structure analysis
    """
    import json
    from pathlib import Path
    
    current_dir = Path.cwd()
    target_path = (current_dir / ui_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{ui_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"UI directory not found: {ui_path}")
    
    analysis = {
        'ui_path': str(target_path),
        'components': [],
        'pages': [],
        'types': [],
        'hooks': [],
        'utils': [],
        'package_info': {},
        'structure': {}
    }
    
    # Analyze package.json
    package_json = target_path / 'package.json'
    if package_json.exists():
        with open(package_json, 'r', encoding='utf-8') as f:
            analysis['package_info'] = json.load(f)
    
    # Analyze src directory structure
    src_dir = target_path / 'src'
    if src_dir.exists():
        # Find all TypeScript/TSX files using separate patterns (the combined pattern doesn't work reliably)
        ts_files = list(src_dir.rglob('*.ts'))
        tsx_files = list(src_dir.rglob('*.tsx'))
        all_files = ts_files + tsx_files
        
        for file_path in all_files:
            relative_path = str(file_path.relative_to(target_path))
            file_type = 'unknown'
            
            # Determine file type based on path and content
            if 'components' in relative_path:
                file_type = 'component'
            elif 'pages' in relative_path:
                file_type = 'page'
            elif 'types' in relative_path or file_path.name == 'types.ts':
                file_type = 'types'
            elif 'hooks' in relative_path:
                file_type = 'hook'
            elif 'utils' in relative_path or 'lib' in relative_path:
                file_type = 'utility'
            elif file_path.suffix == '.tsx':
                # Default TSX files to component if not otherwise categorized
                file_type = 'component'
            
            file_info = {
                'path': relative_path,
                'type': file_type,
                'name': file_path.stem,
                'size': file_path.stat().st_size
            }
            
            # Read file content for basic analysis
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_info['has_exports'] = 'export' in content
                    file_info['has_imports'] = 'import' in content
                    file_info['has_interfaces'] = 'interface' in content
                    file_info['has_props'] = 'Props' in content or 'props:' in content
                    file_info['has_state'] = 'useState' in content or 'useEffect' in content
                    file_info['lines_of_code'] = len(content.splitlines())
            except Exception as e:
                file_info['read_error'] = str(e)
            
            if file_type == 'component':
                analysis['components'].append(file_info)
            elif file_type == 'page':
                analysis['pages'].append(file_info)
            elif file_type == 'types':
                analysis['types'].append(file_info)
            elif file_type == 'hook':
                analysis['hooks'].append(file_info)
            elif file_type == 'utility':
                analysis['utils'].append(file_info)
    
    # Analyze directory structure
    def analyze_dir_structure(dir_path: Path, prefix: str = ''):
        structure = {}
        for item in dir_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure[item.name] = analyze_dir_structure(item, f"{prefix}{item.name}/")
            elif item.is_file() and item.suffix in ['.ts', '.tsx', '.js', '.jsx']:
                structure[item.name] = 'file'
        return structure
    
    if src_dir.exists():
        analysis['structure'] = analyze_dir_structure(src_dir)
    
    return json.dumps(analysis, indent=2)

@tool
def generate_ui_structure_json(ui_path: str) -> str:
    """
    Generate a comprehensive UI_STRUCTURE.json file that describes the entire UI tree structure.
    This file will be read by the Code Agent to understand the UI layout, routes, components, 
    states, and file relations without scanning source code.
    
    Args:
        ui_path: Path to the UI directory (e.g., 'generated_app/BlueToDo/ui')
        
    Returns:
        Success message with the path to the generated UI_STRUCTURE.json file
    """
    import json
    import re
    from pathlib import Path
    
    current_dir = Path.cwd()
    target_path = (current_dir / ui_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{ui_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"UI directory not found: {ui_path}. Please ensure you have copied the template to the ui/ folder using copy_template_to_ui_folder() first.")
    
    # Initialize the structure
    structure = {
        "appName": "",
        "version": "1.0.0",
        "rootDir": "ui/",
        "routes": [],
        "components": [],
        "stateManagement": {"pattern": "unknown", "stores": []},
        "apiClients": [],
        "styles": {"system": "unknown", "files": []},
        "assets": [],
        "files": []
    }
    
    # Get app name from package.json
    package_json = target_path / 'package.json'
    if package_json.exists():
        with open(package_json, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
            structure["appName"] = package_data.get("name", "UnknownApp")
            structure["version"] = package_data.get("version", "1.0.0")
    
    # Check if this is a React/TypeScript project or vanilla HTML/CSS/JS project
    src_dir = target_path / 'src'
    package_json = target_path / 'package.json'
    
    if src_dir.exists() and package_json.exists():
        # React/TypeScript project - analyze src directory
        # Find all TypeScript/TSX files
        ts_files = list(src_dir.rglob('*.ts'))
        tsx_files = list(src_dir.rglob('*.tsx'))
        all_files = ts_files + tsx_files
    else:
        # Vanilla HTML/CSS/JS project - analyze files directly in ui directory
        # Find all HTML, CSS, and JS files
        html_files = list(target_path.rglob('*.html'))
        css_files = list(target_path.rglob('*.css'))
        js_files = list(target_path.rglob('*.js'))
        all_files = html_files + css_files + js_files
    
    # Analyze each file
    for file_path in all_files:
        relative_path = str(file_path.relative_to(target_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                
                # Basic file info
                file_info = {
                    "path": relative_path,
                    "lines": len(lines)
                }
                structure["files"].append(file_info)
                
                # Determine file type and analyze accordingly
                if file_path.suffix == '.tsx':
                    analyze_component_file(file_path, content, structure, target_path)
                elif file_path.suffix == '.ts':
                    analyze_typescript_file(file_path, content, structure, target_path)
                elif file_path.suffix == '.html':
                    analyze_html_file(file_path, content, structure, target_path)
                elif file_path.suffix == '.css':
                    # CSS files are already handled by analyze_styles, just add to files list
                    pass
                elif file_path.suffix == '.js':
                    analyze_js_file(file_path, content, structure, target_path)
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    # Analyze styles
    analyze_styles(target_path, structure)
    
    # Analyze assets
    analyze_assets(target_path, structure)
    
    # Analyze routing (look for common routing patterns)
    if src_dir.exists() and package_json.exists():
        analyze_routing(src_dir, structure)
        analyze_state_management(src_dir, structure)
    else:
        # For vanilla projects, set basic routing and state management
        structure["routes"] = [{"path": "/", "component": "index.html"}]
        structure["stateManagement"]["pattern"] = "vanilla-js"
    
    # Sort arrays alphabetically for consistency
    structure["components"].sort(key=lambda x: x.get("name", ""))
    structure["routes"].sort(key=lambda x: x.get("path", ""))
    structure["files"].sort(key=lambda x: x.get("path", ""))
    structure["styles"]["files"].sort()
    structure["assets"].sort()
    
    # Write the UI_STRUCTURE.json file
    output_file = target_path / 'UI_STRUCTURE.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    return f"Successfully generated UI_STRUCTURE.json at {output_file}"

@tool
def read_ui_structure_json(ui_path: str) -> str:
    """
    Read and return the UI_STRUCTURE.json file that contains the complete UI metadata.
    This file is generated by the UI agent and contains structured information about
    components, routes, state management, and file organization.
    
    Args:
        ui_path: Path to the UI directory (e.g., 'generated_app/BlueToDo/ui')
        
    Returns:
        JSON string containing the complete UI structure metadata
    """
    import json
    from pathlib import Path
    
    current_dir = Path.cwd()
    target_path = (current_dir / ui_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{ui_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"UI directory not found: {ui_path}. Please ensure you have copied the template to the ui/ folder using copy_template_to_ui_folder() first.")
    
    # Look for UI_STRUCTURE.json file
    ui_structure_file = target_path / 'UI_STRUCTURE.json'
    
    if not ui_structure_file.exists():
        return f"Error: UI_STRUCTURE.json not found in {ui_path}. This file should be generated by the UI agent first."
    
    try:
        with open(ui_structure_file, 'r', encoding='utf-8') as f:
            ui_structure = json.load(f)
        
        return json.dumps(ui_structure, indent=2, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in UI_STRUCTURE.json - {str(e)}"
    except Exception as e:
        return f"Error reading UI_STRUCTURE.json: {str(e)}"

def analyze_component_file(file_path: Path, content: str, structure: dict, target_path: Path):
    """Analyze a React component file and extract metadata."""
    import re
    
    relative_path = str(file_path.relative_to(target_path))
    component_name = file_path.stem
    
    # Extract props from interface definitions
    props = []
    props_match = re.findall(r'interface\s+(\w+Props)\s*\{([^}]+)\}', content, re.DOTALL)
    for interface_name, props_content in props_match:
        prop_matches = re.findall(r'(\w+)(?:\?)?\s*:\s*([^;,\n]+)', props_content)
        props.extend([prop[0] for prop in prop_matches])
    
    # Extract state hooks
    state = []
    state_matches = re.findall(r'useState<([^>]+)>\(', content)
    state.extend(state_matches)
    
    # Extract event handlers
    events = []
    event_matches = re.findall(r'(on\w+)\s*[:=]', content)
    events.extend(event_matches)
    
    # Extract imports
    imports = []
    import_matches = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
    imports.extend(import_matches)
    
    # Determine component type
    component_type = "page" if "pages" in relative_path else "component"
    
    component_info = {
        "name": component_name,
        "path": relative_path,
        "type": component_type,
        "props": sorted(list(set(props))),
        "state": sorted(list(set(state))),
        "events": sorted(list(set(events))),
        "imports": sorted(list(set(imports)))
    }
    
    structure["components"].append(component_info)

def analyze_typescript_file(file_path: Path, content: str, structure: dict, target_path: Path):
    """Analyze a TypeScript file (types, hooks, utils)."""
    import re
    
    relative_path = str(file_path.relative_to(target_path))
    
    # Check if it's a types file
    if 'types' in relative_path or file_path.name == 'types.ts':
        # Extract interface definitions
        interfaces = re.findall(r'interface\s+(\w+)', content)
        # Extract type definitions
        types = re.findall(r'type\s+(\w+)', content)
        
        # Add to components as type definitions
        for interface_name in interfaces:
            structure["components"].append({
                "name": interface_name,
                "path": relative_path,
                "type": "interface",
                "props": [],
                "state": [],
                "events": [],
                "imports": []
            })

def analyze_html_file(file_path: Path, content: str, structure: dict, target_path: Path):
    """Analyze an HTML file and extract component information."""
    import re
    
    relative_path = str(file_path.relative_to(target_path))
    
    # Extract data-component attributes to identify components
    components = re.findall(r'data-component="([^"]+)"', content)
    
    # Extract IDs to identify main sections
    ids = re.findall(r'id="([^"]+)"', content)
    
    # Extract script sources to identify JS dependencies
    script_srcs = re.findall(r'<script[^>]*src="([^"]+)"', content)
    
    # Create a main page component
    component_info = {
        "name": file_path.stem.title(),
        "path": relative_path,
        "type": "page",
        "props": [],
        "state": [],
        "events": ["click", "input", "submit", "change"],
        "imports": script_srcs,
        "components": components,
        "sections": ids
    }
    
    structure["components"].append(component_info)

def analyze_js_file(file_path: Path, content: str, structure: dict, target_path: Path):
    """Analyze a JavaScript file and extract function/event information."""
    import re
    
    relative_path = str(file_path.relative_to(target_path))
    
    # Extract function definitions
    functions = re.findall(r'function\s+(\w+)', content)
    arrow_functions = re.findall(r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', content)
    method_definitions = re.findall(r'(\w+)\s*:\s*function', content)
    
    all_functions = functions + arrow_functions + method_definitions
    
    # Extract event listeners
    event_listeners = re.findall(r'addEventListener\s*\(\s*["\']([^"\']+)["\']', content)
    
    # Extract DOM queries
    dom_queries = re.findall(r'(?:document|element)\.(?:querySelector|getElementById|getElementsByClassName)\s*\(\s*["\']([^"\']+)["\']', content)
    
    # Create a module component
    component_info = {
        "name": file_path.stem.title(),
        "path": relative_path,
        "type": "module",
        "props": [],
        "state": [],
        "events": list(set(event_listeners)),
        "imports": [],
        "functions": all_functions,
        "dom_hooks": dom_queries
    }
    
    structure["components"].append(component_info)

def analyze_styles(target_path: Path, structure: dict):
    """Analyze styling approach and files."""
    # Check for common styling files
    style_files = []
    
    # Look for CSS files
    css_files = list(target_path.rglob('*.css'))
    for css_file in css_files:
        style_files.append(str(css_file.relative_to(target_path)))
    
    # Look for Tailwind config
    tailwind_config = target_path / 'tailwind.config.js'
    if tailwind_config.exists():
        structure["styles"]["system"] = "tailwind"
    elif style_files:
        structure["styles"]["system"] = "css"
    else:
        structure["styles"]["system"] = "unknown"
    
    structure["styles"]["files"] = style_files

def analyze_assets(target_path: Path, structure: dict):
    """Analyze asset files."""
    asset_extensions = ['.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp']
    
    for ext in asset_extensions:
        asset_files = list(target_path.rglob(f'*{ext}'))
        for asset_file in asset_files:
            structure["assets"].append(str(asset_file.relative_to(target_path)))

def analyze_routing(src_dir: Path, structure: dict):
    """Analyze routing configuration."""
    import re
    
    # Look for common routing patterns
    routing_files = ['App.tsx', 'main.tsx', 'index.tsx', 'router.tsx', 'routes.tsx']
    
    for routing_file in routing_files:
        file_path = src_dir / routing_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for route definitions
                    route_matches = re.findall(r'path\s*[:=]\s*[\'"]([^\'"]+)[\'"]', content)
                    component_matches = re.findall(r'element\s*[:=]\s*<(\w+)', content)
                    
                    for i, path in enumerate(route_matches):
                        component = component_matches[i] if i < len(component_matches) else "Unknown"
                        structure["routes"].append({
                            "path": path,
                            "component": component,
                            "layout": "default"
                        })
            except Exception as e:
                print(f"Error analyzing routing in {file_path}: {e}")

def analyze_state_management(src_dir: Path, structure: dict):
    """Analyze state management patterns."""
    # Look for state management patterns
    context_files = list(src_dir.rglob('*Context*.tsx'))
    store_files = list(src_dir.rglob('*Store*.ts'))
    redux_files = list(src_dir.rglob('*redux*'))
    
    if redux_files:
        structure["stateManagement"]["pattern"] = "redux"
    elif context_files:
        structure["stateManagement"]["pattern"] = "context"
    elif store_files:
        structure["stateManagement"]["pattern"] = "store"
    else:
        structure["stateManagement"]["pattern"] = "hooks"

@tool
def read_project_requirements(project_path: str) -> str:
    """
    Read and analyze project requirements from PRD.md and app_spec.json.
    
    Args:
        project_path: Path to the project directory (e.g., 'generated_app/BlueToDo')
        
    Returns:
        JSON string containing analyzed requirements
    """
    import json
    from pathlib import Path
    
    current_dir = Path.cwd()
    target_path = (current_dir / project_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{project_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"Project directory not found: {project_path}")
    
    requirements = {
        'project_path': str(target_path),
        'prd_content': '',
        'spec_content': '',
        'spec_data': {},
        'features': [],
        'data_model': {},
        'validation_rules': [],
        'ui_requirements': {},
        'functional_requirements': [],
        'non_functional_requirements': []
    }
    
    # Read PRD.md
    prd_path = target_path / 'PRD.md'
    if prd_path.exists():
        with open(prd_path, 'r', encoding='utf-8') as f:
            requirements['prd_content'] = f.read()
    
    # Read app_spec.json
    spec_path = target_path / 'app_spec.json'
    if spec_path.exists():
        with open(spec_path, 'r', encoding='utf-8') as f:
            requirements['spec_content'] = f.read()
            try:
                requirements['spec_data'] = json.loads(requirements['spec_content'])
            except json.JSONDecodeError as e:
                requirements['spec_parse_error'] = str(e)
    
    # Extract key information from spec
    if requirements['spec_data']:
        requirements['features'] = requirements['spec_data'].get('features', [])
        requirements['app_name'] = requirements['spec_data'].get('app_name', '')
        requirements['display_name'] = requirements['spec_data'].get('display_name', '')
        requirements['description'] = requirements['spec_data'].get('description', '')
    
    return json.dumps(requirements, indent=2)

@tool
def generate_functional_code(ui_path: str, project_path: str, target_component: str) -> str:
    """
    Generate functional code for a specific component based on requirements and UI structure.
    
    Args:
        ui_path: Path to the UI directory
        project_path: Path to the project directory containing requirements
        target_component: Name of the component to generate functional code for
        
    Returns:
        Generated functional code as a string
    """
    from pathlib import Path
    import json
    
    current_dir = Path.cwd()
    ui_target = (current_dir / ui_path).resolve()
    project_target = (current_dir / project_path).resolve()
    
    # Security checks
    if not str(ui_target).startswith(str(current_dir)) or not str(project_target).startswith(str(current_dir)):
        raise ValueError("Access denied: Paths must be within current directory")
    
    # Read requirements
    requirements_str = read_project_requirements(project_path)
    requirements = json.loads(requirements_str)
    
    # Read UI structure
    ui_structure_str = analyze_ui_structure(ui_path)
    ui_structure = json.loads(ui_structure_str)
    
    # Find the target component
    target_component_info = None
    for component in ui_structure.get('components', []):
        if component['name'] == target_component:
            target_component_info = component
            break
    
    if not target_component_info:
        return f"Component '{target_component}' not found in UI structure"
    
    # Generate functional code based on component type and requirements
    component_path = target_component_info['path']
    full_path = ui_target / component_path
    
    if not full_path.exists():
        return f"Component file not found: {component_path}"
    
    # Read existing component code
    with open(full_path, 'r', encoding='utf-8') as f:
        existing_code = f.read()
    
    # This is a placeholder - in a real implementation, you would use AI to generate
    # functional code based on the requirements and existing UI structure
    generated_code = f"""
// Generated functional code for {target_component}
// Based on requirements: {requirements.get('app_name', 'Unknown')}
// Features: {', '.join(requirements.get('features', []))}

{existing_code}

// TODO: Implement actual functionality based on requirements
// - Add state management
// - Implement data persistence
// - Add validation logic
// - Connect to backend if needed
"""
    
    return generated_code

@tool
def implement_data_persistence(ui_path: str, project_path: str) -> str:
    """
    Implement data persistence functionality for the application.
    
    Args:
        ui_path: Path to the UI directory
        project_path: Path to the project directory containing requirements
        
    Returns:
        Implementation status and created files
    """
    from pathlib import Path
    import json
    
    current_dir = Path.cwd()
    ui_target = (current_dir / ui_path).resolve()
    project_target = (current_dir / project_path).resolve()
    
    # Security checks
    if not str(ui_target).startswith(str(current_dir)) or not str(project_target).startswith(str(current_dir)):
        raise ValueError("Access denied: Paths must be within current directory")
    
    # Read requirements
    requirements_str = read_project_requirements(project_path)
    requirements = json.loads(requirements_str)
    
    # Create data persistence utilities
    persistence_code = """
// Data persistence utilities
export class DataPersistence {
  private static storageKey: string;
  
  constructor(appName: string) {
    DataPersistence.storageKey = `${appName}-data`;
  }
  
  static save<T>(data: T): void {
    try {
      localStorage.setItem(DataPersistence.storageKey, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save data:', error);
    }
  }
  
  static load<T>(): T | null {
    try {
      const data = localStorage.getItem(DataPersistence.storageKey);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to load data:', error);
      return null;
    }
  }
  
  static clear(): void {
    try {
      localStorage.removeItem(DataPersistence.storageKey);
    } catch (error) {
      console.error('Failed to clear data:', error);
    }
  }
}
"""
    
    # Check if this is a React/Vite project or vanilla JS project
    main_tsx_path = ui_target / 'src' / 'main.tsx'
    main_js_path = ui_target / 'js' / 'main.js'  # Fixed: Use correct template path
    index_js_path = ui_target / 'index.js'  # Fallback for other templates
    
    if main_tsx_path.exists():
        # React/Vite project - don't modify main.tsx, just return success
        return f"Data persistence skipped for React/Vite project. Use React hooks and localStorage directly in components."
    elif main_js_path.exists():
        # Vanilla JS project - modify js/main.js (bare-bones-vanilla-main template)
        target_file = main_js_path
        file_type = "vanilla JS"
    elif index_js_path.exists():
        # Fallback for other templates that use index.js
        target_file = index_js_path
        file_type = "vanilla JS"
    else:
        return f"Error: Neither src/main.tsx, js/main.js, nor index.js found in {ui_path}. Please ensure the template has been copied correctly."
    
    # Read existing content
    with open(target_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # For vanilla JS projects, just return success - let the implementation agent handle the actual code
    return f"Data persistence foundation ready for {file_type} project. Implementation agent will modify {target_file.relative_to(current_dir)} with complete functionality."

@tool
def implement_state_management(ui_path: str, project_path: str) -> str:
    """
    Implement state management for the application.
    
    Args:
        ui_path: Path to the UI directory
        project_path: Path to the project directory containing requirements
        
    Returns:
        Implementation status and created files
    """
    from pathlib import Path
    import json
    
    current_dir = Path.cwd()
    ui_target = (current_dir / ui_path).resolve()
    project_target = (current_dir / project_path).resolve()
    
    # Security checks
    if not str(ui_target).startswith(str(current_dir)) or not str(project_target).startswith(str(current_dir)):
        raise ValueError("Access denied: Paths must be within current directory")
    
    # Read requirements
    requirements_str = read_project_requirements(project_path)
    requirements = json.loads(requirements_str)
    
    # Check if this is a React/Vite project or vanilla JS project
    main_tsx_path = ui_target / 'src' / 'main.tsx'
    main_js_path = ui_target / 'js' / 'main.js'  # Fixed: Use correct template path
    index_js_path = ui_target / 'index.js'  # Fallback for other templates
    
    if main_tsx_path.exists():
        # React/Vite project - don't modify main.tsx, just return success
        return f"State management skipped for React/Vite project. Use React hooks (useState, useEffect) directly in components."
    elif main_js_path.exists():
        # Vanilla JS project - modify js/main.js (bare-bones-vanilla-main template)
        target_file = main_js_path
        file_type = "vanilla JS"
    elif index_js_path.exists():
        # Fallback for other templates that use index.js
        target_file = index_js_path
        file_type = "vanilla JS"
    else:
        return f"Error: Neither src/main.tsx, js/main.js, nor index.js found in {ui_path}. Please ensure the template has been copied correctly."
    
    # Read existing content
    with open(target_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # For vanilla JS projects, just return success - let the implementation agent handle the actual code
    return f"State management foundation ready for {file_type} project. Implementation agent will modify {target_file.relative_to(current_dir)} with complete functionality."

@tool
def validate_implementation(ui_path: str) -> str:
    """
    Validate the implemented functionality by checking for common issues.
    
    Args:
        ui_path: Path to the UI directory
        
    Returns:
        Validation report as JSON string
    """
    from pathlib import Path
    import json
    import subprocess
    
    current_dir = Path.cwd()
    target_path = (current_dir / ui_path).resolve()
    
    # Security check
    if not str(target_path).startswith(str(current_dir)):
        raise ValueError(f"Access denied: Path '{ui_path}' is outside current directory")
    
    if not target_path.exists():
        raise FileNotFoundError(f"UI directory not found: {ui_path}")
    
    validation_report = {
        'timestamp': str(Path.cwd()),
        'ui_path': str(target_path),
        'checks': {},
        'errors': [],
        'warnings': [],
        'suggestions': []
    }
    
    # Check if package.json exists (optional in vanilla template)
    package_json = target_path / 'package.json'
    if package_json.exists():
        validation_report['checks']['package_json'] = 'found'
    else:
        # Do not fail validation for missing package.json in vanilla JS flow
        validation_report['warnings'].append('package.json not found (ok for vanilla UI)')
    
    # Check for main entry files
    main_files = ['src/main.tsx', 'src/App.tsx', 'index.html']
    for file in main_files:
        file_path = target_path / file
        if file_path.exists():
            validation_report['checks'][file] = 'found'
        else:
            validation_report['warnings'].append(f'{file} not found')
    
    # Check for TypeScript compilation
    try:
        result = subprocess.run(
            ['npx', 'tsc', '--noEmit'],
            cwd=target_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            validation_report['checks']['typescript'] = 'passed'
        else:
            validation_report['errors'].append(f'TypeScript errors: {result.stderr}')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        validation_report['warnings'].append('TypeScript check skipped (tsc not available)')
    
    # Check for functional implementation
    src_dir = target_path / 'src'
    if src_dir.exists():
        has_hooks = any((src_dir / 'hooks').glob('*.ts')) or any((src_dir / 'hooks').glob('*.tsx'))
        has_utils = any((src_dir / 'utils').glob('*.ts')) or any((src_dir / 'utils').glob('*.tsx'))
        
        validation_report['checks']['hooks'] = 'found' if has_hooks else 'missing'
        validation_report['checks']['utils'] = 'found' if has_utils else 'missing'
        
        if not has_hooks:
            validation_report['suggestions'].append('Consider adding custom hooks for state management')
        if not has_utils:
            validation_report['suggestions'].append('Consider adding utility functions for data persistence')
    
    # HTML Structure Validation (NEW)
    validation_report['checks']['html_structure'] = 'passed'
    html_files = list(target_path.glob('*.html')) + list(target_path.glob('**/*.html'))
    
    for html_file in html_files:
        try:
            html_content = html_file.read_text(encoding='utf-8')
            html_issues = _validate_html_structure(html_content, str(html_file.relative_to(target_path)))
            
            if html_issues['errors']:
                validation_report['checks']['html_structure'] = 'failed'
                validation_report['errors'].extend(html_issues['errors'])
            
            if html_issues['warnings']:
                validation_report['warnings'].extend(html_issues['warnings'])
                
        except Exception as e:
            validation_report['warnings'].append(f'Could not validate HTML structure in {html_file.name}: {str(e)}')
    
    return json.dumps(validation_report, indent=2)


def _validate_html_structure(html_content: str, file_path: str) -> dict:
    """
    Validate HTML structure for common issues like unclosed tags, malformed structure.
    
    Args:
        html_content: The HTML content to validate
        file_path: Path to the HTML file (for error reporting)
        
    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    import re
    
    issues = {'errors': [], 'warnings': []}
    
    # Check for basic HTML structure
    if not html_content.strip():
        issues['errors'].append(f'HTML file {file_path} is empty')
        return issues
    
    # Check for DOCTYPE
    if not re.search(r'<!DOCTYPE\s+html\s*>', html_content, re.IGNORECASE):
        issues['warnings'].append(f'Missing DOCTYPE declaration in {file_path}')
    
    # Check for html, head, body tags
    if not re.search(r'<html[^>]*>', html_content, re.IGNORECASE):
        issues['errors'].append(f'Missing <html> tag in {file_path}')
    
    if not re.search(r'<head[^>]*>', html_content, re.IGNORECASE):
        issues['errors'].append(f'Missing <head> tag in {file_path}')
    
    if not re.search(r'<body[^>]*>', html_content, re.IGNORECASE):
        issues['errors'].append(f'Missing <body> tag in {file_path}')
    
    # Check for matching opening/closing tags
    issues.update(_check_tag_matching(html_content, file_path))
    
    # Check for common modal structure issues
    issues.update(_check_modal_structure(html_content, file_path))
    
    return issues


def _check_tag_matching(html_content: str, file_path: str) -> dict:
    """Check for properly matched opening and closing tags."""
    import re
    
    issues = {'errors': [], 'warnings': []}
    
    # Find all opening and closing tags
    opening_tags = re.findall(r'<(\w+)[^>]*>', html_content)
    closing_tags = re.findall(r'</(\w+)>', html_content)
    
    # Check for self-closing tags that should be closed
    self_closing_tags = {'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
    
    # Count tag occurrences
    tag_counts = {}
    for tag in opening_tags:
        if tag.lower() not in self_closing_tags:
            tag_counts[tag.lower()] = tag_counts.get(tag.lower(), 0) + 1
    
    for tag in closing_tags:
        if tag.lower() in tag_counts:
            tag_counts[tag.lower()] -= 1
    
    # Report unmatched tags
    for tag, count in tag_counts.items():
        if count > 0:
            issues['errors'].append(f'Unclosed <{tag}> tag in {file_path} (missing {count} closing tag(s))')
        elif count < 0:
            issues['errors'].append(f'Extra closing </{tag}> tag in {file_path} (missing {abs(count)} opening tag(s))')
    
    return issues


def _check_modal_structure(html_content: str, file_path: str) -> dict:
    """Check for proper modal structure, especially modal-content containers."""
    import re
    
    issues = {'errors': [], 'warnings': []}
    
    # Find all modal divs
    modal_pattern = r'<div[^>]*class[^>]*modal[^>]*>'
    modal_matches = list(re.finditer(modal_pattern, html_content, re.IGNORECASE))
    
    for i, modal_match in enumerate(modal_matches):
        modal_start = modal_match.start()
        modal_end = modal_match.end()
        
        # Extract the modal section by finding the next modal with class="modal" or end of file
        next_modal_pos = modal_end
        while next_modal_pos < len(html_content):
            next_modal_match = re.search(r'<div[^>]*class[^>]*modal[^>]*>', html_content[next_modal_pos:], re.IGNORECASE)
            if next_modal_match:
                next_modal_pos += next_modal_match.start()
                break
            else:
                next_modal_pos = len(html_content)
                break
        
        modal_section = html_content[modal_start:next_modal_pos]
        
        # Check if modal-content div exists within this modal
        modal_content_pattern = r'<div[^>]*class[^>]*modal-content[^>]*>'
        modal_content_match = re.search(modal_content_pattern, modal_section, re.IGNORECASE)
        
        if not modal_content_match:
            issues['errors'].append(f'Modal {i+1} in {file_path} is missing required <div class="modal-content"> container')
    
    return issues


# Shared state manager for agent communication
class AgentState:
    def __init__(self):
        self.current_project = None
        self.projects = {}  # Dictionary to store multiple projects
        self.base_path = Path("generated_app").resolve()
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
                'template_path': Path("templates/bare-bones-vanilla-main"),
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
        return Path("templates/bare-bones-vanilla-main")
        
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
    
    # If a project is already selected, do not override it implicitly
    if agent_state.current_project and agent_state.current_project != project_name:
        # Do not change the current project; return informative message
        return (
            f"Current project already set to '{agent_state.current_project}'. "
            f"Ignoring request to switch to '{project_name}'."
        )
    
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
    List all existing projects in the generated_app folder.
    
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
def get_app_folder_path() -> str:
    """
    Get the app folder path from the global state.
    
    Returns:
        The app folder path relative to current working directory
    """
    global agent_state
    app_folder = agent_state.get_app_folder_path()
    if app_folder:
        # Convert absolute path to relative path from current working directory
        from pathlib import Path
        current_dir = Path.cwd()
        try:
            relative_path = app_folder.relative_to(current_dir)
            return str(relative_path)
        except ValueError:
            # If the path is not relative to current dir, return the absolute path as string
            return str(app_folder)
    # Fall back to base path if no project selected
    return str(agent_state.base_path) if agent_state.base_path else "No app folder path set"

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
def get_feedback_tickets_path() -> str:
    """Get feedback tickets JSON file path for current project."""
    global agent_state
    app_folder = agent_state.get_app_folder_path()
    return str(app_folder / "feedback_tickets.json") if app_folder else "No path set"

@tool
def get_enhancement_summary_path() -> str:
    """Get enhancement summary MD file path for current project."""
    global agent_state
    app_folder = agent_state.get_app_folder_path()
    return str(app_folder / "enhancement_summary.md") if app_folder else "No path set"

@tool
def get_test_report_path() -> str:
    """Get QA test report path for current project."""
    global agent_state
    app_folder = agent_state.get_app_folder_path()
    return str(app_folder / "code_prototype_test_report.md") if app_folder else "No path set"

@tool
def analyze_qa_report_for_fixes_needed() -> str:
    """
    Analyze the QA test report to determine if the auto_fix_agent should run.
    Returns 'YES' if fixes are needed, 'NO' if the app is functional, or 'ERROR' if report can't be read.
    
    Uses priority-based analysis focusing on executive summary and critical issues.
    """
    global agent_state
    try:
        app_folder = agent_state.get_app_folder_path()
        if not app_folder:
            return "ERROR: No current project set"
        
        test_report_path = app_folder / "code_prototype_test_report.md"
        if not test_report_path.exists():
            return "ERROR: QA test report not found"
        
        # Read the test report
        with open(test_report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        # Analyze the report for critical issues
        report_lower = report_content.lower()
        
        # PRIORITY 1: Check Executive Summary - Prototype Status (highest priority)
        if 'prototype status: non-functional' in report_lower or '**prototype status**: non-functional' in report_lower:
            return "YES: App is non-functional"
        elif 'prototype status: functional' in report_lower or '**prototype status**: functional' in report_lower:
            return "NO: App is functional"
        
        # PRIORITY 2: Check Critical Issues Count (explicit numbers)
        if ('critical issues: 1' in report_lower or 'critical issues: 2' in report_lower or 'critical issues: 3' in report_lower or
            '**critical issues**: 1' in report_lower or '**critical issues**: 2' in report_lower or '**critical issues**: 3' in report_lower):
            return "YES: Critical issues found"
        elif ('critical issues: 0' in report_lower or 'critical issues:0' in report_lower or
              '**critical issues**: 0' in report_lower or '**critical issues**:0' in report_lower):
            return "NO: No critical issues found"
        
        # PRIORITY 3: Check Recommendation (explicit guidance)
        if ('recommendation: major rework required' in report_lower or 
            '**recommendation**: major rework required' in report_lower):
            return "YES: Major rework required"
        elif ('recommendation: ready for development' in report_lower or
              '**recommendation**: ready for development' in report_lower):
            return "NO: Ready for development"
        
        # PRIORITY 4: Check for explicit blocking issues (specific patterns)
        if '0 blocking issues found' in report_lower:
            return "NO: No blocking issues found"
        elif 'app crashes' in report_lower or 'app won\'t start' in report_lower:
            return "YES: App won't start or crashes"
        
        # PRIORITY 5: Check for partial functionality with critical fixes needed
        elif 'partially functional' in report_lower and 'needs critical fixes' in report_lower:
            return "YES: Partially functional with critical fixes needed"
        
        # PRIORITY 6: Conservative fallback - if unclear, assume fixes needed
        # This prevents the false negative you experienced
        else:
            return "YES: Status unclear, assuming fixes needed (conservative approach)"
            
    except Exception as e:
        return f"ERROR: Failed to analyze QA report: {str(e)}"

@tool
def generate_vanilla_js_code(component_type: str, functionality: str, requirements: str) -> str:
    """
    Generate vanilla JavaScript code for specific functionality.
    
    Args:
        component_type: Type of component (e.g., 'task_manager', 'form_handler', 'data_persistence')
        functionality: Specific functionality needed (e.g., 'add_item', 'delete_item', 'save_data')
        requirements: Detailed requirements for the functionality
        
    Returns:
        Generated vanilla JavaScript code as a string
    """
    import json
    
    # Common vanilla JS patterns for different functionalities
    patterns = {
        'task_manager': {
            'add_item': '''
// Add new item to the list
function addItem() {
    const input = document.getElementById('item-input');
    const itemText = input.value.trim();
    
    if (itemText === '') {
        alert('Please enter an item');
        return;
    }
    
    const item = {
        id: Date.now(),
        text: itemText,
        completed: false,
        createdAt: new Date().toISOString()
    };
    
    // Add to data array
    items.push(item);
    
    // Save to localStorage
    saveData();
    
    // Update UI
    renderItems();
    
    // Clear input
    input.value = '';
}

// Render all items
function renderItems() {
    const container = document.getElementById('items-container');
    container.innerHTML = '';
    
    items.forEach(item => {
        const itemElement = createItemElement(item);
        container.appendChild(itemElement);
    });
}

// Create item element
function createItemElement(item) {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `
        <span class="item-text ${item.completed ? 'completed' : ''}">${item.text}</span>
        <button onclick="toggleItem(${item.id})">${item.completed ? 'Undo' : 'Complete'}</button>
        <button onclick="deleteItem(${item.id})">Delete</button>
    `;
    return div;
}
''',
            'delete_item': '''
// Delete item from list
function deleteItem(id) {
    if (confirm('Are you sure you want to delete this item?')) {
        items = items.filter(item => item.id !== id);
        saveData();
        renderItems();
    }
}

// Toggle item completion
function toggleItem(id) {
    const item = items.find(item => item.id === id);
    if (item) {
        item.completed = !item.completed;
        saveData();
        renderItems();
    }
}
''',
            'data_persistence': '''
// Save data to localStorage
function saveData() {
    try {
        localStorage.setItem('app-data', JSON.stringify(items));
    } catch (error) {
        console.error('Failed to save data:', error);
        alert('Failed to save data');
    }
}

// Load data from localStorage
function loadData() {
    try {
        const data = localStorage.getItem('app-data');
        if (data) {
            items = JSON.parse(data);
        }
    } catch (error) {
        console.error('Failed to load data:', error);
        items = [];
    }
}

// Initialize app
function initApp() {
    loadData();
    renderItems();
    
    // Add event listeners
    document.getElementById('add-button').addEventListener('click', addItem);
    document.getElementById('item-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addItem();
        }
    });
}

// Start app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
'''
        },
        'form_handler': {
            'validation': '''
// Form validation
function validateForm(formData) {
    const errors = [];
    
    // Required field validation
    if (!formData.name || formData.name.trim() === '') {
        errors.push('Name is required');
    }
    
    if (!formData.email || formData.email.trim() === '') {
        errors.push('Email is required');
    }
    
    // Email format validation
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
        errors.push('Please enter a valid email address');
    }
    
    return errors;
}

// Handle form submission
function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        message: document.getElementById('message').value
    };
    
    const errors = validateForm(formData);
    
    if (errors.length > 0) {
        showErrors(errors);
        return;
    }
    
    // Process form data
    processFormData(formData);
}

// Show validation errors
function showErrors(errors) {
    const errorContainer = document.getElementById('error-messages');
    errorContainer.innerHTML = errors.map(error => `<div class="error">${error}</div>`).join('');
}
'''
        }
    }
    
    # Get the appropriate pattern
    if component_type in patterns and functionality in patterns[component_type]:
        base_code = patterns[component_type][functionality]
        
        # Add custom requirements if provided
        if requirements:
            base_code += f'''
// Custom requirements: {requirements}
'''
        
        return base_code
    else:
        return f'''
// Generated code for {component_type} - {functionality}
// Requirements: {requirements}

// TODO: Implement {functionality} for {component_type}
// This is a placeholder - implement the actual functionality based on requirements
'''

@tool
def copy_template_to_ui_folder() -> str:
    """
    Copy the UI template to the ui/ folder within the current app directory.
    This creates a working HTML/CSS/JS app structure that can be modified for the UI design.
    
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
    
    # Ensure app folder exists
    if app_folder and not app_folder.exists():
        mkdir(str(app_folder))

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

# Example usage with smolagents
if __name__ == "__main__":
    from smolagents import CodeAgent, InferenceClientModel

    # Create an agent with the file tools
    model = InferenceClientModel()
    agent = CodeAgent(
        tools=[read_file, write_file, list_files, mkdir, build_app_spec_from_docs],
        model=model
    )

    print("FileTool is ready to use with smolagents!")