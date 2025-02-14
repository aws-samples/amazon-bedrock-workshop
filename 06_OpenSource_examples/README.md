# Open-Source Module: Amazon Bedrock Integration with LangChain and Agentic Frameworks

Welcome to the **Open-Source Module**, where we demonstrate how to use [Amazon Bedrock](https://aws.amazon.com/bedrock/) with popular open-source libraries and frameworks. This repository includes a series of Jupyter notebooks that range from **high-level LangChain use cases** to **advanced agentic frameworks** with retrieval-augmented generation (RAG) and agent evaluation. Additionally, we provide an example using **CrewAI** for building a React-style agents, contrasting with the Agentic workflow approach in **LandGraph**.

## Table of Contents
- [Overview](#overview)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [High-Level Use Cases Notebooks](#high-level-use-cases)
- [Agentic Frameworks, Evaluations and RAG](#agentic-frameworks-evaluations-and-rag)

---

## Overview

**Amazon Bedrock** is a fully managed service that lets you easily build and scale generative AI applications with foundation models (FMs) from top AI providers, all accessible via a single API. In this module, we:

Illustrate **high-level examples** of text generation, code translation, and summarization using Bedrock with **LangChain**.  
Dive into **advanced agent-based setups** using RAG (retrieval-augmented generation), multi-agent frameworks, agent evaluation, and React-based agents (via **CrewAI**) as an alternative to **LandGraph**’s workflow approach.

---

## Prerequisites

**AWS Account & Credentials**  
You’ll need access to Amazon Bedrock. Ensure your AWS CLI or environment variables are properly configured to allow these notebooks to authenticate.

**Python 3.12+**  
Install and use a version of Python that is 3.12 or higher.

**JupyterLab or Jupyter Notebook**  
You can run the `.ipynb` notebooks locally or in a managed environment (e.g., Amazon SageMaker).

---

## Installation

**Clone the Repository**  
   ```bash
   git clone https://github.com/aws-samples/amazon-bedrock-workshop.git
   cd amazon-bedrock-workshop/06_OpenSource_examples
   run pip install -r requirements.txt
```
---
## Notebook Descriptions

### High-Level Use Cases

These notebooks are located in `text-generation-with-langchain` and demonstrate core ways to use Amazon Bedrock with LangChain:
- ***01_zero_shot_generation.ipynb***:
Zero-shot text generation with foundation models on Bedrock, wrapped in LangChain’s prompt interface.
- ***02_code_interpret_w_langchain.ipynb***:
Code interpretation and generation, showing how to integrate Bedrock models with LangChain abstractions for developer workflows.
- ***03_code_translate_w_langchain.ipynb***:
Demonstrates code translation from one programming language to another, powered by Bedrock + LangChain’s flexible prompt layering.
- ***04_long_text_summarization_using_LCEL_chains_on_Langchain.ipynb***:
Explores how to summarize lengthy documents or text using LCEL (Language Chain Execution Logic) in LangChain, backed by Bedrock models.

### Agentic Frameworks, Evaluations and RAG

Beyond the high-level examples, you’ll find a set of notebooks that delve into agent frameworks, retrieval-augmented generation, and agent evaluation (using **Ragas**). Some of these also highlight the difference between a React agent approach (using **CrewAI**) and a workflow agentic approach (using **LandGraph**).
- ***advance-langragph-multi-agent-setup.ipynb***: 
Shows how to set up a multi-agent environment leveraging LandGraph workflows and Amazon Bedrock.
- ***find-relevant-information-using-RAG.ipynb***:
Demonstrates retrieval-augmented generation (RAG) with Bedrock for more accurate and context-rich responses.
- ***intermediate-langragph-agent-setup-w-tools.ipynb***:
Focuses on an intermediate agentic workflow in LandGraph, integrating additional tools to handle complex tasks.
- ***ragas-agent-evaluation.ipynb***:
Explains evaluating agent performance using Ragas, focusing on retrieval and generation quality with Bedrock.
- ***simple-crewai-agent-setup.ipynb***:
Illustrates a minimal React agent approach using CrewAI, contrasting with LandGraph workflows.
- ***simple-langragph-agent-setup.ipynb***:
Provides a starting point for building a single-agent flow with LandGraph, leveraging Bedrock behind the scenes.
---
AWS Configuration
Make sure your environment is set up with AWS credentials that can call Amazon Bedrock. If necessary, export environment variables or configure the AWS CLI.
Run & Explore
Execute the cells in each notebook sequentially. You can modify prompts, model parameters, agent setups, or workflows to see how results change.

For more information on the fine-grained action and resource permissions in Bedrock, check out the Bedrock Developer Guide.

