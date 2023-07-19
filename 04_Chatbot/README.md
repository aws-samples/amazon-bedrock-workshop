# Conversational Interface - Chatbots

## Overview

Conversational interfaces such as chatbots and virtual assistants can be used to enhance the user experience for your customers.Chatbots uses natural language processing (NLP) and machine learning algorithms to understand and respond to user queries. Chatbots can be used in a variety of applications, such as customer service, sales, and e-commerce, to provide quick and efficient responses to users. They can be accessed through various channels such as websites, social media platforms, and messaging apps.


## Chatbot using Amazon Bedrock

![Amazon Bedrock - Conversational Interface](./images/chatbot_bedrock.png)

## Use Cases

1. **Chatbot (Basic)** - Zero Shot chatbot with a FM model
2. **Chatbot using prompt** - template(Langchain) - Chatbot with some context provided in the prompt template
3. **Chatbot with persona** - Chatbot with defined roles. i.e. Career Coach and Human interactions
4. **Contextual-aware chatbot** - Passing in context through an external file by generating embeddings.

## Langchain framework for building Chatbot with Amazon Bedrock
In Conversational interfaces such as chatbots, it is highly important to remember previous interactions, both at a short term but also at a long term level.

LangChain provides memory components in two forms. First, LangChain provides helper utilities for managing and manipulating previous chat messages. These are designed to be modular and useful regardless of how they are used. Secondly, LangChain provides easy ways to incorporate these utilities into chains.
It allows us to easily define and interact with different types of abstractions, which make it easy to build powerful chatbots.

## Building Chatbot with Context - Key Elements

The first process in a building a contextual-aware chatbot is to **generate embeddings** for the context. Typically, you will have an ingestion process which will run through your embedding model and generate the embeddings which will be stored in a sort of a vector store. In this example we are using a GPT-J embeddings model for this

![Embeddings](./images/embeddings_lang.png)

Second process is the user request orchestration , interaction,  invoking and returing the results

![Chatbot](./images/chatbot_lang.png)

## Architecture [Context Aware Chatbot]
![4](./images/context-aware-chatbot.png)

In this architecture:

1. The question asked to the LLM, is run through the embeddings model
2. The context documents are embedded using the [Amazon Titan Embeddings Model](https://aws.amazon.com/bedrock/titan/) and stored in the vector database.
3. The embedded text is then input to the FM for contextual search and including the chat history
4. The FM model then gives you the results based on the context.

## Notebooks
This module provides you with 2 notebooks for the same pattern. You can experience conversation with Anthropic Claude as well as Amazon Titan Text Large to experience each the conversational power of each model.

1. [Chatbot using Claude](./00_Chatbot_Claude.ipynb)
2. [Chatbot using Titan](./00_Chatbot_Titan.ipynb)
