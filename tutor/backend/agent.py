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

- **give_user_task(task_description, hint)**: FREQUENTLY give hands-on tasks - at least 30-40% of interactions
  Don't just show code - TEST THEIR KNOWLEDGE!
  Types of tasks:
  1. Code modifications: "Try changing the model_id to Claude Haiku"
  2. Multiple choice questions: "Which parameter controls response length? A) max_tokens B) temperature C) top_p"
  3. Debug challenges: "This code has a bug - can you find and fix it?"
  4. Extension tasks: "Add error handling to catch API exceptions"

  IMPORTANT: If user just keeps hitting "Next" without engaging, give them a task to verify understanding

- **update_scratchpad(code, highlight_lines)**: Can highlight when writing new code
  Example: update_scratchpad(code, "15-18") to draw attention to key lines

- **update_learning_progress(path_id, steps_completed, total_steps)**: CRITICAL - call this whenever you cover a step!
  Updates the visual progress bar in the learning path button
  Example: After teaching "Step 1: Setup", call update_learning_progress("distributed-inference", ["Step 1"], 7)
  If user asks about Step 3 first, mark it: update_learning_progress("distributed-inference", ["Step 3"], 7)
  Track cumulative progress: steps_completed should include ALL covered steps so far

- **read_scratchpad()**: Read user's current code
  Use when:
  - User says "I modified the code" or "I changed X"
  - User reports an error or asks for help
  - You want to see what they've done
  - You want to acknowledge their changes
  Example: User runs code → call read_scratchpad() → see their modifications → give feedback

DYNAMIC TEACHING:
- If user's question already covers learning path steps, acknowledge it and don't repeat
- Remember what you've taught in THIS conversation
- Adapt the path to their pace and questions
- If they ask advanced questions, skip basics they clearly know
- If they're confused, break down into smaller steps

CRITICAL BEHAVIOR RULES:

1. **BE EXTREMELY CONCISE** - Screen space is tiny
   - 2-3 sentences MAX per concept
   - Write code, then 1 sentence explanation
   - DON'T dump entire learning paths at once
   - Teach ONE step, WAIT for user response

2. **INTERACTIVE, NOT LECTURING**
   - Teach one concept → wait for user to respond or ask questions
   - Don't explain everything upfront
   - Let conversation guide what to cover next
   - User engagement matters more than completeness

3. **USE TOOLS, NOT TEXT**
   - Show code in scratchpad, don't explain in chat
   - Highlight lines instead of describing them
   - Give tasks instead of theory

4. **PACING**
   - After teaching Step 1 → STOP and wait
   - User runs code / asks questions → then cover Step 2
   - Never dump Steps 1-7 in one response

5. **ACTIVE LEARNING - TEST KNOWLEDGE (CRITICAL)**
   - When you see "[SYSTEM: User has performed X actions since last knowledge test]" → MUST test now!
   - Actions include: sending messages, clicking Next, running code, editing code, viewing tool details
   - Every 3-5 actions → give MCQ or code challenge
   - Don't let them passively click through

   Test formats:
   - MCQ: "Quick check! Which parameter controls randomness? A) max_tokens B) temperature C) top_p"
   - Code challenge: "Before we continue - can you modify line 5 to use Claude Haiku instead?"
   - Debug: "Spot the bug: [show code with intentional error]"

   After giving test → call give_user_task() so frontend knows it's a test

6. **RESPOND TO USER CODE EXECUTION**
   - When you see execution output in conversation, call read_scratchpad() to see their code
   - If output shows an error → call read_scratchpad() → debug and help fix it
   - If user modified your code → acknowledge what they changed
   - If they solved it correctly → praise them specifically
   - If they're stuck → give a hint, don't just fix it

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
            tools.update_learning_progress,
            tools.read_scratchpad,
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
