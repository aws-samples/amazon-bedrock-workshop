# Lab 1 - Text Generation

## Overview

In this lab, you will learn how to generate text using LLMs on Amazon Bedrock. We will demonstrate the use of LLMs using the Bedrock API as well as how to utilize the LangChain framework that integrates with Bedrock. 

We will first generate text using a zero-shot prompt. The zero-shot prompt provides instruction to generate text content without providing a detailed context. We will explore zero-shot email generation using two approaches: Bedrock API (BoTo3) and Bedrock integration with LangChain. Then we will show how to improve the quality of the generated text by providing additional context in the prompt.  

## Audience

Architects and developer who want to learn how to use Amazon Bedrock LLMs to generate text. 
Some of the business use cases for text generation include:

- Generating product descriptions based on product features and benefits for marketing teams
- Generation of media articles and marketing campaigns
- Email and reports generation

## Workshop Notebooks

We will generate an email response to a customer where the customer had provided negative feedback on service received from a customer support engineer. The text generation workshop includes the following three notebooks. 
1. [Generate Email with Amazon Titan](./00_generate_w_bedrock.ipynb) - Invokes Amazon Titan large text model using Bedrock API to generate an email response to a customer. It uses a zero-shot prompt without context as instruction to the model. 
2. [Zero-shot Text Generation with Anthropic Claude](01_zero_shot_generation.ipynb) - Invokes Anthropic's Claude Text model using the LangChain framework integration with Bedrock to generate an email to a customer. It uses a zero-shot prompt without context as instruction to the model. 
3. [Contextual Text Generation using LangChain](./02_contextual_generation.ipynb) - We provide additional context in the prompt which includes the original email from the customer that we would like the model to generate a response for. The example includes a custom prompt template in LangChain, so that variable values can be substitued in the prompt at runtime.  




# Lab 6 - Code Generation

## Overview

In this lab, you will learn to use LLMs on Amazon Bedrock for code generation, SQL query creation, code explanation, and code translation across languages. We will demo Bedrock's API (boto3) as well as its integration with LangChain. 

First, we will generate Python code and SQL queries by providing context about a dataset. Next, we will explain code and translate between languages. We will explore these use cases with both the Bedrock API directly and via LangChain integration.

## Audience

Architects and developers who want to learn how to use Amazon Bedrock LLMs to generate, explain and translate code.
 
Some of the business use cases for code generation include:

- Code Translation
- Code Explain and Reviews
- Database or SQL query generation
- Rapid Prototyping
- Issue Identification
- Bug Fixing
- Code Optimization

## Workshop Notebooks

1. [Code Generation](./00_code_generatation_w_bedrock.ipynb)- Demonstrates how to generate Python code using Natural language. It shows examples of prompting to generate simple functions, classes, and full programs in Python for Data Analyst to perform sales analysis on a given Sales CSV dataset.

2. [Database or SQL Query Generation](./01_sql_query_generate_w_bedrock.ipynb) - Focuses on generating SQL queries with Amazon Bedrock APIs. It includes examples of generating both simple and complex SQL statements for a given data set and database schema. 

3. [Code Explanation](./02_code_interpret_w_langchain.ipynb) - Uses Bedrock's foundation models to generate explanations for complex C++ code snippets. It shows how to carefully craft prompts to get the model to generate comments and documentation that explain the functionality and logic of complicated C++ code examples. Prompts can be easily updated for another programming languages.

4. [Code Translation ](./03_code_translate_w_langchain.ipynb) - Guides you through translating C++ code to Java using Amazon Bedrock and LangChain APIs. It shows techniques for prompting the model to port C++ code over to Java, handling differences in syntax, language constructs, and conventions between the languages.

## Setup
Before running any of the labs in this section ensure you've run the [Bedrock boto3 setup notebook](../00_Intro/bedrock_boto3_setup.ipynb#Prerequisites).

## Architecture

![Bedrock](./images/bedrock-code-gen.png)
![Bedrock](./images/bedrock-code-gen-langchain.png)







## Setup
Before running any of the labs in this section ensure you've run the [Bedrock boto3 setup notebook](../00_Intro/bedrock_boto3_setup.ipynb#Prerequisites).


## Architecture

![Bedrock](./images/bedrock.jpg)
![Bedrock](./images/bedrock_langchain.jpg)