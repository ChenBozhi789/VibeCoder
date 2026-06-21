## Multi-agent orchestration in VibeCoder

This project now supports a **hierarchical manager/worker multi-agent pipeline** built on top of `smolagents`.

### Manager + workers

- **Manager agent** (`manager_agent` prompt, created via `create_manager_with_workers`) is a `CodeAgent` that:
  - Receives the raw user requirements.
  - Orchestrates the standard phases in order: PRD → UI → Implementation → QA → Auto-fix.
  - Delegates work to specialized worker agents via `managed_agents`.
  - Optionally reports progress back to the backend using a small `update_phase_status` tool.

- **Worker agents** (mixed models) are stage-specific `CodeAgent`s:
  - `prd_worker` (Gemini-3-Pro) – PRD.md and app_spec.json; long-context understanding.
  - `ui_worker` (Gemini-3-Pro) – UI layout, CSS, UI_STRUCTURE.json; creative/visual.
  - **Implementation (3 sub-phases, GPT-5.2):** `impl_layout_worker` (mark up HTML id/data-*), `impl_logic_worker` (state + events in main.js), `impl_persistence_worker` (localStorage). Legacy `implementation_worker` remains for sequential pipeline.
  - `qa_worker` (GPT-5.2) – unit/E2E tests and code_prototype_test_report.md.
  - `auto_fix_worker` (GPT-5.2) – local/targeted fixes (single function or file).
  - `auto_fix_global_worker` (Gemini-3-Pro) – cross-component/whole-repo fixes when “change A broke B”.

- **Manager** uses GPT-5.2 for orchestration and structured task planning.

Model IDs are configurable via env: `VIBECODER_GEMINI_MODEL_ID`, `VIBECODER_GPT_MODEL_ID` (defaults: `gemini/gemini-3-pro-preview`, `gpt-5.2`).

All workers reuse the existing prompt templates in `prompts/agents/*.j2` and the shared tools in `am_tools.py`.

### Where the manager is used

- **HTTP API path** (`backend/services/generator_service.py`):
  - When the environment variable `USE_MANAGER_ORCHESTRATION` is set to a truthy value (`1`, `true`, `yes`, `on`),
    `run_app_generation_task` builds a manager via `create_manager_with_workers` and calls it once with a high-level task.
  - A dynamic `update_phase_status` tool is injected so the manager can update `task_manager` progress between phases.
  - When the flag is disabled (default), the original sequential per-stage pipeline is used.

- **Local engine path** (`vibecoder_engine.VibeCoderEngine.generate_app`):
  - A new `use_manager: bool = False` parameter switches between:
    - `use_manager=False` – existing sequential `get_agent(stage)` + `_run_agent_with_retry` flow.
    - `use_manager=True` – a manager built via `create_manager_with_workers` runs the whole pipeline as one call.

### Prompts

- The manager prompt lives at `prompts/agents/manager_agent.j2` and documents:
  - The available worker agents and their responsibilities.
  - The required phase order and expected artifacts.
  - How to delegate work and when to consider auto-fix.

Worker prompts:
- `prompts/agents/prd_agent.j2`, `ui_agent.j2`, `qa_agent.j2`, `auto_fix_agent.j2`
- Implementation (manager path): `impl_layout_agent.j2`, `impl_logic_agent.j2`, `impl_persistence_agent.j2`
- Sequential path still uses `implementation_agent.j2`

### Implementation entrypoints

- **Team factory**: `backend/services/agent_factory.py`
  - `create_prd_worker_agent`, `create_ui_worker_agent`,
    `create_impl_layout_worker_agent`, `create_impl_logic_worker_agent`, `create_impl_persistence_worker_agent`,
    `create_qa_worker_agent`, `create_autofix_worker_agent`, `create_autofix_global_worker_agent`
  - `create_implementation_worker_agent` kept for sequential pipeline.
  - `_build_gemini_model()`, `_build_gpt52_model()` for mixed-model assignment.
  - `create_manager_with_workers(task_context: dict)` – returns manager (GPT-5.2) with layout → logic → persistence + QA + auto-fix workers.

- **Backend pipeline**: `backend/services/generator_service.py`
  - `run_app_generation_task` – feature-flagged switch between sequential and manager-driven orchestration.

- **Local engine**: `vibecoder_engine.py`
  - `VibeCoderEngine.generate_app(user_requirements: str, use_manager: bool = False)`

