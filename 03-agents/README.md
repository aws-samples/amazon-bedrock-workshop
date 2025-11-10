# Module 3 - Agents

## Overview

This module provides a comprehensive introduction to building enterprise-ready GenAI agents using Strands Agents SDK and Amazon Bedrock AgentCore Runtime. You'll learn how to create intelligent agents that can interact with external tools, knowledge bases, and databases to accomplish complex tasks autonomously.

## What You'll Learn

In this module, you will:

- Understand the fundamentals of AI agents and agentic workflows
- Build agents using Strands Agents SDK
- Deploy agents to Amazon Bedrock AgentCore Runtime
- Integrate agents with Amazon Bedrock Knowledge Bases
- Connect agents to Amazon DynamoDB for data operations
- Implement tool calling and function execution
- Create a restaurant assistant agent with reservation capabilities
- Test and invoke deployed agents

## Notebooks

### 01-agents.ipynb

Build and deploy a complete GenAI agent:

1. **Setup** - Install dependencies and configure AWS services
2. **Deploy Prerequisites** - Set up Knowledge Base and DynamoDB table
3. **Create Agent** - Build agent with Strands SDK
4. **Define Tools** - Implement custom functions for the agent
5. **Local Testing** - Test agent functionality locally
6. **Deploy to AgentCore** - Package and deploy to serverless runtime
7. **Invoke Agent** - Call deployed agent via API
8. **Monitor and Debug** - Review agent execution and logs

## Prerequisites

To run the notebooks in this module, you will need:

- Python 3.10+
- AWS credentials with permissions to:
  - Call Anthropic Claude 3.7 Sonnet on Amazon Bedrock
  - Create and manage Amazon Bedrock Knowledge Bases
  - Create and manage Amazon S3 buckets
  - Read/write/delete Amazon DynamoDB tables
  - Access Amazon Bedrock AgentCore
  - Create and manage IAM roles

## Architecture

The agent architecture includes:

- **Strands Agent SDK** - Framework for building model-driven agents
- **Amazon Bedrock AgentCore Runtime** - Serverless hosting environment
- **Amazon Bedrock Knowledge Base** - RAG-powered information retrieval
- **Amazon DynamoDB** - Persistent storage for reservations
- **Custom Tools** - Functions for restaurant operations

## Use Case: Restaurant Assistant

The example agent implements a restaurant assistant that can:

- Answer questions about restaurants using Knowledge Base
- Check table availability
- Make and manage reservations
- Query reservation details from DynamoDB
- Provide personalized recommendations

## Contributing

We welcome community contributions! Please ensure your sample aligns with [AWS best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.
