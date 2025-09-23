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
# Generate AppSpec from user requirements and plan
def build_app_spec_from_docs(user_req_path: str, plan_path: str, out_path: str) -> AppSpec:
    """
    Build an AppSpec JSON from two markdown files.

    Args:
        user_req_path: Path (string) to user_requirements.md
        plan_path: Path (string) to plan.md
        out_path: Path (string) to write spec/app_spec.json

    Returns:
        A message containing the absolute path to the written JSON file.
    """
    client = OpenAI()  # Use env variable 
    user_req = Path(user_req_path).read_text(encoding="utf-8")
    plan_md  = Path(plan_path).read_text(encoding="utf-8")

    system = (
        "You convert the given user requirements + plan into a valid AppSpec JSON. "
        "Be strict with types. If a field is missing, infer safe defaults."
    )
    user = f"""
        [USER_REQUIREMENTS_MD]
        {user_req}

        [PLAN_MD]
        {plan_md}

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


# @tool
# def run_npm(command: str) -> str:
#     """
#     Run an npm command in the current project directory.
#     Captures stdout/stderr and returns them to the agent for debugging.
#     """
#     try:
#         result = subprocess.run(
#             command,
#             shell=True,
#             capture_output=True,
#             text=True,
#             check=False
#         )
#         output = f"Exit Code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
#         return output
#     except Exception as e:
#         return f"Error running npm command: {str(e)}"


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