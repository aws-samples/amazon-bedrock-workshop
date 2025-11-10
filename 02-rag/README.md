# Module 2 - Knowledge Bases and RAG

## Overview

This module provides a comprehensive introduction to Amazon Bedrock Knowledge Bases and Retrieval Augmented Generation (RAG). You'll learn how to build production-ready RAG applications that ground foundation model responses in your own data, improving accuracy and reducing hallucinations.

## What You'll Learn

In this module, you will:

- Understand the fundamentals of Retrieval Augmented Generation (RAG)
- Create and configure Amazon Bedrock Knowledge Bases
- Set up Amazon OpenSearch Serverless for vector storage
- Ingest and index documents for semantic search
- Build fully-managed RAG applications with RetrieveAndGenerate API
- Implement customized RAG workflows with Retrieve API
- Compare managed vs customized RAG approaches
- Clean up resources properly

## Notebooks

### 01-create-kb-and-ingest-documents.ipynb

Learn how to set up the foundation for RAG applications:

1. **Setup** - Configure AWS services and permissions
2. **Create S3 Data Source** - Upload and organize your documents
3. **Configure OpenSearch Serverless** - Set up vector index for embeddings
4. **Create Knowledge Base** - Build and configure Amazon Bedrock Knowledge Base
5. **Ingest Documents** - Synchronize data source and create vector embeddings

### 02-managed-rag.ipynb

Build a fully-managed Q&A application:

1. **RetrieveAndGenerate API** - Use the simplified, managed RAG approach
2. **Query Knowledge Base** - Ask questions and get grounded responses
3. **Source Attribution** - Track where answers come from
4. **Response Quality** - Understand how RAG improves accuracy

### 03-customized-rag.ipynb

Implement advanced RAG patterns with full control:

1. **Retrieve API** - Get granular control over retrieval
2. **Custom Prompting** - Design your own prompt templates
3. **Response Formatting** - Customize output structure
4. **Advanced Filtering** - Apply metadata filters and ranking
5. **Orchestration** - Build custom RAG workflows

### 04-cleanup.ipynb

Properly clean up resources:

1. **Delete Knowledge Base** - Remove Bedrock Knowledge Base
2. **Clean S3 Buckets** - Delete data sources
3. **Remove OpenSearch Index** - Clean up vector storage
4. **Delete IAM Roles** - Remove service permissions

## Prerequisites

To run the notebooks in this module, you will need:

- Python 3.10+
- AWS credentials with permissions to:
  - Create and delete Amazon IAM roles
  - Create, update, and delete Amazon S3 buckets
  - Access Amazon Bedrock
  - Access Amazon OpenSearch Serverless
- The following models enabled in your Amazon Bedrock Console:
  - Amazon Titan Text Embeddings V2
  - Amazon Nova Micro

## Contributing

We welcome community contributions! Please ensure your sample aligns with [AWS best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.
