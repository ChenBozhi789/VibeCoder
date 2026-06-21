"""
与 API 调用相关的 App 生成服务：供 FastAPI 后台任务调用，负责 task_id 沙箱、进度上报与管线执行。
本质与根目录的 app_generator.py 相同（都是执行 app generation），但本模块是 API 入口，
包含 task_manager、BackgroundTasks、按 task_id 的沙箱等；app_generator.py 为纯后端 CLI，无 API/前端。
"""
import sys
import os
import time
from pathlib import Path

# --- 关键：添加根目录到 sys.path 以便导入根目录的模块 ---
# 假设 backend/services/generator_service.py 在 backend/services 下
# 我们需要回退两层找到 am_tools
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent
sys.path.append(str(root_dir))
# -----------------------------------------------------

from smolagents import CodeAgent, ToolCallingAgent, OpenAIServerModel, tool
from smolagents.utils import AgentGenerationError
from backend.utils.task_manager import task_manager, TaskStatus
from backend.services.agent_factory import (
    create_prd_worker_agent,
    create_ui_worker_agent,
    create_impl_layout_worker_agent,
    create_impl_logic_worker_agent,
    create_impl_persistence_worker_agent,
    create_qa_worker_agent,
    create_autofix_worker_agent,
    _OpenAIServerModelNoStop,
)

# import tools
try:
    from am_tools import (
        mkdir,
        write_file,
        read_file,
        list_files,
        build_app_spec_from_docs,
        set_app_name,
        get_app_name,
        get_prd_path,
        get_spec_path,
        get_user_requirements,
        get_template_path,
        get_ui_design_path,
        copy_template_to_ui_folder,
        set_ui_memory,
        get_ui_memory,
        get_all_ui_memory,
        get_current_project,
        generate_ui_structure_json,
        read_ui_structure_json,
        validate_implementation,
        read_project_requirements,
        analyze_qa_report_for_fixes_needed,
        generate_vanilla_js_code,
        agent_state,
        get_app_folder_path,
    )
    from prompt_loader import prompt_loader
except ImportError as e:
    print(f"Import Error: {e}. Make sure am_tools.py is in the root directory.")

try:
    from litellm.exceptions import RateLimitError as _LiteLLMRateLimitError
except ImportError:
    _LiteLLMRateLimitError = None  # type: ignore[misc, assignment]


def _friendly_api_error_message(exc: BaseException) -> str | None:
    """Turn common provider errors into short, actionable task log lines."""
    e: BaseException | None = exc
    seen: set[int] = set()
    while e is not None and id(e) not in seen:
        seen.add(id(e))
        text = f"{type(e).__name__}: {e}"
        if _LiteLLMRateLimitError is not None and isinstance(e, _LiteLLMRateLimitError):
            return (
                "Gemini API 配额或频率已达上限（429）。"
                "请在前端改用「gemini-2.5-pro」或「gemini-2.5-flash」，"
                "或设置环境变量 VIBECODER_GEMINI_3_MODEL_ID 指向仍有额度的模型；"
                "也可在 Google AI 控制台检查计费与每日配额，通常约 24 小时后按日配额会重置。"
            )
        if "429" in text or "RateLimitError" in text or "RESOURCE_EXHAUSTED" in text:
            if "quota" in text.lower() or "generativelanguage" in text.lower():
                return (
                    "Gemini API 配额或频率已达上限（429）。"
                    "请换用 gemini-2.5-pro / gemini-2.5-flash 或调整 VIBECODER_GEMINI_3_MODEL_ID；"
                    "详见 https://ai.google.dev/gemini-api/docs/rate-limits"
                )
        e = e.__cause__

    return None


def _is_transient_generation_error(exc: BaseException) -> bool:
    """Heuristics for provider hiccups that are often fixed by one retry."""
    text = str(exc).lower()
    patterns = (
        "no choices",
        "returned no choices",
        "list index out of range",
        "resource_exhausted",
        "rate limit",
        "429",
        "timeout",
        "service unavailable",
    )
    return any(p in text for p in patterns)


# 初始化模型 (全局复用)
_UNIFIED_MODEL_ID = os.environ.get("VIBECODER_FORCE_MODEL_ID", "gpt-5.4-2026-03-05")
_UNIFIED_MODEL = _OpenAIServerModelNoStop(_UNIFIED_MODEL_ID)

def get_model_by_name(model_name: str):
    # Temporarily force all stages/models to a single GPT model.
    return _UNIFIED_MODEL


def _get_autofix_model():
    """
    Auto-fix uses a stable Gemini model by default.
    Set VIBECODER_AUTOFIX_MODEL=flash to force gemini-2.5-flash.
    """
    return _UNIFIED_MODEL


def _resolve_stage_models(model_name: str):
    """
    Route Gemini 3.1 only to core generation stages.
    - Core stages (PRD/UI/Implementation): use selected model
    - Non-core stages (QA and other support steps): prefer Gemini 2.5 Pro when selected is Gemini 3.1
    """
    selected_model = get_model_by_name(model_name)
    return selected_model, selected_model

def run_app_generation_task(task_id: str, user_requirements: str, model_name: str = "gpt-5.4-2026-03-05"):
    """
    这是后台执行的主函数。
    它是同步的，将由 FastAPI 的 BackgroundTasks 在线程池中运行。
    """
    try:
        core_model, non_core_model = _resolve_stage_models(model_name)
        # 0. 系统托管沙箱初始化：为当前任务创建独立目录，并绑定到 agent_state.base_path
        #
        # 设计理念：
        #   - 「System prepares the room; the Agent just works in it」
        #   - 每个 task_id 对应一个完全隔离的文件系统沙箱
        #   - 所有 Agent 文件操作都被硬绑定在该沙箱之下，禁止逃逸
        project_root = Path(__file__).resolve().parent.parent.parent
        task_sandbox_root = (project_root / "generated_app" / task_id).resolve()
        task_sandbox_root.mkdir(parents=True, exist_ok=True)

        # 将 am_tools 的全局 agent_state base_path 指向本任务沙箱
        agent_state.base_path = task_sandbox_root
        # 注入用户需求，使 get_user_requirements 在后台/API 模式下直接返回此项，不再等待 stdin
        agent_state.initial_user_requirements = user_requirements or ""

        # 1. 任务开始
        task_manager.update_task(
            task_id,
            status=TaskStatus.RUNNING.value,
            progress=0,
            log=f"Task initializing: created dedicated sandbox directory: {task_sandbox_root}",
        )

        # Feature flag: use hierarchical manager orchestration instead of sequential pipeline
        use_manager = os.environ.get("USE_MANAGER_ORCHESTRATION", "false").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )

        if use_manager:
            # ------------------------------
            # Manager-style orchestration（Python 负责调度，每个 worker 使用自己的 prompt）
            # ------------------------------

            @tool
            def update_phase_status(phase: str, progress: int, message: str = "") -> str:
                """
                Update task progress and log from inside the manager-style orchestration.

                Args:
                    phase: Logical phase name, e.g. \"PRD\", \"UI\", \"Implementation\", \"QA\", \"DONE\".
                    progress: Overall numeric progress percentage from 0 to 100.
                    message: Optional human-readable status message for this phase.

                Returns:
                    A short confirmation string.
                """
                log_msg = f"[{phase}] {message}" if message else f"[{phase}]"
                task_manager.update_task(task_id, progress=progress, log=log_msg)
                return "ok"

            task_context = {
                "user_requirements": user_requirements,
                "manager_tools": [update_phase_status],
            }

            task_manager.update_task(
                task_id,
                progress=5,
                log=f"🤖 Using hierarchical orchestration with model: {model_name}...",
            )

            # 构建各阶段 worker agents（Implementation 拆为 layout → logic → persistence）
            core_context = {
                **task_context,
                "model": core_model,
            }
            qa_context = {
                **task_context,
                "model": non_core_model,
            }
            prd_agent = create_prd_worker_agent(core_context)
            ui_agent = create_ui_worker_agent(core_context)
            impl_layout_agent = create_impl_layout_worker_agent(core_context)
            impl_logic_agent = create_impl_logic_worker_agent(core_context)
            impl_persistence_agent = create_impl_persistence_worker_agent(core_context)
            qa_agent = create_qa_worker_agent(qa_context)

            # ==========================
            # Phase 1: PRD
            # ==========================
            update_phase_status("PRD", 5, "Generating PRD and app_spec...")
            base_prd_prompt = prompt_loader.load_agent_prompt("prd_agent")
            full_prd_prompt = f"{base_prd_prompt}\n\n[USER REQUIREMENTS]\n{user_requirements}"
            prd_agent.run(full_prd_prompt)
            update_phase_status("PRD", 25, "PRD 阶段完成")

            # ==========================
            # Phase 2: UI
            # ==========================
            update_phase_status("UI", 30, "Generating UI...")
            ui_task = prompt_loader.load_agent_prompt("ui_agent")
            for _attempt in range(2):
                try:
                    ui_agent.run(ui_task)
                    break
                except AgentGenerationError as _e:
                    if _attempt == 0 and _is_transient_generation_error(_e):
                        update_phase_status("UI", 30, "UI stage got empty/invalid model output, retrying once...")
                        time.sleep(2)
                        continue
                    raise
            update_phase_status("UI", 50, "UI 阶段完成")

            # ==========================
            # Phase 3: Implementation (三子阶段: layout → logic → persistence)
            # ==========================
            update_phase_status("Implementation", 55, "Implementing (Layout markup HTML)...")

            # 确保 UI_STRUCTURE.json 存在
            app_folder_path = agent_state.get_app_folder_path()
            ui_structure_file = os.path.join(app_folder_path, "ui", "UI_STRUCTURE.json")
            if not os.path.exists(ui_structure_file):
                update_phase_status("Implementation", 58, "UI_STRUCTURE.json missing, generating...")
                try:
                    generate_ui_structure_json(os.path.join(app_folder_path, "ui"))
                except Exception as e:
                    update_phase_status("Implementation", 58, f"Failed to generate UI structure file: {e}")

            layout_task = prompt_loader.load_agent_prompt("impl_layout_agent")
            impl_layout_agent.run(layout_task)
            update_phase_status("Implementation", 65, "Layout completed, implementing Logic (state + events)...")

            logic_task = prompt_loader.load_agent_prompt("impl_logic_agent")
            impl_logic_agent.run(logic_task)
            update_phase_status("Implementation", 75, "Logic completed, adding Persistence...")

            persistence_task = prompt_loader.load_agent_prompt("impl_persistence_agent")
            impl_persistence_agent.run(persistence_task)
            update_phase_status("Implementation", 80, "Implementation phase completed")

            # ==========================
            # Phase 4: QA & Auto-Fix
            # ==========================
            update_phase_status("QA", 85, "Running QA tests...")
            qa_task = prompt_loader.load_agent_prompt("qa_agent")
            qa_agent.run(qa_task)

            fixes_analysis = analyze_qa_report_for_fixes_needed()
            if fixes_analysis.startswith("YES"):
                update_phase_status("AutoFix", 90, "Issues detected, running auto-fix...")
                # Keep auto-fix on a stable model to avoid empty-response loops
                # seen on gemini-3.1-pro-preview in CodeAgent mode.
                auto_fix_context = {
                    **task_context,
                    "model": _get_autofix_model(),
                }
                auto_fix_agent = create_autofix_worker_agent(auto_fix_context)
                auto_fix_task = prompt_loader.load_agent_prompt("auto_fix_agent")
                for _attempt in range(2):
                    try:
                        auto_fix_agent.run(auto_fix_task)
                        break
                    except AgentGenerationError as _e:
                        if "no choices" not in str(_e).lower() and "returned no choices" not in str(_e).lower():
                            raise
                        if _attempt == 0:
                            update_phase_status("AutoFix", 90, "Auto-fix got empty response, retrying once...")
                            continue
                        raise
                update_phase_status("AutoFix", 95, "Auto-fix completed")
            else:
                update_phase_status("AutoFix", 90, f"No auto-fix needed: {fixes_analysis}")

            # 完成：读取最终项目路径并更新任务状态
            final_path = agent_state.get_app_folder_path()
            task_manager.update_task(
                task_id,
                status=TaskStatus.COMPLETED.value,
                progress=100,
                log="🎉 All tasks completed! (Manager-style orchestration)",
                result={
                    "app_name": agent_state.get_app_name(),
                    "path": str(final_path),
                },
            )
            return

        # ------------------------------
        # 默认：顺序式管线（原有实现）
        # ------------------------------

        # 定义重试参数
        max_retries = 3
        retry_delay = 5

        # ==========================================
        # Phase 1: PRD Generation
        # ==========================================
        task_manager.update_task(task_id, progress=5, log=f"[1/4] Starting PRD Agent with {model_name}...")
        
        # 实例化 Agent (每次任务重新实例化以保证状态隔离)
        prd_agent = ToolCallingAgent(
            tools=[
                mkdir, 
                get_user_requirements, 
                write_file, 
                set_app_name, 
                get_app_name, 
                get_prd_path, 
                get_spec_path, 
                build_app_spec_from_docs],
            model=core_model,
        )
        
        # 加载 Prompt 并注入用户需求
        base_prd_prompt = prompt_loader.load_agent_prompt("prd_agent")
        # 关键修改：将用户输入直接追加到 Prompt，确保 Agent 知道要做什么
        full_prd_prompt = f"{base_prd_prompt}\n\n[USER REQUIREMENTS]\n{user_requirements}"
        
        for attempt in range(max_retries):
            try:
                task_manager.update_task(task_id, log=f"PRD Agent attempt ({attempt + 1}/{max_retries})...")
                prd_agent.run(full_prd_prompt)
                task_manager.update_task(task_id, log="✅ PRD generation completed")
                break
            except Exception as e:
                task_manager.update_task(task_id, log=f"❌ PRD Agent 失败: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception("PRD Agent failed after retries")

        task_manager.update_task(task_id, progress=25, log="PRD phase completed")

        # ==========================================
        # Phase 2: UI Design
        # ==========================================
        task_manager.update_task(task_id, progress=30, log="[2/4] Starting UI Agent...")
        
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
                get_current_project,
                generate_ui_structure_json,
            ],
            model=core_model,
            additional_authorized_imports=['json']
        )
        ui_task = prompt_loader.load_agent_prompt("ui_agent")

        for _attempt in range(2):
            try:
                ui_agent.run(ui_task)
                break
            except AgentGenerationError as _e:
                if _attempt == 0 and _is_transient_generation_error(_e):
                    task_manager.update_task(
                        task_id,
                        log="⚠️ UI Agent got empty/invalid model output, retrying once..."
                    )
                    time.sleep(2)
                    continue
                raise
        task_manager.update_task(task_id, progress=50, log="✅ UI design completed")

        # ==========================================
        # Phase 3: Implementation
        # ==========================================
        task_manager.update_task(task_id, progress=55, log="[3/4] Starting Implementation Agent...")

        # 检查 UI Structure
        app_folder_path = agent_state.get_app_folder_path()
        ui_structure_file = os.path.join(app_folder_path, "ui", "UI_STRUCTURE.json")
        if not os.path.exists(ui_structure_file):
             task_manager.update_task(task_id, log="⚠️ UI_STRUCTURE.json missing, generating...")
             try:
                 generate_ui_structure_json(os.path.join(app_folder_path, "ui"))
             except Exception as e:
                 task_manager.update_task(task_id, log=f"Warning: failed to generate structure file {e}")

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
                get_current_project,
                read_ui_structure_json,
                generate_ui_structure_json,
            ],
            # Use selected model
            model=core_model,
            additional_authorized_imports=['json'],
            max_steps=30,
        )
        impl_task = prompt_loader.load_agent_prompt("implementation_agent")
        implementation_agent.run(impl_task)
        task_manager.update_task(task_id, progress=80, log="✅ Code implementation completed")

        # ==========================================
        # Optional early exit: only test first 3 agents
        # ==========================================
        if os.environ.get("VIBECODER_TEST_FIRST_THREE_AGENTS_ONLY", "false").lower() in (
            "1",
            "true",
            "yes",
            "on",
        ):
            final_path = agent_state.get_app_folder_path()
            task_manager.update_task(
                task_id,
                status=TaskStatus.COMPLETED.value,
                progress=100,
                log="✅ As configured, only the first three stages (PRD / UI / Implementation) were run; QA and AutoFix were skipped.",
                result={
                    "app_name": agent_state.get_app_name(),
                    "path": str(final_path),
                },
            )
            return

        # ==========================================
        # Phase 4: QA & Auto Fix
        # ==========================================
        task_manager.update_task(task_id, progress=85, log="[4/4] Running QA tests...")
        
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
                get_current_project,
                read_ui_structure_json,
                validate_implementation,
                read_project_requirements,
            ],
            model=non_core_model,
        )
        qa_agent.run(prompt_loader.load_agent_prompt("qa_agent"))
        
        # Check Fixes
        fixes_analysis = analyze_qa_report_for_fixes_needed()
        if fixes_analysis.startswith("YES"):
             task_manager.update_task(task_id, progress=90, log="🔧 Issues detected, running auto-fix...")
             _autofix_model = _get_autofix_model()
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
                    get_current_project,
                    read_ui_structure_json,
                    validate_implementation,
                    read_project_requirements,
                    generate_vanilla_js_code,
                ],
                model=_autofix_model,
                max_steps=30,
             )
             _autofix_prompt = prompt_loader.load_agent_prompt("auto_fix_agent")
             for _attempt in range(2):
                 try:
                     auto_fix_agent.run(_autofix_prompt)
                     break
                 except AgentGenerationError as _e:
                     if "no choices" not in str(_e).lower() and "returned no choices" not in str(_e).lower():
                         raise
                     if _attempt == 0:
                         task_manager.update_task(task_id, log="⚠️ Auto-fix got empty response, retrying once...")
                         continue
                     raise
             task_manager.update_task(task_id, log="✅ Auto-fix completed")
        
        # ==========================================
        # Completion
        # ==========================================
        final_path = agent_state.get_app_folder_path()
        task_manager.update_task(
            task_id, 
            status=TaskStatus.COMPLETED.value, 
            progress=100, 
            log="🎉 All tasks completed!",
            result={
            "app_name": agent_state.get_app_name(),
            "path": str(final_path),
            # 后面可以加 preview url
            }
        )

    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg) # 打印到控制台方便调试
        friendly = _friendly_api_error_message(e)
        log_line = f"❌ Task failed: {friendly}" if friendly else f"❌ Task failed: {str(e)}"
        task_manager.update_task(task_id, status=TaskStatus.FAILED.value, log=log_line)

def run_refinement_task(task_id: str, feedback: str, model_name: str = "gpt-5.4-2026-03-05"):
    """
    Human feedback loop: applies user-requested changes to an existing generated app.
    Uses the same Auto Fix agent as the pipeline, with a feedback-injected prompt and
    USER_FEEDBACK.md written in the task sandbox for traceability.
    """
    try:
        # 1. Setup Sandbox (CRITICAL: Must match the original task path)
        project_root = Path(__file__).resolve().parent.parent.parent
        task_sandbox_root = (project_root / "generated_app" / task_id).resolve()

        if not task_sandbox_root.exists():
            raise FileNotFoundError(f"Sandbox for task {task_id} not found.")

        agent_state.base_path = task_sandbox_root

        # 2. Persist feedback for the agent and for traceability
        feedback_file = task_sandbox_root / "USER_FEEDBACK.md"
        feedback_content = f"""# User Feedback

{feedback}

---
*This feedback was submitted via the /api/refine human feedback loop.*
"""
        feedback_file.write_text(feedback_content, encoding="utf-8")

        # 3. Update task status
        task_manager.update_task(
            task_id,
            status=TaskStatus.RUNNING.value,
            log=f"🔄 Refinement started using model: {model_name}. User feedback: {feedback[:80]}{'…' if len(feedback) > 80 else ''}",
        )

        # 4. Instantiate Refinement Agent
        _autofix_model = _get_autofix_model()
        
        refinement_agent = CodeAgent(
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
                get_current_project,
                read_ui_structure_json,
                validate_implementation,
                read_project_requirements,
                generate_vanilla_js_code,
            ],
            model=_autofix_model,
            additional_authorized_imports=["json"],
            max_steps=30,
        )

        # 5. Load refine_agent prompt and inject user feedback (Jinja2 variable: user_feedback)
        refine_prompt = prompt_loader.load_agent_prompt("refine_agent", user_feedback=feedback)
        refinement_agent.run(refine_prompt)

        # 6. Complete
        final_path = agent_state.get_app_folder_path()
        task_manager.update_task(
            task_id,
            status=TaskStatus.COMPLETED.value,
            progress=100,
            log="✅ Refinement completed based on user feedback.",
            result={
                "app_name": agent_state.get_app_name(),
                "path": str(final_path),
            },
        )

    except Exception as e:
        import traceback
        print(f"Refinement Error: {traceback.format_exc()}")
        friendly = _friendly_api_error_message(e)
        log_line = f"❌ Refinement failed: {friendly}" if friendly else f"❌ Refinement failed: {str(e)}"
        task_manager.update_task(
            task_id,
            status=TaskStatus.FAILED.value,
            log=log_line,
        )