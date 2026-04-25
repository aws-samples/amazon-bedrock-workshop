"""Test that agent ACTUALLY uses tools when asked."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from strands import Agent
from strands.models import BedrockModel
from strands.types.content import Message
import tutor_tools

# Mock streamlit
import streamlit as st
st.session_state.code = ''
st.session_state.code_generated_count = 0
st.session_state.current_learning_path = None


def test_responses_api_query():
    """Test the EXACT query: 'Guide me through the Responses API with Mantle'"""
    print("=" * 70)
    print("TEST: User asks 'Guide me through the Responses API with Mantle'")
    print("=" * 70)

    # Exactly as in streamlit_app.py
    conversation_history = [
        {
            "role": "assistant",
            "content": "👋 Welcome! I'm your Amazon Bedrock tutor."
        }
    ]

    messages = []
    for msg in conversation_history:
        if msg["role"] in ["user", "assistant"]:
            content = msg["content"]
            if isinstance(content, str):
                content = [{'text': content}]
            messages.append(Message(role=msg["role"], content=content))

    # System prompt from streamlit_app.py
    system_prompt = """You are an expert Amazon Bedrock tutor in an interactive workshop with a live code scratchpad.

The interface has two panels:
- LEFT: This chat where you explain concepts
- RIGHT: A code scratchpad where users can edit and run Python code

🚨 MANDATORY TOOL USAGE WORKFLOW 🚨

When a user asks ANY question about a topic, you MUST follow this EXACT sequence:

STEP 1: ALWAYS call find_learning_paths tool first
- Search for keywords from the user's question
- Example: user asks "responses API" → call find_learning_paths(query="responses API")
- Example: user asks "embeddings" → call find_learning_paths(query="embeddings")
- DO NOT skip this step. ALWAYS search first.

STEP 2: If matches found, call load_learning_path
- Use the path_id from the search results
- Example: if find_learning_paths returns id="distributed-inference", call load_learning_path(path_id="distributed-inference")

STEP 3: Follow the loaded curriculum EXACTLY
- Present the content step-by-step from the learning path
- Use update_scratchpad tool to write the code examples
- Guide the user through each step

STEP 4: If NO matches found, then explain conversationally
- Only if find_learning_paths returns empty results
- Then write example code and use update_scratchpad

When explaining:
- Use the update_scratchpad tool to write example code to the scratchpad
- Point them to the scratchpad: "**Check the code in the scratchpad → and hit ▶ Run to try it!**"
- Be encouraging and hands-on

Code guidelines:
- Write complete, runnable Python using boto3
- Always set region_name='us-east-1'
- Use inference profile IDs (e.g., 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
- Be concise and practical
- Users can edit your code, so make it a good starting point

Available models:
- Claude Sonnet 4.5: us.anthropic.claude-sonnet-4-5-20250929-v1:0
- Claude Haiku 4.5: us.anthropic.claude-haiku-4-5-20251001-v1:0
- Nova Lite: us.amazon.nova-lite-v1:0
- Nova Pro: us.amazon.nova-pro-v1:0
"""

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
        callback_handler=None
    )

    print("\n1. User prompt: 'Guide me through the Responses API with Mantle'")
    user_prompt = "Guide me through the Responses API with Mantle"

    # Enable detailed event logging to see tool calls
    print("\n2. Invoking agent...")
    result = asyncio.run(agent.invoke_async(user_prompt))

    # Extract response
    content_blocks = result.message.get('content', [])
    text_parts = []
    for block in content_blocks:
        if isinstance(block, dict) and 'text' in block:
            text_parts.append(block['text'])
    response_text = '\n'.join(text_parts)

    print(f"\n3. Response preview:")
    print(f"   {response_text[:400]}...")

    print(f"\n4. Stop reason: {result.stop_reason}")

    # Check if agent mentioned the learning path
    response_lower = response_text.lower()

    print(f"\n5. Verification:")
    if 'distributed-inference' in response_lower or ('mantle' in response_lower and 'openai' in response_lower):
        print("   ✅ Response mentions the distributed-inference learning path")
    else:
        print("   ❌ Response does NOT mention the learning path")
        print(f"   Full response:\n{response_text}")
        raise AssertionError("Agent did not use find_learning_paths tool or mention the learning path!")

    # Check if code was written to scratchpad
    if st.session_state.code and len(st.session_state.code) > 50:
        print(f"   ✅ Code written to scratchpad ({len(st.session_state.code)} chars)")
        print(f"   Code preview: {st.session_state.code[:100]}...")
    else:
        print("   ⚠️  No code written to scratchpad")

    print("\n" + "=" * 70)
    print("✅ TEST PASSED - Agent used tools and found learning path!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_responses_api_query()
        print("\n🎉 All tool usage tests passed!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
