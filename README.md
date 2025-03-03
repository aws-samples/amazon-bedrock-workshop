# Amazon Bedrock Workshop [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

This hands-on workshop, aimed at developers and solution builders, introduces how to leverage foundation models (FMs) through [Amazon Bedrock](https://aws.amazon.com/bedrock/). This code goes alongside the self-paced or instructor lead workshop here - https://catalog.us-east-1.prod.workshops.aws/amazon-bedrock/en-US

**Please follow the prerequisites listed in the link above or ask your AWS workshop instructor how to get started.**

Amazon Bedrock is a fully managed service that provides access to FMs from third-party providers and Amazon; available via an API. With Bedrock, you can choose from a variety of models to find the one that’s best suited for your use case.

Within this series of labs, you'll explore some of the most common usage patterns we are seeing with our customers for Generative AI. We will show techniques for generating text and images, creating value for organizations by improving productivity. This is achieved by leveraging foundation models to help in composing emails, summarizing text, answering questions, building chatbots, and creating images. While the focus of this workshop is for you to gain hands-on experience implementing these patterns via Bedrock APIs and SDKs, you will also have the option of exploring integrations with open-source packages like [LangChain](https://python.langchain.com/docs/get_started/introduction) and [FAISS](https://faiss.ai/index.html).

Labs include:

- **01 - Text Generation** \[Estimated time to complete - 45 mins\] [![Test - pass](https://img.shields.io/badge/Test-pass-2ea44f)](https://)
    - Text generation with Bedrock
    - Text summarization with Titan and Claude
    - QnA with Titan
    - Entity extraction
- **02 - Knowledge bases and RAG** \[Estimated time to complete - 45 mins\] [![Test - pass](https://img.shields.io/badge/Test-pass-2ea44f)](https://)
    - Managed RAG retrieve and generate example
    - Langchain RAG retrieve and generate example
- **03 - Model customization** \[Estimated time to complete - 30 mins\] [![Test - pass](https://img.shields.io/badge/Test-pass-2ea44f)](https://)
    - Fine tuning Titan lite, Llama2
    - **Note** - _You must run this on your own AWS account, and this will not work on AWS Workshop Studio!_
- **04 - Image and Multimodal** \[Estimated time to complete - 30 mins\] [![Test - pass](https://img.shields.io/badge/Test-pass-2ea44f)](https://)
    - Bedrock Titan image generator
    - Bedrock Stable Diffusion XL
    - Bedrock Titan Multimodal embeddings
- **05 - Agents** \[Estimated time to complete - 30 mins\] [![Test - pass](https://img.shields.io/badge/Test-pass-2ea44f)](https://)
    - Customer service agent
    - Insurance claims agent
- **06 - Open source examples (optional)** \[Estimated time to complete - 30 mins\] [![Test - fail](https://img.shields.io/badge/Test-fail-red)](https://)
    - Langchain Text Generation examples
    - Langchain KB RAG examples
    - Langchain Chatbot examples
    - NVIDIA NeMo Guardrails examples
    - NodeJS Bedrock examples

<div align="center">

![imgs/11-overview](imgs/11-overview.png "Overview of the different labs in the workshop")

</div>

You can also refer to these [Step-by-step guided instructions on the workshop website](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/en-US).


## Getting started

### Choose a notebook environment

This workshop is presented as a series of **Python notebooks**, which you can run from the environment of your choice:

- For a fully-managed environment with rich AI/ML features, we'd recommend using [SageMaker Studio](https://aws.amazon.com/sagemaker/studio/). To get started quickly, you can refer to the [instructions for domain quick setup](https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html).
- For a fully-managed but more basic experience, you could instead [create a SageMaker Notebook Instance](https://docs.aws.amazon.com/sagemaker/latest/dg/howitworks-create-ws.html).
- If you prefer to use your existing (local or other) notebook environment, make sure it has [credentials for calling AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).


### Enable AWS IAM permissions for Bedrock

The AWS identity you assume from your notebook environment (which is the [*Studio/notebook Execution Role*](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html) from SageMaker, or could be a role or IAM User for self-managed notebooks), must have sufficient [AWS IAM permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) to call the Amazon Bedrock service.

To grant Bedrock access to your identity, you can:

- Open the [AWS IAM Console](https://us-east-1.console.aws.amazon.com/iam/home?#)
- Find your [Role](https://us-east-1.console.aws.amazon.com/iamv2/home?#/roles) (if using SageMaker or otherwise assuming an IAM Role), or else [User](https://us-east-1.console.aws.amazon.com/iamv2/home?#/users)
- Select *Add Permissions > Create Inline Policy* to attach new inline permissions, open the *JSON* editor and paste in the below example policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockFullAccess",
            "Effect": "Allow",
            "Action": ["bedrock:*"],
            "Resource": "*"
        }
    ]
}
```

> ⚠️ **Note:** With Amazon SageMaker, your notebook execution role will typically be *separate* from the user or role that you log in to the AWS Console with. If you'd like to explore the AWS Console for Amazon Bedrock, you'll need to grant permissions to your Console user/role too. You can run the notebooks anywhere as long as you have access to the AWS Bedrock service and have appropriate credentials

For more information on the fine-grained action and resource permissions in Bedrock, check out the Bedrock Developer Guide.


### Clone and use the notebooks

> ℹ️ **Note:** In SageMaker Studio, you can open a "System Terminal" to run these commands by clicking *File > New > Terminal*

Once your notebook environment is set up, clone this workshop repository into it.

```sh
sudo yum install -y unzip
git clone https://github.com/aws-samples/amazon-bedrock-workshop.git
cd amazon-bedrock-workshop
```

[![HitCount](https://hits.dwyl.com/aws-samples/amazon-bedrock-workshop.svg?style=flat-square&show=unique)](http://hits.dwyl.com/aws-samples/amazon-bedrock-workshop)


You're now ready to explore the lab notebooks! Start with [00_Prerequisites/bedrock_basics.ipynb](00_Prerequisites/bedrock_basics.ipynb) for details on how to install the Bedrock SDKs, create a client, and start calling the APIs from Python. Here is the directory structure at a high level:

```
Directory structure:
└── aws-samples-amazon-bedrock-workshop/
    ├── README.md
    ├── CODE_OF_CONDUCT.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── RELEASE_NOTES.md
    ├── 00_Prerequisites/
    │   ├── README.md
    │   ├── Getting_started_with_Converse_API.ipynb
    │   └── bedrock_basics.ipynb
    ├── 01_Text_generation/
    │   ├── README.md
    │   ├── 01_text_and_code_generation_w_bedrock.ipynb
    │   ├── emails/
    │   │   ├── 00_treasure_island.txt
    │   │   └── 01_return.txt
    │   └── images/
    │       └── nova/
    ├── 02_KnowledgeBases_and_RAG/
    │   ├── README.md
    │   ├── 0_create_ingest_documents_test_kb.ipynb
    │   ├── 1_managed-rag-kb-retrieve-generate-api.ipynb
    │   ├── 2_Langchain-rag-retrieve-api-mistral-and-claude-3-haiku.ipynb
    │   ├── 3_Langchain-rag-retrieve-api-claude-3.ipynb
    │   ├── 4_CLEAN_UP.ipynb
    │   ├── requirements.txt
    │   ├── utility.py
    │   └── images/
    ├── 03_Model_customization/
    │   ├── README.md
    │   ├── 00_setup.ipynb
    │   ├── 01_fine-tuning-titan-lite.ipynb
    │   ├── 02_fine-tuning_llama2.ipynb
    │   ├── 03_continued_pretraining_titan_text.ipynb
    │   └── 04_cleanup.ipynb
    ├── 04_Image_and_Multimodal/
    │   ├── README.md
    │   ├── bedrock-titan-multimodal-embeddings.ipynb
    │   ├── nova-canvas-notebook.ipynb
    │   ├── nova-reel-notebook.ipynb
    │   ├── AmazonNova/
    │   │   ├── NovaCanvas/
    │   │   │   ├── 00-NovaCanvas-prerequisites.ipynb
    │   │   │   ├── 01-text-to-image.ipynb
    │   │   │   ├── 02-image-inpainting.ipynb
    │   │   │   ├── 03-image-outpainting.ipynb
    │   │   │   ├── 04-background-removal.ipynb
    │   │   │   ├── 05-image-variation.ipynb
    │   │   │   ├── 06-image-conditioning.ipynb
    │   │   │   ├── 07-color-conditioning.ipynb
    │   │   │   ├── utils.py
    │   │   │   └── images/
    │   │   └── NovaReel/
    │   │       ├── 00-NovaReel-prerequisites.ipynb
    │   │       ├── 01-text-to-video.ipynb
    │   │       ├── 02-image-to-video.ipynb
    │   │       ├── video_gen_util.py
    │   │       └── images/
    │   └── images/
    │       └── octank_color_palette.JPG
    ├── 05_Agents/
    │   ├── README.md
    │   ├── 00_inline_agents.ipynb
    │   ├── 01_create_agent.ipynb
    │   ├── 02_associate_knowledge_base_to_agent.ipynb
    │   ├── 03_invoke_agent.ipynb
    │   ├── 04_clean_up_agent_resources.ipynb
    │   ├── agent.py
    │   ├── knowledge_base.py
    │   ├── requirements.txt
    │   ├── images/
    │   └── kb_documents/
    ├── 06_OpenSource_examples/
    │   ├── README.md
    │   ├── advance-langgraph-multi-agent-setup.ipynb
    │   ├── find-relevant-information-using-RAG.ipynb
    │   ├── intermediate-langgraph-agent-setup-w-tools.ipynb
    │   ├── ragas-agent-evaluation.ipynb
    │   ├── requirements.txt
    │   ├── simple-crewai-agent-setup.ipynb
    │   ├── simple-langgraph-agent-setup.ipynb
    │   ├── utils.py
    │   ├── data/
    │   │   ├── section_doc_store.pkl
    │   │   ├── section_vector_store.pkl
    │   │   ├── synthetic_travel_data.csv
    │   │   └── travel_guides/
    │   ├── images/
    │   └── text-generation-with-langchain/
    │       ├── 01_zero_shot_generation.ipynb
    │       ├── 02_code_interpret_w_langchain.ipynb
    │       ├── 03_code_translate_w_langchain.ipynb
    │       ├── 04_long text summarization using LCEL chains on Langchain.ipynb
    │       ├── images/
    │       └── letters/
    │           └── 2022-letter.txt
    ├── 07_Cross_Region_Inference/
    │   ├── README.md
    │   └── Getting_started_with_Cross-region_Inference.ipynb
    ├── imgs/
    └── .github/
        └── ISSUE_TEMPLATE/
            └── bug_report.md
```

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=aws-samples/amazon-bedrock-workshop&type=Date)](https://star-history.com/#aws-samples/amazon-bedrock-workshop&Date)

# 👥 Contributors

Thanks to our awesome contributors! 🚀🚀🚀

[![contributors](https://contrib.rocks/image?repo=aws-samples/amazon-bedrock-workshop&max=2000)](https://github.com/aws-samples/amazon-bedrock-workshop/graphs/contributors)
