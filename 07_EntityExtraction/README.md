# Lab 7 - Entity Extraction
## Overview
Entity extraction is an NLP technique that allows us to automatically extract specific data from naturally written text, such as news, emails, books, etc.
That data can then later be saved to a database, used for lookup or any other type of processing.
There are many different techniques and approaches for entity extraction, in this module we will focus on using LLM for entity extraction.

LLM Entity Extraction works by sending a prompt instruction to the model, asking the model to extract entities you specify, like following example:

```xml
Given the email, please read it and analyse the contents.
If a name of a book is mentioned, return it.

<email>
{book_question_email}
</email>

Book Name:
```

In order to get the model running an entity extraction task, we use a technique called prompt engineering.
We create a prompt which contains instructions (in plain text) about what is expected when it processes our data and about the response.
If you would like to learn more about it, please look into [this](https://www.promptingguide.ai/).

## Why it is relevant
Classic entity extraction programs usually limit you to pre-defined classes, such as name, address, price, etc. or require you to provide many examples of types of entities you are interested in.
By using a LLM for entity extraction in most cases you are only required to specify what you need to extract in natural language. This gives you flexibility and accuracy in your queries while saving time by removing necessity of data labeling.

In this module, you will be able to work with Amazon Bedrock API to extract entities based on simple descriptions.

## Target Audience
This module can be executed by any developer familiar with Python, also by data scientists and other technical people.