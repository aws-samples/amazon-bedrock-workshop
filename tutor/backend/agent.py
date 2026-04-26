"""
Bedrock tutor agent - FastAPI version
"""
from typing import AsyncIterator, Optional, List, Dict, Any
from strands import Agent
from strands.models import BedrockModel
from strands.types.content import Message
import tools


def create_tutor_agent(
    conversation_history: List[Dict[str, str]],
    region: str,
    learning_path_content: Optional[str] = None
) -> Agent:
    """Create a tutor agent with tools and system prompt"""

    # Convert conversation history to strands Message format
    messages = []
    for msg in conversation_history:
        if msg["role"] in ["user", "assistant"]:
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
   - DO NOT answer without searching first

2. IF learning path found: Call load_learning_path(path_id="<id>")
   - Follow it EXACTLY step-by-step
   - Use update_scratchpad tool to write code examples
   - Use ONLY the code patterns shown in the learning path

3. IF NO learning path found: Then answer from general knowledge

When explaining:
- Be CONCISE - screen space is limited
- Use update_scratchpad tool to write code examples
- Point to scratchpad: "**Check the code in the scratchpad → and hit ▶ Run!**"
- Focus on essentials, not lengthy explanations

Code guidelines:
- Write complete, runnable Python using boto3
- Always set region_name='{region}'
- Use inference profile IDs (e.g., 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
- Be concise and practical

Available models:
- Claude Sonnet 4.5: us.anthropic.claude-sonnet-4-5-20250929-v1:0
- Claude Haiku 4.5: us.anthropic.claude-haiku-4-5-20251001-v1:0
- Nova Lite: us.amazon.nova-lite-v1:0
- Nova Pro: us.amazon.nova-pro-v1:0
"""

    # Add learning path context if provided
    if learning_path_content:
        system_prompt += f"\n\n# ACTIVE LEARNING PATH\n\n{learning_path_content}\n\n"
        system_prompt += "Follow the teaching flow in the learning path. Present each step progressively."

    # Create agent
    agent = Agent(
        model=BedrockModel(
            model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        ),
        messages=messages,
        tools=[
            tools.update_scratchpad,
            tools.find_learning_paths,
            tools.load_learning_path
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
) -> AsyncIterator[Dict[str, Any]]:
    """
    Invoke the agent and stream response events.

    Yields:
        Dict events with 'type' key:
        - {'type': 'text', 'content': str}
        - {'type': 'tool_use', 'name': str, 'input': dict, 'tool_use_id': str}
        - {'type': 'tool_result', 'tool_use_id': str, 'content': str, 'status': str}
    """
    agent = create_tutor_agent(conversation_history, region, learning_path_content)
    tool_uses = {}

    async for event in agent.stream_async(prompt):
        if not isinstance(event, dict):
            continue

        # Text data
        if 'data' in event:
            yield {'type': 'text', 'content': event['data']}

        # Tool use events
        elif event.get('type') == 'tool_use_stream':
            tool_use = event.get('current_tool_use', {})
            tool_id = tool_use.get('toolUseId')
            tool_name = tool_use.get('name')
            tool_input = tool_use.get('input', '')

            if tool_id:
                tool_uses[tool_id] = {
                    'name': tool_name,
                    'input': tool_input
                }

        # Tool use completed
        elif 'event' in event and 'contentBlockStop' in event['event']:
            for tool_id, tool_data in tool_uses.items():
                try:
                    import json
                    parsed_input = json.loads(tool_data['input'])
                    yield {
                        'type': 'tool_use',
                        'name': tool_data['name'],
                        'input': parsed_input,
                        'tool_use_id': tool_id
                    }
                except (json.JSONDecodeError, KeyError):
                    pass
            tool_uses.clear()

        # Tool result events
        elif 'message' in event:
            message = event['message']
            if message.get('role') == 'user':
                for content_block in message.get('content', []):
                    if 'toolResult' in content_block:
                        tool_result = content_block['toolResult']
                        tool_id = tool_result.get('toolUseId')
                        status = tool_result.get('status', 'success')

                        result_content = tool_result.get('content', [])
                        result_text = ''
                        for result_block in result_content:
                            if 'text' in result_block:
                                result_text += result_block['text']

                        yield {
                            'type': 'tool_result',
                            'tool_use_id': tool_id,
                            'content': result_text,
                            'status': status
                        }
