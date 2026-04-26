# Amazon Bedrock Interactive Tutor

An interactive learning environment for Amazon Bedrock with real-time code examples and streaming responses.

## Features

- **Real-time streaming**: WebSocket-based streaming for immediate text and code updates
- **Live code scratchpad**: Code updates instantly when the AI generates examples
- **Inline tool indicators**: See when tools are called during the conversation
- **Learning paths**: Guided tutorials for key Bedrock concepts
- **Code execution**: Run Python code examples directly in the browser

## Architecture

- **Backend**: FastAPI + strands-agents (Python)
- **Frontend**: Vanilla JavaScript with WebSockets
- **Communication**: WebSocket for streaming (works through SageMaker proxy)

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
pip install websockets  # Required for WebSocket support
```

## Running

```bash
./start.sh
```

Access at: `https://<your-sagemaker-domain>/jupyterlab/default/proxy/8002/`

## Key Files

- `backend/main.py` - FastAPI server with WebSocket endpoint
- `backend/agent.py` - Bedrock agent logic using strands-agents
- `backend/tools.py` - Agent tools (update_scratchpad, find_learning_paths, etc.)
- `frontend/index.html` - Single-page app with all CSS/JS inline

## How It Works

1. User sends message via WebSocket
2. Backend streams agent responses in real-time
3. When `update_scratchpad` tool is called, code appears immediately in the scratchpad
4. Tool badges appear inline in the conversation
5. User can run the generated code and see output
