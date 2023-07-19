# Prerequisites

- This workshop must be executed into your own account with access on Amazon Bedrock. 
- Run this workshop in **us-east-1 (N. Virginia)** region.
- If you are running on SageMaker Studio, here is recommended kernel configuration: 
    - Image: Data Science 3.0
    - Instance Type: ml.t3.medium

## IAM Policy for Bedrock

Following IAM policy should be created to grant access on Bedrock APIs:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Action": "bedrock:*",
            "Resource": "*"
        }
    ]
}
```

Now, please proceed to the environment setup.

# Environment Setup

## Boto3 Setup

First, to be able to execute this workshop, you should have [Python](https://www.python.org/getit/) installed. 

>  Python version >= 3.9

Next, you need to install boto3 (and botocore) [AWS SDK for Python (Boto3)](https://aws.amazon.com/sdk-for-python/) libraries. Both libraries contain required dependencies related with Bedrock APIs. 

This can be downloaded using the script on the root of this repository

```sh
bash download-dependencies.sh
```

To install it, run the following commands:


```python
%pip install ../dependencies/botocore-1.29.162-py3-none-any.whl 
%pip install ../dependencies/boto3-1.26.162-py3-none-any.whl 
%pip install ../dependencies/awscli-1.27.162-py3-none-any.whl 
```

> `boto3` version must be >= 1.26.162 and `botocore` version must be >= 1.29.162

## AWS Credentials (optional)

If you are running this workshop in your local computer, such as Microsoft VS Code, PyCharm, etc., you should run the following snippet, which will configure your credentials (to be able to run AWS API calls):

```python
import sys, os
module_path = "../utils"
sys.path.append(os.path.abspath(module_path))
import bedrock as util_w

os.environ['LANGCHAIN_ASSUME_ROLE'] = '<YOUR_VALUES>'
boto3_bedrock = util_w.get_bedrock_client(os.environ['LANGCHAIN_ASSUME_ROLE'])
```

## LangChain installation

It's also necessary to install [LangChain](https://python.langchain.com/en/latest/index.html). LangChain is a framework for developing applications powered by language models.

```python
%pip install langchain==0.0.190 --quiet
```

> `LangChain` version must be >= `0.0.190`

## Explanation of Bedrock API

First, you instantiate a client session on `boto3` to make calls on Bedrock API:

```python
bedrock = boto3.client(service_name='bedrock',
                       region_name='us-east-1',
                       endpoint_url='https://bedrock.us-east-1.amazonaws.com')
```

Next, you call `InvokeModel` API for sending requests to a foundation model. 
Following is an example of API request to send a text to Amazon Titan Model. 

```python
response = bedrock.invoke_model(body={
                                   "inputText": "this is where you place your input text",
                                   "textGenerationConfig": {
                                       "maxTokenCount": 4096,
                                       "stopSequences": [],
                                       "temperature":0,
                                       "topP":1
                                       },
                                },
                                modelId="amazon.titan-tg1-large", 
                                accept=accept, 
                                contentType=contentType)

```

Where:

* **inputText**: Text prompt to be send to the Bedrock API.
* **textGenerationConfig**: Model specific parameters (varies for each model) to be considered during inference time.

## Conclusion

**Congratulations!** In this section, you installed all prerequisite and understood Bedrock API. 

**Now, you can start the workshop**.