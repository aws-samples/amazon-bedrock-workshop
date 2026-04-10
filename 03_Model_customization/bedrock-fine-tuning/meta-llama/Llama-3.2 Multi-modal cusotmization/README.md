# Fine-Tuning Llama 3.2 with Vision Capabilities using Amazon Bedrock

This repository demonstrates how to fine-tune Meta's Llama 3.2 model with vision capabilities using Amazon Bedrock. Learn how to prepare multi-modal data, train a custom model, and run inference with your fine-tuned model.

## Contents

- [Step01-DataPreparation.ipynb](./Step01-DataPreparation.ipynb) - Prepare data for fine-tuning Llama 3.2 with vision capabilities. This notebook covers downloading and processing a subset of the llava-instruct dataset with COCO images, formatting the data according to the Bedrock conversation schema, and preparing training, validation, and test datasets.

- [Step02-Customization.ipynb](./Step02-Customization.ipynb) - Fine-tune and evaluate the Llama 3.2 multi-modal model. This notebook covers creating and monitoring a fine-tuning job, visualizing training metrics, setting up provisioned throughput, running inference with the fine-tuned model on test images, and cleaning up AWS resources.

## Prerequisites

- An AWS account with access to Amazon Bedrock
- Appropriate IAM permissions for Bedrock, S3, and IAM role creation
- Python 3.8+ environment with required libraries

## Important Notes
- Llama 3.2 fine-tuning is currently only available in the us-west-2 AWS region
- Fine-tuning jobs may take several hours to complete depending on dataset size
- The COCO image dataset is approximately 19.3 GB in size and requires at least 25 GB of free disk space


## Contributing

We welcome community contributions! Please ensure your sample aligns with AWS [best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.