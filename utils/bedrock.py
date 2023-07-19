import json
import boto3
import os
from typing import Any, Dict, List, Optional
from pydantic import root_validator
from time import sleep
from enum import Enum
import boto3
from botocore.config import Config

def get_bedrock_client(assumed_role=None, region='us-east-1', url_override = None):
    boto3_kwargs = {}
    session = boto3.Session()

    target_region = os.environ.get('AWS_DEFAULT_REGION',region)

    print(f"Create new client\n  Using region: {target_region}")
    if 'AWS_PROFILE' in os.environ:
        print(f"  Using profile: {os.environ['AWS_PROFILE']}")

    retry_config = Config(
        region_name = target_region,
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    boto3_kwargs = {}

    if assumed_role:
        print(f"  Using role: {assumed_role}", end='')
        sts = session.client("sts")
        response = sts.assume_role(
            RoleArn=str(assumed_role), #
            RoleSessionName="langchain-llm-1"
        )
        print(" ... successful!")
        boto3_kwargs['aws_access_key_id']=response['Credentials']['AccessKeyId']
        boto3_kwargs['aws_secret_access_key']=response['Credentials']['SecretAccessKey']
        boto3_kwargs['aws_session_token']=response['Credentials']['SessionToken']

    if url_override:
        boto3_kwargs['endpoint_url']=url_override

    bedrock_client = session.client(
        service_name='bedrock',
        config=retry_config,
        region_name= target_region,
        **boto3_kwargs
        )
 
    print("boto3 Bedrock client successfully created!")
    print(bedrock_client._endpoint)
    return bedrock_client


class BedrockMode(Enum):
    IMAGE = "image"


class BedrockModel(Enum):
    STABLE_DIFFUSION = "stability.stable-diffusion-xl"


class Bedrock:
    __DEFAULT_EMPTY_EMBEDDING = [
        0.0
    ] * 4096  # - we need to return an array of floats 4096 in size
    __RETRY_BACKOFF_SEC = 3
    __RETRY_ATTEMPTS = 3

    def __init__(self, client=None) -> None:
        if client is None:
            self.client = get_bedrock_client(assumed_role=None)
        else:
            assert str(type(client)) == "<class 'botocore.client.Bedrock'>", f"The client passed in not a valid boto3 bedrock client, got {type(client)}"
            self.client = client

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        bedrock_client = get_bedrock_client(assumed_role=None) #boto3.client("bedrock")
        values["client"] = bedrock_client
        return values
    
    def generate_image(self, prompt: str, init_image: Optional[str] = None, **kwargs):
        """
        Invoke Bedrock model to generate embeddings.
        Args:
            text (str): Input text
        """
        mode = BedrockMode.IMAGE
        model_type = BedrockModel.STABLE_DIFFUSION
        payload = self.prepare_input(
            prompt, init_image=init_image, mode=mode, model_type=model_type, **kwargs
        )
        response = self._invoke_model(model_id=model_type, body_string=payload)
        _, _, img_base_64 = self.extract_results(response, model_type)
        return img_base_64

    @staticmethod
    def extract_results(response, model_type: BedrockModel, verbose=False):
        response = response["body"].read()
        if verbose:
            print(f"response body readlines() returns: {response}")

        json_obj = json.loads(response)
        if model_type == BedrockModel.STABLE_DIFFUSION:
            in_token_count, out_token_count = None, None
            if json_obj["result"] == "success":
                model_output = json_obj["artifacts"][0]["base64"]
            else:
                model_output = None
        else:
            raise Exception(f" This class is for Stable Diffusion ONLY::model_type={model_type}")

        return in_token_count, out_token_count, model_output

    @staticmethod
    def prepare_input(
        prompt_text,
        negative_prompts=[],
        stop_sequences=[],
        cfg_scale=10,
        seed=1,
        steps=50,
        start_schedule=0.5,
        init_image=None,
        style_preset='photographic',
        mode=BedrockMode.IMAGE,
        model_type=BedrockModel.STABLE_DIFFUSION,
        **kwargs,
    ):
        stop_sequences = stop_sequences[
            :1
        ]  # Temporary addition as Bedrock models can't take multiple stop_sequences yet. Will change later.
        if mode == BedrockMode.IMAGE:
            if model_type in [BedrockModel.STABLE_DIFFUSION]:
                positives = [{"text": prompt_text, "weight": 1}]
                negatives = [{"text": prompt, "weight": -1} for prompt in negative_prompts]
                json_obj = {
                    "text_prompts": positives + negatives,
                    "cfg_scale": cfg_scale,
                    "seed": seed,
                    "steps": steps,
                    "style_preset": style_preset
                }
                if init_image is not None:
                    json_obj["init_image"] = init_image
                    json_obj["start_schedule"] = start_schedule
            else:
                raise Exception(
                    'Unsupported model_type, only "STABLE_DIFFUSION" model_type is supported.'
                )

        return json.dumps(json_obj)

    def list_models(self):
        response = self.client.list_foundation_models()
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response["modelSummaries"]
        else:
            raise Exception("Invalid response")

    def _invoke_model(self, model_id: BedrockModel, body_string: str):
        body = bytes(body_string, "utf-8")
        response = None
        for attempt_no in range(self.__RETRY_ATTEMPTS):
            try:
                response = self.client.invoke_model(
                    modelId=model_id.value,
                    contentType="application/json",
                    accept="application/json",
                    body=body,
                )
                break
            except:
                print(
                    f"bedrock:invoke_model: Attempt no. {attempt_no+1} failed:: Retrying after {self.__RETRY_BACKOFF_SEC} seconds!"
                )
                sleep(self.__RETRY_BACKOFF_SEC)
                continue
        return response


