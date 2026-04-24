# Amazon Bedrock Workshop Tutor

Interactive AI tutor for learning Amazon Bedrock with guided learning paths and live code execution.

## Setup

```bash
# 1. Create virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Start the tutor
.venv/bin/streamlit run streamlit_app.py
```

## Files

- `streamlit_app.py` - Main application
- `requirements.txt` - Python dependencies  
- `learning_paths/` - Markdown lesson plans with YAML frontmatter
- `.streamlit/config.toml` - Anthropic light theme

## Learning Paths

Guided lessons cover:
- Text Generation (Claude Converse API)
- Embeddings (Titan Multimodal)
- RAG (Knowledge Bases)
- Responses API (Mantle/OpenAI-compatible)

All dependencies (boto3, openai, streamlit, etc.) are in `requirements.txt` and installed in the venv.
