# Amazon Nova Tool Use Finetuning with Amazon Bedrock

## Description
This repository demonstrates how to perform fine-tuning with the Amazon Nova models for tool usage using Amazon Bedrock. 

## Contents

There are four noteboooks which wlak you trough tool calling using Amazon Bedrock APIs with and without fine-tuning.

- [01_toolcall_nova_bedrock_invokeAPI_and_converseAPI.ipynb](./tooluse_finetuner_main/notebooks/01\_toolcall_nova_bedrock_invokeAPI_and_converseAPI.ipynb) - In this notebook we use Amazon Bedrock invoke and converse api for tool use with predefined set of tools. We show how the tool config, prompt and messages API should look like to align with Bedrock converse API and Bedrock invoke API. You can check how they work by using different input questions.

- [02_prepare_toolcall_dataset_for_bedrock_nova_ft.ipynb](./tooluse_finetuner_main/notebooks/02\_prepare_toolcall_dataset_for_bedrock_nova_ft.ipynb) - In this notebook we convert the dataset  to a format required by Amazon Nova for finetuning through Amazon Bedrock invoke api or Amazon Bedrock console. 

- [03_toolcall_fullfinetune_nova_bedrock.ipynb](./tooluse_finetuner_main/notebooks/03\_toolcall_fullfinetune_nova_bedrock.ipynb) - In this notebook we setup the IAM roles with the s3 bucket which has the formatted tran and test tooluse dataset. Then we create and start a new finetuning job with Amazon Nova using Bedrock API. Note that finetuning can be done directly from Amazon Bedrock console as well. 

- [04_toolcall_test_inference_finetuned_nova_bedrock.ipynb](./tooluse_finetuner_main/notebooks/04\_toolcall_test_inference_finetuned_nova_bedrock.ipynb) - In this notebook we show you how to deploy your finetuned model using provisioned throughput and run inference with it. We  also calculate the accuracy metrics on validation set for both tool usage and args calling.

We also have eight python files corresponding to the tools that we will be using in this dataset.
The dataset for tooluse is in  - [./tooluse_finetuner_main/assets/](./tooluse_finetuner_main/assets/)

## Contributing

We welcome community contributions! Please ensure your sample aligns with AWS [best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.