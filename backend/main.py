import os
import sys
import threading
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Optional: enable LiteLLM debug (set LITELLM_DEBUG=1 or true when troubleshooting)
if os.environ.get("LITELLM_DEBUG", "").lower() in ("1", "true", "yes"):
    import litellm
    litellm.set_verbose = True
    # litellm._turn_on_debug()  # even more verbose; may log API keys—use only locally
import uvicorn
from pydantic import BaseModel

# 确保从 backend 目录运行时也能导入 backend.* 包
_current_dir = Path(__file__).resolve().parent
_project_root = _current_dir.parent  # VibeCoder/VibeCoder
if str(_project_root) not in sys.path:
    sys.path.append(str(_project_root))

from backend.utils.task_manager import task_manager, TaskStatus
from backend.utils.session_manager import session_manager
from backend.services.generator_service import run_app_generation_task, run_refinement_task

FORCED_MODEL_ID = os.environ.get("VIBECODER_FORCE_MODEL_ID", "gpt-5.4-2026-03-05")

# 1. initialize APP
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_APP_DIR = os.path.join(BASE_DIR, "generated_app")

os.makedirs(GENERATED_APP_DIR, exist_ok=True)

# Custom StaticFiles to disable caching for generated apps
class NoCacheStaticFiles(StaticFiles):
    def is_not_modified(self, response_headers, request_headers) -> bool:
        return False

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.mount("/generated_app", NoCacheStaticFiles(directory=GENERATED_APP_DIR), name="generated_app")

@app.on_event("startup")
async def startup():
    """确保 agent_state.base_path 指向项目根目录下的 generated_app。"""
    try:
        from am_tools import agent_state
        project_root = Path(__file__).resolve().parent.parent
        agent_state.base_path = (project_root / "generated_app").resolve()
        agent_state.base_path.mkdir(exist_ok=True)
    except Exception:
        pass  # 不影响启动

# 2. configure CORS (to allow your React frontend to access)
# allow all origins to access, this is the easiest way to set up in development stage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production environment, here should be replaced with the specific address of the frontend
    allow_credentials=True, # allow credentials (cookies, headers, etc.)
    allow_methods=["*"], # allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    user_requirements: str
    model: str = FORCED_MODEL_ID

class GenerateResponse(BaseModel):
    status: str
    message: str
    task_id: str

class RefineRequest(BaseModel):
    task_id: str
    feedback: str
    model: str = FORCED_MODEL_ID

class ChatRequest(BaseModel):
    message: str
    model: str = FORCED_MODEL_ID

class ChatResponse(BaseModel):
    status: str
    message: str
    reply: str

class CreateSessionRequest(BaseModel):
    initial_message: str = "New Chat"

class AddMessageRequest(BaseModel):
    message: dict

# 3. define health check interface
# GET request, path is /api/health
@app.get("/api/health")
async def health_check():
    """
    health check interface, to confirm if the backend service is running. 
    """
    return {
        "status": "success",
        "message": "VibeCoder Backend is running!",
        "service": "api"
    }

# ==========================================
# Session Management APIs
# ==========================================
@app.get("/api/sessions")
async def get_all_sessions():
    """Get a list of all chat sessions (summaries)."""
    try:
        sessions = session_manager.get_all_sessions()
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get the full details of a specific chat session, including all messages."""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        return {"status": "success", "session": session}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/sessions")
async def create_session(request: CreateSessionRequest):
    """Create a new empty chat session."""
    try:
        session = session_manager.create_session(request.initial_message)
        return {"status": "success", "session": session}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.put("/api/sessions/{session_id}/messages")
async def add_message_to_session(session_id: str, request: AddMessageRequest):
    """Append a new message to an existing session."""
    try:
        success = session_manager.add_message(session_id, request.message)
        if success:
            return {"status": "success", "message": "Message added"}
        else:
            return {"status": "error", "message": "Session not found or update failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    try:
        success = session_manager.delete_session(session_id)
        if success:
            return {"status": "success", "message": "Session deleted"}
        else:
            return {"status": "error", "message": "Session not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==========================================
# Legacy Task & Generation APIs
# ==========================================
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Discuss mode: Direct chat with AI models without triggering the generation pipeline.
    Provides current date/time context to prevent the model from getting the date wrong.
    """
    try:
        import litellm
        from datetime import datetime
        
        message = (request.message or "").strip()
        if not message:
            return {"status": "error", "message": "Message is required", "reply": ""}

        # Inject real-time context
        now = datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = now.strftime("%A")
        
        system_prompt = f"You are VibeCoder Chat, a helpful AI programming assistant. Today's date is {current_time_str} ({day_of_week}). Use this information for any time-sensitive queries."

        # Temporarily force all chat traffic to the same model as generation/refine.
        litellm_model = FORCED_MODEL_ID

        response = litellm.completion(
            model=litellm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            api_key=os.environ.get("GEMINI_API_KEY") if "gemini" in litellm_model else (os.environ.get("ANTHROPIC_API_KEY") if "claude" in litellm_model else None)
        )
        reply = response.choices[0].message.content
        return {
            "status": "success",
            "message": "Chat successful",
            "reply": reply
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "reply": ""}

@app.post("/api/generate")
async def generate_task(request: GenerateRequest):
    """
    Generate app from user requirements.
    创建任务后立即在独立线程中运行 generator_service，返回 task_id 供前端轮询进度。
    使用独立线程避免长时间任务阻塞 worker，导致 GET /api/all_tasks 等请求卡住。
    """
    try:
        user_requirements = (request.user_requirements or "").strip()
        if not user_requirements:
            return {"status": "error", "message": "user_requirements is required"}

        task_id = task_manager.create_task()
        thread = threading.Thread(
            target=run_app_generation_task,
            args=(task_id, user_requirements, request.model),
            daemon=True,
            name=f"gen-{task_id[:8]}",
        )
        thread.start()
        return {
            "status": "success",
            "message": "Generation task created",
            "task_id": task_id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/api/all_tasks_id")
async def get_all_tasks_id():
    """
    Get all task ids.
    """
    return {
        "status": "success",
        "task_ids": task_manager.retrieve_task_id()
    }

@app.get("/api/all_tasks")
async def get_all_tasks():
    """
    Get all tasks.
    """
    return {
        "status": "success",
        "tasks": task_manager.get_all_tasks()
    }

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """
    查询单个任务状态、进度、日志 and 结果。
    """
    task = task_manager.get_task(task_id)
    if not task:
        return {"status": "error", "message": "Task not found"}
    return {"status": "success", "task": task}

@app.post("/api/refine")
async def refine_task(request: RefineRequest):
    """
    Human feedback loop: submit feedback to refine an existing generated app.
    Accepts task_id (from a completed generation) and feedback (free text).
    Runs the Auto Fix agent with the feedback as the change request; updates the same task.
    Poll GET /api/tasks/{task_id} for status; when status is "completed", the app has been updated.
    """
    try:
        feedback = (request.feedback or "").strip()
        if not feedback:
            return {"status": "error", "message": "feedback is required"}

        task = task_manager.get_task(request.task_id)
        if not task:
            return {"status": "error", "message": "Task not found"}

        # Optional: avoid refining while another run is in progress
        if task.get("status") == TaskStatus.RUNNING.value:
            return {"status": "error", "message": "Task is still running; wait for it to complete before refining"}

        thread = threading.Thread(
            target=run_refinement_task,
            args=(request.task_id, feedback, request.model),
            daemon=True,
            name=f"refine-{request.task_id[:8]}",
        )
        thread.start()
        return {
            "status": "success",
            "message": "Refinement task started",
            "task_id": request.task_id,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 4. allow to start directly by python main.py (optional)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
