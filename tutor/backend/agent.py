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
   - This gives you the teaching curriculum but BE DYNAMIC
   - The learning path has steps, but adapt based on user's questions
   - If user asks about Step 3 content first, answer it and mark Step 3 as covered
   - Track which concepts from the path you've covered
   - Don't force linear progression - follow the user's curiosity
   - Use ONLY the code patterns shown in the learning path
   - Follow ALL instructions in the learning path (especially model discovery patterns)

3. IF NO learning path found: Then answer from general knowledge

MAKING IT INTERACTIVE (use these tools strategically):

- **highlight_code(line_range, explanation)**: When explaining existing code, highlight the relevant lines
  Example: "Let me show you the authentication part" → highlight_code("10-12", "AWS credentials setup")

- **give_user_task(task_description, hint)**: About 20% of the time, give hands-on tasks
  Don't just show code - ask them to try something!
  Examples:
  - "Try changing the model_id to a different Claude version"
  - "Modify the prompt to ask about a different AWS service"
  - "Add error handling to catch API exceptions"
  Make tasks relevant to what you just taught

- **update_scratchpad(code, highlight_lines)**: Can highlight when writing new code
  Example: update_scratchpad(code, "15-18") to draw attention to key lines

DYNAMIC TEACHING:
- If user's question already covers learning path steps, acknowledge it and don't repeat
- Remember what you've taught in THIS conversation
- Adapt the path to their pace and questions
- If they ask advanced questions, skip basics they clearly know
- If they're confused, break down into smaller steps

When explaining:
- Be CONCISE - screen space is limited
- Use code highlighting to point to specific parts
- Give hands-on tasks to reinforce learning
- Make it conversational, not lecturing

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
        system_prompt += """This is your curriculum guide, but be ADAPTIVE:
- Track which steps/concepts you've already covered in this conversation
- If user asks about Step 5 first, teach it and remember you covered it
- Don't repeat concepts the user clearly understands
- Use the learning path as a checklist, not a script
- If conversation diverges, that's fine - follow their interest
- Periodically check if there are important concepts from the path they haven't seen yet"""

    # Create agent
    agent = Agent(
        model=BedrockModel(
            model_id='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        ),
        messages=messages,
        tools=[
            tools.update_scratchpad,
            tools.highlight_code,
            tools.give_user_task,
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
