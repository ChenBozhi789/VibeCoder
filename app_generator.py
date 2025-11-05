from smolagents import PlanningStep, CodeAgent, ToolCallingAgent, tool
from smolagents.models import OpenAIServerModel, LiteLLMModel
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
    copy_template_to_ui_folder, analyze_qa_report_for_fixes_needed, generate_vanilla_js_code
) 
from pathlib import Path
from datetime import datetime
import json, os
from prompt_loader import prompt_loader
import time
import litellm

# Force UTF-8 encoding on Windows
import sys
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

# Import agent_state from am_tools for backward compatibility
from am_tools import agent_state

os.environ['LITELLM_LOG'] = 'DEBUG'

# initialize LiteLLMModel
gemini_model = LiteLLMModel(
    model_id="gemini/gemini-2.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY"),
    max_retries=3
)

gemini_pro_model = LiteLLMModel(
    model_id="gemini/gemini-2.5-pro",
    api_key=os.environ.get("GEMINI_API_KEY"),
    max_retries=3
)

# 1. PRD Agent (Enhanced - now includes spec generation)
prd_agent = ToolCallingAgent(
    tools=[
        mkdir,
        get_user_requirements,
        write_file,
        set_app_name,
        get_app_name,
        get_prd_path,
        get_spec_path,
        build_app_spec_from_docs,
    ],
    model=OpenAIServerModel('gpt-5'),
    # step_callbacks={PlanningStep: print},
)

# Can optimize this path to be more dynamic
storage_folder = "generated_app"
# Final path: C:\Users\cbz\Desktop\VibeCoder\VibeCoder\generated_app
final_path = Path(storage_folder).resolve()

# Agent definitions (will be executed only when run directly)
if __name__ == "__main__":
    # 1. PRD Agent execution
    prd_task = prompt_loader.load_agent_prompt("prd_agent")
    
    # Add retry mechanism for PRD Agent
    max_retries = 3
    retry_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            print(f"🚀 PRD Agent attempt {attempt + 1}/{max_retries}")
            prd_agent.run(prd_task)
            print("✅ PRD Agent completed successfully")
            break
        except Exception as e:
            print(f"❌ PRD Agent attempt {attempt + 1} failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            if attempt < max_retries - 1 and is_retryable_error(e):
                print(f"⏳ Retryable error detected. Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            elif attempt < max_retries - 1:
                print(f"⏳ Non-retryable error, but attempting retry anyway. Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("🔄 All retries exhausted. Continuing with UI phase...")

    # 2. UI agent
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
        # model=OpenAIServerModel('gpt-5'),
        model=gemini_pro_model,
        additional_authorized_imports=['json'],
        # step_callbacks={PlanningStep: print},
    )

    ui_task = prompt_loader.load_agent_prompt("ui_agent")

    # Add retry mechanism for UI Agent
    for attempt in range(max_retries):
        try:
            print(f"🚀 UI Agent attempt {attempt + 1}/{max_retries}")
            ui_agent.run(ui_task)
            print("✅ UI Agent completed successfully")
            break
        except Exception as e:
            print(f"❌ UI Agent attempt {attempt + 1} failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print("🔄 All retries exhausted. Continuing with implementation phase...")

    # print("\n[INFO] UI Agent finished. Waiting for 30 seconds to ensure a fresh API rate limit window...")
    # time.sleep(30)

    print("\n--- Implementation Phase ---")

    # Ensure we have a current project before starting implementation phase
    current_project = agent_state.get_current_project()
    if not current_project:
        print("❌ No current project set. Auto-selecting...")
        projects = []
        if agent_state.base_path.exists():
            for item in agent_state.base_path.iterdir():
                if item.is_dir():
                    projects.append(item.name)
        if projects:
            agent_state.set_current_project(projects[0])
            current_project = projects[0]
            print(f"✅ Auto-selected project: {projects[0]}")
        else:
            print("❌ No projects found. Please run PRD and UI agents first.")
            exit(1)

    print(f"✅ Implementation Agent working on project: {current_project}")

    # Pre-check: Ensure UI_STRUCTURE.json exists
    app_folder_path = agent_state.get_app_folder_path()
    ui_folder_path = f"{app_folder_path}/ui"
    ui_structure_file = f"{ui_folder_path}/UI_STRUCTURE.json"

    print(f"🔍 Checking for UI_STRUCTURE.json at: {ui_structure_file}")
    if not os.path.exists(ui_structure_file):
        print("⚠️ UI_STRUCTURE.json missing. Generating it now...")
        try:
            from am_tools import generate_ui_structure_json
            result = generate_ui_structure_json(ui_folder_path)
            print(f"✅ Generated UI_STRUCTURE.json: {result}")
        except Exception as e:
            print(f"❌ Failed to generate UI_STRUCTURE.json: {e}")
            print("🔄 Continuing anyway...")
    else:
        print("✅ UI_STRUCTURE.json exists")

    # 3. Single Implementation Agent - combines plan, utils, storage, state, markup, frontend, styling
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
            print(f"🚀 Implementation Agent attempt {attempt + 1}/{max_retries}")
            implementation_agent.run(implementation_task)
            print("✅ Implementation Agent completed successfully")
            break
        except Exception as e:
            print(f"❌ Implementation Agent attempt {attempt + 1} failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print("🔄 All retries exhausted. Continuing with validation phase...")

    print("\n--- Implementation Validation ---")

    # 4. Validation - Quick check that everything works together
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
    max_steps=10,  # limit steps to prevent token overflow
    )

    # Load validation task from template
    validation_task = prompt_loader.load_agent_prompt("validation_agent")

    # Add retry mechanism for Validation Agent
    for attempt in range(max_retries):
        try:
            print(f"🚀 Validation Agent attempt {attempt + 1}/{max_retries}")
            validation_agent.run(validation_task)
            print("✅ Validation Agent completed successfully")
            break
        except Exception as e:
            print(f"❌ Validation Agent attempt {attempt + 1} failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print("🔄 All retries exhausted. Continuing with QA phase...")

    # 4. QA agent
    qa_agent = ToolCallingAgent(
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
    # step_callbacks={PlanningStep: print},
    )

    qa_task = prompt_loader.load_agent_prompt("qa_agent")

    # Add retry mechanism for QA Agent
    print("🚀 Start running QA agent")
    for attempt in range(max_retries):
        try:
            print(f"🚀 QA Agent attempt {attempt + 1}/{max_retries}")
            qa_agent.run(qa_task)
            print("✅ QA Agent completed successfully")
            break
        except Exception as e:
            print(f"❌ QA Agent attempt {attempt + 1} failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print("🔄 All retries exhausted. Continuing with Auto Fix phase...")

    # 5. Conditional Auto Fix agent - only runs if QA report indicates fixes are needed
    print("\n--- Auto Fix Decision Phase ---")
    
    # Analyze QA report to determine if fixes are needed
    print("🔍 Analyzing QA test report to determine if fixes are needed...")
    fixes_analysis = analyze_qa_report_for_fixes_needed()
    print(f"📊 Analysis Result: {fixes_analysis}")
    
    if fixes_analysis.startswith("YES"):
        print("🔧 Fixes needed! Starting Auto Fix agent...")
        print(f"💡 Reason: {fixes_analysis}")
        
        auto_fix_agent = CodeAgent(
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
           max_steps=30,  # Increased steps for more thorough fixing
           # step_callbacks={PlanningStep: print},
        )

        auto_fix_task = prompt_loader.load_agent_prompt("auto_fix_agent")

        # Add a retry mechanism for Auto Fix agent
        max_retries = 3
        retry_delay = 10  # seconds

        for attempt in range(max_retries):
            try:
                print(f"🚀 Auto Fix agent attempt {attempt + 1}/{max_retries}")
                auto_fix_agent.run(auto_fix_task)
                print("✅ Auto Fix agent completed successfully")
                break
            except Exception as e:
                print(f"❌ Auto Fix agent attempt {attempt + 1} failed: {e}")
                print(f"Error type: {type(e).__name__}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    print("🔄 All retries exhausted. Continuing with next phase...")
    else:
        print("✅ No fixes needed! Skipping Auto Fix agent.")
        print(f"💡 Reason: {fixes_analysis}")
        print("🚀 Proceeding to next phase...")

