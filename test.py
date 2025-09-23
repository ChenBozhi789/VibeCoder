from smolagents import PlanningStep, ToolCallingAgent, OpenAIServerModel, tool
from am_tools import mkdir, read_file, write_file, get_user_feedback, build_app_spec_from_docs
from pathlib import Path


# PRD Agent
requirement_interview_agent = ToolCallingAgent(
    tools=[
        get_user_feedback,
        write_file, 
        mkdir, 
    ],
    model=OpenAIServerModel('gpt-5-mini'),
    step_callbacks={PlanningStep: print},
)

# Can optimize this path to be more dynamic
test_folder = "Requirements_Gatherer/Optimization"
final_path = Path(test_folder).resolve() # C:\Users\cbz\Desktop\VibeCoder\VibeCoder\TESTER
# app_name will be collected during the interview

# Example task + human feedback loop
prd_task = f"""
## 📝 PRD Task

You are a helpful Product Manager.  
Your mission is to guide the user through a short interview to gather app requirements, then save them to **PRD.md**.

---

## 📋 Requirement Rules
- Start by asking for the **app name**.  
- Ask **one question at a time** in plain, everyday language.  
- Follow this order of questions:

  1. **Purpose & users** → What problem should the app solve, and who will use it?  
  2. **Features** → What main things should people be able to do? (e.g., add tasks, set reminders, organize, etc.)  
  3. **Look & feel** → How should it look and work? (simple list, mobile-friendly, desktop, or both)  
  4. **Information to save** → What details do you want to keep for each item? (title, notes, due date, reminder, etc.)  
  5. **Rules** → Any checks needed when people enter info? (title required, dates must make sense)  
  6. **Other needs** → Should it work offline, load quickly, or be easy for everyone to use?  
  7. **Extras** → Do you want backup/export, the app to be installable offline, or special branding?  
  8. **When it's done** → What would make you feel the app is complete? How should it handle empty lists or mistakes?  

---

## 📋 Questioning Principles
- **One Step at a Time** → Keep questions simple and clear.  
- **Everyday Language** → Avoid jargon; focus on what the app does and who uses it.  
- **Guided, Multiple-Choice** → Offer examples or options, but let the user type their own.  
- **Logical Flow** → Start with the big picture, then go into details.  

---

## ✅ Final PRD Summary
At the end of the interview, summarize all answers clearly in **PRD.md**.  
Include: purpose, features, UI/UX notes, data model, rules, non-functional needs, extras, and success criteria.  
Format the output in clean Markdown with headings and bullet points.  

---

## 📂 File Handling Rules

1. **Folder Path Convention**  
   - Use the app name in the folder path:  
     ```
     {final_path}/<app_name>
     ```
2. **Files to Create (after requirements interview)**  
   - `PRD.md` → contains the gathered requirements.
3. **Create Folder if Missing**  
   - If the parent folder does not exist, create it first:  
     ```python
     mkdir(path)
     ```
4. **Write Files**  
   - Save files using:  
     ```python
     write_file(path, content)
     ```
5. **Restriction**  
   - ❌ Do not write anywhere else.
"""


# print("🚀 Start running Requirement interview agent")
# requirement_interview_agent.run(prd_task)

with open(f"{final_path}/MiracleBooking/PRD.md", "r", encoding="utf-8") as f:
  prd_text = f.read()

# Planning Agent
planning_agent = ToolCallingAgent(
    tools=[
        read_file,
        write_file
    ],
    model=OpenAIServerModel('gpt-5-mini'),
    step_callbacks={PlanningStep: print},
)

# Test for memory
# requirement_interview_agent.run("Please describe what we've talked about so far")

plan_task = f"""
You are a skilled software architect.  
You review Product Requirements Documents (PRD) and break the work down into a series of tasks for the development team.  
We'll hand these tasks to another team, so your plan must be clear, scoped, and developer-ready.  

You are the **Planning Agent**.  
Based on the `PRD.md`, create `PLAN.md` for developers.  

---

## Plan Structure
- **Overview** → App purpose and context.  
- **Functional Requirements** → Features written as user stories with acceptance criteria. Clearly mark which are **MVP** features and which are optional.  
- **Traceability Table** → A mapping from each PRD requirement to the corresponding plan section(s).  
- **Non-Functional Requirements** → Offline use, fast load, accessibility, performance.  
- **UI/UX Design** → Respect PRD style preferences (do not add extra UI patterns beyond what's in the PRD, unless very minimal). Describe screens, flows, and interactions.  
- **Data Model** → Use localStorage/IndexedDB. Present schema as tables (fields, types).  
- **Validation & Edge Cases** → Input rules, empty states, error handling.  
- **Storage & Persistence** → Local-first emphasis. Offline caching. Export/import backup **only if explicitly mentioned in PRD**; otherwise place in Future Enhancements.  
- **Implementation Plan** → Tech stack, folder/file structure, modular organization.  
- **QA Checklist** → Use `[ ]` checkboxes for functionality, offline mode, accessibility, performance.  
- **Success Criteria** → Define conditions for MVP “done” status.  
- **Future Enhancements** → Capture any extra features not in PRD, or enhancements the team may add later.  

---

## Formatting
- Use clear Markdown headings.  
- Use bullet points and tables where helpful.  
- Use blockquotes for important notes.  
- Add emojis sparingly (✅, ⚠️, 💡).  

---

## Scope Discipline
- Expand only on features explicitly in PRD.  
- If you propose additional ideas, list them strictly under **Future Enhancements**.  
- Respect the simplicity of the PRD's intent.  

---

## INSTRUCTIONS
Please review the PRD carefully and produce an implementation plan that follows the above structure.  
Write your plan to: `{final_path}/MiracleBooking/PLAN.md`
"""

# print("🚀 Start running Planning agent")
# planning_agent.run(plan_task)

# Review agent
review_agent = ToolCallingAgent(
    tools=[
        read_file,
        write_file,
        build_app_spec_from_docs
    ],
    model=OpenAIServerModel('gpt-5-mini'),
    step_callbacks={PlanningStep: print},
)


review_task = f"""
You are the Review Agent.  
Your mission is to review `user_requirements.md` and `plan.md`.  

---

## Review Tasks
1. Verify every requirement from `user_requirements.md` is covered in `plan.md`.  
2. Ensure terminology consistency (same feature names in both files).  
3. Check that `plan.md` includes all sections:  
   - Overview  
   - Functional Requirements  
   - Non-Functional Requirements  
   - UI/UX Design  
   - Data Model  
   - Validation & Edge Cases  
   - Storage & Persistence  
   - Implementation Plan  
   - QA Checklist  
   - Success Criteria  
   - Future Enhancements  
4. Identify missing or unclear points → ask user for clarification.  
5. Approve only when documents are complete and ready to build `app_spec.json`.
6. Build AppSpec from user requirements and plan  
     ```python
     build_app_spec_from_docs(user_req_path, plan_path, app_spec_path)
     ```

---

## INSTRUCTIONS

Please review the PRD.md and PLAN.md, and save the file that you write to `{final_path}/MiracleBooking/app_spec.json`
"""

print("🚀 Start running Review agent")
review_agent.run(review_task)


# app_spec_task = ""
# app_spec_agent = Agent(...)
# app_spec_agent.run(app_apec_task)

# The app_spec.json file is written to disk at this point

