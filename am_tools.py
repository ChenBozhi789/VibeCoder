import os
from pathlib import Path
from typing import Optional
from smolagents import tool
import subprocess
from app_spec import AppSpec
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
def build_app_spec_from_docs(user_req_path: str, out_path: str) -> AppSpec:
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
        "Be strict with types. If a field is missing, infer safe defaults."
    )
    user = f"""
        [PRD_MD]
        {user_req}

        [OUTPUT_SCHEMA]
        - Produce an AppSpec with fields:
        app_name (kebab-case),
        display_name,
        description,
        author (optional),
        version (optional),
        template_name (default: "react-simple-spa"),
        output_dir (default: "result"),
        custom_content (optional JSX),
        features (string array).
        """

    resp = client.responses.parse(
        model="gpt-5-mini",
        input=[{"role": "system", "content": system},
               {"role": "user", "content": user}],
        text_format=AppSpec
    )

    spec: AppSpec = resp.output_parsed  # 已是强类型对象
    
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(spec.model_dump_json(indent=2), encoding="utf-8")
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