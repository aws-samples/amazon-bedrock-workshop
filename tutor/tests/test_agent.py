"""Test the strands agent setup."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from strands import Agent
from strands.models import BedrockModel
from strands.types.content import Message
import tutor_tools


def test_agent_basic():
    """Test basic agent invocation."""
    print("Testing basic agent invocation...")

    agent = Agent(
        model=BedrockModel(
            model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
        ),
        tools=[
            tutor_tools.update_scratchpad,
            tutor_tools.find_learning_paths,
            tutor_tools.load_learning_path
        ],
        system_prompt="You are a helpful assistant.",
        callback_handler=None
    )

    # Test invoke_async
    result = asyncio.run(agent.invoke_async("Say hello"))

    print(f"✓ Agent invoked successfully")
    print(f"  Stop reason: {result.stop_reason}")
    print(f"  Message type: {type(result.message)}")
    print(f"  Content: {result.message.get('content', str(result.message))[:100]}...")

    return result


def test_agent_with_tools():
    """Test agent with tool calling."""
    print("\nTesting agent with tool calling...")

    agent = Agent(
        model=BedrockModel(
            model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
        ),
        tools=[
            tutor_tools.find_learning_paths,
        ],
        system_prompt="Search for learning paths when asked.",
        callback_handler=None
    )

    result = asyncio.run(agent.invoke_async("Find learning paths about embeddings"))

    print(f"✓ Tool calling works")
    print(f"  Stop reason: {result.stop_reason}")
    print(f"  Response: {result.message.get('content', str(result.message))[:200]}...")

    return result


def test_message_history():
    """Test agent with message history."""
    print("\nTesting agent with message history...")

    messages = [
        Message(role="user", content="My name is Alice"),
        Message(role="assistant", content="Nice to meet you, Alice!"),
    ]

    agent = Agent(
        model=BedrockModel(
            model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
        ),
        messages=messages,
        system_prompt="Remember user information.",
        callback_handler=None
    )

    result = asyncio.run(agent.invoke_async("What is my name?"))

    print(f"✓ Message history works")
    print(f"  Response: {result.message.get('content', str(result.message))}")

    return result


if __name__ == "__main__":
    print("=== Testing Strands Agent Setup ===\n")

    try:
        test_agent_basic()
        print("\n✅ Basic test passed")
    except Exception as e:
        print(f"\n❌ Basic test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    try:
        test_agent_with_tools()
        print("\n✅ Tool test passed")
    except Exception as e:
        print(f"\n❌ Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    try:
        test_message_history()
        print("\n✅ Message history test passed")
    except Exception as e:
        print(f"\n❌ Message history test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n=== All tests passed! ===")
