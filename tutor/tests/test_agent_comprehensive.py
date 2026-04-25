"""Comprehensive agent test simulating actual streamlit usage."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from strands import Agent
from strands.models import BedrockModel
from strands.types.content import Message


def test_actual_conversation_flow():
    """
    Test the EXACT flow that happens in streamlit:
    1. Start with welcome message
    2. User asks a question
    3. Agent responds
    """
    print("=" * 60)
    print("COMPREHENSIVE TEST: Simulating Real Streamlit Flow")
    print("=" * 60)

    # Simulate initial session state with welcome message
    conversation_history = [
        {
            "role": "assistant",
            "content": "👋 Welcome! I'm your Amazon Bedrock tutor.\n\nAsk me anything — I'll explain concepts and write runnable code."
        }
    ]

    print("\n1. Initial conversation history:")
    for msg in conversation_history:
        print(f"   {msg['role']}: {msg['content'][:80]}...")

    # User asks a question
    user_prompt = "Guide me through the Responses API with Mantle"
    print(f"\n2. User asks: '{user_prompt}'")

    # Build messages for strands (exactly as streamlit does)
    messages = []
    for msg in conversation_history:
        if msg["role"] in ["user", "assistant"]:
            # Convert string content to list of content blocks
            content = msg["content"]
            if isinstance(content, str):
                content = [{'text': content}]
            messages.append(Message(role=msg["role"], content=content))

    print(f"\n3. Converted {len(messages)} messages to strands format")
    for i, msg in enumerate(messages):
        print(f"   Message {i}: role={msg['role']}, content blocks={len(msg['content'])}")

    # Create agent
    print("\n4. Creating strands agent...")
    agent = Agent(
        model=BedrockModel(
            model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        ),
        messages=messages,
        system_prompt="You are an expert Amazon Bedrock tutor.",
        callback_handler=None
    )
    print("   ✓ Agent created")

    # Invoke agent
    print(f"\n5. Invoking agent with prompt: '{user_prompt}'")
    try:
        result = asyncio.run(agent.invoke_async(user_prompt))
        print("   ✓ Agent invoked successfully!")

        # Extract response (exactly as streamlit does)
        if hasattr(result, 'message') and isinstance(result.message, dict):
            content_blocks = result.message.get('content', [])
            text_parts = []
            for block in content_blocks:
                if isinstance(block, dict) and 'text' in block:
                    text_parts.append(block['text'])
            response_text = '\n'.join(text_parts) if text_parts else str(result.message)
        else:
            response_text = str(result)

        print(f"\n6. Response extracted:")
        print(f"   Length: {len(response_text)} characters")
        print(f"   Preview: {response_text[:200]}...")

        print(f"\n7. Stop reason: {result.stop_reason}")

        # Verify response is reasonable
        assert len(response_text) > 10, "Response too short"
        assert result.stop_reason in ['end_turn', 'max_tokens', 'stop_sequence'], f"Unexpected stop reason: {result.stop_reason}"

        print("\n" + "=" * 60)
        print("✅ COMPREHENSIVE TEST PASSED!")
        print("=" * 60)

        return response_text

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_with_tool_calling():
    """Test that tools can be called (testing find_learning_paths)."""
    print("\n" + "=" * 60)
    print("TEST: Tool Calling with find_learning_paths")
    print("=" * 60)

    # Import tools
    import tutor_tools

    # Mock streamlit session_state for tool
    import streamlit as st
    if not hasattr(st.session_state, 'code'):
        st.session_state.code = ""
        st.session_state.code_generated_count = 0
        st.session_state.current_learning_path = None

    agent = Agent(
        model=BedrockModel(
            model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        ),
        tools=[
            tutor_tools.find_learning_paths,
            tutor_tools.update_scratchpad
        ],
        system_prompt="""When the user asks about a topic, use find_learning_paths to search for it.
Then tell them what you found.""",
        callback_handler=None
    )

    print("\n1. Asking agent to search for 'responses API'...")
    result = asyncio.run(agent.invoke_async("Search for learning paths about responses API"))

    content_blocks = result.message.get('content', [])
    text_parts = []
    for block in content_blocks:
        if isinstance(block, dict) and 'text' in block:
            text_parts.append(block['text'])
    response_text = '\n'.join(text_parts)

    print(f"\n2. Response: {response_text[:300]}...")
    print(f"\n3. Stop reason: {result.stop_reason}")

    # Check if response mentions the learning path
    assert 'distributed-inference' in response_text.lower() or 'responses api' in response_text.lower() or 'mantle' in response_text.lower(), \
        "Response should mention the found learning path"

    print("\n✅ Tool calling test passed!")


if __name__ == "__main__":
    try:
        # Run comprehensive test
        test_actual_conversation_flow()

        # Run tool test
        test_with_tool_calling()

        print("\n" + "🎉" * 30)
        print("ALL COMPREHENSIVE TESTS PASSED!")
        print("🎉" * 30)

    except Exception as e:
        print(f"\n💥 TEST SUITE FAILED: {e}")
        sys.exit(1)
