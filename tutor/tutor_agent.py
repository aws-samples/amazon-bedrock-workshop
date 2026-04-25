"""Bedrock tutor agent using strands framework."""

import asyncio
from typing import AsyncIterator, Optional, List, Dict, Any
from strands import Agent
from strands.models import BedrockModel
from strands.types.content import Message
import tutor_tools


def create_tutor_agent(
    conversation_history: List[Dict[str, str]],
    region: str,
    learning_path_content: Optional[str] = None
) -> Agent:
    """
    Create a tutor agent with tools and system prompt.

    Args:
        conversation_history: List of messages with 'role' and 'content'
        region: AWS region for Bedrock
        learning_path_content: Optional learning path curriculum to inject

    Returns:
        Configured Agent instance
    """
    # Convert conversation history to strands Message format
    messages = []
    for msg in conversation_history:
        if msg["role"] in ["user", "assistant"]:
            # Content must be list of content blocks
            content = msg["content"]
            if isinstance(content, str):
                content = [{'text': content}]
            messages.append(Message(role=msg["role"], content=content))

    # Build system prompt
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
   - Follow it EXACTLY step-by-step, presenting each concept progressively
   - Use ONLY the code patterns shown in the learning path (do NOT substitute with your own examples)
   - Use update_scratchpad tool to write the exact code examples from the learning path

3. IF NO learning path found: Then answer from general knowledge
   - Only after searching confirms no curated content exists

You cannot answer questions about Bedrock topics without first using find_learning_paths. You must search the learning path database first.

When explaining:
- Use the update_scratchpad tool to write example code to the scratchpad
- Point them to the scratchpad: "**Check the code in the scratchpad → and hit ▶ Run to try it!**"
- Be encouraging and hands-on

Code guidelines:
- Write complete, runnable Python using boto3
- Always set region_name='{region}'
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
    if learning_path_content:
        system_prompt += f"\n\n# ACTIVE LEARNING PATH\n\n{learning_path_content}\n\n"
        system_prompt += "Follow the teaching flow in the learning path. Present each step progressively, "
        system_prompt += "write the code examples to the scratchpad, and guide the user through the concepts."

    # Create agent
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

    return agent


async def invoke_agent(
    prompt: str,
    conversation_history: List[Dict[str, str]],
    region: str,
    learning_path_content: Optional[str] = None
) -> AsyncIterator[str]:
    """
    Invoke the agent and stream response text.

    Args:
        prompt: User's current message
        conversation_history: Previous messages
        region: AWS region
        learning_path_content: Optional learning path to inject

    Yields:
        Text chunks as they're generated
    """
    agent = create_tutor_agent(conversation_history, region, learning_path_content)

    async for event in agent.stream_async(prompt):
        if isinstance(event, dict) and 'data' in event:
            yield event['data']


def invoke_agent_sync(
    prompt: str,
    conversation_history: List[Dict[str, str]],
    region: str,
    learning_path_content: Optional[str] = None
) -> str:
    """
    Synchronous wrapper for invoke_agent.

    Returns:
        Complete response text
    """
    async def collect():
        text = ""
        async for chunk in invoke_agent(prompt, conversation_history, region, learning_path_content):
            text += chunk
        return text

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(collect())
