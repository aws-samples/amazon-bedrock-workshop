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
import tutor_agent

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

# Agent wrapper using tutor_agent module
def call_bedrock_agent(prompt: str, conversation_history: list, response_container=None, learning_path_id=None):
    """Call Bedrock agent using tutor_agent module."""

    # Get learning path content if provided
    learning_path_content = None
    if learning_path_id and learning_path_id in LEARNING_PATHS:
        path = LEARNING_PATHS[learning_path_id]
        learning_path_content = f"# LEARNING PATH: {path['title']}\n\n{path['content']}"

    try:
        # Stream agent response
        import asyncio

        async def stream_agent():
            """Stream agent events and show inline."""
            response_text = ""
            tool_calls = []

            # Create placeholders in container for inline display
            tool_placeholders = {}
            text_placeholder = None
            if response_container:
                text_placeholder = response_container.empty()

            async for event in tutor_agent.invoke_agent(
                prompt=prompt,
                conversation_history=conversation_history,
                region=REGION,
                learning_path_content=learning_path_content
            ):
                if event['type'] == 'text':
                    response_text += event['content']
                    if text_placeholder:
                        text_placeholder.markdown(response_text)

                elif event['type'] == 'tool_use':
                    tool_calls.append({
                        'name': event['name'],
                        'input': event['input'],
                        'tool_use_id': event.get('tool_use_id')
                    })

                    # Show tool inline immediately
                    if response_container:
                        with response_container.expander(f"🔧 {event['name']}", expanded=False):
                            st.json(event['input'])

                    # Handle update_scratchpad specially - update session state immediately
                    if event['name'] == 'update_scratchpad':
                        code = event['input'].get('code', '')
                        print(f"[STREAMLIT] update_scratchpad event received, code length: {len(code)}")
                        if code:
                            print(f"[STREAMLIT] Updating session_state.code (was {len(st.session_state.code)} chars)")
                            st.session_state.code = code
                            st.session_state.code_generated_count = st.session_state.get('code_generated_count', 0) + 1
                            st.session_state.code_was_updated = True
                            print(f"[STREAMLIT] Now {len(st.session_state.code)} chars, hash: {hash(code)}")

                    # Recreate text placeholder after tool so text continues below
                    if response_container and text_placeholder:
                        text_placeholder = response_container.empty()
                        if response_text:
                            text_placeholder.markdown(response_text)

            return response_text, tool_calls

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        response_text, tool_calls = loop.run_until_complete(stream_agent())

        # Store tool calls as content blocks for display
        content_blocks = []
        for tool in tool_calls:
            content_blocks.append({
                'type': 'tool',
                'name': tool['name'],
                'input': tool['input']
            })
        if response_text:
            content_blocks.append({
                'type': 'text',
                'content': response_text
            })

        st.session_state.last_content_blocks = content_blocks

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
    st.session_state.code = """# Amazon Bedrock Responses API Example
# Stateful conversations with server-managed context

import os
from openai import OpenAI

# Setup (get your API key from Bedrock console)
os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"
os.environ["OPENAI_API_KEY"] = "your-bedrock-api-key-here"

client = OpenAI()

# Turn 1: Start a conversation
response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[{"role": "user", "content": "What is Amazon Bedrock?"}]
)

print(f"Turn 1: {response.output_text}")
print(f"Response ID: {response.id}")

# Turn 2: Continue with context (server remembers!)
response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[{"role": "user", "content": "What models does it support?"}],
    previous_response_id=response.id  # <-- Links to previous turn
)

print(f"\\nTurn 2: {response.output_text}")
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
                # Create container for inline display of tools and text
                response_container = st.container()

                # Call Bedrock with streaming
                response = call_bedrock_agent(
                    st.session_state.messages[-1]["content"],
                    st.session_state.messages[:-1],
                    response_container=response_container,
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

                # Debug: Check if code was actually updated
                if st.session_state.get('code_was_updated'):
                    print(f"[RERUN] Code was updated during this turn, current length: {len(st.session_state.code)}")
                    del st.session_state.code_was_updated

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

