# Amazon Bedrock Workshop [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

This hands-on workshop, aimed at developers and solution builders, introduces how to leverage foundation models (FMs) through [Amazon Bedrock](https://aws.amazon.com/bedrock/). This code goes alongside the self-paced or instructor-led workshop here - https://catalog.us-east-1.prod.workshops.aws/amazon-bedrock/en-US

**Please follow the prerequisites listed in the link above or ask your AWS workshop instructor how to get started.**

Amazon Bedrock is a fully managed service that provides access to FMs from third-party providers and Amazon via an API. With Bedrock, you can choose from a variety of models to find the one best suited for your use case.

Within this series of labs, you'll explore the most common usage patterns for Generative AI on AWS. You will gain hands-on experience with text generation, retrieval-augmented generation, agentic AI, and open-weight models via Bedrock APIs and SDKs.

## Labs

- **01 - Text Generation** \[~25 mins\]
    - Converse API and Invoke Model API
    - Summarization, code generation, function calling
    - Multi-turn conversations and streaming
    - Cross-regional inference profiles

- **02 - Knowledge Bases and RAG** \[~35 mins\]
    - Create a Knowledge Base with OpenSearch Serverless
    - RetrieveAndGenerate API (managed RAG)
    - Retrieve API (custom RAG pipeline)

- **03 - Model Customization** \[~30 mins — own account only, not available on Workshop Studio\]
    - Fine-tuning, continued pre-training, distillation
    - Reinforcement fine-tuning

- **04 - Agents** \[~30 mins\]
    - Restaurant booking assistant using Strands Agents framework
    - Tool use with DynamoDB and Knowledge Bases
    - Deployment to Amazon Bedrock AgentCore Runtime

- **05 - Distributed Inference Engine** \[~20 mins\]
    - OpenAI-compatible endpoint for open-weight models
    - Chat Completions and Responses API
    - Stateful conversations, tool use, structured output

## Getting started

### Prerequisites

This workshop runs in **Amazon SageMaker Studio** with a pre-configured JupyterLab space. If you are at an AWS-run event, your environment is already set up — open Studio and click the JupyterLab space to get started.

For self-paced use in your own account, deploy the workshop CloudFormation stack from `static/bedrock-workshop-studio.yaml`. This creates a SageMaker Studio domain, a JupyterLab space, and automatically clones this repository into it.

### IAM permissions

The SageMaker execution role needs `bedrock:*` at minimum. The CloudFormation template in this repo provisions all required permissions automatically.

### Clone the notebooks

If running outside of Workshop Studio, clone this repository into your notebook environment:

```sh
git clone https://github.com/aws-samples/amazon-bedrock-workshop.git
cd amazon-bedrock-workshop
```

### Model access

Amazon Bedrock now [automatically enables access](https://aws.amazon.com/blogs/security/simplified-amazon-bedrock-model-access/) to all serverless foundation models. Anthropic models require a one-time usage form submission via the Bedrock console.

---

[![HitCount](https://hits.dwyl.com/aws-samples/amazon-bedrock-workshop.svg?style=flat-square&show=unique)](http://hits.dwyl.com/aws-samples/amazon-bedrock-workshop)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=aws-samples/amazon-bedrock-workshop&type=Date)](https://star-history.com/#aws-samples/amazon-bedrock-workshop&Date)

# Contributors

[![contributors](https://contrib.rocks/image?repo=aws-samples/amazon-bedrock-workshop&max=2000)](https://github.com/aws-samples/amazon-bedrock-workshop/graphs/contributors)
