# Lab 5.2 - Building Agents for Bedrock using Boto3 SDK

## Overview
In this lab we will demonstrate how to build, test and deploy Agents via [AWS Boto3 SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

Boto3 provides two clients for Agents for Bedrock:
- [AgentsforBedrock](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent.html) represented by ``bedrock-agent``, provides functions related to the Agent's configuration and
- [AgentsforBedrockRuntime](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html) represented by ``bedrock-agent-runtime`` provides functions related to the Agent's and Knowledge Base's invocation.

The table below details the SDK functionalities

| **Functions**                                               | **Boto3 SKD Client**  | **Scope**                 |
|-------------------------------------------------------------|-----------------------|---------------------------|
| Create, Update, Delete and Prepare **Agent**                | bedrock-agent         | Agent Configuration       |
| Associate, Update and Disassociate **Agent Knowledge Base** | bedrock-agent         | Agent Configuration       |
| Create, Update and Delete **Agent Action Group**            | bedrock-agent         | Agent Configuration       |
| Create, Update and Delete **Agent Alias**                   | bedrock-agent         | Agent Configuration       |
| Invoke **Agent**                                            | bedrock-agent-runtime | Agent invocation          |
| Query **Knowledge Base**                                    | bedrock-agent-runtime | Knowledge Base invocation |

We will perform the following actions using the Boto3 SDK:
1. **Create Agent:** create an agent using this API by connecting to 
the bedrock client.

2. **Create Agent Action Group:** create and assign an action group to the agent 
(with corresponding lambda and openAPI schema)

3. **Prepare Agent:** Prepare an agent for deployment.

4. **Create Agent Alias:** Creating the agent alias to use in the duration of 
invoking the agent and getting the response

5. **Invoke Agent:** Invoke the agent that you created to get a response from 
it while it queries from the knowledge base

6. **Delete Agent Action Group:** Delete an action group from the agent 
configuration

7. **Delete Agent Alias:** Delete an existing alias of the agent

8. **Delete Agent Version:** Delete any existing versions of the agent

9. **Delete Agent:** Delete the entire agent

This folder contains the API schema, AWS Lambda function and notebook, 
`create_and_invoke_agent` with the code for the use case.

You can find detailed instructions on the [Bedrock Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/en-US/90-agents).