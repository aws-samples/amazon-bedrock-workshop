# Lab 3 - Custom Models 


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
- In this module, please run the [00_setup.ipynb](./00_setup.ipynb) first to make sure resources are properly set up for the following notebooks in this lab.
- At the end of the module, please run the [04_cleanup.ipynb](./04_cleanup.ipynb) to make sure resources are removed to avoid unnecessary costs.


## Patterns

On this workshop, you will be able to learn following patterns on customizing FMs in Bedrock:

2. [Fine-tune and Evaluate Llama2 in Bedrock for Summarization](./02_fine-tune_and_evaluate_llama2_bedrock_summarization.ipynb): Demonstrates an end-to-end workflow for fine-tuning, provisioning and evaluating a Meta Llama2 in Amazon Bedrock.