import os
import sys
from langchain.llms.bedrock import Bedrock
from functools import lru_cache
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers import register_llm_provider

def get_model(params):

    from utils import bedrock

    boto3_bedrock = bedrock.get_bedrock_client(
        assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
        region=os.environ.get("AWS_DEFAULT_REGION", None),
        runtime=True,
    )

    inference_modifier = {
        "max_tokens_to_sample": params['max_tokens_to_sample'],
        "temperature": params['temperature'],
        "top_k": 250,
        "top_p": 1
    }

    llm = Bedrock(
        model_id='anthropic.claude-instant-v1',
        client=boto3_bedrock,
        model_kwargs=inference_modifier,
    )
    return llm

@lru_cache
def get_bedrock_claude_v2():
    from .bedrock_borg_models import BedrockBorgModels
    borg_models = BedrockBorgModels()

    params = {"temperature": 0, "max_length": 1024, "max_tokens_to_sample": 450}

    # if you want to change the model_id,
    # you can do so here by changing the get_model() function
    llm = get_model(params)
    borg_models.llm = llm
    return llm


BedrockLLM = get_llm_instance_wrapper(
    llm_instance=get_bedrock_claude_v2(), llm_type="bedrock_llm"
)

def bootstrap():
    register_llm_provider("amazon_bedrock", BedrockLLM)

