# Fine-Tuning Foundation Models with Amazon Bedrock

You can customize Foundation Models(FMs) on Bedrock through fine-tuning. We provide examples on how to set up the resources, fine-tune and evaluate the customized model, and clean up the resources after running the examples. 

## Contents

- [01_setup.ipynb](./01\_setup.ipynb) - Setup for running customization notebooks both for fine-tuning and continued pre-training using Amazon Bedrock. In this notebook, we will create set of roles and an S3 bucket which will be used for other notebooks in this module. 

- [02_fine-tune_and_evaluate_llama31_8B_bedrock_summarization.ipynb](./02\_fine-tune_and_evaluate_llama31_8B_bedrock_summarization.ipynb) - In this notebook, we build an end-to-end workflow for fine-tuning, provisioning and evaluating the Foundation Models (FMs) in Amazon Bedrock. We choose [Meta Llama 3.1 8B](https://aws.amazon.com/bedrock/llama/) as our FM to perform the customization through fine-tuning, we then create provisioned throughput of the fine-tuned model, test the provisioned model invocation, and finally evaluate the fine-tuned model performance using [fmeval](https://github.com/aws/fmeval) on the summarization accuracy metrics.

- [03_cleanup.ipynb](./03\_cleanup.ipynb) - Clean up all the resources that you have created in the previous notebooks to avoid unnecessary cost associated with the resources. 


## Contributing

We welcome community contributions! Please ensure your sample aligns with AWS [best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.