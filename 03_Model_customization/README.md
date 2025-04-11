# Lab 10 - Custom Models 


<div class="alert alert-block alert-warning">
<b>Warning:</b> This module cannot be executed in Workshop Studio Accounts, and you will have to run this notebook in your own account.
</div>


## Overview
Model customization is the process of providing training data to a model in order to improve its performance for specific use-cases. You can customize Amazon Bedrock foundation models in order to improve their performance and create a better customer experience. Amazon Bedrock currently provides the following customization methods.

- Fine-tuning

    Provide labeled data in order to train a model to improve performance on specific tasks. By providing a training dataset of labeled examples, the model learns to associate what types of outputs should be generated for certain types of inputs. The model parameters are adjusted in the process and the model's performance is improved for the tasks represented by the training dataset.

- Continued Pre-training 

    Provide unlabeled data to pre-train a foundation model by familiarizing it with certain types of inputs. You can provide data from specific topics in order to expose a model to those areas. The Continued Pre-training process will tweak the model parameters to accommodate the input data and improve its domain knowledge. For example, you can train a model with private data, such as business documents, that are not publically available for training large language models. Additionally, you can continue to improve the model by retraining the model with more unlabeled data as it becomes available.

## Relevance
Using your own data, you can privately and securely customize foundation models (FMs) in Amazon Bedrock to build applications that are specific to your domain, organization, and use case. Custom models enable you to create unique user experiences that reflect your company’s style, voice, and services.

- With fine-tuning, you can increase model accuracy by providing your own task-specific labeled training dataset and further specialize your FMs. 
- With continued pre-training, you can train models using your own unlabeled data in a secure and managed environment with customer managed keys. Continued pre-training helps models become more domain-specific by accumulating more robust knowledge and adaptability—beyond their original training.

This module walks you through how to customize models through fine-tuning and continued pre-training, how to provision the custom models with provisioned throughput, and how to compare and evaluate model performance. 

## Target Audience

This module can be executed by any developer familiar with Python, also by data scientists and other technical people who aspire to customize FMs in Bedrock. 

## Setup
- In this module, please run the the 01_setup.ipynb notebook first to make sure resources are properly set up for the following notebooks in this lab.
- At the end of the module, please run the 03_cleanup.ipynb to make sure resources are removed to avoid unnecessary costs.


## Patterns

In this workshop, you will be able to learn following patterns on customizing FMs in Bedrock:


# Fine tuning - 

1. [Fine-tune and Evaluate Amazon Nova in Bedrock ](./bedrock-models-fine-tuning/amazon-nova/01_Amazon_Nova_Finetuning_Walkthrough.ipynb): Demonstrates an end-to-end workflow for fine-tuning, provisioning and evaluating a Amazon Nova in Amazon Bedrock.
2. [Fine-tune and Evaluate Claude Haiku in Bedrock](./bedrock-models-fine-tuning/claude-haiku/02_fine-tune_Claude_Haiku.ipynb): Demonstrates an end-to-end workflow for fine-tuning, provisioning and evaluating a Claude Haiku in Amazon Bedrock.
3. [Fine-tune and Evaluate Meta Llama 3 in Bedrock](./bedrock-models-fine-tuning/meta-llama/Llama-3.2%20Multi-modal%20cusotmization/02_fine-tune_llama3.2.ipynb): Demonstrates an end-to-end workflow for fine-tuning, provisioning and evaluating a Meta Llama 3.2 multimodal customization in Amazon Bedrock.

# Continued Pretraining - 

1. [Continued Pretraining with Amazon Titan ](./continued%20Pre-training/02_continued_pretraining_titan_text.ipynb): Demonstrates an end-to-end workflow for continued pretraining Amazon Titan model in Amazon Bedrock.