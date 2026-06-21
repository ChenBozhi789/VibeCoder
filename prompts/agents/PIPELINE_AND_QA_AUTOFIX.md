# Pipeline Overview: PRD to Generation End, QA & Auto Fix Agents

This document describes the full app-generation pipeline and the roles of the **QA Agent** and **Auto Fix Agent** so you can refine their prompts.

---

## 1. Full Pipeline: PRD to Generation End

There are **two orchestration modes**; both end with optional QA and Auto Fix.

### 1.1 Sequential pipeline (default)

Used when `USE_MANAGER_ORCHESTRATION` is not set or is `false`.

| Phase | Progress | Agent | Inputs | Outputs |
|-------|----------|--------|--------|---------|
| **0. Init** | 0% | (System) | `user_requirements`, `task_id` | Sandbox dir `generated_app/<task_id>/`, `agent_state.base_path` set |
| **1. PRD** | 5→25% | PRD Agent | User requirements (injected in prompt) | `PRD.md`, `app_spec.json`, app name set |
| **2. UI** | 30→50% | UI Agent | PRD, app_spec, template | `ui/index.html`, `ui/css/style.css`, optionally `ui/UI_STRUCTURE.json` |
| **3. Implementation** | 55→80% | **Single** Implementation Agent | PRD, app_spec, UI_STRUCTURE, index.html | `ui/js/main.js` (state, events, persistence); may read/ensure UI_STRUCTURE |
| **4. QA** | 85% | QA Agent | PRD, app_spec, UI_STRUCTURE, index.html, main.js, style.css | `code_prototype_test_report.md` |
| **4b. Fix gate** | — | (System) | `analyze_qa_report_for_fixes_needed()` reads report | Returns `"YES"` or `"NO"` |
| **5. Auto Fix** | 90→95% | Auto Fix Agent | **Only if gate is YES**; report + PRD/spec/UI/code | Edits to `ui/index.html`, `ui/js/main.js`, `ui/css/style.css`; `auto_fix_report.md` |
| **6. Done** | 100% | — | — | Task status COMPLETED, result path returned |

**Early exit:** If `VIBECODER_TEST_FIRST_THREE_AGENTS_ONLY=true`, the pipeline stops after Phase 3 (Implementation). Phases 4–5 (QA and Auto Fix) are **skipped**.

### 1.2 Manager-style pipeline

Used when `USE_MANAGER_ORCHESTRATION=true`. The runner is a linear Python script (no manager LLM); each phase uses its own agent and prompt.

| Phase | Progress | Agent(s) | Outputs |
|-------|----------|----------|---------|
| 0. Init | 0% | (System) | Sandbox, `agent_state` |
| 1. PRD | 5→25% | PRD Agent | `PRD.md`, `app_spec.json` |
| 2. UI | 30→50% | UI Agent | `ui/index.html`, `ui/css/style.css`, UI_STRUCTURE if generated |
| 3. Implementation | 55→80% | **Three workers in order:** | |
| 3a. Layout | 55→65% | Impl Layout Agent | Updates **only** `ui/index.html`: adds stable `id` / `data-*` for interactive elements |
| 3b. Logic | 65→75% | Impl Logic Agent | **Only** `ui/js/main.js`: state, event handlers (no persistence) |
| 3c. Persistence | 75→80% | Impl Persistence Agent | Adds localStorage (or similar) to `main.js` |
| 4. QA | 85% | QA Agent | `code_prototype_test_report.md` |
| 4b. Fix gate | — | `analyze_qa_report_for_fixes_needed()` | YES/NO |
| 5. Auto Fix | 90→95% | Auto Fix Agent | Same as sequential (only if YES) |
| 6. Done | 100% | — | COMPLETED |

So: **sequential** = one Implementation agent does layout + logic + persistence; **manager** = three implementation workers (layout → logic → persistence), then same QA and Auto Fix.

---

## 2. QA Agent: Work Content

### 2.1 Role and constraint

- **Role:** Act as a **tester only**. Find and document problems; **do not change** HTML/CSS/JS.
- **Output:** A single artifact that downstream and humans use: **`code_prototype_test_report.md`** at project root (`get_project_root() + "/code_prototype_test_report.md"`).

### 2.2 Inputs (what the agent reads)

- **Requirements (the “truth”):** PRD (`get_prd_path()`), app_spec (`get_spec_path()`), `read_ui_structure_json()`.
- **Implementation (the “reality”):** `index.html`, `js/main.js`, `css/style.css` under `get_ui_folder()`.
- **Automated check:** `validate_implementation()` (no args) — syntax, missing files, basic structure.

### 2.3 Workflow (from prompt)

1. **Gather context**  
   Confirm project (`get_current_project()`), load PRD, app_spec, UI_STRUCTURE, then list and read the actual UI files.

2. **Technical validation**  
   Call `validate_implementation()` and record result (e.g. syntax/files pass or fail).

3. **Logic & functional analysis**  
   - Compare UI_STRUCTURE and PRD to `index.html`: planned sections and interactive elements vs what exists.  
   - Mentally trace `main.js`: persistence (e.g. localStorage), event listeners, TODOs or missing handlers.

4. **Generate report**  
   Write **only** to `code_prototype_test_report.md` with the required markdown sections (see below).  
   Final message must be a single JSON object: `{"status": "success"|"failed", "summary": "...", "changed_files": ["..."]}`; include the report path in `changed_files`.

### 2.4 Required report structure (parsed by system / Auto Fix)

The report **must** follow this shape so the fix gate and Auto Fix can use it:

- **Executive Summary:** Status (Functional / Partially Functional / Broken), Critical Issues Count, Recommendation (Ready for User / Needs Fixes).
- **1. Technical Validation:** Result of `validate_implementation()` (e.g. Syntax, Files).
- **2. Functional Gaps (PRD vs Code):** Table: Feature Required | Implemented? | Notes/Issues.
- **3. Critical Issues List (Blocking Bugs):** For each: Issue description, File, Severity, Fix Suggestion.
- **4. UI/UX Observations:** Free-form list.

The system uses this report to decide whether to run Auto Fix (`analyze_qa_report_for_fixes_needed()`) and the Auto Fix agent uses it to know **what** to fix.

### 2.5 Tools (QA agent)

Allowed: `read_file`, `write_file` (only for the report), `list_files`, project/path helpers (`get_current_project`, `set_current_project`, `list_existing_projects`, `get_app_name`, `get_prd_path`, `get_spec_path`, `get_ui_design_path`, `get_app_folder_path`, `get_project_root`, `get_ui_folder`, `get_ui_structure_path`), `read_ui_structure_json`, `validate_implementation`, `read_project_requirements`.  
Forbidden: e.g. `python_interpreter`, `generate_ui_structure_json`, `analyze_qa_report_for_fixes_needed`, code-generation tools.

---

## 3. Auto Fix Agent: Work Content

### 3.1 Role and constraints

- **Role:** Read the QA report and **apply code fixes** so the app becomes functional. Only fix; do not redesign.
- **Scope:** Vanilla HTML/CSS/JavaScript only (e.g. `bare-bones-vanilla-main` template). No React/TypeScript.
- **Safety:** If the report says no critical issues (e.g. “Critical Issues: 0”, “Functional”, “Ready for Development”), **do not change any file**; exit and state that no fixes are needed.

### 3.2 When it runs

- **Orchestration:** The **pipeline** calls `analyze_qa_report_for_fixes_needed()`. If the return value **starts with `"YES"`**, the Auto Fix agent is run with its standard prompt. Otherwise it is skipped.
- **Logic of the gate:** The helper reads `code_prototype_test_report.md`, looks for keywords (e.g. error, bug, missing, broken, fail, critical) and for “Critical Issues Count: N” with N > 0 or status “Broken” / “Partially Functional”, and returns `"YES - Issues found..."` or `"NO - No critical issues..."`. So **QA report wording and structure directly control whether Auto Fix runs**.

### 3.3 Inputs (what the agent reads)

- **Primary:** `code_prototype_test_report.md` (path: `get_project_root() + "/code_prototype_test_report.md"`).
- **Context:** PRD (`get_prd_path()`), app_spec (`get_spec_path()`), `read_ui_structure_json()`, optional `implementation_plan.md` under project root.
- **Current code:** `index.html`, `js/main.js`, `css/style.css` under `get_ui_folder()`.

### 3.4 Workflow (from prompt)

1. **Analyze report**  
   Confirm project, read the test report, verify that it actually describes critical issues. If not, stop and do not modify code.

2. **Prioritize fixes**  
   Order by: missing core files → missing JS functions → missing event handlers → missing persistence → missing DOM updates. Plan which files to change and what to add.

3. **Implement fixes**  
   - Fix HTML (structure, IDs for JS).  
   - Fix JS (event listeners, state, optional use of `generate_vanilla_js_code(...)` for patterns).  
   - Fix CSS (styles, layout).  
   - Add persistence (e.g. localStorage) and basic behavior (CRUD, validation) as required by the report and PRD.

4. **Validation**  
   Call `validate_implementation()` and fix any remaining syntax/structure issues.

5. **Report**  
   Write **`auto_fix_report.md`** at project root with: Fix Summary, Files Modified, Fix Details per issue, Validation Results, Next Steps. Final message must be a single JSON object: `{"status": "success"|"failed", "summary": "...", "changed_files": [...]}`.

### 3.5 Tools (Auto Fix agent)

Allowed: `read_file`, `write_file`, `list_files`, `mkdir`, same project/path helpers as QA, `read_ui_structure_json`, `validate_implementation`, `read_project_requirements`, **`analyze_qa_report_for_fixes_needed`**, **`generate_vanilla_js_code`**.  
Forbidden: e.g. `get_ui_memory`, `copy_template_to_ui_folder`, `generate_ui_structure_json`.  
File changes: only under `get_ui_folder()` (index.html, js/main.js, css/style.css) and the two report files at project root; no new arbitrary files/dirs.

---

## 4. Handoff: QA → Fix Gate → Auto Fix

1. **QA** always runs after Implementation and writes **`code_prototype_test_report.md`**.
2. **Pipeline** then calls **`analyze_qa_report_for_fixes_needed()`** (no agent; Python code). It reads the report and returns a string starting with `"YES"` or `"NO"`.
3. **Auto Fix** runs **only if** the result starts with `"YES"`. It reads the same report and the codebase, applies fixes, and writes **`auto_fix_report.md`**.

So: **QA defines “what is wrong” in a structured report; the gate decides “whether to fix”; Auto Fix uses the report to decide “what to change” and then changes only the UI files (and writes the fix report).** For your two remaining agent prompts (QA and Auto Fix), you can tune:

- **QA:** What to compare (e.g. IDs/classes in HTML vs JS, CSS classes used in JS vs style.css, navigation/view switching), how to phrase status and “Critical Issues” so the gate and Auto Fix behave as you want.
- **Auto Fix:** How to interpret “Critical Issues” and “Fix Suggestion”, in what order to fix (e.g. selector consistency first, then navigation, then persistence), and how to avoid over-changing when the report says “no critical issues”.

This document and the two agent prompts together define the full pipeline from PRD to generation end and the exact work content of the QA and Auto Fix agents.
