---
id: distributed-inference
title: "Distributed Inference with Mantle (Responses API)"
description: "Use OpenAI-compatible APIs with Bedrock for stateful conversations"
keywords:
  - responses api
  - mantle
  - openai
  - stateful
  - conversation
  - chat completions
  - distributed inference
  - project mantle
difficulty: intermediate
duration: "25 minutes"
prerequisites:
  - Understanding of text generation
  - Familiarity with REST APIs
  - OpenAI SDK experience (helpful but not required)
models:
  - Any model on bedrock-mantle endpoint
apis:
  - bedrock-mantle (OpenAI-compatible)
  - responses API
  - chat completions API
---

# Distributed Inference with Mantle (Responses API)

This learning path teaches how to use Amazon Bedrock's OpenAI-compatible APIs (Project Mantle) for stateful conversations. The Responses API manages conversation context server-side, eliminating the need to send full chat history with each request.

## Teaching Flow

⚠️ **CRITICAL INSTRUCTION FOR THIS LEARNING PATH:**
- **USE OPENAI SDK ONLY** - Do NOT use boto3 or bedrock-runtime client
- **DEFAULT TO API KEYS** - Show short-term API key authentication first
- **ONLY MENTION IAM IF ASKED** - AWS credentials (SigV4) are an advanced option

### Step 1: Setup with OpenAI SDK
**Goal:** Configure the OpenAI SDK to connect to Bedrock's Mantle endpoint

**What to show:**
- Install OpenAI SDK (`pip install openai`)
- Configure endpoint URL for Bedrock Mantle
- Authenticate with short-term API key (DEFAULT)
- Test connection by listing models

**Code pattern:**
```python
# Install the OpenAI SDK
# !pip install openai

import os
from openai import OpenAI

# Configure Bedrock Mantle endpoint
os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.REGION.api.aws/v1"
os.environ["OPENAI_API_KEY"] = "your-bedrock-api-key-here"

# Create client
client = OpenAI()

# Test connection - list available models
models = client.models.list()
print(f"✓ Connected! Found {len(models.data)} models")

# See what models are available
for model in models.data[:5]:
    print(f"  - {model.id}")
```

**Key points to emphasize:**
- Mantle provides OpenAI SDK compatibility for Bedrock
- API keys are created in the Bedrock console (not AWS IAM)
- Region must match your Bedrock resources (us-east-1, us-west-2, etc.)
- Same models as standard Bedrock, different access pattern

**How to get API key:**
1. Open Bedrock console
2. Navigate to: Left sidebar → API keys
3. Click "Generate key"
4. Choose "Short-term key" (expires in hours/days)
5. Copy the key and paste in code above

**Note:** AWS IAM credentials are also supported but more complex. Only mention if user specifically asks about alternatives to API keys.

**Common pitfalls:**
- Using boto3/bedrock-runtime instead of OpenAI SDK ❌
- Wrong endpoint URL format (must include region and /v1)
- Not setting OPENAI_BASE_URL before creating client

---

### Step 2: Chat Completions API (Stateless)
**Goal:** Use the familiar OpenAI Chat Completions pattern

**What to show:**
- Send messages with full conversation history
- Stateless pattern - each request is independent
- Streaming responses

**Code pattern:**
```python
from openai import OpenAI

client = OpenAI()

# Single request with full context
response = client.chat.completions.create(
    model="openai.gpt-oss-120b",  # Bedrock model ID
    messages=[
        {"role": "system", "content": "You are a helpful AWS expert."},
        {"role": "user", "content": "What is Amazon Bedrock?"}
    ]
)

print(response.choices[0].message.content)
```

**Key points to emphasize:**
- Chat Completions is stateless - you manage the conversation history
- Must send full message history with each request
- Same API as OpenAI, works with Bedrock models
- Client manages all context

**Multi-turn conversation:**
```python
# Client-managed conversation history
messages = [
    {"role": "system", "content": "You are a helpful AWS expert."}
]

def chat(user_message):
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="openai.gpt-oss-120b",
        messages=messages
    )
    
    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply

# Turn 1
print(chat("What is Amazon S3?"))

# Turn 2 - context maintained by client
print(chat("How does it compare to EBS?"))
```

**Best practices:**
- Keep conversation history manageable (token limits apply)
- Trim old messages when history gets long
- System message sets behavior for entire conversation

---

### Step 3: Responses API (Stateful)
**Goal:** Use server-managed conversation state instead of client history

**What to show:**
- Responses API maintains context server-side
- Chain responses using `previous_response_id`
- No need to send full conversation history

**Code pattern:**
```python
from openai import OpenAI

client = OpenAI()

# Turn 1 - initial request
response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(f"Turn 1: {response.output_text}")
print(f"Response ID: {response.id}\n")

# Turn 2 - chain using previous_response_id
response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[
        {"role": "user", "content": "What river runs through it?"}
    ],
    previous_response_id=response.id  # Server maintains context
)

print(f"Turn 2: {response.output_text}")
print(f"Response ID: {response.id}\n")

# Turn 3 - continue the chain
response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[
        {"role": "user", "content": "How long is that river?"}
    ],
    previous_response_id=response.id
)

print(f"Turn 3: {response.output_text}")
```

**Key points to emphasize:**
- Responses API is **stateful** - server remembers conversation
- Use `previous_response_id` to chain responses
- Each response gets a unique ID for retrieval/chaining
- Significantly reduces payload size (only send new message)
- Better for long conversations

**Responses API vs Chat Completions:**
| Chat Completions | Responses API |
|-----------------|---------------|
| Stateless | Stateful |
| Client manages history | Server manages history |
| Send full context each time | Send only new message + ID |
| Larger payloads | Smaller payloads |
| OpenAI-standard | Bedrock-specific extension |

---

### Step 4: Streaming with Responses API
**Goal:** Stream responses for progressive display

**What to show:**
- Stream text as it's generated
- Handle streaming events
- Maintain conversation context while streaming

**Code pattern:**
```python
from openai import OpenAI

client = OpenAI()

# Stream a response
stream = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[
        {"role": "user", "content": "Explain how S3 encryption works."}
    ],
    stream=True
)

print("Streaming: ", end="", flush=True)

for event in stream:
    if hasattr(event, 'type') and event.type == 'response.output_text.delta':
        print(event.delta, end="", flush=True)

print("\n")
```

**Key points to emphasize:**
- Streaming provides better UX (progressive display)
- Events arrive incrementally - display as received
- Still get a response ID for chaining
- Use `flush=True` for immediate display

**Streaming multi-turn conversation:**
```python
def stream_response(user_input, previous_id=None):
    """Stream a response and return the response ID."""
    stream = client.responses.create(
        model="openai.gpt-oss-120b",
        input=[{"role": "user", "content": user_input}],
        previous_response_id=previous_id,
        stream=True
    )
    
    response_id = None
    for event in stream:
        if hasattr(event, 'type'):
            if event.type == 'response.output_text.delta':
                print(event.delta, end="", flush=True)
            elif event.type == 'response.done':
                response_id = event.response.id
    
    print("\n")
    return response_id

# Turn 1
print("User: What is Amazon Bedrock?")
print("Assistant: ", end="")
resp_id = stream_response("What is Amazon Bedrock?")

# Turn 2 - chain with streaming
print("\nUser: What models does it support?")
print("Assistant: ", end="")
resp_id = stream_response("What models does it support?", previous_id=resp_id)
```

---

### Step 5: Retrieving Previous Responses
**Goal:** Access conversation history via response IDs

**What to show:**
- Retrieve responses by ID
- Access conversation history
- Useful for resuming conversations or auditing

**Code pattern:**
```python
from openai import OpenAI

client = OpenAI()

# Create a response
response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[
        {"role": "user", "content": "List 3 AWS storage services."}
    ]
)

response_id = response.id
print(f"Created response: {response_id}")
print(f"Output: {response.output_text}\n")

# Later, retrieve by ID
retrieved = client.responses.retrieve(response_id)
print(f"Retrieved response: {retrieved.id}")
print(f"Output: {retrieved.output_text}")
print(f"Model used: {retrieved.model}")
print(f"Status: {retrieved.status}")
```

**Key points to emphasize:**
- Every response gets a unique ID
- Retrieve responses later for auditing, debugging, or resuming
- Response includes full context: input, output, model, status
- IDs persist server-side (check retention policy)

**Use cases:**
- Resume conversations across sessions
- Audit conversation flows
- Debug model responses
- Build conversation analytics

---

### Step 6: Background Mode for Async Inference
**Goal:** Submit long-running requests asynchronously

**What to show:**
- Background mode for async processing
- Poll for completion
- Useful for batch or long-generation tasks

**Code pattern:**
```python
from openai import OpenAI
import time

client = OpenAI()

# Submit in background mode
response = client.responses.create(
    model="openai.gpt-oss-120b",
    input=[
        {
            "role": "user",
            "content": (
                "Write a detailed comparison of microservices vs "
                "monolithic architectures, covering scalability, "
                "deployment, testing, and operational complexity."
            )
        }
    ],
    background=True  # Async processing
)

print(f"Request submitted: {response.id}")
print(f"Status: {response.status}")

# Poll for completion
while response.status == "in_progress":
    print("  ⏳ Processing...")
    time.sleep(2)
    response = client.responses.retrieve(response.id)

print(f"\n✓ Complete!")
print(f"Output: {response.output_text}")
```

**Key points to emphasize:**
- Background mode returns immediately (async)
- Poll with `retrieve()` to check status
- Status transitions: in_progress → completed / failed
- Only available with Responses API (not Chat Completions)

**Use cases:**
- Batch processing
- Long document generation
- Non-interactive workflows
- Queueing multiple requests

**Best practices:**
- Implement exponential backoff when polling
- Set reasonable timeout limits
- Handle failure states gracefully

---

## Summary

By the end of this path, learners should be able to:
- Use OpenAI SDK with Bedrock via Mantle endpoint
- Understand Chat Completions (stateless) vs Responses API (stateful)
- Build stateful conversations with server-managed context
- Stream responses for progressive display
- Retrieve and resume conversations by ID
- Use background mode for async inference

## Next Steps
- Explore tool use (function calling) with Responses API
- Add guardrails for content safety
- Use Projects API for workload isolation
- Implement structured outputs with JSON schemas

## Technical Notes

**Endpoint URL Format:**
```
https://bedrock-mantle.{REGION}.api.aws/v1
```

**Authentication:**
- Bedrock API keys (generated in console)
- SigV4 signing with AWS credentials (requires token generator)

**Key Differences:**

**Chat Completions:**
- Stateless (client manages history)
- OpenAI-standard API
- Send full conversation each time

**Responses API:**
- Stateful (server manages history)
- Bedrock extension to OpenAI
- Chain with `previous_response_id`
- Supports background mode
- Smaller payloads for long conversations

**Model IDs:**
- Use Mantle model IDs (e.g., `openai.gpt-oss-120b`)
- Different from standard Bedrock IDs
- List with `client.models.list()`

**Cost Considerations:**
- Charged per token (input + output)
- Responses API doesn't reduce token usage (context still processed)
- Background mode has same cost as synchronous
- Server-managed state reduces network bandwidth
