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
- **DEFAULT TO provide_token()** - Use AWS credentials via token generator (works in SageMaker/notebooks)
- **API KEYS ARE ALTERNATIVE** - Only mention short-term API keys if user asks or has issues with credentials

### Step 1: Setup with OpenAI SDK
**Goal:** Configure the OpenAI SDK to connect to Bedrock's Mantle endpoint

**What to show:**
- Install OpenAI SDK (`pip install openai`)
- Configure endpoint URL for Bedrock Mantle
- Authenticate with AWS credentials via provide_token() (DEFAULT)
- Test connection by listing models
- **IMPORTANT:** When user asks to use a specific model (e.g., "Claude", "Haiku"), ALWAYS list models first, filter by keyword, then use the correct model ID

**Code pattern:**
```python
# Install the OpenAI SDK and AWS token generator
# !pip install openai aws-bedrock-token-generator

import os
from openai import OpenAI
from aws_bedrock_token_generator import provide_token

# Configure Bedrock Mantle endpoint
os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"

# Use AWS credentials (default method in SageMaker/notebooks)
client = OpenAI(
    api_key=provide_token()
)

# Test connection - list available models
models = client.models.list()
print(f"✓ Connected! Found {len(models.data)} models")

# See what models are available
for model in models.data[:5]:
    print(f"  - {model.id}")
```

**Key points to emphasize:**
- Mantle provides OpenAI SDK compatibility for Bedrock
- `provide_token()` automatically uses your AWS credentials (IAM role/profile)
- Works seamlessly in SageMaker, EC2, or local environments with AWS CLI configured
- Region must match your Bedrock resources (us-east-1, us-west-2, etc.)
- Same models as standard Bedrock, different access pattern
- **CRITICAL:** Model IDs in Mantle are different from standard Bedrock (e.g., `anthropic.claude-3-5-sonnet-20241022-v2:0` vs model names in Mantle). Always list and filter models to find the correct ID.

**Authentication options (in order of preference):**
1. **provide_token()** - Uses AWS credentials automatically (recommended)
2. **API keys** - Generate short-term keys in Bedrock console (alternative)

**Note:** API keys can be used if you prefer explicit credentials or are outside AWS environment.

**Common pitfalls:**
- Using boto3/bedrock-runtime instead of OpenAI SDK ❌
- Wrong endpoint URL format (must include region and /v1)
- Not setting OPENAI_BASE_URL before creating client
- Forgetting to install aws-bedrock-token-generator package

---

### Step 2: Finding Responses API Compatible Models
**Goal:** Discover which models support the Responses API

⚠️ **CRITICAL:** Not all models support the Responses API! You'll get a 400 error: `The model 'X' does not support the '/v1/responses' API`

**What to show:**
- List available models
- Filter for Responses API compatible models (typically OpenAI models)
- Chat Completions API works with ALL models, Responses API only works with specific models

**Code pattern:**
```python
from openai import OpenAI
from aws_bedrock_token_generator import provide_token
import os

os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"
client = OpenAI(api_key=provide_token())

# List all models
models = client.models.list()
print(f"Total models: {len(models.data)}\n")

# Responses API typically works with OpenAI-family models
# For other models (Claude, Llama, etc.), use Chat Completions API instead
openai_models = [m for m in models.data if 'openai' in m.id.lower() or 'gpt' in m.id.lower()]

print("Models compatible with Responses API (OpenAI family):")
for model in openai_models[:5]:
    print(f"  - {model.id}")

if openai_models:
    model_id = openai_models[0].id
    print(f"\n✓ Using: {model_id}")
else:
    print("\n⚠️  No OpenAI models found. Use Chat Completions API for other models.")
```

**Key points:**
- **Responses API compatibility is limited** - primarily OpenAI-family models
- Claude, Llama, Titan, and most other models will throw 400 errors with Responses API
- **Chat Completions API works with ALL models** - use this for broader compatibility
- Always test a model first or filter for known-compatible families
- If you get 400 "does not support '/v1/responses' API" → switch to Chat Completions (Step 3)

---

### Step 3: Chat Completions API (Works with ALL Models)
**Goal:** Use the familiar OpenAI Chat Completions pattern - compatible with every Bedrock model

**What to show:**
- Send messages with full conversation history
- Stateless pattern - each request is independent
- Works with Claude, Llama, Titan, Nova, and ALL other models
- **Use this when Responses API throws compatibility errors**

**Code pattern:**
```python
from openai import OpenAI
from aws_bedrock_token_generator import provide_token
import os

os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"
client = OpenAI(api_key=provide_token())

# Works with ANY model - let's use Claude
models = client.models.list().data
claude_models = [m for m in models if 'claude' in m.id.lower() and 'sonnet' in m.id.lower()]
model_id = claude_models[0].id if claude_models else models[0].id

print(f"Using model: {model_id}\n")

# Single request with full context
response = client.chat.completions.create(
    model=model_id,
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
- **Works with ALL Bedrock models** (Claude, Llama, Titan, Nova, OpenAI, etc.)
- Same API as OpenAI, seamless compatibility
- Client manages all context
- **Default choice for most use cases**

**Multi-turn conversation with Chat Completions:**
```python
from openai import OpenAI
from aws_bedrock_token_generator import provide_token
import os

os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"
client = OpenAI(api_key=provide_token())

# Find any model (Chat Completions works with all)
models = client.models.list().data
model_id = models[0].id if models else "anthropic.claude-3-5-sonnet-20241022-v2:0"
print(f"Using: {model_id}\n")

# Client-managed conversation history
messages = [
    {"role": "system", "content": "You are a helpful AWS expert."}
]

def chat(user_message):
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model=model_id,
        messages=messages
    )
    
    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply

# Turn 1
print("Q: What is Amazon S3?")
print(f"A: {chat('What is Amazon S3?')}\n")

# Turn 2 - context maintained by client
print("Q: How does it compare to EBS?")
print(f"A: {chat('How does it compare to EBS?')}")
```

**Best practices:**
- Keep conversation history manageable (token limits apply)
- Trim old messages when history gets long
- System message sets behavior for entire conversation
- Works with **any model** on Bedrock Mantle endpoint

---

### Step 4: Responses API (Stateful - Limited Model Support)
**Goal:** Use server-managed conversation state instead of client history

⚠️ **IMPORTANT:** Responses API only works with specific models (primarily OpenAI family). If you get a 400 error, use Chat Completions API instead.

**What to show:**
- Responses API maintains context server-side
- Chain responses using `previous_response_id`
- No need to send full conversation history
- Only use with compatible models (check Step 2)

**Code pattern:**
```python
from openai import OpenAI
from aws_bedrock_token_generator import provide_token
import os

os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"
client = OpenAI(api_key=provide_token())

# Find OpenAI-compatible model for Responses API
models = client.models.list().data
openai_models = [m for m in models if 'openai' in m.id.lower() or 'gpt' in m.id.lower()]

if not openai_models:
    print("⚠️  No Responses API compatible models found. Use Chat Completions instead.")
    exit()

model_id = openai_models[0].id
print(f"Using: {model_id}\n")

# Turn 1 - initial request
response = client.responses.create(
    model=model_id,
    input=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(f"Turn 1: {response.output_text}")
print(f"Response ID: {response.id}\n")

# Turn 2 - chain using previous_response_id
response = client.responses.create(
    model=model_id,
    input=[
        {"role": "user", "content": "What river runs through it?"}
    ],
    previous_response_id=response.id  # Server maintains context
)

print(f"Turn 2: {response.output_text}")
print(f"Response ID: {response.id}\n")

# Turn 3 - continue the chain
response = client.responses.create(
    model=model_id,
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
- **⚠️  Limited model compatibility** - only OpenAI-family models typically work
- If you get 400 "does not support '/v1/responses' API" → use Chat Completions instead

**Responses API vs Chat Completions:**
| Chat Completions | Responses API |
|-----------------|---------------|
| Stateless | Stateful |
| Client manages history | Server manages history |
| Send full context each time | Send only new message + ID |
| Larger payloads | Smaller payloads |
| **Works with ALL models** | **Limited model support** |
| OpenAI-standard | Bedrock-specific extension |

---

### Step 5: Streaming with Chat Completions (All Models)
**Goal:** Stream responses for progressive display - works with ALL models

**What to show:**
- Stream text as it's generated
- Handle streaming events
- Works with Claude, Llama, OpenAI, and all other models

**Code pattern:**
```python
from openai import OpenAI
from aws_bedrock_token_generator import provide_token
import os

os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"
client = OpenAI(api_key=provide_token())

# Find any model (streaming works with all)
models = client.models.list().data
model_id = models[0].id if models else "anthropic.claude-3-5-sonnet-20241022-v2:0"
print(f"Using: {model_id}\n")

# Stream a response
stream = client.chat.completions.create(
    model=model_id,
    messages=[
        {"role": "user", "content": "Explain how S3 encryption works."}
    ],
    stream=True
)

print("Streaming: ", end="", flush=True)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n")
```

**Key points to emphasize:**
- Streaming provides better UX (progressive display)
- Events arrive incrementally - display as received
- Use `flush=True` for immediate display
- **Works with ALL models** on Bedrock Mantle

**Streaming multi-turn conversation:**
```python
from openai import OpenAI
from aws_bedrock_token_generator import provide_token
import os

os.environ["OPENAI_BASE_URL"] = "https://bedrock-mantle.us-east-1.api.aws/v1"
client = OpenAI(api_key=provide_token())

models = client.models.list().data
model_id = models[0].id

messages = [{"role": "system", "content": "You are a helpful AWS expert."}]

def stream_chat(user_input):
    """Stream a response and update conversation history."""
    messages.append({"role": "user", "content": user_input})
    
    stream = client.chat.completions.create(
        model=model_id,
        messages=messages,
        stream=True
    )
    
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    
    messages.append({"role": "assistant", "content": full_response})
    print("\n")

# Turn 1
print("User: What is Amazon Bedrock?")
print("Assistant: ", end="")
stream_chat("What is Amazon Bedrock?")

# Turn 2
print("\nUser: What models does it support?")
print("Assistant: ", end="")
stream_chat("What models does it support?")
```

---

### Step 6: Retrieving Previous Responses
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

### Step 7: Background Mode for Async Inference
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
- Authenticate with AWS credentials using provide_token()
- Understand Chat Completions (works with ALL models) vs Responses API (limited compatibility)
- Know which models support Responses API (primarily OpenAI family)
- Build conversations with Chat Completions (recommended for most use cases)
- Build stateful conversations with Responses API (when compatible models available)
- Stream responses for progressive display
- Retrieve and resume conversations by ID (Responses API only)
- Use background mode for async inference (Responses API only)

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
- **Primary:** AWS credentials via `provide_token()` from aws-bedrock-token-generator
- **Alternative:** Bedrock API keys (generated in console)

**Key Differences:**

**Chat Completions:**
- Stateless (client manages history)
- OpenAI-standard API
- Send full conversation each time
- **Works with ALL Bedrock models** ✓
- Recommended for most use cases

**Responses API:**
- Stateful (server manages history)
- Bedrock extension to OpenAI
- Chain with `previous_response_id`
- Supports background mode
- Smaller payloads for long conversations
- **Limited model compatibility** (primarily OpenAI family) ⚠️
- Use only when you have compatible models

**Model Compatibility:**
- Chat Completions: Claude, Llama, Titan, Nova, OpenAI, all others ✓
- Responses API: Primarily OpenAI-family models only ⚠️
- If you get 400 "does not support '/v1/responses' API" → use Chat Completions
- Always test model compatibility or filter for known-compatible families

**Model IDs:**
- Use Mantle model IDs (e.g., `anthropic.claude-3-5-sonnet-20241022-v2:0`)
- Different from standard Bedrock IDs
- List with `client.models.list()`
- Filter by keyword to find specific models

**Cost Considerations:**
- Charged per token (input + output)
- Responses API doesn't reduce token usage (context still processed)
- Background mode has same cost as synchronous
- Server-managed state reduces network bandwidth only
