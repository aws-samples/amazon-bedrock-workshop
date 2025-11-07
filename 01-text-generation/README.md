# Module 1 - Text Generation with Amazon Bedrock

## Overview

This module provides a comprehensive introduction to Amazon Bedrock's text generation capabilities using the **Converse API**. You'll learn how to leverage foundation models for various text generation tasks, from simple summarization to complex function calling scenarios.

## What You'll Learn

In this module, you will:

- Master the basics of the Amazon Bedrock **Invoke API**
- Explore the powerful **Converse API** and its advanced features
- Implement multi-turn conversations with context management
- Use streaming responses for real-time content generation
- Enable function calling to integrate external tools
- Compare performance across different state-of-the-art models
- Leverage Cross-Regional Inference for improved reliability

## Notebooks

### 01-text-generation.ipynb

This hands-on notebook covers:

1. **Setup** - Initialize Bedrock clients and configure model access
2. **Text Summarization** - Compare Invoke API vs Converse API approaches
3. **Converse API Deep Dive** - Understand the unified interface and its benefits
4. **Model Flexibility** - Easily switch between different foundation models
5. **Cross-Regional Inference** - Enhance application resilience and throughput
6. **Multi-turn Conversations** - Build contextual dialogues
7. **Streaming Responses** - Implement real-time content delivery
8. **Code Generation** - Use LLMs to generate functional code
9. **Function Calling** - Integrate external tools and APIs

## Prerequisites

To run the notebooks in this module, you will need:

- Python 3.10+
- AWS credentials with permissions to access Amazon Bedrock

## Key Concepts

### Converse API Benefits

The Converse API provides a unified interface that:
- Works consistently across all Amazon Bedrock models
- Simplifies multi-turn conversation management
- Supports streaming responses out of the box
- Enables function calling for tool integration
- Reduces code complexity when switching between models

### Cross-Regional Inference

Amazon Bedrock's Cross-Regional Inference automatically:
- Selects optimal AWS regions for processing requests
- Provides up to 2x higher throughput limits
- Manages traffic bursts across multiple regions
- Maintains data residency compliance
- Minimizes latency when possible

## Getting Started

1. Ensure you have the required prerequisites
2. Open `01-text-generation.ipynb` in Jupyter
3. Follow the step-by-step instructions in the notebook
4. Experiment with different models and parameters

## Contributing

We welcome community contributions! Please ensure your sample aligns with [AWS best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.
