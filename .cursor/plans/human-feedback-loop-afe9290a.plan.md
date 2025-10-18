<!-- afe9290a-ada5-4f7b-b97a-0cabda72e6ff bbf75e5a-0a44-405e-883b-26517fc7366d -->
# Human Feedback Loop Implementation

## Overview

Add two new agents to the SDLC pipeline: `feedback_agent` (collects human notes) and `enhance_agent` (implements improvements). These activate when QA passes, allowing iterative enhancement with automatic QA validation.

## File Structure

### New Files to Create

1. **`prompts/templates/agents/feedback_agent.j2`** (300-400 lines)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Prompt template for the feedback collection agent
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Reads the test report and working app
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Asks user for improvement notes
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Converts notes into 2-5 actionable tickets
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Saves tickets to `feedback_tickets.json`

2. **`prompts/templates/agents/enhance_agent.j2`** (400-500 lines)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Prompt template for the enhancement agent (CodeAgent)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Reads tickets from `feedback_tickets.json`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Implements all tickets automatically
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Documents changes in `enhancement_summary.md`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Validates changes still work

### Files Stored Per Project

In each project folder (e.g., `Multiple_Agents_Simulation/FutureToDo/`):

1. **`feedback_tickets.json`** - Structured tickets
   ```json
   {
     "tickets": [
       {
         "id": 1,
         "title": "Add dark mode toggle",
         "description": "User wants dark/light theme switch",
         "priority": "medium",
         "status": "pending"
       }
     ],
     "feedback_round": 1,
     "original_feedback": "raw user notes here"
   }
   ```

2. **`enhancement_summary.md`** - What was changed
   ```markdown
   # Enhancement Summary - Round 1
   ## Tickets Implemented: 3/3
   - [✓] Ticket #1: Add dark mode toggle
     - Changes: Added ThemeContext, toggle button in header
     - Files modified: App.tsx, components/Header.tsx
   ```


## Implementation Steps

### Step 1: Create feedback_agent.j2

- ToolCallingAgent that collects human feedback
- Tools needed: `read_file`, `write_file`, `get_user_requirements`, `get_app_folder_path`, `get_current_project`
- Workflow:

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                1. Read `code_prototype_test_report.md` to understand app status
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                2. Read PRD and implementation docs for context
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                3. Ask user: "The app passed QA. What improvements would you like?"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                4. Convert raw feedback into 2-5 specific, actionable tickets
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                5. Save to `feedback_tickets.json` with priority levels
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                6. Confirm tickets with user (show what will be implemented)

### Step 2: Create enhance_agent.j2

- CodeAgent that implements all tickets automatically
- Tools needed: `read_file`, `write_file`, `list_files`, `generate_functional_code`, `implement_state_management`, `validate_implementation`, `get_app_folder_path`, `read_ui_structure_json`
- Workflow:

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                1. Read `feedback_tickets.json` to get enhancement tickets
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                2. Read current implementation to understand structure
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                3. For each ticket (all automatically):

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Plan the changes needed
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Modify/create necessary files
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Update ticket status to "completed"

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                1. Run `validate_implementation()` to ensure no breaks
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                2. Create `enhancement_summary.md` documenting all changes
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                3. Update `feedback_tickets.json` with completion status

### Step 3: Add Agent Tools to test_sdlc.py

Add after line 314 (after `get_all_ui_memory` tool):

```python
@tool
def get_feedback_tickets_path() -> str:
    """Get the feedback tickets file path for current project."""
    global agent_state
    app_folder = agent_state.get_app_folder_path()
    return str(app_folder / "feedback_tickets.json") if app_folder else "No path set"

@tool
def get_enhancement_summary_path() -> str:
    """Get the enhancement summary file path for current project."""
    global agent_state
    app_folder = agent_state.get_app_folder_path()
    return str(app_folder / "enhancement_summary.md") if app_folder else "No path set"
```

### Step 4: Create Agent Instances in test_sdlc.py

Add after the commented-out auto_fix_agent (after line 509):

```python
# 6. Feedback Agent - ToolCallingAgent (Human Feedback Loop)
feedback_agent = ToolCallingAgent(
   tools=[
      read_file,
      write_file,
      list_files,
      get_user_requirements,
      get_app_name,
      get_prd_path,
      get_spec_path,
      get_app_folder_path,
      set_current_project,
      list_existing_projects,
      get_current_project,
      get_feedback_tickets_path,
      read_project_requirements
   ],
   model=OpenAIServerModel('gpt-5-mini'),
)

feedback_task = prompt_loader.load_agent_prompt("feedback_agent")

print("🎯 Start running Feedback agent")
feedback_agent.run(feedback_task)

# 7. Enhance Agent - CodeAgent (Implements Feedback)
enhance_agent = CodeAgent(
   tools=[
      read_file,
      write_file,
      list_files,
      get_app_name,
      get_prd_path,
      get_spec_path,
      get_app_folder_path,
      set_current_project,
      list_existing_projects,
      get_current_project,
      read_ui_structure_json,
      generate_functional_code,
      implement_data_persistence,
      implement_state_management,
      validate_implementation,
      get_feedback_tickets_path,
      get_enhancement_summary_path
   ],
   model=OpenAIServerModel('gpt-5'),
   max_steps=40,
)

enhance_task = prompt_loader.load_agent_prompt("enhance_agent")

print("🚀 Start running Enhancement agent")
enhance_agent.run(enhance_task)

# 8. Re-run QA Agent After Enhancement
print("🔄 Re-running QA agent after enhancements")
qa_agent.run(qa_task)
```

### Step 5: Uncomment QA Agent

Uncomment lines 450-476 in `test_sdlc.py` to activate the QA agent before the feedback loop.

## Pipeline Flow

```
implementation_agent (line 448)
    ↓
qa_agent (line 476) ← uncommented
    ↓
  [if errors] → auto_fix_agent (commented out for now)
    ↓
  [if passes] → feedback_agent (NEW)
    ↓
enhance_agent (NEW)
    ↓
qa_agent (re-run automatically)
```

## Success Criteria

1. **Feedback Collection Works**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - User can provide natural language feedback
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Agent converts feedback to 2-5 clear tickets
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Tickets saved to `feedback_tickets.json`

2. **Enhancement Implementation Works**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - All tickets implemented automatically
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - No compilation/TypeScript errors after changes
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - `validate_implementation()` passes
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Changes documented in `enhancement_summary.md`

3. **App Still Functions**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - QA agent re-runs successfully
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Original features still work
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - New enhancements are functional
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - No regressions introduced

4. **Short Running Time**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Uses `gpt-5-mini` for feedback agent (faster, cheaper)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Uses `gpt-5` for enhance agent (better code generation)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Automatic ticket selection (no manual intervention)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Max 40 steps for enhance_agent (prevents runaway)

## Key Design Decisions

- **Efficiency**: feedback_agent uses ToolCallingAgent + gpt-5-mini (faster than CodeAgent)
- **Reliability**: All tickets implemented automatically, validation runs at end
- **Short Runtime**: Auto-select all tickets, no user confirmations during implementation
- **Simple Storage**: JSON for structured tickets, Markdown for human-readable summaries
- **Location**: All files in project folder (e.g., `Multiple_Agents_Simulation/FutureToDo/`)

### To-dos

- [ ] Add get_feedback_tickets_path() and get_enhancement_summary_path() tools to test_sdlc.py
- [ ] Create prompts/templates/agents/feedback_agent.j2 template
- [ ] Create prompts/templates/agents/enhance_agent.j2 template
- [ ] Uncomment QA agent code (lines 450-476) in test_sdlc.py
- [ ] Add feedback_agent and enhance_agent instances with QA re-run to test_sdlc.py