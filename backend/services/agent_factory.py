import os
from typing import Dict, Any, List, Optional

from smolagents import CodeAgent
from smolagents.models import LiteLLMModel, OpenAIServerModel

# Wrapper for OpenAI server models that do not support the 'stop' parameter (e.g. gpt-5.2).
# smolagents only excludes gpt-5.1 in supports_stop_parameter; gpt-5.2 is not in the regex
# and thus the library incorrectly sends 'stop', causing 400 from the API.


class _OpenAIServerModelNoStop(OpenAIServerModel):
    """OpenAIServerModel that never sends the 'stop' parameter (for gpt-5 series compatibility)."""

    @property
    def supports_stop_parameter(self) -> bool:
        return False

    def _prepare_completion_kwargs(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Ensure 'stop' is never sent to the API (gpt-5.2 and similar models reject it)."""
        completion_kwargs = super()._prepare_completion_kwargs(*args, **kwargs)
        completion_kwargs.pop("stop", None)
        return completion_kwargs


# Prompt loader singleton (root-level helper)
from prompt_loader import prompt_loader

# Shared tools from am_tools
from am_tools import (
    read_file,
    write_file,
    mkdir,
    list_files,
    get_current_project,
    set_current_project,
    list_existing_projects,
    get_app_name,
    get_prd_path,
    get_spec_path,
    get_template_path,
    get_ui_design_path,
    copy_template_to_ui_folder,
    set_ui_memory,
    get_ui_memory,
    get_all_ui_memory,
    get_app_folder_path,
    get_project_root,
    get_ui_folder,
    get_ui_structure_path,
    generate_ui_structure_json,
    read_ui_structure_json,
    implement_data_persistence,
    implement_state_management,
    validate_implementation,
    read_project_requirements,
    analyze_qa_report_for_fixes_needed,
    generate_vanilla_js_code,
)

# --- Mixed model plan:
# Manager (项目经理): gpt-4o
# PRD (产品): Claude 3.5 Sonnet
# UI (设计): Claude 3.5 Sonnet
# Impl Layout/Logic/Persist (编码): Claude 3.5 Sonnet
# QA (测试): gpt-4o
# Auto Fix (维修工，本地 / 全局): Claude 3.5 Sonnet
_UNIFIED_MODEL_ID = os.environ.get("VIBECODER_FORCE_MODEL_ID", "gpt-5.4-2026-03-05")


def _build_openai_4o_model():
    """
    gpt-4o: 创意与理解阶段（PRD、UI、全局 Auto-Fix）。
    用于需求分析、UI 设计与跨组件问题诊断。
    """
    return _OpenAIServerModelNoStop(_UNIFIED_MODEL_ID)


def _build_gpt52_model():
    """
    GPT-4o: 闭环纠错与编排（QA、局部 Auto-Fix、Manager 编排）。
    任务拆解与 JSON 规范输出更稳定。
    Uses _OpenAIServerModelNoStop so the API is not sent the unsupported 'stop' parameter.
    """
    return _OpenAIServerModelNoStop(_UNIFIED_MODEL_ID)


def _build_gpt52_codex_model():
    """
    Claude Sonnet 3.5: 编码阶段专用（Implementation 三子阶段 + 旧版单阶段 implementation_worker）。
    专用于 HTML 标注、状态/事件逻辑、持久化等代码生成。
    """
    return _OpenAIServerModelNoStop(_UNIFIED_MODEL_ID)


def _build_base_model():
    """
    Fallback: 当未显式指定模型时使用（例如兼容旧调用）。
    默认使用 GPT-5.2。
    """
    return _build_gpt52_model()


def _ensure_model(context: Dict[str, Any]):
    """Reuse a model from context if provided, otherwise use GPT-5.2."""
    model = context.get("model")
    if model is not None and (isinstance(model, LiteLLMModel) or isinstance(model, OpenAIServerModel)):
        return model
    return _build_gpt52_model()


def create_prd_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Build the PRD worker agent (Claude 3.5 Sonnet).
    Creative/understanding phase: long context, no complex RAG; writes PRD & app_spec.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            mkdir,
            read_file,
            write_file,
            list_files,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            read_project_requirements,
        ],
        model=model,
        name="prd_worker",
        description="Generates and updates PRD.md and app_spec.json for the current project.",
        additional_authorized_imports=["json"],
    )


def create_ui_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Build the UI worker agent (Claude 3.5 Sonnet).
    Creative phase: UI layout, CSS variables, React/Tailwind or vanilla HTML/CSS/JS.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            mkdir,
            list_files,
            read_file,
            write_file,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_template_path,
            get_ui_design_path,
            copy_template_to_ui_folder,
            set_ui_memory,
            get_ui_memory,
            get_all_ui_memory,
            get_app_folder_path,
            generate_ui_structure_json,
        ],
        model=model,
        name="ui_worker",
        description="Designs and maintains the HTML/CSS UI for the current project.",
        additional_authorized_imports=["json"],
    )


def create_implementation_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Legacy single implementation worker (gpt-5.2-codex). Kept for sequential pipeline.
    For manager orchestration, prefer impl_layout_worker → impl_logic_worker → impl_persistence_worker.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            read_file,
            write_file,
            mkdir,
            list_files,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_app_folder_path,
            get_project_root,
            get_ui_folder,
            get_ui_structure_path,
            read_ui_structure_json,
            generate_ui_structure_json,
            implement_data_persistence,
            implement_state_management,
            validate_implementation,
            read_project_requirements,
        ],
        model=model,
        name="implementation_worker",
        description="Implements business logic, state management, and data persistence for the UI prototype.",
        additional_authorized_imports=["json"],
        max_steps=40,
    )


def create_impl_layout_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Implementation sub-phase 1 (Claude 3.5 Sonnet): Mark up UI for logic binding.
    Only adds/ensures stable id and data-* attributes on interactive elements; no business logic.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_app_folder_path,
            get_project_root,
            get_ui_folder,
            get_ui_structure_path,
            read_ui_structure_json,
            generate_ui_structure_json,
        ],
        model=model,
        name="impl_layout_worker",
        description="Marks up HTML with stable ids and data-attributes for interactive elements. Does not write JS logic or change CSS structure.",
        additional_authorized_imports=["json"],
        max_steps=25,
    )


def create_impl_logic_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Implementation sub-phase 2 (Claude 3.5 Sonnet): State + event binding only.
    Writes a single state object and event handlers in main.js; no persistence.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_app_folder_path,
            get_project_root,
            get_ui_folder,
            get_ui_structure_path,
            read_ui_structure_json,
            read_project_requirements,
            validate_implementation,
        ],
        model=model,
        name="impl_logic_worker",
        description="Implements state object and event handlers in main.js. No localStorage; persistence is handled by impl_persistence_worker.",
        additional_authorized_imports=["json"],
        max_steps=35,
    )


def create_impl_persistence_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Implementation sub-phase 3 (Claude 3.5 Sonnet): Persistence layer only.
    Adds load/save/init for state via localStorage; does not change state shape or core logic.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_app_folder_path,
            get_project_root,
            get_ui_folder,
            get_ui_structure_path,
            read_ui_structure_json,
            read_project_requirements,
            implement_data_persistence,
            validate_implementation,
        ],
        model=model,
        name="impl_persistence_worker",
        description="Adds localStorage (or other) persistence for app state. Does not alter state structure or event handlers.",
        additional_authorized_imports=["json"],
        max_steps=25,
    )


def create_qa_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Build the QA worker agent (gpt-4o).
    Unit tests & E2E; writes code_prototype_test_report.md.
    """
    model = task_context.get("model") or _build_openai_4o_model()

    return CodeAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_ui_design_path,
            get_app_folder_path,
            get_project_root,
            get_ui_folder,
            get_ui_structure_path,
            read_ui_structure_json,
            validate_implementation,
            read_project_requirements,
        ],
        model=model,
        name="qa_worker",
        description="Tests the generated prototype against the PRD and UI design, writing a QA report.",
        additional_authorized_imports=["json"],
    )


def create_autofix_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Build the Auto-Fix worker (Claude 3.5 Sonnet) for local/targeted fixes.
    Single-function errors, small patches; direct in-place fixes.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            mkdir,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_ui_design_path,
            get_app_folder_path,
            get_project_root,
            get_ui_folder,
            get_ui_structure_path,
            read_ui_structure_json,
            validate_implementation,
            read_project_requirements,
            analyze_qa_report_for_fixes_needed,
            generate_vanilla_js_code,
        ],
        model=model,
        name="auto_fix_worker",
        description="Applies targeted, local fixes (single function or file). Use for unit/function-level errors from QA.",
        additional_authorized_imports=["json"],
        max_steps=40,
    )


def create_autofix_global_worker_agent(task_context: Dict[str, Any]) -> CodeAgent:
    """
    Build the Auto-Fix Global worker (Claude 3.5 Sonnet) for cross-component/whole-repo issues.
    Use when "change in component A broke page B" or when broad codebase reasoning is needed.
    """
    model = task_context.get("model") or _build_gpt52_codex_model()

    return CodeAgent(
        tools=[
            read_file,
            write_file,
            list_files,
            mkdir,
            get_current_project,
            set_current_project,
            list_existing_projects,
            get_app_name,
            get_prd_path,
            get_spec_path,
            get_ui_design_path,
            get_app_folder_path,
            get_project_root,
            get_ui_folder,
            get_ui_structure_path,
            read_ui_structure_json,
            validate_implementation,
            read_project_requirements,
            analyze_qa_report_for_fixes_needed,
            generate_vanilla_js_code,
        ],
        model=model,
        name="auto_fix_global_worker",
        description="Fixes global or cross-component issues (e.g. changing component A broke page B). Reasons over the full codebase.",
        additional_authorized_imports=["json"],
        max_steps=40,
    )


def create_manager_with_workers(task_context: Optional[Dict[str, Any]] = None) -> CodeAgent:
    """
    Create the top-level manager agent (gpt-4o) with all worker agents.
    Mixed model team aligned to design:
    - Manager: gpt-4o
    - PRD/UI: Claude 3.5 Sonnet
    - Impl (layout/logic/persist): Claude 3.5 Sonnet
    - QA: gpt-4o
    - Auto-fix (local/global): Claude 3.5 Sonnet
    """
    task_context = task_context or {}
    manager_model = task_context.get("model") or _build_openai_4o_model()

    # Build worker team (each uses its designated model)
    prd_worker = create_prd_worker_agent(task_context)
    ui_worker = create_ui_worker_agent(task_context)
    impl_layout_worker = create_impl_layout_worker_agent(task_context)
    impl_logic_worker = create_impl_logic_worker_agent(task_context)
    impl_persistence_worker = create_impl_persistence_worker_agent(task_context)
    qa_worker = create_qa_worker_agent(task_context)
    auto_fix_worker = create_autofix_worker_agent(task_context)
    auto_fix_global_worker = create_autofix_global_worker_agent(task_context)

    manager_tools: List[Any] = [read_file, list_files]
    extra_manager_tools: List[Any] = task_context.get("manager_tools") or []
    manager_tools.extend(extra_manager_tools)

    manager_agent = CodeAgent(
        tools=manager_tools,
        model=manager_model,
        managed_agents=[
            prd_worker,
            ui_worker,
            impl_layout_worker,
            impl_logic_worker,
            impl_persistence_worker,
            qa_worker,
            auto_fix_worker,
            auto_fix_global_worker,
        ],
        name="project_manager",
        description=(
            "High-level project manager. Implementation runs in three sub-phases: "
            "impl_layout_worker (mark up HTML) → impl_logic_worker (state + events) → impl_persistence_worker (localStorage). "
            "Uses auto_fix_worker for local fixes and auto_fix_global_worker for cross-component issues."
        ),
        additional_authorized_imports=["json", "datetime", "textwrap"],
        max_steps=50,
    )

    return manager_agent