# Amazon Bedrock Workshop [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

This hands-on workshop introduces how to leverage foundation models through [Amazon Bedrock](https://aws.amazon.com/bedrock/). Learn to build production-ready generative AI applications using text generation, RAG, agents, and visual content creation.

**Workshop Website:** https://catalog.us-east-1.prod.workshops.aws/amazon-bedrock/en-US

## What You'll Build

This workshop covers the most common generative AI patterns through hands-on labs:

- **Text Generation** - Master the Converse API, streaming, function calling, and multi-turn conversations
- **RAG Applications** - Build intelligent Q&A systems with Amazon Bedrock Knowledge Bases
- **AI Agents** - Create autonomous agents that use tools and external data sources
- **Visual Content** - Generate images and videos with multimodal models
- **Responsible AI** - Implement guardrails and safety measures

## Modules

### [01 - Text Generation](./01-text-generation/) 
*Estimated time: 25 mins*

Learn Amazon Bedrock's Converse API for text generation, code generation, streaming responses, and function calling. Compare multiple foundation models and implement Cross-Regional Inference.

### [02 - Knowledge Bases and RAG](./02-rag/)
*Estimated time: 35 mins*

Build retrieval-augmented generation applications using Amazon Bedrock Knowledge Bases. Implement both managed and customized RAG workflows with OpenSearch Serverless.

### [03 - Agents](./03-agents/)
*Estimated time: 30 mins*

Create enterprise-ready AI agents using Strands Agents SDK and Amazon Bedrock AgentCore Runtime. Build a restaurant assistant that integrates with Knowledge Bases and DynamoDB.

### [04 - Visual Content Generation](./04-visual-content-generation/)
*Estimated time: 30 mins*

Generate images with Amazon Nova Canvas and videos with Amazon Nova Reel. Build semantic search with multimodal embeddings using Titan models.

### [05 - Responsible AI](./05-responsible-ai/)
*Estimated time: 20 mins*

Implement Amazon Bedrock Guardrails to ensure safe, responsible AI applications with content filtering and topic controls.

### [06 - What's Next](./06-whats-next/)
*Estimated time: 20 mins*

Explore advanced topics and find references for further reading.

## Getting Started

### Prerequisites

- AWS Account with Amazon Bedrock access
- Python 3.10+
- Notebook environment (SageMaker Studio recommended)

### Setup

1. **Clone the Repository**:

```bash
git clone https://github.com/aws-samples/amazon-bedrock-workshop.git
cd amazon-bedrock-workshop
```

2. **Review Module Prerequisites** - Each notebook includes a prerequisites section with specific requirements and IAM permissions needed for that module.

3. **Start with Module 01** and progress sequentially through the modules.

## Recommended Environment

For the best experience, use [Amazon SageMaker Studio](https://aws.amazon.com/sagemaker/studio/):
- Fully managed Jupyter environment
- Pre-configured with AWS credentials
- Rich AI/ML features and integrations
- [Quick setup guide](https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html)

Alternatively, you can use SageMaker Notebook Instances or your local environment with AWS credentials configured.

## Additional Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/)
- [Workshop Website](https://catalog.us-east-1.prod.workshops.aws/amazon-bedrock/en-US)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=aws-samples/amazon-bedrock-workshop&type=Date)](https://star-history.com/#aws-samples/amazon-bedrock-workshop&Date)

## Contributors

Thanks to our awesome contributors! 🚀

[![contributors](https://contrib.rocks/image?repo=aws-samples/amazon-bedrock-workshop&max=2000)](https://github.com/aws-samples/amazon-bedrock-workshop/graphs/contributors)

---

[![HitCount](https://hits.dwyl.com/aws-samples/amazon-bedrock-workshop.svg?style=flat-square&show=unique)](http://hits.dwyl.com/aws-samples/amazon-bedrock-workshop)
