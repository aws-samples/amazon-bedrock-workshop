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

# Tool definitions
TOOLS = [
    {
        "toolSpec": {
            "name": "update_scratchpad",
            "description": "Updates the code scratchpad with new Python code. Use this whenever you write code examples for the user.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Complete Python code to display in the scratchpad"
                        }
                    },
                    "required": ["code"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "find_learning_paths",
            "description": "Search for relevant learning paths based on keywords or topics. Use this when the user asks about a specific topic (e.g., 'responses API', 'embeddings', 'RAG').",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (keywords or topic to find)"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "load_learning_path",
            "description": "Load a specific learning path by ID to get the full teaching content. Use this after finding a relevant path with find_learning_paths.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "path_id": {
                            "type": "string",
                            "description": "The ID of the learning path to load (e.g., 'text-generation', 'embeddings', 'rag', 'distributed-inference')"
                        }
                    },
                    "required": ["path_id"]
                }
            }
        }
    }
]

# Simple agent that calls Bedrock directly with tool support
def call_bedrock_agent(prompt: str, conversation_history: list, stream_placeholder=None, learning_path_id=None):
    """Call Bedrock Claude model directly with tool calling and streaming."""
    client = boto3.client('bedrock-runtime', region_name=REGION)

    # Build message history
    messages = []
    for msg in conversation_history:
        if msg["role"] in ["user", "assistant"]:
            messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })

    # Add current prompt
    messages.append({
        "role": "user",
        "content": [{"text": prompt}]
    })

    # Base system prompt
    system_prompt = """You are an expert Amazon Bedrock tutor in an interactive workshop with a live code scratchpad.

The interface has two panels:
- LEFT: This chat where you explain concepts
- RIGHT: A code scratchpad where users can edit and run Python code

When users ask questions:
1. First check if the question is about a specific topic that might have a learning path (e.g., "responses API", "embeddings", "RAG", "text generation")
   - Use find_learning_paths tool to search for relevant learning paths
   - If a relevant learning path is found, use load_learning_path to load it and follow that curriculum
2. Explain the concept conversationally in the chat
3. Use the update_scratchpad tool to write example code to the scratchpad
4. Point them to the scratchpad: "**Check the code in the scratchpad → and hit ▶ Run to try it!**"
5. Be encouraging and hands-on

Tools available:
- find_learning_paths: Search for learning paths by keywords/topics
- load_learning_path: Load a specific learning path curriculum
- update_scratchpad: Write code examples to the scratchpad

Code guidelines:
- Write complete, runnable Python using boto3
- Always set region_name='""" + REGION + """'
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
        response = client.converse_stream(
            modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
            messages=messages,
            system=[{"text": system_prompt}],
            inferenceConfig={
                'temperature': 0.7,
                'maxTokens': 2000
            },
            toolConfig={"tools": TOOLS}
        )

        # Process streaming response - track content blocks in order
        content_blocks = []  # List of {type: 'text'|'tool', content: ...}
        current_block = None
        current_text = ""
        stop_reason = None
        usage = None

        for event in response['stream']:
            if 'contentBlockStart' in event:
                start = event['contentBlockStart']
                block_index = start.get('contentBlockIndex', 0)

                # Save previous text block if any
                if current_text:
                    content_blocks.append({"type": "text", "content": current_text})
                    current_text = ""

                if 'toolUse' in start.get('start', {}):
                    current_block = {
                        "type": "tool",
                        "name": start['start']['toolUse']['name'],
                        "tool_use_id": start['start']['toolUse']['toolUseId'],
                        "input": ""
                    }

            elif 'contentBlockDelta' in event:
                delta = event['contentBlockDelta']['delta']
                if 'text' in delta:
                    text_chunk = delta['text']
                    current_text += text_chunk
                    if stream_placeholder:
                        stream_placeholder.markdown(current_text)
                elif 'toolUse' in delta:
                    if current_block and current_block['type'] == 'tool':
                        current_block["input"] += delta['toolUse']['input']

            elif 'contentBlockStop' in event:
                # Finalize current block
                if current_block and current_block['type'] == 'tool':
                    try:
                        tool_input = json.loads(current_block["input"])
                        current_block["input"] = tool_input

                        # Handle different tool types
                        if current_block['name'] == 'update_scratchpad':
                            code = tool_input.get('code', '')
                            st.session_state.code = code
                            st.session_state.code_generated_count += 1

                        elif current_block['name'] == 'find_learning_paths':
                            # Search learning paths by keywords
                            query = tool_input.get('query', '').lower()
                            matches = []
                            for path_id, path_data in LEARNING_PATHS.items():
                                keywords = [k.lower() for k in path_data.get('keywords', [])]
                                title = path_data.get('title', '').lower()
                                description = path_data.get('description', '').lower()

                                if (query in title or query in description or
                                    any(query in kw or kw in query for kw in keywords)):
                                    matches.append({
                                        'id': path_id,
                                        'title': path_data['title'],
                                        'description': path_data['description']
                                    })

                            current_block["result"] = matches

                        elif current_block['name'] == 'load_learning_path':
                            # Load full learning path content
                            path_id = tool_input.get('path_id', '')
                            if path_id in LEARNING_PATHS:
                                path_data = LEARNING_PATHS[path_id]
                                current_block["result"] = {
                                    'id': path_id,
                                    'title': path_data['title'],
                                    'content': path_data['content'][:5000]  # Limit content size
                                }
                                # Set as current learning path
                                st.session_state.current_learning_path = path_id
                            else:
                                current_block["result"] = {"error": f"Learning path '{path_id}' not found"}

                        content_blocks.append(current_block)
                    except json.JSONDecodeError:
                        pass
                    current_block = None

            elif 'messageStop' in event:
                stop_reason = event['messageStop'].get('stopReason')
                # Save any remaining text
                if current_text:
                    content_blocks.append({"type": "text", "content": current_text})

            elif 'metadata' in event:
                usage = event['metadata'].get('usage')

        # Store content blocks in order
        st.session_state.last_content_blocks = content_blocks

        # Store metadata
        st.session_state.last_response_metadata = {
            "stopReason": stop_reason,
            "usage": usage
        }

        # Return just text for backwards compat
        text_parts = [b['content'] for b in content_blocks if b['type'] == 'text']
        return ''.join(text_parts) if text_parts else "Code updated!"

    except Exception as e:
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
        {"role": "assistant", "content": "👋 Welcome! I'm your Amazon Bedrock tutor.\n\nAsk me anything — I'll explain concepts and write runnable code. Edit it, run it, break it, learn from it.\n\nNo labs, no steps. Just explore."}
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

