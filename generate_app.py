import argparse
import os
import sys
import json
import time
import threading
from dotenv import load_dotenv
from pathlib import Path
from smolagents import CodeAgent, WebSearchTool, ToolCallingAgent, PlanningStep
from smolagents.models import OpenAIServerModel
from template_generator import generate_app_from_template
from app_spec import AppSpec
from am_tools import read_file, write_file, mkdir, list_files, get_user_feedback, build_app_spec_from_docs # , run_npm
from generate_prompt import scan_app, pick_tasks, render_prompt, ensure_parent_written
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from langfuse import get_client



# Load environment variables from .env file
load_dotenv()

 
langfuse = get_client()
 
# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

SmolagentsInstrumentor().instrument()

if not os.environ.get("LANGFUSE_PUBLIC_KEY"):
    raise ValueError("LANGFUSE_PUBLIC_KEY environment variable is not set.")


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
    # 1. PRD Agent
    requirement_interview_agent = ToolCallingAgent(
        tools=[
            get_user_feedback,
            write_file, 
            mkdir, 
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    # Can optimize this path to be more dynamic
    storage_folder = "result"
    final_path = Path(storage_folder).resolve() # C:\Users\cbz\Desktop\VibeCoder\VibeCoder\result
    # app_name will be collected during the interview

    # Example task + human feedback loop
    prd_task = f"""
    ## 📝 PRD Task

    You are a helpful Product Manager.  
    Your mission is to guide the user through a short interview to gather app requirements, then save them to **PRD.md**.

    ---

    ## 📋 Requirement Rules
    - Start by asking for the **app name**.  
    - Ask **one question at a time** in plain, everyday language.  
    - Follow this order of questions:

    1. **Purpose & users** → What problem should the app solve, and who will use it?  
    2. **Features** → What main things should people be able to do? (e.g., add tasks, set reminders, organize, etc.)  
    3. **Look & feel** → How should it look and work? (simple list, mobile-friendly, desktop, or both)  
    4. **Information to save** → What details do you want to keep for each item? (title, notes, due date, reminder, etc.)  
    5. **Rules** → Any checks needed when people enter info? (title required, dates must make sense)  
    6. **Other needs** → Should it work offline, load quickly, or be easy for everyone to use?  
    7. **Extras** → Do you want backup/export, the app to be installable offline, or special branding?  
    8. **When it's done** → What would make you feel the app is complete? How should it handle empty lists or mistakes?  

    ---

    ## 📋 Questioning Principles
    - **One Step at a Time** → Keep questions simple and clear.  
    - **Everyday Language** → Avoid jargon; focus on what the app does and who uses it.  
    - **Guided, Multiple-Choice** → Offer examples or options, but let the user type their own.  
    - **Logical Flow** → Start with the big picture, then go into details.  

    ---

    ## ✅ Final PRD Summary
    At the end of the interview, summarize all answers clearly in **PRD.md**.  
    Include: purpose, features, UI/UX notes, data model, rules, non-functional needs, extras, and success criteria.  
    Format the output in clean Markdown with headings and bullet points.  

    ---

    ## 📂 File Handling Rules

    1. **Folder Path Convention**  
    - Use the app name in the folder path:  
        ```
        {final_path}/<app_name>
        ```
    2. **Files to Create (after requirements interview)**  
    - `PRD.md` → contains the gathered requirements.
    3. **Create Folder if Missing**  
    - If the parent folder does not exist, create it first:  
        ```python
        mkdir(path)
        ```
    4. **Write Files**  
    - Save files using:  
        ```python
        write_file(path, content)
        ```
    5. **Restriction**  
    - ❌ Do not write anywhere else.
    """

    print("🚀 Start running Requirement interview agent")
    requirement_interview_agent.run(prd_task)

    # 2. Review agent
    review_agent = ToolCallingAgent(
        tools=[
            read_file,
            write_file
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    review_task = f"""
    You are the Review Agent.  
    Your mission is to review `user_requirements.md` and `plan.md`.  

    ---

    ## Review Tasks
    1. Verify every requirement from `user_requirements.md` is covered in `plan.md`.  
    2. Ensure terminology consistency (same feature names in both files).  
    3. Check that `plan.md` includes all sections:  
    - Overview  
    - Functional Requirements  
    - Non-Functional Requirements  
    - UI/UX Design  
    - Data Model  
    - Validation & Edge Cases  
    - Storage & Persistence  
    - Implementation Plan  
    - QA Checklist  
    - Success Criteria  
    - Future Enhancements  
    4. Identify missing or unclear points → ask user for clarification.  
    5. Approve only when documents are complete and ready to build `app_spec.json`.  

    ---

    ## INSTRUCTIONS

    Please review the PRD.md and PLAN.md, and save the file that you write to `{final_path}/<app_name>/app_spec.json`
    """

    print("🚀 Start running Review agent")
    review_agent.run(review_task)

    # 3. UI agent - CodeAgent
    ui_agent = ToolCallingAgent(
        tools=[
            read_file,
            write_file
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    ui_task = f"""
    The prompt will be added later
    """

    print("🚀 Start running UI agent")
    ui_agent.run(ui_task)

    # 4. Code agent - CodeAgent
    code_agent = CodeAgent(
        tools=[
            read_file,
            write_file
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    code_task = f"""
    The prompt will be added later
    """

    print("🚀 Start running Code agent")
    code_agent.run(code_task)

    # 5. QA agent - ToolCallingAgent
    qa_agent = ToolCallingAgent(
        tools=[
            read_file,
            write_file
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    qa_task = f"""
    The prompt will be added later
    """

    print("🚀 Start running QA agent")
    qa_agent.run(qa_task)

    # 6. User feedback agent - ToolCallingAgent
    user_feedback_agent = ToolCallingAgent(
        tools=[
            get_user_feedback
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    user_feedback_task = f"""
    The prompt will be added later
    """

    print("🚀 Start running User feedback agent")
    user_feedback_agent.run(user_feedback_task)

    # 7. Code enhancement agent - CodeAgent
    code_enhancement_agent = CodeAgent(
        tools=[
            read_file,
            write_file
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    code_enhancement_task = f"""
    The prompt will be added later
    """

    print("🚀 Start running Code enhancement agent")
    code_enhancement_agent.run(code_enhancement_task)


    # Path to your spec file (adjust if needed)
    spec_files  = list(final_path.rglob("app_spec.json"))
    if not spec_files :
        return FileNotFoundError("❌ No app_spec.json found under result/")
    spec_path = max(spec_files, key=lambda p: p.stat().st_mtime)

    if spec_path.exists():
        # Load JSON and parse into AppSpec
        with open(spec_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        app_spec = AppSpec(**data)  # Pydantic validates structure
    else:
        # Fallback (hardcoded default if no JSON found)
        app_spec = AppSpec(
            app_name="tester-app-6",
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
    print("🚀 Start running Enhancement agent")
    Enhance_agent = ToolCallingAgent(
        tools=[
            # File system operations for enhancements
            read_file, 
            write_file, 
            list_files, 
            mkdir #,
            # run_npm
        ],
        model=OpenAIServerModel("gpt-5-mini"),
        max_steps=5,
        stream_outputs=False,  # Unenable streaming for real-time feedback
        # additional_authorized_imports=["subprocess", "shutil", "json", "re"],        
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
        Enhance_agent.run(prompt_text)

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