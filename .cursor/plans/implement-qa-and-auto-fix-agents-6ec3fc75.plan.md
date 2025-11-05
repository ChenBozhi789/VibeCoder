<!-- 6ec3fc75-49fa-488f-b1ae-4c542bf8ca6c 1bddadc8-87ae-476b-9b75-9789cab9f900 -->
# Implement QA Agent and Auto Fix Agent

## Overview

Complete the implementation of `qa_agent` and `auto_fix_agent` in the SDLC pipeline by creating their Jinja2 prompt templates and updating the code to use `prompt_loader` for consistency.

## Current State Analysis

The agents are already uncommented in `test_sdlc.py` (lines 473-1065) with:

- **qa_agent**: ToolCallingAgent with inline task prompt (lines 473-757)
- **auto_fix_agent**: CodeAgent with inline task prompt (lines 759-1065)

Both use Jinja2 templates like other agents (prd_agent, spec_agent, ui_agent, mvd_agent).

## Implementation Steps

### 1. Create QA Agent Jinja2 Template

**File**: `prompts/templates/agents/qa_agent.j2`

Extract the qa_task prompt (lines 496-754) into a Jinja2 template file. The template should contain:

- Phase 1: Understand what was built (project status, implementation docs, code structure)
- Phase 2: Automated code validation
- Phase 3: Functional testing (core features, UI, data persistence, error handling)
- Phase 4: Evaluation and reporting
- Phase 5: Generate test report (mandatory deliverable: `code_prototype_test_report.md`)

**Key deliverables**:

- An comprehensive test report with executive summary, technical validation, functional test results, critical issues, and recommendations

### 2. Create Auto Fix Agent Jinja2 Template

**File**: `prompts/templates/agents/auto_fix_agent.j2`

Extract the auto_fix_task prompt (lines 787-1062) into a Jinja2 template file. The template should contain:

- Phase 1: Analyze test report that qa_agent generated (project status, test report, supporting docs, current code state)
- Phase 2: Prioritize fixes (critical blocking issues, fix plan)
- Phase 3: Implement fixes (core files, utilities, imports, functionality)
- Phase 4: Validation and testing
- Phase 5: Generate fix report (mandatory deliverable: `auto_fix_report.md`)

**Implementation guidelines**:

- Code quality standards (TypeScript, React best practices, error handling)
- File organization and data management
- User experience improvements

### 3. Update test_sdlc.py

**Changes in `test_sdlc.py`**:

Replace inline prompts with prompt_loader calls:

```python
# Line 496: Replace inline qa_task with:
qa_task = prompt_loader.load_agent_prompt("qa_agent")

# Line 787: Replace inline auto_fix_task with:
auto_fix_task = prompt_loader.load_agent_prompt("auto_fix_agent")
```

Ensure `prompt_loader` is already imported at the top (line 11).

### 4. Verify Template Consistency

Ensure both templates follow the same structure as existing agent templates:

- Use proper Jinja2 syntax
- No template variables needed (both prompts are static)
- Proper indentation and formatting
- Clear section headers and instructions

## Files to Modify

1. **Create**: `prompts/templates/agents/qa_agent.j2` (new file)
2. **Create**: `prompts/templates/agents/auto_fix_agent.j2` (new file)
3. **Modify**: `test_sdlc.py` (lines 496 and 787 - replace inline prompts with prompt_loader calls)

## Success Criteria

- Both Jinja2 templates are created with complete prompt content
- `test_sdlc.py` uses `prompt_loader.load_agent_prompt()` for both agents
- Templates are consistent with existing agent template structure
- No functionality changes - agents work exactly as before
- Code is cleaner and follows the established pattern

### To-dos

- [ ] Create qa_agent.j2 template with complete prompt content from lines 496-754
- [ ] Create auto_fix_agent.j2 template with complete prompt content from lines 787-1062
- [ ] Update test_sdlc.py to use prompt_loader for qa_task and auto_fix_task