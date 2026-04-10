# Citation-Aware Model Distillation Pipeline

A comprehensive implementation of a four-stage pipeline for distilling knowledge from larger language models into smaller, specialized models for citation-aware question answering.

## Overview

This implementation provides a systematic approach to create smaller, efficient models that maintain high-quality citation capabilities. The pipeline consists of four main stages:
1. Data preparation
2. Model distillation
3. Batch inference
4. Evaluation

## Pipeline Components

### 1. Data Preparation (`01_prepare_data.ipynb`)

- Utilizes SQuAD v2.0 dataset for citation-aware training
- Implements structured XML output format for consistent answer generation
- Handles both answerable and "impossible" questions
- Creates optimized training sets with 10% ground truth answers for effective distillation

### 2. Model Distillation (`02_distill.ipynb`)

- **Teacher Model**: Nova Premier (us.amazon.nova-premier-v1:0)
- **Student Model**: Nova Lite (amazon.nova-lite-v1:0:300k)
- Features:
  - Supports provisioned throughput deployment
  - Implements advanced system prompts for citation generation
  - Optimized knowledge transfer process

### 3. Batch Inference (`03_batch_inference.ipynb`, `batch_inference_simulator.py`)

- Efficient batch processing implementation with:
  - Robust retry mechanisms
  - Distributed processing architecture
  - Comprehensive error handling and monitoring
  - Support for multiple model variants comparison

### 4. Evaluation (`04_evaluate.ipynb`, `eval_jsonl_parser.py`)

Implements comprehensive metrics for citation quality assessment:
- Citation Coverage
- Correctness
- Completeness
- Faithfulness
- Helpfulness
- Logical Coherence

Additional features:
- XML parsing and validation of citations
- Automated evaluation using Bedrock's RAG evaluation capabilities

## Technical Requirements

### AWS Infrastructure

- Active AWS Account with Bedrock access
- Required IAM roles with permissions for:
  - S3 access (data storage)
  - Bedrock model access
  - Evaluation job execution

### Storage Requirements

S3 buckets configured for:
- Training data storage
- Model output storage
- Evaluation results storage

### Deployment Requirements

- Provisioned Throughput endpoint for the distilled model
- Python environment with dependencies:
  ```
  boto3
  pandas
  numpy
  tqdm