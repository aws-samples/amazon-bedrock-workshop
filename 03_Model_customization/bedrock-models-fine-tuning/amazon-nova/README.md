# amazon-nova-domain-specific-finetuning

This repo provides example scripts for fine-tuning Amazon Nova models, hosting fine-tuned models through provisioned throughput and performing inference on MTbench style questions.

## Get-started

### Notebook walkthrough

`01_fine-tune_Amazon_Nova.ipynb`: This notebook demonstrates the end-to-end process of fine-tuning Amazon Nova models using Amazon Bedrock, including selecting the base model, configuring hyperparameters, creating and monitoring the fine-tuning job, deploying the fine-tuned model with provisioned throughput and evaluating the performance of the fine-tuned model.

`02_Inference_Amazon_Nova.ipynb`: This notebook walk-through how to conduct inference on fine-tuned Amazon Nova models. We first demonstrate a single example followed by example scripts for running batch inference.


## Installation
Please install dependencies using the `requirements.txt` file
`pip install -r requirements.txt`


## Support
Reach out to florawan@amazon.com 


## License
This library is licensed under the MIT-0 License. See the [LICENSE](https://ssh.gitlab.aws.dev/genaiic-reusable-assets/demo-artifacts/olympus-domain-specific-finetuning/-/blob/main/LICENSE.txt) file.


## Disclaimer
This repository is not production-ready and requires additional considerations on topics such as for security, reliability, and scalability before real-world deployment.