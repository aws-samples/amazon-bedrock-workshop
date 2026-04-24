---
id: text-generation
title: "Text Generation with Claude"
description: "Learn to call Claude models using the Converse API"
difficulty: beginner
duration: "10 minutes"
prerequisites:
  - Basic Python knowledge
  - AWS credentials configured
models:
  - Claude Sonnet 4.5
  - Claude Haiku 4.5
apis:
  - bedrock-runtime.converse
---

# Text Generation with Claude

This learning path teaches the fundamentals of calling Claude models on Amazon Bedrock.

## Teaching Flow

### Step 1: Minimal Hello World
**Goal:** Get Claude to respond to a simple prompt

**What to show:**
- Import boto3 and create bedrock-runtime client
- Use the Converse API with a single user message
- Print the response text

**Code pattern:**
```python
import boto3

client = boto3.client('bedrock-runtime', region_name='REGION')

response = client.converse(
    modelId='us.anthropic.claude-haiku-4-5-20251001-v1:0',
    messages=[
        {'role': 'user', 'content': [{'text': 'Hello! Introduce yourself.'}]}
    ]
)

print(response['output']['message']['content'][0]['text'])
```

**Key points to emphasize:**
- Use inference profile IDs (e.g., `us.anthropic.claude-haiku-4-5-...`)
- Response structure: `response['output']['message']['content'][0]['text']`
- Start with Haiku for fast responses

**Common pitfalls:**
- Using base model IDs instead of inference profiles
- Not extracting text from the nested response structure

---

### Step 2: Control Output with Parameters
**Goal:** Understand how temperature and maxTokens affect responses

**What to show:**
- Add `inferenceConfig` with temperature and maxTokens
- Demonstrate temperature=0.0 for deterministic output
- Show temperature=1.0 for creative output
- Set maxTokens to control response length

**Code pattern:**
```python
response = client.converse(
    modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    messages=[
        {'role': 'user', 'content': [{'text': 'Write a creative story about a robot.'}]}
    ],
    inferenceConfig={
        'temperature': 0.9,  # Higher = more creative
        'maxTokens': 500     # Limit response length
    }
)
```

**Key points to emphasize:**
- Temperature range: 0.0 (deterministic) to 1.0 (creative)
- Default temperature is 1.0
- maxTokens prevents runaway responses
- Temperature=0.0 is ideal for classification, extraction, structured tasks
- Temperature=0.7-1.0 is good for creative writing, brainstorming

**Best practices:**
- Start with temperature=0.7 as a balanced default
- Use temperature=0.0 for production systems requiring consistency
- Set maxTokens to prevent unexpected costs

---

### Step 3: Multi-turn Conversations
**Goal:** Build a conversation with context

**What to show:**
- Add multiple messages with alternating user/assistant roles
- Show how Claude remembers context from earlier messages
- Demonstrate the conversation pattern

**Code pattern:**
```python
messages = [
    {'role': 'user', 'content': [{'text': 'My name is Alice.'}]},
    {'role': 'assistant', 'content': [{'text': 'Nice to meet you, Alice! How can I help you today?'}]},
    {'role': 'user', 'content': [{'text': 'What is my name?'}]}
]

response = client.converse(
    modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    messages=messages
)
```

**Key points to emphasize:**
- Messages must alternate between user and assistant
- Earlier messages provide context for the current request
- This is how chatbots work - each turn builds on previous context

---

### Step 4: System Prompts for Behavior Control
**Goal:** Use system prompts to set persona and guidelines

**What to show:**
- Add a `system` parameter to set Claude's behavior
- Show how system prompts affect all responses
- Demonstrate role-playing or expertise setting

**Code pattern:**
```python
response = client.converse(
    modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    messages=[
        {'role': 'user', 'content': [{'text': 'Explain quantum computing.'}]}
    ],
    system=[
        {'text': 'You are a patient teacher explaining complex topics to beginners. Use simple analogies and avoid jargon.'}
    ]
)
```

**Key points to emphasize:**
- System prompt sets the "personality" and constraints
- Use for: setting expertise level, output format, safety guidelines
- System prompts persist across all messages in the conversation
- More effective than putting instructions in the user message

**Best practices:**
- Be specific and directive in system prompts
- Use system prompts for output formatting (JSON, markdown, etc.)
- Keep system prompts focused and not too long

---

## Summary

By the end of this path, learners should be able to:
- Call Claude models using the Converse API
- Control creativity and length with inferenceConfig
- Build multi-turn conversations with context
- Use system prompts to guide behavior

## Next Steps
- Explore streaming responses for better UX
- Try tool use for function calling
- Experiment with image inputs (multimodal)
