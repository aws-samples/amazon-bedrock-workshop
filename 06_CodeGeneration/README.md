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


## Architecture

![Bedrock](./images/bedrock-code-gen.png)
![Bedrock](./images/bedrock-code-gen-langchain.png)