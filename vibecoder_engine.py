from pathlib import Path
from dotenv import load_dotenv
import os
import sys
import time
import json
from typing import Optional, Callable, Dict, Any

# Force UTF-8 encoding on Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

load_dotenv()


class VibeCoderEngine:
    """
    Main engine class for orchestrating app generation.
    Encapsulates all agent creation, execution, and state management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the VibeCoderEngine.
        
        Args:
            config: Configuration dictionary with optional keys:
                - api_key: API key for models (defaults to GEMINI_API_KEY env var)
                - base_path: Base path for generated apps (defaults to 'generated_app')
                - max_retries: Maximum retry attempts for agents (defaults to 3)
                - retry_delay: Delay between retries in seconds (defaults to 10)
        """
        self.config = config or {}
        self.api_key = self.config.get('api_key') or os.getenv('GEMINI_API_KEY')
        
        # Fix: Use default value to avoid Path(None, ...) error
        base_path_str = self.config.get('base_path', 'generated_app')
        self.base_path = Path(base_path_str).resolve()
        self.base_path.mkdir(exist_ok=True)
        
        # Retry configuration
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 10)

        # Session state management
        self.session_state = {
            'project_name': None,
            'app_name': None,
            'user_requirements': None,
            'requirements_file_path': None,
            'current_step': None,
            'completed_steps': [],
            'agent_instances': {},  # Save agent instances for reuse
            'conversation_history': []  # Dialog history
        }

        # Model instances (lazy initialization)
        self.models = {
            'gemini_pro': None,
            'gemini_3_pro': None,
        }

        # Agent instances (lazy initialization) - organized by stage
        # Stages: 'prd', 'ui', 'implementation', 'qa', 'auto_fix'
        self.agents: Dict[str, Any] = {
            'prd': None,
            'ui': None,
            'implementation': None,
            'qa': None,
            'auto_fix': None,
        }

        # Progress callback and logger
        self.progress_callback: Optional[Callable] = None
        self.logger = None
        
        # Import agent_state and sync base_path
        # Handle import from VibeCoder subdirectory
        try:
            from VibeCoder.am_tools import agent_state
        except ImportError:
            from am_tools import agent_state
        self.agent_state = agent_state
        # Sync base_path with agent_state
        self.agent_state.base_path = self.base_path

    def _log(self, message: str, level: str = 'info'):
        """Internal logging method."""
        if self.logger:
            getattr(self.logger, level)(message)
        else:
            print(f"[{level.upper()}] {message}")

    def _report_progress(self, step: str, status: str, details: Optional[str] = None):
        """Report progress to callback if set."""
        if self.progress_callback:
            self.progress_callback({
                'step': step,
                'status': status,
                'details': details,
                'timestamp': time.time()
            })

    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable (temporary API issues)."""
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

    def _initialize_models(self):
        """Lazy initialization of AI models."""
        if self.models['gemini_pro'] is None:
            from backend.utils.normalized_litellm_model import NormalizedLiteLLMModel
            self.models['gemini_pro'] = NormalizedLiteLLMModel(
                model_id="gemini/gemini-2.5-pro",
                api_key=self.api_key,
                max_retries=3
            )
        if self.models['gemini_3_pro'] is None:
            from backend.utils.normalized_litellm_model import NormalizedLiteLLMModel
            self.models['gemini_3_pro'] = NormalizedLiteLLMModel(
                model_id="gemini/gemini-3.1-pro-preview",
                api_key=self.api_key,
                max_retries=3
            )

    def get_agent(self, stage: str):
        """
        Get or create an agent for a specific stage.
        Uses lazy initialization - agents are created only when needed.
        
        Args:
            stage: The stage name. Valid values:
                - 'prd': PRD (Product Requirements Document) agent
                - 'ui': UI design agent
                - 'implementation': Implementation agent
                - 'qa': QA (Quality Assurance) agent
                - 'auto_fix': Auto-fix agent
        
        Returns:
            The agent instance for the specified stage
        
        Raises:
            ValueError: If stage is not recognized
        """
        if stage not in self.agents:
            raise ValueError(
                f"Unknown stage: {stage}. "
                f"Valid stages are: {list(self.agents.keys())}"
            )
        
        # Return existing agent if already created
        if self.agents[stage] is not None:
            return self.agents[stage]
        
        # Initialize models if not already done
        self._initialize_models()
        
        # Create agent based on stage
        self._log(f"Creating {stage} agent...")
        
        if stage == 'prd':
            self.agents[stage] = self._create_prd_agent()
        elif stage == 'ui':
            self.agents[stage] = self._create_ui_agent()
        elif stage == 'implementation':
            self.agents[stage] = self._create_implementation_agent()
        elif stage == 'qa':
            self.agents[stage] = self._create_qa_agent()
        elif stage == 'auto_fix':
            self.agents[stage] = self._create_auto_fix_agent()
        
        # Store in session state for tracking
        if 'agent_instances' not in self.session_state:
            self.session_state['agent_instances'] = {}
        self.session_state['agent_instances'][stage] = self.agents[stage]
        
        return self.agents[stage]
    
    # Create agent instances for each stage
    def _get_user_requirements_from_file(self, question_for_user: str) -> str:
        """Get user requirements from the pre-provided input file.
        
        Args:
            question_for_user: The question to ask the user (will be displayed but user input comes from file)
        
        Returns:
            The user's requirements as a string from the input file
        """
        requirements_file = os.environ.get('USER_REQUIREMENTS_FILE')
        if requirements_file and os.path.exists(requirements_file):
            with open(requirements_file, 'r', encoding='utf-8') as f:
                response = f.read().strip()
            return response
        
        # Fallback to environment variable
        return os.environ.get('USER_REQUIREMENTS', '')
    
    # Create PRD agent instance
    def _create_prd_agent(self):
        """Create the PRD (Product Requirements Document) agent. Uses Gemini-3-Pro-Preview."""
        from smolagents import ToolCallingAgent, tool
        
        # Handle import from VibeCoder subdirectory
        try:
            from VibeCoder.am_tools import (
                mkdir, write_file, set_app_name, get_app_name,
                get_prd_path, get_spec_path, build_app_spec_from_docs
            )
        except ImportError:
            from am_tools import (
                mkdir, write_file, set_app_name, get_app_name,
                get_prd_path, get_spec_path, build_app_spec_from_docs
            )
        
        @tool
        def get_user_requirements_tool(question_for_user: str) -> str:
            """Get user requirements from the pre-provided input file.
            
            Args:
                question_for_user: The question to ask the user (displayed but input comes from file)
            
            Returns:
                The user's requirements as a string from the input file
            """
            return self._get_user_requirements_from_file(question_for_user)
        
        self._initialize_models()
        return ToolCallingAgent(
            tools=[
                mkdir,
                get_user_requirements_tool,
                write_file,
                set_app_name,
                get_app_name,
                get_prd_path,
                get_spec_path,
                build_app_spec_from_docs,
            ],
            model=self.models['gemini_3_pro'],
        )
    
    # Create UI agent instance
    def _create_ui_agent(self):
        """Create the UI agent. Uses Gemini-3-Pro-Preview."""
        from smolagents import CodeAgent
        
        # Handle import from VibeCoder subdirectory
        try:
            from VibeCoder.am_tools import (
                mkdir, list_files, read_file, write_file,
                get_app_name, get_prd_path, get_spec_path,
                get_template_path, get_ui_design_path,
                copy_template_to_ui_folder, set_ui_memory,
                get_ui_memory, get_all_ui_memory,
                set_current_project, list_existing_projects,
                get_current_project, generate_ui_structure_json
            )
        except ImportError:
            from am_tools import (
                mkdir, list_files, read_file, write_file,
                get_app_name, get_prd_path, get_spec_path,
                get_template_path, get_ui_design_path,
                copy_template_to_ui_folder, set_ui_memory,
                get_ui_memory, get_all_ui_memory,
                set_current_project, list_existing_projects,
                get_current_project, generate_ui_structure_json
            )
        
        self._initialize_models()
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
            model=self.models['gemini_3_pro'],
            additional_authorized_imports=['json'],
        )
    
    # Create implementation agent instance
    def _create_implementation_agent(self):
        """Create the implementation agent. Uses GPT-5.2-Codex."""
        from smolagents import CodeAgent
        
        # Handle import from VibeCoder subdirectory
        try:
            from VibeCoder.am_tools import (
                read_file, write_file, mkdir, list_files,
                get_app_name, get_prd_path, get_spec_path,
                get_app_folder_path, set_current_project,
                list_existing_projects, get_current_project,
                read_ui_structure_json, generate_ui_structure_json
            )
        except ImportError:
            from am_tools import (
                read_file, write_file, mkdir, list_files,
                get_app_name, get_prd_path, get_spec_path,
                get_app_folder_path, set_current_project,
                list_existing_projects, get_current_project,
                read_ui_structure_json, generate_ui_structure_json
            )
        
        try:
            from backend.services.agent_factory import _OpenAIServerModelNoStop
        except ImportError:
            from VibeCoder.backend.services.agent_factory import _OpenAIServerModelNoStop  # type: ignore
        # 使用标准对话模型 gpt-5.2，避免非 chat 模型在 v1/chat/completions 端点上的 404 错误。
        impl_model = _OpenAIServerModelNoStop(
            os.environ.get("VIBECODER_IMPL_MODEL_ID", "gpt-5.2")
        )
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
            model=impl_model,
            additional_authorized_imports=['json'],
            max_steps=30,
        )
    
    # Create QA agent instance
    def _create_qa_agent(self):
        """Create the QA agent. Uses GPT-5.2-Thinking (reasoning mode)."""
        from smolagents import ToolCallingAgent, tool
        
        # Handle import from VibeCoder subdirectory
        try:
            from VibeCoder.am_tools import (
                read_file, write_file, list_files,
                get_app_name, get_prd_path, get_spec_path,
                get_ui_design_path, get_app_folder_path,
                set_current_project, list_existing_projects,
                get_current_project, read_ui_structure_json,
                validate_implementation, read_project_requirements
            )
        except ImportError:
            from am_tools import (
                read_file, write_file, list_files,
                get_app_name, get_prd_path, get_spec_path,
                get_ui_design_path, get_app_folder_path,
                set_current_project, list_existing_projects,
                get_current_project, read_ui_structure_json,
                validate_implementation, read_project_requirements
            )
        
        @tool
        def get_user_requirements_tool(question_for_user: str) -> str:
            """Get user requirements from the pre-provided input file.
            
            Args:
                question_for_user: The question to ask the user (displayed but input comes from file)
            
            Returns:
                The user's requirements as a string from the input file
            """
            return self._get_user_requirements_from_file(question_for_user)
        
        try:
            from backend.services.agent_factory import _OpenAIServerModelNoStop
        except ImportError:
            from VibeCoder.backend.services.agent_factory import _OpenAIServerModelNoStop  # type: ignore
        # QA 也统一使用 gpt-5.2 对话模型，避免非 chat 模型报错。
        qa_model = _OpenAIServerModelNoStop(
            os.environ.get("VIBECODER_QA_MODEL_ID", "gpt-5.2")
        )
        return ToolCallingAgent(
            tools=[
                read_file,
                write_file,
                list_files,
                get_user_requirements_tool,
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
            model=qa_model,
        )
    
    # Create auto-fix agent instance
    def _create_auto_fix_agent(self):
        """Create the auto-fix agent. Uses Gemini-2.5-Pro for stability."""
        from smolagents import CodeAgent, tool
        
        # Handle import from VibeCoder subdirectory
        try:
            from VibeCoder.am_tools import (
                read_file, write_file, list_files, mkdir,
                get_app_name, get_prd_path, get_spec_path,
                get_ui_design_path, get_app_folder_path,
                set_current_project, list_existing_projects,
                get_current_project, read_ui_structure_json,
                validate_implementation, read_project_requirements,
                generate_vanilla_js_code
            )
        except ImportError:
            from am_tools import (
                read_file, write_file, list_files, mkdir,
                get_app_name, get_prd_path, get_spec_path,
                get_ui_design_path, get_app_folder_path,
                set_current_project, list_existing_projects,
                get_current_project, read_ui_structure_json,
                validate_implementation, read_project_requirements,
                generate_vanilla_js_code
            )
        
        @tool
        def get_user_requirements_tool(question_for_user: str) -> str:
            """Get user requirements from the pre-provided input file.
            
            Args:
                question_for_user: The question to ask the user (displayed but input comes from file)
            
            Returns:
                The user's requirements as a string from the input file
            """
            return self._get_user_requirements_from_file(question_for_user)
        
        self._initialize_models()
        return CodeAgent(
            tools=[
                read_file,
                write_file,
                list_files,
                mkdir,
                get_user_requirements_tool,
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
            # Auto-fix is sensitive to empty model outputs; keep a stable default here.
            model=self.models['gemini_pro'],
            max_steps=30,
        )
    
    def reset_agents(self, stage: Optional[str] = None):
        """
        Reset agent instances. Useful for reinitialization or testing.
        
        Args:
            stage: If provided, reset only the specified stage's agent.
                  If None, reset all agents.
        """
        if stage is not None:
            if stage in self.agents:
                self.agents[stage] = None
                if 'agent_instances' in self.session_state:
                    self.session_state['agent_instances'].pop(stage, None)
                self._log(f"Reset {stage} agent")
        else:
            # Reset all agents
            for stage_name in self.agents:
                self.agents[stage_name] = None
            if 'agent_instances' in self.session_state:
                self.session_state['agent_instances'].clear()
            self._log("Reset all agents")

    def _parse_worker_final_output(self, result: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Try to extract and validate worker final output as JSON.
        Expected format: {"status": "success"|"failed", "summary": "...", "changed_files": [...]}
        Returns the parsed dict if valid, None otherwise.
        """
        if result is None or not isinstance(result, str):
            return None
        s = result.strip()
        # Try direct parse
        try:
            obj = json.loads(s)
            if isinstance(obj, dict) and "status" in obj:
                return obj
        except json.JSONDecodeError:
            pass
        # Try parsing from each "{" position (from last to first) to handle trailing text
        for i in reversed([i for i, c in enumerate(s) if c == "{"]):
            try:
                obj = json.loads(s[i:])
                if isinstance(obj, dict) and "status" in obj:
                    return obj
            except json.JSONDecodeError:
                continue
        return None

    _FINAL_JSON_REMINDER = (
        "\n\n[CRITICAL] Your previous response did not end with valid JSON. "
        "You MUST end with exactly one JSON object, no other text before or after: "
        '{"status": "success" or "failed", "summary": "...", "changed_files": ["path1", "path2"]}. '
        "No other characters outside the JSON."
    )

    def _run_agent_with_retry(
        self,
        agent,
        task: str,
        agent_name: str,
        validate_final_json: bool = False,
    ) -> bool:
        """
        Run an agent with retry logic.
        If validate_final_json is True, the agent's return value is validated as JSON
        (status, summary, changed_files). On format failure, one retry is done with a format reminder.
        """
        self._log(f"{agent_name} is starting")
        self._report_progress(agent_name, 'starting')
        format_retry_done = False

        for attempt in range(self.max_retries):
            try:
                self._log(f"🚀 {agent_name} attempt {attempt + 1}/{self.max_retries}")
                current_task = task
                if format_retry_done:
                    current_task = task + self._FINAL_JSON_REMINDER
                run_result = agent.run(current_task)
                if validate_final_json:
                    parsed = self._parse_worker_final_output(run_result)
                    if parsed is None:
                        if not format_retry_done:
                            format_retry_done = True
                            self._log(f"⚠️ {agent_name} final output was not valid JSON; retrying once with format reminder...")
                            continue
                        self._log(f"❌ {agent_name} final output format invalid after retry (expected JSON with status/summary/changed_files)")
                        self._report_progress(agent_name, 'error', 'Invalid final output format')
                        return False
                self._log(f"✅ {agent_name} completed successfully")
                self._report_progress(agent_name, 'completed')
                self.session_state['completed_steps'].append(agent_name)
                return True
            except Exception as e:
                self._log(f"❌ {agent_name} attempt {attempt + 1} failed: {e}")
                self._log(f"Error type: {type(e).__name__}")
                self._report_progress(agent_name, 'error', str(e))
                format_retry_done = False
                if attempt < self.max_retries - 1:
                    if self._is_retryable_error(e):
                        self._log(f"⏳ Retryable error detected. Waiting {self.retry_delay} seconds...")
                    else:
                        self._log(f"⏳ Non-retryable error, but attempting retry. Waiting {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self._log(f"🔄 All retries exhausted for {agent_name}")
                    return False
        return False

    def generate_app(self, user_requirements: str, use_manager: bool = False) -> bool:
        """
        Main method to generate an app from user requirements.
        
        Args:
            user_requirements: The user's requirements as a string
            
        Returns:
            bool: True if generation completed successfully, False otherwise
        """
        try:
            self.session_state['user_requirements'] = user_requirements
            self._log("Starting app generation...")

            import tempfile

            # Create temporary requirements file for tools that expect it
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
            temp_file.write(user_requirements)
            temp_file.close()
            os.environ['USER_REQUIREMENTS_FILE'] = temp_file.name

            # Import prompt loader
            try:
                from VibeCoder.prompt_loader import prompt_loader
            except ImportError:
                from prompt_loader import prompt_loader

            # Handle import from VibeCoder subdirectory for helper functions
            try:
                from VibeCoder.am_tools import (
                    agent_state, analyze_qa_report_for_fixes_needed,
                    generate_ui_structure_json
                )
            except ImportError:
                from am_tools import (
                    agent_state, analyze_qa_report_for_fixes_needed,
                    generate_ui_structure_json
                )

            if use_manager:
                # ---------------------------------
                # Manager-driven orchestration path
                # ---------------------------------
                try:
                    from backend.services.agent_factory import create_manager_with_workers
                except ImportError:
                    # When running from repo root without package context
                    from VibeCoder.backend.services.agent_factory import create_manager_with_workers  # type: ignore

                task_context = {
                    "user_requirements": user_requirements,
                }
                manager_agent = create_manager_with_workers(task_context=task_context)

                manager_base_prompt = prompt_loader.load_agent_prompt("manager_agent", **task_context)

                manager_task = f"""
                    You are orchestrating the full VibeCoder app generation pipeline for a single local run.

                    User requirements:
                    {user_requirements}

                    Follow the standard phases in order:
                    1) PRD generation
                    2) UI design
                    3) Implementation
                    4) QA
                    5) Auto-fix (only if QA report indicates significant issues)
                """
                
                full_manager_task = manager_base_prompt + "\n\n" + manager_task
                if not self._run_agent_with_retry(manager_agent, full_manager_task, "Manager Agent"):
                    return False

                # Cleanup temp file
                try:
                    os.remove(temp_file.name)
                except Exception:
                    pass

                self._log("✅ App generation completed successfully via Manager Agent!")
                return True

            # ---------------------------------
            # Default sequential pipeline (existing behavior)
            # ---------------------------------

            # 1. PRD Agent execution
            prd_agent = self.get_agent('prd')
            prd_task = prompt_loader.load_agent_prompt("prd_agent")
            if not self._run_agent_with_retry(prd_agent, prd_task, "PRD Agent", validate_final_json=True):
                return False

            # 2. UI Agent execution
            # UI 阶段只需要正确写出文件，不依赖结构化 JSON 结果，
            # 因此不强制要求最终输出为 JSON，避免因格式问题导致整条流水线失败。
            ui_agent = self.get_agent('ui')
            ui_task = prompt_loader.load_agent_prompt("ui_agent")
            if not self._run_agent_with_retry(ui_agent, ui_task, "UI Agent", validate_final_json=False):
                return False

            # Ensure we have a current project before starting implementation phase
            current_project = self.agent_state.get_current_project()
            if not current_project:
                projects = []
                if self.agent_state.base_path.exists():
                    for item in self.agent_state.base_path.iterdir():
                        if item.is_dir():
                            projects.append(item.name)
                if projects:
                    self.agent_state.set_current_project(projects[0])
                    current_project = projects[0]
                    self._log(f"Auto-selected project: {current_project}")
                else:
                    self._log("No projects found. Please run PRD and UI agents first.", 'error')
                    return False
            else:
                self._log(f"Current project: {current_project}")

            # Ensure UI_STRUCTURE.json exists
            app_folder_path = self.agent_state.get_app_folder_path()
            ui_folder_path = f"{app_folder_path}/ui"
            ui_structure_file = f"{ui_folder_path}/UI_STRUCTURE.json"

            if not os.path.exists(ui_structure_file):
                self._log("UI_STRUCTURE.json missing. Generating it now...")
                try:
                    result = generate_ui_structure_json(ui_folder_path)
                    self._log(f"Generated UI_STRUCTURE.json: {result}")
                except Exception as e:
                    self._log(f"Failed to generate UI_STRUCTURE.json: {e}", 'warning')
                    self._log("Continuing anyway...")

            # 3. Implementation Agent execution
            implementation_agent = self.get_agent('implementation')
            implementation_task = prompt_loader.load_agent_prompt("implementation_agent")
            if not self._run_agent_with_retry(implementation_agent, implementation_task, "Implementation Agent", validate_final_json=True):
                return False

            # 4. QA Agent execution
            qa_agent = self.get_agent('qa')
            qa_task = prompt_loader.load_agent_prompt("qa_agent")
            if not self._run_agent_with_retry(qa_agent, qa_task, "QA Agent", validate_final_json=True):
                return False

            # 5. Auto Fix agent (conditional)
            fixes_analysis = analyze_qa_report_for_fixes_needed()
            should_run = fixes_analysis.startswith("YES")

            if should_run:
                self._log(f"Auto-fix needed: {fixes_analysis}")
                auto_fix_agent = self.get_agent('auto_fix')
                auto_fix_task = prompt_loader.load_agent_prompt("auto_fix_agent")
                if not self._run_agent_with_retry(auto_fix_agent, auto_fix_task, "Auto Fix Agent", validate_final_json=True):
                    self._log("Auto Fix Agent failed, but continuing...", 'warning')
            else:
                self._log(f"No auto-fix needed: {fixes_analysis}")

            # Cleanup
            try:
                os.remove(temp_file.name)
            except Exception:
                pass

            self._log("✅ App generation completed successfully!")
            return True
            
        except Exception as e:
            self._log(f"Error in app generation: {e}", 'error')
            import traceback
            self._log(traceback.format_exc(), 'error')
            return False

    def set_progress_callback(self, callback: Callable):
        """Set a callback function for progress updates."""
        self.progress_callback = callback

    def set_logger(self, logger):
        """Set a logger instance."""
        self.logger = logger

    def get_session_state(self) -> Dict[str, Any]:
        """Get current session state."""
        return self.session_state.copy()

    def reset_session(self):
        """Reset session state."""
        self.session_state = {
            'project_name': None,
            'app_name': None,
            'user_requirements': None,
            'requirements_file_path': None,
            'current_step': None,
            'completed_steps': [],
            'agent_instances': {},
            'conversation_history': []
        }
        # Optionally reset agents when resetting session
        # Uncomment the next line if you want to reset agents on session reset
        # self.reset_agents()