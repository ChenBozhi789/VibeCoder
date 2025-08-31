import argparse
import os
import sys
import time
import threading
from dotenv import load_dotenv
from pathlib import Path
from smolagents import CodeAgent, WebSearchTool
from smolagents.models import OpenAIServerModel
from template_generator import generate_app_from_template
from app_spec import AppSpec
from am_tools import read_file, write_file, mkdir, list_files # , run_npm
from generate_prompt import scan_app, pick_tasks, render_prompt, ensure_parent_written

# Load environment variables from .env file
load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class ProgressIndicator:
    """Simple progress indicator for long-running operations."""
    
    def __init__(self, message="Processing"):
        self.message = message
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the progress indicator."""
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        print(f"\n{self.message}", end="", flush=True)
    
    def stop(self):
        """Stop the progress indicator."""
        self.running = False
        if self.thread:
            self.thread.join()
        print("\n")
    
    def _animate(self):
        """Animate the progress indicator."""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        while self.running:
            print(f"\r{self.message} {chars[i % len(chars)]}", end="", flush=True)
            time.sleep(0.1)
            i += 1


# (Option 2) No inline fallback; prompt is always (re)generated after app creation.


def main(verbose: bool = False):
    """
    Generate React app using template-based approach with smolagents.
    
    Args:
        verbose: If True, show detailed progress and agent steps
    """
    # Create app specification
    app_spec = AppSpec(
        app_name="tester-app-5-gpt-5",  # task-manager-app
        display_name="Task Manager",
        description="A modern React task management application with localStorage persistence",
        author="VibeCoder",
        template_name="react-simple-spa",
        output_dir="result",
        custom_content='''<h1 className="text-4xl font-bold">Task Manager</h1>
      <p className="text-lg text-gray-600 mb-8">Organize your tasks efficiently</p>
      <Button>Get Started</Button>''',
        features=["localStorage", "responsive", "dark-mode"]
    )

    # Step 1: Generate base template locally (fast)
    print("📂 Creating base template...")
    try:
        template_result = generate_app_from_template(
            app_name=app_spec.app_name,
            display_name=app_spec.display_name,
            description=app_spec.description,
            author=app_spec.author,
            version=app_spec.version,
            template_name=app_spec.template_name,
            output_dir=app_spec.output_dir,
            custom_content=app_spec.custom_content
        )
        print(f" {template_result}")
    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        return None

    # Step 2: Initialize CodeAgent for enhancements (if needed)
    agent = CodeAgent(
        tools=[
            # File system operations for enhancements
            read_file, 
            write_file, 
            list_files, 
            mkdir #,
            # run_npm
        ],
        model=OpenAIServerModel("gpt-5"),
        max_steps=1,
        stream_outputs=False,  # Unenable streaming for real-time feedback
        additional_authorized_imports=["subprocess", "shutil", "json", "re"],        
    )

    # Step 3: Create enhancement prompt AFTER app creation (always rebuild)
    app_path = f"{app_spec.output_dir}/{app_spec.app_name}"
    app_dir = Path(app_path).resolve()
    try:
        # Use the same rules as generate_prompt.py
        ctx = scan_app(app_dir)  # project snapshot
        tasks = pick_tasks(ctx, goal="add dark mode and a README", profile="baseline", allow_new_deps=False)
        prompt_text = render_prompt(ctx, tasks, change_budget=8, allow_new_deps=False)
        prompt_path = app_dir / "prompts" / "enhancement_prompt.j2"
        ensure_parent_written(prompt_path, prompt_text)
        print(f"📝 Enhancement prompt rebuilt at: {prompt_path}")
    except Exception as e:
        print(f"⚠️ Failed to build enhancement prompt: {e}")
        return None
    
    # Step 4: Use agent to enhance the app
    print("🧠 Enhancing the app with AI...")
    cwd_before = os.getcwd()
    try:
        # Work inside the generated app so file tools hit correct paths
        os.chdir(app_path)
        # Run the agent: it will call read_file/write_file/etc. to edit the project
        agent.run(prompt_text)

    except Exception as e:
        print(f"\n⚠️ AI enhancement encountered an issue: {e}")
    finally:
        os.chdir(cwd_before)

    # # For now, just complete without agent enhancement
    # # Later we can add enhancement prompts here if needed 
    # enhancement_prompt = f"""
    # The React application has been generated at: {app_path}

    # The app includes:
    # - React 19 with TypeScript
    # - Vite build system
    # - TailwindCSS v4 styling
    # - Shadcn UI components
    # - Basic structure and configuration

    # You can explore the generated files and make any improvements if needed.
    # For now, the base template is complete and ready to use.
    # """

    print(f"🚀 Generating React app: {app_spec.display_name}")
    print(f"📍 Output location: {app_spec.output_dir}/{app_spec.app_name}")
    
    if verbose:
        print("📋 App Specification:")
        print(f"   • Name: {app_spec.app_name}")
        print(f"   • Display Name: {app_spec.display_name}")
        print(f"   • Description: {app_spec.description}")
        print(f"   • Template: {app_spec.template_name}")
        print(f"   • Author: {app_spec.author}")
        print()
    
    # For now, we only generate the template (no agent needed)
    # Future enhancement: add agent-based improvements here
    
    print("✅ App generation completed!")
    print(f"🎯 Your app is ready in: {app_spec.output_dir}/{app_spec.app_name}")
    print(f"🏃 To run: cd {app_spec.output_dir}/{app_spec.app_name} && npm install && npm run dev")
    
    if verbose:
        print()
        print("📁 Generated files:")
        try:
            app_path = Path(app_spec.output_dir) / app_spec.app_name
            for file in sorted(app_path.rglob("*")):
                if file.is_file() and not any(part.startswith('.') or part == 'node_modules' for part in file.parts):
                    relative_path = file.relative_to(app_path)
                    print(f"   • {relative_path}")
        except Exception:
            print("   (Could not list files)")

if __name__ == "__main__":
    # Check for verbose flag
    verbose_mode = "--verbose" in sys.argv or "-v" in sys.argv
    main(verbose=verbose_mode)