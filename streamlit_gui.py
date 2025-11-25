import streamlit as st
import subprocess
import threading
import queue
import time
import os
import sys
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform.startswith('win'):
    import codecs
    # Set environment variables for UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
import json
import http.server
import socketserver
import webbrowser
# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # dotenv not installed, try to load .env manually
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

# Page configuration
st.set_page_config(
    page_title="VibeCoder: App Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables for session state
if 'user_requirements' not in st.session_state:
    st.session_state.user_requirements = ""
if 'generation_in_progress' not in st.session_state:
    st.session_state.generation_in_progress = False
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'process_logs' not in st.session_state:
    st.session_state.process_logs = []
if 'last_generated_app' not in st.session_state:
    st.session_state.last_generated_app = None
if 'log_file_path' not in st.session_state:
    st.session_state.log_file_path = None
if 'last_log_size' not in st.session_state:
    st.session_state.last_log_size = 0
if 'generation_start_time' not in st.session_state:
    st.session_state.generation_start_time = None

class ProcessLogger:
    """Handles real-time logging from subprocess"""
    def __init__(self):
        self.log_queue = queue.Queue()
        self.logs = []
    
    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_queue.put(log_entry)
        self.logs.append(log_entry)
    
    def get_logs(self):
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs

def run_app_generator(user_input, log_file):
    """Run the app generator with user input"""
    try:
        # Ensure generation_log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Check if API key is set
        if not os.environ.get('GEMINI_API_KEY'):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("❌ Error: GEMINI_API_KEY environment variable is not set.\n")
                f.write("Please set your Gemini API key as an environment variable.\n")
                f.write("Example: export GEMINI_API_KEY='your_api_key_here'\n")
                f.flush()
            return False
        
        # Write initial message to log file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("🚀 Starting app generation process...\n")
            f.write("📋 Initializing AI agents...\n")
            f.write("🔧 Setting up project structure...\n")
            f.flush()
        
        # Run the wrapper script with user input and redirect output to log file
        # Use the same Python executable that's running Streamlit
        python_executable = sys.executable
        # Pass environment variables to the subprocess
        env = os.environ.copy()
        # Ensure UTF-8 encoding for the subprocess
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        process = subprocess.Popen(
            [python_executable, 'app_generator_wrapper.py', user_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            cwd=os.getcwd(),
            env=env,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Stream output to both console and log file with timestamps
        with open(log_file, 'a', encoding='utf-8') as f:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    if line:  # Only process non-empty lines
                        timestamp = time.strftime("%H:%M:%S")
                        formatted_line = f"[{timestamp}] {line}"
                        print(formatted_line)  # Also print to console for debugging
                        f.write(formatted_line + "\n")
                        f.flush()
        
        return_code = process.poll()
        
        # Write completion message
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = time.strftime("%H:%M:%S")
            if return_code == 0:
                f.write(f"[{timestamp}] ✅ App generation completed successfully!\n")
                f.write(f"[{timestamp}] 🎉 Your app is ready to use!\n")
            else:
                f.write(f"[{timestamp}] ❌ App generation failed with return code: {return_code}\n")
        
        return return_code == 0
        
    except Exception as e:
        # Write error to log file
        timestamp = time.strftime("%H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] ❌ Error running app generator: {str(e)}\n")
        print(f"Error: {str(e)}")  # Also print to console
        return False

def get_generated_projects():
    """Get list of generated projects"""
    generated_app_path = Path("generated_app")
    if not generated_app_path.exists():
        return []
    
    projects = []
    for item in generated_app_path.iterdir():
        if item.is_dir():
            # Check if it has a ui folder with index.html
            ui_path = item / "ui" / "index.html"
            if ui_path.exists():
                projects.append({
                    'name': item.name,
                    'path': str(ui_path),
                    'created': time.ctime(item.stat().st_mtime)
                })
    
    return sorted(projects, key=lambda x: x['created'], reverse=True)

def display_app_iframe(app_path):
    """Display the app in an iframe with better handling of CSS and JS"""
    if os.path.exists(app_path):
        try:
            import re
            
            # Read the HTML content
            with open(app_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Get the app folder path for relative resources
            app_folder = os.path.dirname(os.path.dirname(app_path))
            ui_folder = os.path.dirname(app_path)
            
            # Create a more complete HTML with embedded CSS and JS
            enhanced_html = html_content
            
            # Find and inline all CSS files using regex
            # Match any link tag containing both href to css file and rel="stylesheet"
            css_pattern = r'<link\s+[^>]*href=["\']([^"\']*css/[^"\']*\.css)["\'][^>]*rel=["\']stylesheet["\'][^>]*>|<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']*css/[^"\']*\.css)["\'][^>]*>'
            css_matches = list(re.finditer(css_pattern, enhanced_html, re.IGNORECASE))
            
            # Process matches in reverse order to maintain string positions
            for match in reversed(css_matches):
                css_url = match.group(1) or match.group(2)  # Get href from either group
                if css_url:
                    css_file = os.path.join(ui_folder, css_url)
                    
                    if os.path.exists(css_file):
                        with open(css_file, 'r', encoding='utf-8') as f:
                            css_content = f.read()
                        # Replace the link tag with embedded style
                        enhanced_html = enhanced_html[:match.start()] + f'<style>{css_content}</style>' + enhanced_html[match.end():]
            
            # Find and inline all JS files using regex
            # Match any script tag with src pointing to js files
            js_pattern = r'<script\s+[^>]*src=["\']([^"\']*js/[^"\']*\.js)["\'][^>]*>\s*</script>'
            js_matches = list(re.finditer(js_pattern, enhanced_html, re.IGNORECASE))
            
            # Process matches in reverse order to maintain string positions
            for match in reversed(js_matches):
                js_url = match.group(1)
                js_file = os.path.join(ui_folder, js_url)
                
                if os.path.exists(js_file):
                    with open(js_file, 'r', encoding='utf-8') as f:
                        js_content = f.read()
                    # Replace the script tag with embedded script
                    enhanced_html = enhanced_html[:match.start()] + f'<script>{js_content}</script>' + enhanced_html[match.end():]
            
            # Create a data URL for the enhanced HTML content
            import base64
            encoded_html = base64.b64encode(enhanced_html.encode()).decode()
            data_url = f"data:text/html;base64,{encoded_html}"
            
            # Display in iframe with better styling
            st.components.v1.iframe(
                data_url, 
                height=700, 
                scrolling=True,
                width=None  # Use full width
            )
            
            # Add action buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.link_button(
                    "🔗 Open in New Tab",
                    f"file://{os.path.abspath(app_path)}",
                    help="Click to open the app in a new browser tab",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Refresh Preview", use_container_width=True):
                    st.rerun()
            
            with col3:
                # Get the app folder to show more options
                if st.button("📁 Open Folder", use_container_width=True):
                    st.info(f"App folder: {os.path.abspath(app_folder)}")
            
            # Show app info
            st.markdown("---")
            st.markdown("**App Information:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"📁 **App Folder:** `{os.path.basename(app_folder)}`")
                st.write(f"📄 **HTML File:** `{os.path.basename(app_path)}`")
            
            with col2:
                css_exists = "✅" if os.path.exists(css_file) else "❌"
                js_exists = "✅" if os.path.exists(js_file) else "❌"
                st.write(f"🎨 **CSS:** {css_exists}")
                st.write(f"⚡ **JavaScript:** {js_exists}")
            
        except Exception as e:
            st.error(f"Error displaying app: {str(e)}")
            # Fallback to simple iframe
            try:
                import base64
                with open(app_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                encoded_html = base64.b64encode(html_content.encode()).decode()
                data_url = f"data:text/html;base64,{encoded_html}"
                st.components.v1.iframe(data_url, height=600, scrolling=True)
            except Exception as e2:
                st.error(f"Fallback also failed: {str(e2)}")
    else:
        st.error(f"App file not found: {app_path}")

def start_local_server(port=8000):
    """Start a local HTTP server for serving generated apps"""
    try:
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except OSError:
        # Port already in use, try next port
        return start_local_server(port + 1)

def cleanup_old_logs():
    """Clean up old generation log files"""
    try:
        import glob
        log_files = glob.glob("generation_log/generation_log_*.txt")
        completion_files = glob.glob("generation_log/generation_log_*_complete.txt")
        
        for log_file in log_files:
            # Remove files older than 1 hour
            if os.path.getmtime(log_file) < time.time() - 3600:
                os.remove(log_file)
        
        for completion_file in completion_files:
            # Remove completion files older than 1 hour
            if os.path.getmtime(completion_file) < time.time() - 3600:
                os.remove(completion_file)
    except:
        pass

def main():
    # Clean up old log files
    cleanup_old_logs()
    
    # Main title
    st.title("🚀 VibeCoder: App Generator")
    st.markdown("Transform your ideas into fully functional web applications with AI-powered multi-agent generation.")
    
    # Sidebar for project history
    with st.sidebar:
        st.header("📁 Project History")
        
        projects = get_generated_projects()
        if projects:
            st.write("**Generated Projects:**")
            for project in projects:
                if st.button(f"📱 {project['name']}", key=f"project_{project['name']}"):
                    st.session_state.current_project = project
                    st.rerun()
            
            # Display current project info
            if st.session_state.current_project:
                st.markdown("---")
                st.write("**Current Project:**")
                st.write(f"📱 {st.session_state.current_project['name']}")
                st.write(f"🕒 Created: {st.session_state.current_project['created']}")
        else:
            st.write("No projects generated yet.")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("💡 App Idea Input")
        
        # Text area for user input
        user_input = st.text_area(
            "Describe your app idea:",
            value=st.session_state.user_requirements,
            placeholder="I need an app called QuickTasks to track my daily to-do list with categories, due dates, and priority levels. It should have a clean interface and allow me to mark tasks as complete.",
            height=150,
            help="Describe what you want your app to do, who will use it, and any key features you need.",
            key="user_input_textarea"
        )
        
        st.session_state.user_requirements = user_input
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate App",
            type="primary",
            disabled=st.session_state.generation_in_progress or not user_input.strip(),
            use_container_width=True
        )
    
    with col2:
        st.header("📱 Generated App")
        
        # Display current project or last generated app
        app_to_display = st.session_state.current_project or st.session_state.last_generated_app
        
        if app_to_display:
            st.write(f"**{app_to_display['name']}**")
            display_app_iframe(app_to_display['path'])
        else:
            st.info("No app selected. Generate a new app or select one from the sidebar.")
    
    # Process logging area - always show if there's a log file
    if st.session_state.log_file_path and os.path.exists(st.session_state.log_file_path):
        with st.expander("📋 Generation Progress", expanded=st.session_state.generation_in_progress):
            # Check for completion
            completion_file = st.session_state.log_file_path.replace('.txt', '_complete.txt')
            if os.path.exists(completion_file):
                # Generation completed, read result
                with open(completion_file, 'r') as f:
                    content = f.read()
                
                success = False
                if 'success:True' in content:
                    success = True
                    # Find the latest generated project
                    projects = get_generated_projects()
                    if projects:
                        st.session_state.last_generated_app = projects[0]
                        st.session_state.current_project = projects[0]
                
                # Update session state
                st.session_state.generation_in_progress = False
                st.session_state.generation_start_time = None
                
                # Clean up completion file
                try:
                    os.remove(completion_file)
                except:
                    pass
                
                # Show completion status
                if success:
                    st.success("✅ App generation completed successfully!")
                else:
                    st.error("❌ App generation failed. Check logs for details.")
                
                # Auto-refresh to update the UI
                time.sleep(1)
                st.rerun()
            
            # Read and display logs from file
            log_text = "Starting app generation..."
            try:
                with open(st.session_state.log_file_path, 'r', encoding='utf-8') as f:
                    log_text = f.read()
            except:
                log_text = "Error reading log file"
            
            # Display logs with better formatting and auto-scroll
            log_container = st.container()
            with log_container:
                st.text_area(
                    "Live Logs:",
                    value=log_text,
                    height=400,
                    disabled=True,
                    key="live_logs_textarea"
                )
            
            # Show progress indicator and auto-refresh
            if st.session_state.generation_in_progress:
                # Create a progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Calculate progress based on log content and time elapsed
                current_log_size = len(log_text)
                log_lines = len(log_text.split('\n'))
                
                # Calculate progress based on log growth and time
                if st.session_state.generation_start_time:
                    elapsed_time = time.time() - st.session_state.generation_start_time
                    # Estimate progress based on typical generation time (2-5 minutes)
                    time_progress = min(0.7, elapsed_time / 300)  # 5 minutes max
                else:
                    time_progress = 0
                
                # Log-based progress
                log_progress = min(0.6, log_lines / 50)  # Rough estimate based on log lines
                
                # Combine both progress indicators
                progress_value = min(0.9, max(time_progress, log_progress))
                progress_bar.progress(progress_value)
                
                # Show status with more details
                elapsed_str = ""
                if st.session_state.generation_start_time:
                    elapsed = int(time.time() - st.session_state.generation_start_time)
                    elapsed_str = f" (Elapsed: {elapsed}s)"
                
                status_text.info(f"🔄 Generation in progress...{elapsed_str} This page will auto-refresh every 2 seconds.")
                
                # Auto-refresh every 2 seconds during generation
                time.sleep(2)
                st.rerun()
            else:
                st.info("📋 Generation completed. You can view the logs above.")
    
    # Handle generate button click
    if generate_button and user_input.strip():
        st.session_state.generation_in_progress = True
        st.session_state.generation_start_time = time.time()
        
        # Create a unique log file for this generation
        timestamp = int(time.time())
        log_file = f"generation_log/generation_log_{timestamp}.txt"
        st.session_state.log_file_path = log_file
        
        # Start generation in a separate thread
        def generation_thread():
            try:
                success = run_app_generator(user_input, log_file)
                
                # Update session state - use a flag file to communicate completion
                completion_file = log_file.replace('.txt', '_complete.txt')
                with open(completion_file, 'w') as f:
                    f.write(f"success:{success}\n")
                
            except Exception as e:
                print(f"Generation thread error: {e}")
                completion_file = log_file.replace('.txt', '_complete.txt')
                with open(completion_file, 'w') as f:
                    f.write(f"success:False\n")
                    f.write(f"error:{str(e)}\n")
        
        # Start the thread
        thread = threading.Thread(target=generation_thread)
        thread.daemon = True
        thread.start()
        
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**VibeCoder** - Powered by AI Multi-Agent Architecture | "
        "Built with Streamlit and Google Gemini Models"
    )

if __name__ == "__main__":
    main()
