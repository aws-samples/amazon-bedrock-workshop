# Amazon Bedrock Model Distillation Samples

This repository contains code samples and notebooks demonstrating how to use Amazon Bedrock Model Distillation. The samples cover two main approaches for creating distillation jobs: using S3 to upload a JSONL file with prompts, and using historical invocation logs.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Notebooks](#notebooks)
4. [Usage](#usage)
5. [Key Benefits](#key-benefits)
6. [Use Cases](#use-cases)
7. [Contributing](#contributing)

## Introduction

Amazon Bedrock Model Distillation allows you to create smaller, faster, and more cost-efficient models that deliver use-case specific accuracy comparable to larger, more capable models. This repository provides practical examples of how to implement model distillation using Amazon Bedrock.

## Prerequisites

Before using these samples, ensure you have:

- An active AWS account
- Selected teacher and student models enabled in Amazon Bedrock
- Confirmed availability of model region and quotas
- Created an IAM role with necessary permissions
- Set up an Amazon S3 bucket for storing distillation job output metrics
- Enabled invocation logging (if using historical invocation logs)
- Sufficient quota for running provisioned throughput during inference

## Notebooks

This repository contains two main notebooks:

1. `Distillation-via-S3-input.ipynb`: Demonstrates how to use S3 to upload a JSONL file with prompts for model distillation.
2. `Historical_invocation_distillation.ipynb`: Shows how to use historical invocation logs to create a distillation job, including generating invocation logs and metadata using ConverseAPI.

## Usage

To use these notebooks:

1. Clone this repository
2. Open the desired notebook in a Jupyter environment
3. Follow the step-by-step instructions in each notebook

Ensure you have the necessary AWS permissions and have set up your environment according to the prerequisites.

## Key Benefits

- Efficiency: Distilled models provide high use-case specific accuracy comparable to the most capable models while being as fast as some of the smallest models.
- Cost Optimization: Inference from distilled models is less expensive compared to larger advanced models.
- Advanced Customization: Bedrock Model Distillation removes the need to create labelled dataset for fine-tuning.
- Ease of Use: Bedrock Model Distillation offers a single workflow that automates the generation of teacher responses, addition of data synthesis, and fine-tunes the student model with optimized hyperparameter tuning.

## Use Cases

- Retrieval-Augmented Generation (RAG)
- Document Summarization
- Chatbot Deployments
- Text Classification

## Contributing

We welcome contributions to improve these samples. Please submit a pull request or open an issue to discuss proposed changes.

