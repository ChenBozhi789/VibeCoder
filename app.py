import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
import sys
import os
import zipfile
import io
import shutil

# Add the VibeCoder directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from smolagents import CodeAgent, ToolCallingAgent
from app_generator import prd_agent, gemini_pro_model
from prompt_loader import prompt_loader
from am_tools import (
    get_current_project, get_app_folder_path, agent_state,
    mkdir, list_files, read_file, write_file,
    get_app_name, get_prd_path, get_spec_path,
    get_template_path, get_ui_design_path,
    copy_template_to_ui_folder, set_ui_memory, get_ui_memory,
    get_all_ui_memory, set_current_project, list_existing_projects,
    read_ui_structure_json,
    generate_ui_structure_json, get_user_requirements,
    validate_implementation,
    read_project_requirements, generate_vanilla_js_code,
    analyze_qa_report_for_fixes_needed
)

# Force UTF-8 encoding on Windows
if sys.platform.startswith('win'):
    import codecs
    # Try to set UTF-8 encoding, but handle cases where detach() is not available
    # (e.g., in Streamlit environment or certain console types)
    try:
        if hasattr(sys.stdout, 'detach'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    except (AttributeError, OSError):
        pass  # Stream already configured or not detachable
    
    try:
        if hasattr(sys.stderr, 'detach'):
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except (AttributeError, OSError):
        pass  # Stream already configured or not detachable
    
    # Set environment variables for UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# Page configuration
st.set_page_config(
    layout="wide",
    page_title="VibeCoder",
    page_icon="🚀"
)

# Helper function to get all available projects
def get_available_projects():
    """Get a list of all available projects in generated_app directory."""
    generated_app_path = Path("generated_app")
    projects = []
    
    if not generated_app_path.exists():
        return projects
    
    for project_dir in generated_app_path.iterdir():
        if project_dir.is_dir():
            ui_dir = project_dir / "ui"
            if ui_dir.exists():
                index_file = ui_dir / "index.html"
                if index_file.exists():
                    projects.append(project_dir.name)
    
    return sorted(projects)

# Helper function to get index.html path for a specific project
def get_project_html_path(project_name):
    """Get the index.html file path for a specific project."""
    if not project_name:
        return None
    
    generated_app_path = Path("generated_app")
    project_dir = generated_app_path / project_name
    ui_dir = project_dir / "ui"
    index_file = ui_dir / "index.html"
    
    if index_file.exists():
        return index_file
    return None

# Helper function to inline CSS and JS files into HTML
def inline_assets(html_content: str, html_file_path: Path) -> str:
    """Inline CSS and JS files referenced in HTML to make them work in iframe.
    
    Args:
        html_content: The HTML content as string
        html_file_path: Path to the HTML file (for resolving relative paths)
    
    Returns:
        HTML content with CSS and JS inlined
    """
    import re
    from pathlib import Path
    
    ui_dir = html_file_path.parent
    
    # Inline CSS files
    css_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
    
    def replace_css(match):
        css_path = match.group(1)
        # Skip external URLs
        if css_path.startswith('http://') or css_path.startswith('https://'):
            return match.group(0)
        
        # Resolve relative path
        css_file = ui_dir / css_path
        if css_file.exists():
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                return f'<style>\n{css_content}\n</style>'
            except Exception as e:
                return match.group(0)  # Keep original if read fails
        return match.group(0)
    
    html_content = re.sub(css_pattern, replace_css, html_content, flags=re.IGNORECASE)
    
    # Inline JS files (optional, but helpful for iframe)
    js_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>'
    
    def replace_js(match):
        js_path = match.group(1)
        # Skip external URLs
        if js_path.startswith('http://') or js_path.startswith('https://'):
            return match.group(0)
        
        # Resolve relative path
        js_file = ui_dir / js_path
        if js_file.exists():
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                return f'<script>\n{js_content}\n</script>'
            except Exception as e:
                return match.group(0)  # Keep original if read fails
        return match.group(0)
    
    html_content = re.sub(js_pattern, replace_js, html_content, flags=re.IGNORECASE)
    
    return html_content

# Helper function to get project files tree
def get_project_files_tree(project_path: Path):
    """Get a list of all files in the project directory."""
    files = []
    if not project_path.exists():
        return files
    
    for root, dirs, filenames in os.walk(project_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in filenames:
            # Skip hidden files
            if filename.startswith('.'):
                continue
            
            file_path = Path(root) / filename
            # Get relative path from project root
            rel_path = file_path.relative_to(project_path)
            files.append(str(rel_path))
    
    return sorted(files)

# Helper function to detect language from file extension
def get_language_from_extension(file_path: str):
    """Detect programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bat': 'batch',
        '.txt': 'text',
    }
    return language_map.get(ext, 'text')

# Helper function to create zip file of project
def create_project_zip(project_path: Path):
    """Create a zip file of the project directory."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                
                file_path = Path(root) / file
                arcname = file_path.relative_to(project_path.parent)
                zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer

# Helper function to get terminal logs
def get_terminal_logs(project_path: Path):
    """Get terminal/logs content from project files."""
    logs = []
    
    # Try to read USER_FEEDBACK.md
    feedback_file = project_path / "USER_FEEDBACK.md"
    if feedback_file.exists():
        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                logs.append(("USER_FEEDBACK.md", f.read()))
        except Exception as e:
            logs.append(("Error", f"Could not read USER_FEEDBACK.md: {e}"))
    
    # Add mock agent activity log
    logs.append(("System", "Agent Activity Log:\n- Project initialized\n- Files generated\n- UI structure created"))
    
    return logs

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "app_generated" not in st.session_state:
    # Check if an app already exists
    st.session_state.app_generated = len(get_available_projects()) > 0

if "generation_in_progress" not in st.session_state:
    st.session_state.generation_in_progress = False

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

# Helper function to create agents
def create_ui_agent():
    """Create the UI agent."""
    return CodeAgent(
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
            get_current_project,
            generate_ui_structure_json
        ],
        model=gemini_pro_model,
        additional_authorized_imports=['json'],
    )

def create_implementation_agent():
    """Create the implementation agent."""
    return CodeAgent(
        tools=[
            read_file,
            write_file,
            mkdir,
            list_files,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_app_folder_path,
            set_current_project,
            list_existing_projects,
            get_current_project,
            read_ui_structure_json,
            generate_ui_structure_json
        ],
        model=gemini_pro_model,
        additional_authorized_imports=['json'],
        max_steps=30,
    )

def create_qa_agent():
    """Create the QA agent."""
    return ToolCallingAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            get_user_requirements,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_ui_design_path,
            get_app_folder_path,
            set_current_project,
            list_existing_projects,
            get_current_project,
            read_ui_structure_json,
            validate_implementation,
            read_project_requirements
        ],
        model=gemini_pro_model,
    )

def create_auto_fix_agent():
    """Create the auto fix agent."""
    return CodeAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            mkdir,
            get_user_requirements,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_ui_design_path,
            get_app_folder_path,
            set_current_project,
            list_existing_projects,
            get_current_project,
            read_ui_structure_json,
            validate_implementation,
            read_project_requirements,
            generate_vanilla_js_code
        ],
        model=gemini_pro_model,
        max_steps=30,
    )

# Helper function to run agents sequentially
def run_initial_generation():
    """Run the initial app generation with prd_agent, ui_agent, implementation_agent, qa_agent, and auto_fix_agent."""
    try:
        # 1. PRD Agent
        with st.status("🚀 Running PRD Agent...", expanded=True) as status:
            prd_task = prompt_loader.load_agent_prompt("prd_agent")
            prd_agent.run(prd_task)
            status.update(label="✅ PRD Agent completed", state="complete")
        
        # 2. UI Agent
        with st.status("🎨 Running UI Agent...", expanded=True) as status:
            ui_agent = create_ui_agent()
            ui_task = prompt_loader.load_agent_prompt("ui_agent")
            ui_agent.run(ui_task)
            status.update(label="✅ UI Agent completed", state="complete")
        
        # 3. Implementation Agent
        with st.status("⚙️ Running Implementation Agent...", expanded=True) as status:
            # Ensure we have a current project
            current_project = agent_state.get_current_project()
            if not current_project:
                projects = []
                if agent_state.base_path.exists():
                    for item in agent_state.base_path.iterdir():
                        if item.is_dir():
                            projects.append(item.name)
                if projects:
                    agent_state.set_current_project(projects[0])
            
            # Pre-check: Ensure UI_STRUCTURE.json exists
            app_folder_path = agent_state.get_app_folder_path()
            ui_folder_path = f"{app_folder_path}/ui"
            ui_structure_file = f"{ui_folder_path}/UI_STRUCTURE.json"
            
            if not os.path.exists(ui_structure_file):
                try:
                    result = generate_ui_structure_json(ui_folder_path)
                    st.info(f"Generated UI_STRUCTURE.json: {result}")
                except Exception as e:
                    st.warning(f"Could not generate UI_STRUCTURE.json: {e}")
            
            implementation_agent = create_implementation_agent()
            implementation_task = prompt_loader.load_agent_prompt("implementation_agent")
            implementation_agent.run(implementation_task)
            status.update(label="✅ Implementation Agent completed", state="complete")
        
        # 4. QA Agent
        with st.status("🔍 Running QA Agent...", expanded=True) as status:
            qa_agent = create_qa_agent()
            qa_task = prompt_loader.load_agent_prompt("qa_agent")
            qa_agent.run(qa_task)
            status.update(label="✅ QA Agent completed", state="complete")
        
        # 5. Auto Fix Agent (conditional)
        with st.status("🔧 Analyzing QA Report...", expanded=True) as status:
            fixes_analysis = analyze_qa_report_for_fixes_needed()
            status.update(label=f"📊 Analysis: {fixes_analysis}", state="complete")
        
        if fixes_analysis.startswith("YES"):
            with st.status("🔧 Running Auto Fix Agent...", expanded=True) as status:
                auto_fix_agent = create_auto_fix_agent()
                auto_fix_task = prompt_loader.load_agent_prompt("auto_fix_agent")
                auto_fix_agent.run(auto_fix_task)
                status.update(label="✅ Auto Fix Agent completed", state="complete")
        else:
            st.info(f"✅ No fixes needed: {fixes_analysis}")
        
        return True
    except Exception as e:
        st.error(f"Error during app generation: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False

# Helper function to handle user feedback
def process_user_feedback(feedback: str):
    """Process user feedback by saving it and running auto_fix_agent."""
    try:
        # Get current project path
        current_project = get_current_project()
        if not current_project:
            # Try to find any project
            projects = []
            if agent_state.base_path.exists():
                for item in agent_state.base_path.iterdir():
                    if item.is_dir():
                        projects.append(item.name)
            
            if projects:
                agent_state.set_current_project(projects[0])
                current_project = projects[0]
            else:
                st.error("No project found. Please generate an app first.")
                return False
        
        app_folder_path = get_app_folder_path()
        feedback_file = Path(app_folder_path) / "USER_FEEDBACK.md"
        
        # Save feedback to file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feedback_content = f"""# User Feedback

**Timestamp**: {timestamp}

## Feedback
{feedback}

---
*This feedback was provided through the VibeCoder Streamlit interface.*
"""
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            f.write(feedback_content)
        
        # Create custom task for auto_fix_agent that includes user feedback
        base_task = prompt_loader.load_agent_prompt("auto_fix_agent")
        custom_task = f"""{base_task}

## USER FEEDBACK (PRIORITY)

**IMPORTANT**: The user has provided feedback that should be addressed. Please read the user feedback file and implement the requested changes.

1. Read the user feedback: `read_file("{feedback_file}")`
2. Understand what changes the user wants
3. Implement the requested changes to the code
4. Focus on the user's specific feedback while maintaining existing functionality

The user feedback is:
```
{feedback}
```

Please prioritize implementing the user's feedback while ensuring the app remains functional.
"""
        
        # Run auto_fix_agent with custom task
        with st.status("🔧 Processing feedback with Auto Fix Agent...", expanded=True) as status:
            auto_fix_agent = create_auto_fix_agent()
            auto_fix_agent.run(custom_task)
            status.update(label="✅ Feedback processed successfully", state="complete")
        
        return True
    except Exception as e:
        st.error(f"Error processing feedback: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False

# Main layout
st.title("🚀 VibeCoder")

# Minimal CSS for better UX (no heavy borders)
st.markdown("""
    <style>
        /* Ensure tabs use full height */
        [data-testid="stTabs"] {
            height: 100%;
        }
        
        [data-testid="stTabs"] > div > div {
            height: calc(100vh - 300px);
            overflow-y: auto;
        }
        
        /* Reduce spacing between tabs and content */
        [data-testid="stTabs"] [data-baseweb="tab-panel"] {
            padding-top: 0.5rem !important;
        }
        
        /* Reduce spacing in tab content area */
        [data-testid="stTabs"] > div > div > div {
            padding-top: 0.5rem !important;
        }
        
        /* Style code editor columns */
        .stCodeBlock {
            max-height: 600px;
            overflow-y: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar: Project Controls
with st.sidebar:
    st.sidebar.title("VibeCoder Controls")
    
    # Reset Project button
    if st.button("🔄 Reset Project", use_container_width=True, type="secondary"):
        # Clear session state
        st.session_state.messages = []
        st.session_state.app_generated = False
        st.session_state.generation_in_progress = False
        st.session_state.selected_file = None
        st.success("Project reset. You can start fresh now.")
        st.rerun()
    
    # Download Code button
    current_project = get_current_project()
    if current_project:
        project_path = Path("generated_app") / current_project
        if project_path.exists():
            zip_buffer = create_project_zip(project_path)
            st.download_button(
                label="📥 Download Code",
                data=zip_buffer,
                file_name=f"{current_project}.zip",
                mime="application/zip",
                use_container_width=True
            )
        else:
            st.info("No project files found to download.")
    else:
        st.info("No active project to download.")
    
    # Add separator line
    st.divider()
    
    # App Selection Section
    st.sidebar.subheader("Select App")
    available_projects = get_available_projects()
    
    if available_projects:
        # Initialize selected project if not exists
        if "selected_preview_project" not in st.session_state:
            st.session_state.selected_preview_project = available_projects[0]
        
        # Display current selected project
        current_selected = st.session_state.selected_preview_project
        st.sidebar.info(f"当前: **{current_selected}**")
        
        # Create buttons for each project
        for project in available_projects:
            # Highlight current selection
            button_type = "primary" if project == current_selected else "secondary"
            if st.sidebar.button(
                f"📱 {project}",
                key=f"app_btn_{project}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.selected_preview_project = project
                st.rerun()
    else:
        st.sidebar.info("暂无可用应用")

# Create two columns - left side smaller, right side larger for preview
col1, col2 = st.columns([1, 3])

# Left Column: Chat Interface
with col1:
    st.subheader("💬 Chat")
    
    # Initial generation button
    if not st.session_state.app_generated and not st.session_state.generation_in_progress:
        if st.button("🚀 Build App", type="primary", use_container_width=True):
            st.session_state.generation_in_progress = True
            st.rerun()
    
    # Show simple notice while generation runs (detailed steps on the right)
    if st.session_state.generation_in_progress and not st.session_state.app_generated:
        st.info("🚧 App generation in progress... see the right panel for detailed steps.")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input for feedback
    if st.session_state.app_generated:
        if prompt := st.chat_input("Provide feedback or request changes..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process feedback
            with st.chat_message("assistant"):
                with st.spinner("Processing your feedback..."):
                    success = process_user_feedback(prompt)
                    if success:
                        st.success("✅ Changes applied successfully! The preview will update shortly.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"I've processed your feedback: '{prompt}'. The changes have been applied to the app."
                        })
                        st.rerun()
                    else:
                        st.error("❌ Failed to process feedback. Please check the error messages above.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Sorry, I encountered an error while processing your feedback: '{prompt}'. Please try again."
                        })

# Right Column: Generation Progress (no preview for now)
with col2:
    st.subheader("⚙️ Generation Progress")
    
    # When generation is running, execute it here so status blocks appear on the right
    if st.session_state.generation_in_progress and not st.session_state.app_generated:
        success = run_initial_generation()
        if success:
            st.session_state.app_generated = True
            st.session_state.generation_in_progress = False
            st.success("✅ App generated successfully!")
            st.rerun()
        else:
            st.session_state.generation_in_progress = False
    else:
        if st.session_state.app_generated:
            st.success("✅ App has been generated. You can now use the chat on the left to iterate.")
        else:
            st.info("点击左侧 \"🚀 Build App\" 按钮开始生成应用，生成过程会在这里显示。")

