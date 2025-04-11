# amazon-nova-domain-specific-finetuning

This repo provides example scripts for fine-tuning Amazon Nova models, hosting fine-tuned models through provisioned throughput and performing inference on MTbench style questions.

## Get-started

### Notebook walkthrough

`01_Amazon_Nova_Finetuning_Walkthrough.ipynb`: This notebook demonstrates the end-to-end process of fine-tuning Amazon Nova models using Amazon Bedrock, including selecting the base model, configuring hyperparameters, creating and monitoring the fine-tuning job, deploying the fine-tuned model with provisioned throughput and evaluating the performance of the fine-tuned model.

`02_Inference_with_Customized_Amazon_Nova.ipynb`: This notebook walk-through how to conduct inference on fine-tuned Amazon Nova models. We first demonstrate a single example followed by example scripts for running batch inference.


### Fine-tuning Nova models via Bedrock API

The `amazon-nova-ft-scripts/` folder provides the following starter scripts:  
- `prep_bedrock_ft_dataset.py`: format training data to be compatible with Amazon Nova model format
- `nova_micro_bedrock_ft.py` and `nova_lite_bedrock_ft.py` for fine-tuning Amazon Nova Micro and Lite accordingly

### Hosting fintuned models through provisioned throughput

The `post-finetune-inference-scripts/helper.get_provisioned_model_id` function provides a quick way to host fine-tuned models through provisioned throughput and returns provisioned model id needed for inference. This step can also be done directly on the Bedrock console.


### Model inference on post-fine-tuned Amazon Nova models

- `post-finetune-inference-scripts/gen_answer.py` provides a starter script for generating answers for MT-bench style questions using customized Amazon Nova models


## Installation
Please install dependencies using the `requirements.txt` file
`pip install -r requirements.txt`


## Support
Reach out to florawan@amazon.com 


## License
This library is licensed under the MIT-0 License. See the [LICENSE](https://ssh.gitlab.aws.dev/genaiic-reusable-assets/demo-artifacts/olympus-domain-specific-finetuning/-/blob/main/LICENSE.txt) file.


## Disclaimer
This repository is not production-ready and requires additional considerations on topics such as for security, reliability, and scalability before real-world deployment.