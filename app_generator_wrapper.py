#!/usr/bin/env python3
"""
Wrapper script for app_generator.py that handles user input from Streamlit GUI
"""
import sys
import os
import tempfile
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    # Set environment variables for UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# Enhanced error handling for API issues
def is_retryable_error(error):
    """Check if an error is retryable (temporary API issues)"""
    error_str = str(error).lower()
    retryable_patterns = [
        'no choices',
        'unexpected api response',
        'rate limit',
        'timeout',
        'connection',
        'temporary',
        'service unavailable',
        'internal server error'
    ]
    return any(pattern in error_str for pattern in retryable_patterns)

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

def main():
    # Get user requirements from command line argument or environment variable
    if len(sys.argv) > 1:
        user_requirements = sys.argv[1]
    else:
        user_requirements = os.environ.get('USER_REQUIREMENTS', '')
    
    if not user_requirements:
        print("Error: No user requirements provided")
        sys.exit(1)
    
    # Create a temporary file with user requirements
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(user_requirements)
    temp_file.close()
    
    # Set environment variable for the requirements file
    os.environ['USER_REQUIREMENTS_FILE'] = temp_file.name
    
    # The get_user_requirements function will be monkey patched after import
    
    # Now run the original app_generator.py logic
    try:
        print("Starting app generation with user requirements...")
        
        # Import the main components we need
        from prompt_loader import prompt_loader
        # Import tools directly (same as original app_generator.py)
        from am_tools import (
            list_files, write_file, mkdir, read_file, build_app_spec_from_docs,
            analyze_ui_structure, generate_functional_code, implement_data_persistence,
            implement_state_management, validate_implementation, read_project_requirements,
            generate_ui_structure_json, read_ui_structure_json,
            # Agent state management tools
            get_user_requirements, set_app_name, set_current_project, list_existing_projects,
            get_current_project, get_app_name, get_prd_path, get_spec_path, get_template_path,
            get_ui_design_path, get_app_folder_path, set_ui_memory, get_ui_memory, get_all_ui_memory,
            get_feedback_tickets_path, get_enhancement_summary_path, get_test_report_path,
            copy_template_to_ui_folder, analyze_qa_report_for_fixes_needed, generate_vanilla_js_code,
            agent_state
        )
        
        # Import the agents and models
        from smolagents import PlanningStep, CodeAgent, ToolCallingAgent
        from smolagents.models import OpenAIServerModel, LiteLLMModel
        
        # Create a new get_user_requirements function that reads from file
        from smolagents import tool
        
        @tool
        def get_user_requirements_from_file(question_for_user: str) -> str:
            """Get user requirements from the pre-provided input file.
            
            Args:
                question_for_user: The question to ask the user (will be displayed but user input comes from file)
            
            Returns:
                The user's requirements as a string from the input file
            """
            print(question_for_user)
            
            # Read from the requirements file
            requirements_file = os.environ.get('USER_REQUIREMENTS_FILE')
            if requirements_file and os.path.exists(requirements_file):
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    response = f.read().strip()
                # Clean up the temporary file
                try:
                    os.remove(requirements_file)
                except:
                    pass
                return response
            
            # Fallback to the original user_requirements
            return user_requirements
        
        # Initialize models
        gemini_pro_model = LiteLLMModel(
            model_id="gemini/gemini-2.5-pro",
            api_key=os.environ.get("GEMINI_API_KEY"),
            max_retries=3
        )
        
        # Create agents
        prd_agent = ToolCallingAgent(
            tools=[
                mkdir,
                get_user_requirements_from_file,
                write_file,
                set_app_name,
                get_app_name,
                get_prd_path,
                get_spec_path,
                build_app_spec_from_docs,
            ],
            model=OpenAIServerModel('gpt-5'),
        )
        
        # 1. PRD Agent execution
        prd_task = prompt_loader.load_agent_prompt("prd_agent")
        
        # Add retry mechanism for PRD Agent
        max_retries = 3
        retry_delay = 10  # seconds

        for attempt in range(max_retries):
            try:
                print(f"PRD Agent attempt {attempt + 1}/{max_retries}")
                prd_agent.run(prd_task)
                print("PRD Agent completed successfully")
                break
            except Exception as e:
                print(f"PRD Agent attempt {attempt + 1} failed: {e}")
                print(f"Error type: {type(e).__name__}")
                
                if attempt < max_retries - 1 and is_retryable_error(e):
                    print(f"Retryable error detected. Waiting {retry_delay} seconds before retry...")
                    import time
                    time.sleep(retry_delay)
                elif attempt < max_retries - 1:
                    print(f"Non-retryable error, but attempting retry anyway. Waiting {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                else:
                    print("All retries exhausted. Continuing with UI phase...")

        # 2. UI agent - CodeAgent
        ui_agent = CodeAgent(
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

        ui_task = prompt_loader.load_agent_prompt("ui_agent")

        # Add retry mechanism for UI Agent
        for attempt in range(max_retries):
            try:
                print(f"UI Agent attempt {attempt + 1}/{max_retries}")
                ui_agent.run(ui_task)
                print("UI Agent completed successfully")
                break
            except Exception as e:
                print(f"UI Agent attempt {attempt + 1} failed: {e}")
                print(f"Error type: {type(e).__name__}")
                
                if attempt < max_retries - 1:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    import time
                    time.sleep(retry_delay)
                else:
                    print("All retries exhausted. Continuing with implementation phase...")

        print("\n--- Implementation Phase ---")

        # Ensure we have a current project before starting implementation phase
        current_project = agent_state.get_current_project()
        if not current_project:
            print("No current project set. Auto-selecting...")
            projects = []
            if agent_state.base_path.exists():
                for item in agent_state.base_path.iterdir():
                    if item.is_dir():
                        projects.append(item.name)
            if projects:
                agent_state.set_current_project(projects[0])
                current_project = projects[0]
                print(f"Auto-selected project: {projects[0]}")
            else:
                print("No projects found. Please run PRD and UI agents first.")
                sys.exit(1)

        print(f"Implementation Agent working on project: {current_project}")

        # Pre-check: Ensure UI_STRUCTURE.json exists
        app_folder_path = agent_state.get_app_folder_path()
        ui_folder_path = f"{app_folder_path}/ui"
        ui_structure_file = f"{ui_folder_path}/UI_STRUCTURE.json"

        print(f"Checking for UI_STRUCTURE.json at: {ui_structure_file}")
        if not os.path.exists(ui_structure_file):
            print("UI_STRUCTURE.json missing. Generating it now...")
            try:
                result = generate_ui_structure_json(ui_folder_path)
                print(f"Generated UI_STRUCTURE.json: {result}")
            except Exception as e:
                print(f"Failed to generate UI_STRUCTURE.json: {e}")
                print("Continuing anyway...")
        else:
            print("UI_STRUCTURE.json exists")

        # 3. Single Implementation Agent
        implementation_agent = CodeAgent(
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

        implementation_task = prompt_loader.load_agent_prompt("implementation_agent")

        # Add a retry mechanism
        max_retries = 3
        retry_delay = 10  # seconds

        for attempt in range(max_retries):
            try:
                print(f"Implementation Agent attempt {attempt + 1}/{max_retries}")
                implementation_agent.run(implementation_task)
                print("Implementation Agent completed successfully")
                break
            except Exception as e:
                print(f"Implementation Agent attempt {attempt + 1} failed: {e}")
                print(f"Error type: {type(e).__name__}")
                
                if attempt < max_retries - 1:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    import time
                    time.sleep(retry_delay)
                else:
                    print("All retries exhausted. Continuing with validation phase...")

        print("\n--- Implementation Validation ---")

        # 4. Validation
        validation_agent = ToolCallingAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            get_app_name,
            get_app_folder_path,
            set_current_project,
            list_existing_projects,
            get_current_project,
            validate_implementation
        ],
        model=gemini_pro_model,
        max_steps=10,
        )

        validation_task = prompt_loader.load_agent_prompt("validation_agent")

        # Add retry mechanism for Validation Agent
        for attempt in range(max_retries):
            try:
                print(f"Validation Agent attempt {attempt + 1}/{max_retries}")
                validation_agent.run(validation_task)
                print("Validation Agent completed successfully")
                break
            except Exception as e:
                print(f"Validation Agent attempt {attempt + 1} failed: {e}")
                print(f"Error type: {type(e).__name__}")
                
                if attempt < max_retries - 1:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    import time
                    time.sleep(retry_delay)
                else:
                    print("All retries exhausted. Continuing with QA phase...")

        # 5. QA agent
        qa_agent = ToolCallingAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            get_user_requirements_from_file,
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

        qa_task = prompt_loader.load_agent_prompt("qa_agent")

        # Add retry mechanism for QA Agent
        print("Start running QA agent")
        for attempt in range(max_retries):
            try:
                print(f"QA Agent attempt {attempt + 1}/{max_retries}")
                qa_agent.run(qa_task)
                print("QA Agent completed successfully")
                break
            except Exception as e:
                print(f"QA Agent attempt {attempt + 1} failed: {e}")
                print(f"Error type: {type(e).__name__}")
                
                if attempt < max_retries - 1:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    import time
                    time.sleep(retry_delay)
                else:
                    print("All retries exhausted. Continuing with Auto Fix phase...")

        # 6. Auto Fix agent (conditional)
        print("\n--- Auto Fix Decision Phase ---")
        
        print("Analyzing QA test report to determine if fixes are needed...")
        fixes_analysis = analyze_qa_report_for_fixes_needed()
        print(f"Analysis Result: {fixes_analysis}")
        
        if fixes_analysis.startswith("YES"):
            print("Fixes needed! Starting Auto Fix agent...")
            print(f"Reason: {fixes_analysis}")
            
            auto_fix_agent = CodeAgent(
               tools=[
                  read_file,
                  write_file,
                  list_files,
                  mkdir,
                  get_user_requirements_from_file,
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
               max_steps=30,  # Increased steps for more thorough fixing
            )

            auto_fix_task = prompt_loader.load_agent_prompt("auto_fix_agent")

            # Add a retry mechanism for Auto Fix agent
            max_retries = 3
            retry_delay = 10  # seconds

            for attempt in range(max_retries):
                try:
                    print(f"Auto Fix agent attempt {attempt + 1}/{max_retries}")
                    auto_fix_agent.run(auto_fix_task)
                    print("Auto Fix agent completed successfully")
                    break
                except Exception as e:
                    print(f"Auto Fix agent attempt {attempt + 1} failed: {e}")
                    print(f"Error type: {type(e).__name__}")
                    
                    if attempt < max_retries - 1:
                        print(f"Waiting {retry_delay} seconds before retry...")
                        import time
                        time.sleep(retry_delay)
                    else:
                        print("All retries exhausted. Continuing with next phase...")
        else:
            print("No fixes needed! Skipping Auto Fix agent.")
            print(f"Reason: {fixes_analysis}")
            print("Proceeding to next phase...")
        
    except Exception as e:
        print(f"Error in app generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()