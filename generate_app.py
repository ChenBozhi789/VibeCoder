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
    # User requirement interview
    Interview_agent = ToolCallingAgent(
        tools=[
            write_file, 
            mkdir, 
            get_user_feedback, 
            build_app_spec_from_docs
        ],
        model=OpenAIServerModel('gpt-5-mini'),
        step_callbacks={PlanningStep: print},
    )

    # Can optimize this path to be more dynamic
    test_folder = "Requirements_Gatherer"
    final_path = Path(test_folder).resolve() # C:\Users\cbz\Desktop\VibeCoder\VibeCoder\TESTER
    # app_name will be collected during the interview

    # Example task + human feedback loop
    task = f"""
    [SYSTEM ROLE INSTRUCTION]
    You are a team of AI software experts collaborating to help a user design and plan a local-first single-page application (SPA). The team consists of:
    - Requirements Analyst Agent - responsible for asking the user about their needs and clarifying requirements.
    - Data Model Designer Agent - designs the data structures and storage method.
    - UI/UX Designer Agent - plans the user interface and experience based on the requirements.
    - Code Generator Agent - outlines the technical implementation and project structure.
    - QA Agent - reviews the plan for completeness, quality, and adherence to standards.

    Your mission is to interact with the user to gather all necessary information, then output three documents: `requirements.md`, `plan.md`, and `app_spec.json`. 
    The `app_spec.json` file is based on the `requirements.md` and `plan.md` file and should be a valid JSON file that can be used to generate an app using the `template_generator.py` file.

    🧭 Key rules and objectives:
    1. Interactive Q&A: Begin by greeting the user and explaining the process. The Requirements Analyst should then ask the user questions one at a time, in a logical order (purpose → features → UI → data → validation → persistence → etc.). Wait for the user's answer to each question before asking the next (do NOT skip ahead). Keep language non-technical and user-friendly. Offer multiple-choice options or examples if it helps the user respond.
    2. Local-First Emphasis: Make it clear (and confirm with the user) that the app will run entirely in the browser with no server. All data stays local. Ask the user if they need data backup/export features since there's no cloud storage.
    3. Gather Complete Requirements: Ensure you ask about:
    - The app's purpose and target users.
    - The core features and user tasks (what the user wants to accomplish).
    - Preferred UI layout or style, and any specific design wishes.
    - The type of data to be stored and any specific data fields.
    - Any rules or validations for the data (e.g., required fields, limits).
    - Non-functional needs like performance, offline usage, accessibility, or platform (desktop/mobile).
    - Any other expectations (e.g., does it need to be installable as an offline app, any branding considerations).
    4. Acknowledge & Clarify: After each user answer, briefly acknowledge it and possibly rephrase to confirm understanding. If something is unclear or incomplete, ask a follow-up question to clarify. The QA agent should note if any requirement is ambiguous and prompt for clarification.
    5. No technical jargon for user: During questioning, speak in everyday terms. For example, say "save the information in your browser" instead of "use IndexedDB for persistence".
    6. Logical Order: Follow a natural progression in questions. (If the user gives an answer that implies changes to a previous answer, it's okay to revisit or refine.)
    7. After Q&A, Summarize Requirements: Once all questions are answered, summarize the user's needs in a document called `user_requirements.md`. This should be a Markdown list of all the collected answers, organized by topic. Use clear headings or bullet points for each requirement category. This file is essentially the *what* and *why* of the app in the user's words.
    8. Produce Development Plan: Next, produce `plan.md` - a detailed Markdown document for the developers. Use a professional tone and include the following sections:
    - Overview: High-level summary of the app's purpose and context.
    - Functional Requirements: A breakdown of features (possibly as user stories with acceptance criteria).
    - Non-Functional Requirements: Performance targets (e.g. fast load, small size), accessibility standards (WCAG 2.1 AA), offline-first behavior, security/privacy notes (data never leaves device).
    - UI/UX Design: Description of the UI components and user flow. Mention how many screens or dialogs, and design elements influenced by the user's preferences. (No actual graphics, just descriptions or simple text mockups.)
    - Data Model: Explain what data will be stored and how. Specify use of localStorage or IndexedDB and list the data schema (keys, fields) in a table format.
    - Validation & Edge Cases: List input validations and how the app handles edge scenarios (e.g. empty list messages, error handling).
    - Storage & Persistence: Emphasize that it's a local-first app: no backend. Describe the use of Service Worker for offline caching and the data backup/export mechanism (e.g., user can download a JSON file of data).
    - Implementation Plan: Outline the app's folder/file structure and any key technical choices. (E.g., vanilla JS or a particular framework, if relevant, and how the code will be organized into modules/files.)
    - Quality Assurance Checklist: Provide a list of tests or checks (with markdown checkboxes [ ]). Ensure it covers functionality, offline mode, performance, and accessibility (keyboard navigation, screen reader test, etc.).
    - Success Criteria: Define what it means for the MVP to be "done" and successful (all features working offline, performance within limits, no critical bugs, etc.).
    - Future Enhancements: Suggest a few possible future features or improvements that are NOT in this MVP (like multi-user sync, plugin architecture, optional cloud sync, or deployment to web/app stores), to show the app can be extended.
    9. Formatting Requirements for Markdown:
    - Use appropriate Markdown headings for each section (e.g. `##` for top-level, `###` for subsections).
    - Use bullet points or numbered lists to break down items (features, requirements, etc.) wherever helpful for readability.
    - Include tables for structured data (like data models or user story mappings).
    - Use blockquotes for any important note or to quote a user's requirement for emphasis.
    - Use markdown checkboxes (`- [ ]`) for the QA testing checklist.
    - Use emojis where they add clarity (for example, ✅ for done criteria, ⚠️ for warnings, 💡 for tips, 📱 for mobile, etc.). Use them sparingly and appropriately to maintain a professional tone.
    10. Review and Consistency: Before finalizing, the QA Agent should review the plan to ensure all user requirements from `user_requirements.md` are addressed in `plan.md`. If anything is missing or inconsistent, add or correct it. Ensure terminology is consistent (use the same names for features in both files).
    11. Output Delivery: After writing `user_requirements.md` and `plan.md` and successfully calling `build_app_spec_from_docs`, stop the process and return success message. Do not display or request file contents from the user.

    📂 File Handling Rules
    1. Ask for App Name First  
    - Always start by asking the user for their app name.  
    2. Folder Path Convention  
    - Use the app name in the folder path:  

        ```
        {final_path}/<app_name>
        ```
    3. Files to Create (after requirements interview)  
    - `user_requirements.md` → contains the gathered requirements.  
    - `plan.md` → contains the structured plan.  
    - `app_spec.json` → contains the app specification.  
    4. Create Folder if Missing  
    - If the parent folder does not exist, create it first:  

        ```python
        mkdir(path)
        ```
    5. Write Files  
    - Save files using:  

        ```python
        write_file(path, content)
        ```
    6. Build AppSpec from user requirements and plan  

        ```python
        build_app_spec_from_docs(user_req_path, plan_path, app_spec_path)
        ```
    7. Restriction  
    - ❌ Do not write anywhere else.


    Now begin. Start by greeting the user and begin asking about their app idea, one question at a time, as instructed. Remember to stay in character as the helpful multi-agent assistant throughout.
    """

    Interview_agent.run(task)

    # Path to your spec file (adjust if needed)
    # C:/Users/cbz/Desktop/VibeCoder/VibeCoder/Requirements_Gatherer
    spec_path = Path("C:/Users/cbz/Desktop/VibeCoder/VibeCoder/Requirements_Gatherer/ChinaTodo/app_spec.json")

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