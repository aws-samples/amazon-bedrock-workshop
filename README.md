# Amazon Bedrock Workshop

This sample repository accompanies a hands-on workshop, aimed at developers and solution builders, introducing how to leverage AI foundation models through [Amazon Bedrock](https://aws.amazon.com/bedrock/) on AWS.

**Find the full guided instructions for the workshop at: https://catalog.workshops.aws/amazon-bedrock**

## Getting started

The code samples are organized into numbered sub-folders corresponding to the modules of the workshop.

### Prerequisites

To get started, you'll first need to set up your AWS Account and the development environment where you'll run the samples. In AWS-hosted events, these may already be provided for you.

For full instructions, refer to the [workshop introduction](https://catalog.workshops.aws/amazon-bedrock) and the [prerequisites steps](https://catalog.workshops.aws/amazon-bedrock/en-US/10-setup). At a high level, you'll need:

- Access to an AWS Account with AWS IAM permissions for:
  - Amazon Bedrock for all labs (including AWS Marketplace permissions to subscribe to new models)
  - Amazon OpenSearch Serverless and Amazon S3 for knowledge base / RAG-related labs
  - Amazon Bedrock AgentCore, AWS CloudFormation, Amazon DynamoDB, and AWS IAM access for agent-related labs
- A development environment with:
  - AWS CLI access [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) with the access above
  - (Recommended) [uv installed](https://docs.astral.sh/uv/), for Python version and Python virtual environment management
  - Python 3.11+
  - This repository downloaded, for example by running, `git clone https://github.com/aws-samples/amazon-bedrock-workshop`

> ⚠️ **Cost warning:** Running these samples in *your own AWS Account* will incur costs!
>
> Refer to the workshop website for more details, and be sure to run cleanup steps promptly when you're finished experimenting, to avoid unnecessary cost.

### Install dependencies

The main required libraries for the workshop are detailed in [pyproject.toml](pyproject.toml).

If you're at an AWS-led event where a temporary account and VS Code Server instance has been provided for you, these dependencies will **already be installed** in an environment at `.venv` in this folder: you can skip to the next section.

If you're using [uv](https://docs.astral.sh/uv/) in your own local IDE (like Kiro or VSCode), you can perform the same setup by opening a terminal and running:

```sh
uv venv .venv
uv sync --all-extras --all-groups
```

If you're using plain pip with some other tool for managing environments, you can run:

```sh
pip install .[all]
```

For a lighter footprint, you could instead choose to install only the extras for the lab(s) you want to follow. For example, `pip install .[lab2,lab4]`.

### Run notebooks

The lab exercises make extensive use of `.ipynb` [Python notebook files](https://code.visualstudio.com/docs/datascience/jupyter-notebooks).

Notebooks bring together rich formatted explanations with interactive code "cells" that run against a live Python interpreter environment. You can run each cell of code by selecting it and either pressing `Shift`+`Enter` on the keyboard, or clicking the ▶️ play button.

When you first open or run a code cell in a notebook, you may be asked to **select a kernel**. If so, choose: Python Environments > .venv (.venv/bin/python)

If you don't see this option, check that the `.venv` folder has been created and follow the "Install dependencies" instructions above if needed. If using your own local IDE like VSCode or Kiro, check you've installed the recommended extensions for Jupyter and Python environment discovery. If you're at an AWS-led event and need help, don't hesitate to ask one of your facilitators!

When you're ready, why not go ahead and try running the first notebook:

▶️ [01_Inference_APIs/01_Inference_APIs.ipynb](01_Inference_APIs/01_Inference_APIs.ipynb)

## Further reading

Keen to explore further beyond this workshop? Check out:

- [aws-samples/amazon-bedrock-samples](https://github.com/aws-samples/amazon-bedrock-samples) for a more comprehensive range of code and notebook samples covering different features and use-cases of Amazon Bedrock
- The [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/) for detailed documentation
- The AI category in the [AWS Solutions Library](https://aws.amazon.com/solutions/ai/)

If you're building solutions powered by generative and agentic AI, it's also well worth exploring [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) - a unified platform to build, connect, and optimize AI agents!

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=aws-samples/amazon-bedrock-workshop&type=Date)](https://star-history.com/#aws-samples/amazon-bedrock-workshop&Date)

## Contributors

We welcome community contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

[![contributors](https://contrib.rocks/image?repo=aws-samples/amazon-bedrock-workshop&max=2000)](https://github.com/aws-samples/amazon-bedrock-workshop/graphs/contributors)
