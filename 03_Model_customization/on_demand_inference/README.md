# On Demand Inference with Amazon Nova Micro

This directory contains notebooks demonstrating how to fine-tune Amazon Nova Micro using Amazon Bedrock and deploy it with on-demand inference capabilities.

## Overview

This tutorial provides an end-to-end workflow for:
- Setting up the required AWS resources and permissions
- Preparing datasets for fine-tuning Nova Micro
- Fine-tuning the Nova Micro model on a summarization task
- Deploying the fine-tuned model with on-demand inference
- Testing the deployed model using various API methods

## Contents

### 01_setup_nova_micro.ipynb
This notebook handles the initial setup required for fine-tuning Nova Micro:

**Key Features:**
- Creates necessary IAM roles and policies for Bedrock customization jobs
- Sets up an S3 bucket for storing training data and model outputs
- Prepares the CNN news article dataset for fine-tuning
- Converts data to the required `bedrock-conversation-2024` schema format
- Uploads processed datasets to S3

**Dataset:**
- Uses the CNN/DailyMail dataset from Hugging Face
- Converts articles and highlights into a summarization task format
- Limits training data to 5,000 samples and validation to 999 samples (within Nova Micro limits)
- Filters data points by length (max 3,000 characters)

**Prerequisites:**
- AWS account with appropriate permissions (IAM, S3, Bedrock)
- SageMaker Studio or Jupyter environment
- Recommended kernel: Data Science 3.0, Python 3, ml.t3.medium

### 02_fine-tune_nova_micro_with_on_demand_inference.ipynb
This notebook demonstrates the complete fine-tuning and deployment process:

**Key Features:**
- Creates and monitors fine-tuning jobs for Nova Micro
- Visualizes training and validation loss curves
- Deploys the fine-tuned model for on-demand inference
- Tests the deployed model using multiple API methods

**Fine-tuning Configuration:**
- Base model: `amazon.nova-micro-v1:0:128k`
- Hyperparameters:
  - Epochs: 2
  - Batch size: 1
  - Learning rate: 0.00005
- Training time: ~60 minutes for 5K records

**API Testing Methods:**
1. **Converse API** - Synchronous conversation with complete response
2. **Converse Stream API** - Streaming response with progressive token delivery
3. **Invoke API** - Direct model invocation with custom parameters
4. **Invoke Stream API** - Streaming version of the Invoke API

**Prerequisites:**
- Completion of `01_setup_nova_micro.ipynb`
- Same kernel and instance as setup notebook
- Region: us-west-2 (required for Nova Micro fine-tuning)

## Getting Started

1. **Setup Environment:**
   ```bash
   pip install boto3 datasets jsonlines pandas matplotlib fmeval awscurl
   ```

2. **Run Setup Notebook:**
   - Execute `01_setup_nova_micro.ipynb` first
   - Ensure all IAM roles and S3 resources are created successfully
   - Verify dataset preparation and upload

3. **Fine-tune and Deploy:**
   - Run `02_fine-tune_nova_micro_with_on_demand_inference.ipynb`
   - Monitor the fine-tuning job progress (takes ~60 minutes)
   - Deploy the model and test with various API methods

## Important Notes

⚠️ **Cost Considerations:**
- Fine-tuning jobs incur charges based on training time and data volume
- On-demand inference deployments have associated costs
- Remember to clean up resources after testing

⚠️ **Regional Requirements:**
- Nova Micro fine-tuning is only available in us-east-1 region
- Ensure your AWS resources are in the correct region

⚠️ **Data Limits:**
- Training dataset: Maximum 20,000 records
- Validation dataset: Maximum 1,000 records
- Individual data points: Recommended max 3,000 characters

## Use Cases

This tutorial is ideal for:
- **Text Summarization:** Fine-tuning models for domain-specific summarization tasks
- **Custom Model Development:** Learning the end-to-end process of model customization
- **API Integration:** Understanding different methods to interact with deployed models
- **Performance Evaluation:** Monitoring training metrics and model performance

## Architecture

The workflow follows this pattern:
1. Data preparation and S3 storage
2. IAM role and policy creation
3. Fine-tuning job submission and monitoring
4. Model deployment with on-demand inference
5. API testing and validation

## Support

For issues or questions:
- Check AWS Bedrock documentation for Nova Micro fine-tuning
- Review IAM permissions if encountering access errors
- Monitor CloudWatch logs for detailed error information
- Ensure all prerequisites are met before proceeding

## Next Steps

After completing this tutorial, consider:
- Experimenting with different hyperparameters
- Using your own datasets for domain-specific fine-tuning
- Implementing the deployed model in production applications
- Exploring other Nova model variants for different use cases
