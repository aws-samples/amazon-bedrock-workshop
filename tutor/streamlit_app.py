"""
Streamlit-based Bedrock Workshop Tutor
Simple POC with agent running in the same process
"""

import streamlit as st
import subprocess
import sys
import io
import os
import json
import traceback
from pathlib import Path
from code_editor import code_editor
import boto3
import yaml
from strands import Agent
from strands.models import BedrockModel
import tutor_tools

# Detect AWS region
def get_region():
    """Detect AWS region from environment or SageMaker metadata."""
    if os.getenv("AWS_REGION"):
        return os.getenv("AWS_REGION")

    try:
        meta_path = "/opt/ml/metadata/resource-metadata.json"
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
                arn = meta.get("ResourceArn", "")
                region = arn.split(":")[3] if ":" in arn else None
                if region:
                    return region
    except Exception:
        pass

    try:
        session = boto3.Session()
        return session.region_name or "us-east-1"
    except Exception:
        pass

    return "us-east-1"

REGION = get_region()

# Load learning paths
def load_learning_paths():
    """Load all learning path markdown files."""
    paths = {}
    learning_paths_dir = Path(__file__).parent / "learning_paths"

    if learning_paths_dir.exists():
        for md_file in learning_paths_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                # Extract frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        body = parts[2].strip()
                        paths[frontmatter['id']] = {
                            **frontmatter,
                            'content': body
                        }
            except Exception as e:
                print(f"Error loading {md_file}: {e}")

    return paths

LEARNING_PATHS = load_learning_paths()

# Agent using strands framework
def call_bedrock_agent(prompt: str, conversation_history: list, stream_placeholder=None, learning_path_id=None):
    """Call Bedrock agent using strands framework with automatic tool calling."""

    # Build message history for strands
    from strands.types.content import Message
    messages = []
    for msg in conversation_history:
        if msg["role"] in ["user", "assistant"]:
            # Content must be a list of content blocks like [{'text': '...'}]
            content = msg["content"]
            if isinstance(content, str):
                content = [{'text': content}]
            messages.append(Message(role=msg["role"], content=content))

    # Base system prompt
    system_prompt = f"""You are an expert Amazon Bedrock tutor in an interactive workshop with a live code scratchpad.

The interface has two panels:
- LEFT: This chat where you explain concepts
- RIGHT: A code scratchpad where users can edit and run Python code

🚨 CRITICAL: YOU DO NOT HAVE DIRECT KNOWLEDGE 🚨

You do NOT have detailed information about specific Bedrock topics memorized. Instead, you have access to curated learning paths through tools.

MANDATORY WORKFLOW for ANY user question:

1. FIRST: Call find_learning_paths(query="<user's topic>")
   - User asks about "responses API" → find_learning_paths(query="responses API")
   - User asks about "embeddings" → find_learning_paths(query="embeddings")
   - DO NOT answer without searching first - you don't have this information

2. IF learning path found: Call load_learning_path(path_id="<id>")
   - This gives you the structured curriculum to follow
   - Follow it step-by-step, presenting each concept progressively
   - Use update_scratchpad tool for code examples

3. IF NO learning path found: Then answer from general knowledge
   - Only after searching confirms no curated content exists

You cannot answer questions about Bedrock topics without first using find_learning_paths. You must search the learning path database first.

When explaining:
- Use the update_scratchpad tool to write example code to the scratchpad
- Point them to the scratchpad: "**Check the code in the scratchpad → and hit ▶ Run to try it!**"
- Be encouraging and hands-on

Code guidelines:
- Write complete, runnable Python using boto3
- Always set region_name='{REGION}'
- Use inference profile IDs (e.g., 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
- Be concise and practical
- Users can edit your code, so make it a good starting point

Available models:
- Claude Sonnet 4.5: us.anthropic.claude-sonnet-4-5-20250929-v1:0
- Claude Haiku 4.5: us.anthropic.claude-haiku-4-5-20251001-v1:0
- Nova Lite: us.amazon.nova-lite-v1:0
- Nova Pro: us.amazon.nova-pro-v1:0
"""

    # Add learning path context if provided
    if learning_path_id and learning_path_id in LEARNING_PATHS:
        path = LEARNING_PATHS[learning_path_id]
        system_prompt += f"\n\n# LEARNING PATH: {path['title']}\n\n"
        system_prompt += f"You are guiding the user through the '{path['title']}' learning path.\n\n"
        system_prompt += f"{path['content']}\n\n"
        system_prompt += "Follow the teaching flow in the learning path. Present each step progressively, "
        system_prompt += "write the code examples to the scratchpad, and guide the user through the concepts."

    try:
        # Create strands agent with tools
        agent = Agent(
            model=BedrockModel(
                model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
            ),
            messages=messages,
            tools=[
                tutor_tools.update_scratchpad,
                tutor_tools.find_learning_paths,
                tutor_tools.load_learning_path
            ],
            system_prompt=system_prompt,
            callback_handler=None  # Disable default printing
        )

        # Stream agent response (async)
        import asyncio

        async def stream_agent():
            """Stream agent events and collect response text."""
            response_text = ""
            async for event in agent.stream_async(prompt):
                # Stream text chunks to placeholder
                if isinstance(event, dict) and 'data' in event:
                    text_chunk = event['data']
                    response_text += text_chunk
                    if stream_placeholder:
                        stream_placeholder.markdown(response_text)
            return response_text

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        response_text = loop.run_until_complete(stream_agent())

        # Store minimal metadata
        st.session_state.last_response_metadata = {
            "stopReason": "complete",
            "usage": None
        }

        return response_text

    except Exception as e:
        return f"Error calling agent: {str(e)}\n\n{traceback.format_exc()}"
        return f"Error calling Bedrock: {str(e)}\n\n{traceback.format_exc()}"

st.set_page_config(
    page_title="Amazon Bedrock Workshop",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# CSS for responsive equal-height layout
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Make containers use consistent viewport-based heights */
    :root {
        --button-row-height: 80px;
        --input-height: 70px;
        --run-button-height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# Calculate viewport-based heights
# Total available: ~90vh (leaving space for margins)
# Buttons: ~80px, Input: ~70px
# Right side splits 50/50 minus run button
# Chat should fill to match
BUTTON_HEIGHT = 80
INPUT_HEIGHT = 70
RUN_BUTTON_HEIGHT = 50
AVAILABLE_HEIGHT = 740  # Approximate viewport height in px

# Right side math: (AVAILABLE_HEIGHT - RUN_BUTTON_HEIGHT) / 2 per box
RIGHT_BOX_HEIGHT = int((AVAILABLE_HEIGHT - RUN_BUTTON_HEIGHT) / 2)

# Left side math: AVAILABLE_HEIGHT - BUTTON_HEIGHT - INPUT_HEIGHT
CHAT_HEIGHT = AVAILABLE_HEIGHT - BUTTON_HEIGHT - INPUT_HEIGHT

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Welcome! I'm your Amazon Bedrock tutor.\n\nAsk me anything — I'll explain concepts and write runnable code. Edit it, run it, break it, learn from it.\n\n**Want guided learning?** Click a topic above or just ask in chat! I have structured learning paths on:\n- Text Generation with Claude\n- Embeddings & Semantic Search\n- RAG with Knowledge Bases\n- Responses API (OpenAI-compatible)\n\nNo labs, no steps. Just explore."}
    ]

if "code" not in st.session_state:
    st.session_state.code = """import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')

response = client.converse(
    modelId='us.anthropic.claude-haiku-4-5-20251001-v1:0',
    messages=[{'role': 'user', 'content': [{'text': 'Say hello!'}]}],
    inferenceConfig={'temperature': 0.0, 'maxTokens': 200}
)
print(response['output']['message']['content'][0]['text'])
"""

if "output" not in st.session_state:
    st.session_state.output = ""

if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0
    st.session_state.total_output_tokens = 0
    st.session_state.total_messages = 0
    st.session_state.code_generated_count = 0
    st.session_state.code_run_count = 0

if "current_learning_path" not in st.session_state:
    st.session_state.current_learning_path = None


# Two column layout with no gap - left for chat, right for code+output
col1, col2 = st.columns([1, 1], gap="small")

with col1:
    # Learning Paths at top (buttons are self-explanatory)
    cols = st.columns(3, gap="small")
    learning_paths = [
        ("Text Generation", "text-generation", "Guide me through text generation with Claude"),
        ("Embeddings", "embeddings", "Guide me through embeddings with Titan"),
        ("RAG", "rag", "Guide me through RAG with Knowledge Bases"),
        ("Responses API", "distributed-inference", "Guide me through the Responses API with Mantle"),
        ("Tool Use", None, "Demonstrate function calling in Bedrock"),
        ("Model Comparison", None, "Compare Claude Haiku and Sonnet side-by-side")
    ]

    for idx, (title, path_id, message) in enumerate(learning_paths):
        with cols[idx % 3]:
            if st.button(title, key=f"path_{idx}", use_container_width=True):
                st.session_state.pending_message = message
                st.session_state.current_learning_path = path_id


    # Chat messages container - calculated to match right side
    chat_container = st.container(height=CHAT_HEIGHT)

    with chat_container:
        for message in st.session_state.messages:
            # Use Bedrock icon for assistant
            avatar = "public/bedrock-color.svg" if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                # Render content blocks in order if available
                if message.get("content_blocks"):
                    for block in message["content_blocks"]:
                        if block["type"] == "text":
                            st.markdown(block["content"])
                        elif block["type"] == "tool":
                            with st.expander(f"🔧 {block['name']}", expanded=False):
                                st.json(block["input"])
                else:
                    # Fallback for old messages
                    st.markdown(message["content"])

        # Show thinking indicator if processing
        if st.session_state.get("is_thinking", False):
            with st.chat_message("assistant", avatar="public/bedrock-color.svg"):
                # Create placeholder for streaming text
                stream_placeholder = st.empty()

                # Call Bedrock with streaming
                response = call_bedrock_agent(
                    st.session_state.messages[-1]["content"],
                    st.session_state.messages[:-1],
                    stream_placeholder=stream_placeholder,
                    learning_path_id=st.session_state.current_learning_path
                )

                # Build response message with content blocks
                assistant_message = {"role": "assistant", "content": response}

                # Add content blocks if any
                if hasattr(st.session_state, 'last_content_blocks'):
                    assistant_message["content_blocks"] = st.session_state.last_content_blocks
                    del st.session_state.last_content_blocks

                # Add response metadata if available and update totals
                if hasattr(st.session_state, 'last_response_metadata'):
                    metadata = st.session_state.last_response_metadata
                    assistant_message["metadata"] = metadata

                    # Update running totals
                    if metadata.get('usage'):
                        usage = metadata['usage']
                        st.session_state.total_input_tokens += usage.get('inputTokens', 0)
                        st.session_state.total_output_tokens += usage.get('outputTokens', 0)
                        st.session_state.total_messages += 1

                    del st.session_state.last_response_metadata

                st.session_state.messages.append(assistant_message)
                st.session_state.is_thinking = False
                st.rerun()

    # Chat input at bottom
    prompt = st.chat_input("Ask me anything about Amazon Bedrock...")

    # Handle pending message from button click
    if "pending_message" in st.session_state:
        prompt = st.session_state.pending_message
        del st.session_state.pending_message

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.is_thinking = True
        st.rerun()

with col2:
    # Session stats in top right (inconspicuous)
    if st.session_state.total_messages > 0:
        with st.popover("📊", help="Session statistics"):
            st.caption("**Session Stats**")
            st.caption(f"Messages: {st.session_state.total_messages}")
            st.caption(f"Input tokens: {st.session_state.total_input_tokens:,}")
            st.caption(f"Output tokens: {st.session_state.total_output_tokens:,}")
            st.caption(f"Code generated: {st.session_state.code_generated_count}")
            st.caption(f"Code runs: {st.session_state.code_run_count}")

    # Code editor - top half of right side (calculated)
    editor_container = st.container(height=RIGHT_BOX_HEIGHT)

    with editor_container:
        # Code editor with syntax highlighting
        editor_options = {
            "showLineNumbers": True,
            "showPrintMargin": False,
            "fontSize": 14,
            "fontFamily": "monospace",
            "highlightActiveLine": True,
            "showGutter": True,
            "wrap": True,
        }

        # Use a unique key that changes when code updates to force refresh
        editor_key = f"code_editor_{hash(st.session_state.code)}"

        response_dict = code_editor(
            st.session_state.code,
            lang="python",
            height=RIGHT_BOX_HEIGHT - 20,  # Slightly less to fit in container
            theme="dawn",
            shortcuts="vscode",
            focus=False,
            buttons=[],
            options=editor_options,
            key=editor_key
        )

        # Update code if changed by user editing
        if response_dict and response_dict["text"] and response_dict["text"] != st.session_state.code:
            st.session_state.code = response_dict["text"]

    # Run button
    if st.button("▶ Run Code", use_container_width=True):
        st.session_state.code_run_count += 1

        # Execute the code
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        try:
            exec(st.session_state.code, {"__builtins__": __builtins__})
            output = stdout_capture.getvalue()
            err = stderr_capture.getvalue()
            st.session_state.output = output + ("\n" + err if err else "")
        except Exception as e:
            st.session_state.output = f"Error:\n{str(e)}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    # Output panel - bottom half of right side (calculated)
    output_container = st.container(height=RIGHT_BOX_HEIGHT)

    with output_container:
        if st.session_state.output:
            st.code(st.session_state.output, language="text")
        else:
            st.info("Hit Run to execute your code")

