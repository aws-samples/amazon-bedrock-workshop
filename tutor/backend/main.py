"""
FastAPI backend for Bedrock Tutor
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import agent logic
import agent
TUTOR_DIR = Path(__file__).parent.parent.parent / "tutor"

app = FastAPI(title="Bedrock Tutor API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/static/{path:path}")
async def serve_static(path: str):
    """Serve static files"""
    return FileResponse(FRONTEND_DIR / "static" / path)


# API Models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]
    learning_path_id: Optional[str] = None


# API Endpoints
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat

    Client sends: {"message": str, "history": [...], "learning_path_id": str | null}
    Server sends: {"type": "text|tool_use|tool_result|done|error", ...}
    """
    await websocket.accept()

    try:
        # Receive initial message from client
        data = await websocket.receive_json()

        message = data.get("message", "")
        history = data.get("history", [])
        learning_path_id = data.get("learning_path_id")
        actions_since_last_test = data.get("actions_since_last_test", 0)

        # Convert history to format expected by tutor_agent
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

        # Add action count context to message if it's high
        if actions_since_last_test >= 3:
            message = f"[SYSTEM: User has performed {actions_since_last_test} actions since last knowledge test. Consider testing their understanding now.]\n\n{message}"

        # Get region
        import os
        region = os.getenv("AWS_REGION", "us-east-1")
        if not region or region == "us-east-1":
            try:
                meta_path = "/opt/ml/metadata/resource-metadata.json"
                if os.path.exists(meta_path):
                    with open(meta_path) as f:
                        meta = json.load(f)
                        arn = meta.get("ResourceArn", "")
                        region = arn.split(":")[3] if ":" in arn else "us-east-1"
            except Exception:
                pass

        # Get learning path content if specified
        learning_path_content = None
        if learning_path_id:
            import yaml
            learning_paths_dir = TUTOR_DIR / "learning_paths"
            if learning_paths_dir.exists():
                for md_file in learning_paths_dir.glob("*.md"):
                    content = md_file.read_text()
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            frontmatter = yaml.safe_load(parts[1])
                            if frontmatter.get('id') == learning_path_id:
                                learning_path_content = f"# LEARNING PATH: {frontmatter['title']}\n\n{parts[2].strip()}"
                                break

        # Stream agent events
        async for event in agent.invoke_agent(
            prompt=message,
            conversation_history=conversation_history,
            region=region,
            learning_path_content=learning_path_content
        ):
            await websocket.send_json(event)

        # Signal completion
        await websocket.send_json({"type": "done"})

    except Exception as e:
        # Send error event
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

    finally:
        await websocket.close()


class ExecuteRequest(BaseModel):
    code: str
    notify_agent: bool = False


@app.post("/api/execute")
async def execute_code(request: ExecuteRequest):
    """Execute Python code and return output"""
    import io
    import sys

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout_capture
    sys.stderr = stderr_capture

    try:
        exec(request.code, {"__builtins__": __builtins__})
        output = stdout_capture.getvalue()
        err = stderr_capture.getvalue()
        full_output = output + ("\n" + err if err else "")

        return {
            "success": True,
            "output": full_output,
            "code": request.code,
            "has_error": bool(err)
        }
    except Exception as e:
        error_output = f"Error: {type(e).__name__}: {str(e)}"
        return {
            "success": False,
            "output": error_output,
            "code": request.code,
            "has_error": True
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@app.get("/api/learning-paths")
async def list_learning_paths():
    """Get all available learning paths"""
    import yaml
    paths = []
    learning_paths_dir = TUTOR_DIR / "learning_paths"
    if learning_paths_dir.exists():
        for md_file in learning_paths_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        paths.append({
                            "id": frontmatter['id'],
                            "title": frontmatter['title'],
                            "description": frontmatter['description']
                        })
            except Exception:
                pass
    return paths


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
