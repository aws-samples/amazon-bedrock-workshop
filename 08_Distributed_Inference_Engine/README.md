# Amazon Bedrock — Distributed Inference Engine (Project Mantle)

Amazon Bedrock's distributed inference engine (Project Mantle) powers OpenAI API-compatible endpoints, enabling you to use the familiar [OpenAI Python SDK](https://github.com/openai/openai-python) with Amazon Bedrock models. It supports both the **Chat Completions API** and the **Responses API**, giving you flexibility to choose between stateless and stateful conversation patterns.

## Contents

This folder contains a comprehensive workshop notebook that walks through all the key capabilities of the Mantle endpoint:

- [mantle_workshop_notebook.ipynb](mantle_workshop_notebook.ipynb) — End-to-end workshop covering:
  1. **Setup & Authentication** — Configure the OpenAI SDK with Bedrock API keys or SigV4 (AWS credentials)
  2. **Discover Models** — List and retrieve available models via the Models API
  3. **Chat Completions API** — Stateless text generation, streaming, and client-managed multi-turn conversations
  4. **Responses API** — Server-managed stateful conversations using `previous_response_id` chaining
  5. **Tool Use (Function Calling)** — Define and invoke tools with both the Responses API and Chat Completions API
  6. **Structured Output** — Guarantee schema-compliant JSON responses using `json_schema` response format and strict tool definitions
  7. **Background Mode** — Asynchronous inference for long-running tasks with polling-based retrieval
  8. **Guardrails** — Apply Amazon Bedrock Guardrails to filter inputs/outputs, including standalone evaluation via the ApplyGuardrail API
  9. **Projects API** — Application-level isolation with separate access control, cost tracking, and observability

## Prerequisites

- An AWS account with access to Amazon Bedrock
- Python 3.9+
- A Bedrock API key (recommended) or AWS credentials configured via `aws configure` / IAM roles
- Model access enabled in the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/home)

## Getting Started

1. Clone this repository and navigate to the `distributed-inference-engine` folder
2. Install dependencies:
   ```bash
   pip install openai requests boto3 aws-bedrock-token-generator
   ```
3. Set your environment variables:
   ```bash
   export OPENAI_BASE_URL="https://bedrock-mantle.us-east-1.api.aws/v1"
   export OPENAI_API_KEY="your-bedrock-api-key-here"
   ```
4. Open the notebook and follow the sections sequentially

## Estimated Time

~90 minutes to complete all sections.

## Contributing

We welcome community contributions! Please ensure your sample aligns with AWS [best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.
