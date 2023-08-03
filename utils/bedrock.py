# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Helper utilities for working with Amazon Bedrock from Python notebooks"""
# Python Built-Ins:
import os
from typing import Optional

# External Dependencies:
import boto3
from botocore.config import Config


def get_bedrock_client(
    assumed_role: Optional[str] = None,
    endpoint_url: Optional[str] = None,
    region: Optional[str] = None,
):
    """Create a boto3 client for Amazon Bedrock, with optional configuration overrides

    Parameters
    ----------
    assumed_role :
        Optional ARN of an AWS IAM role to assume for calling the Bedrock service. If not
        specified, the current active credentials will be used.
    endpoint_url :
        Optional override for the Bedrock service API Endpoint. If setting this, it should usually
        include the protocol i.e. "https://..."
    region :
        Optional name of the AWS Region in which the service should be called (e.g. "us-east-1").
        If not specified, AWS_REGION or AWS_DEFAULT_REGION environment variable will be used.
    """
    if region is None:
        target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
    else:
        target_region = region

    print(f"Create new client\n  Using region: {target_region}")

    # Create the session
    boto3_session_kwargs = {"region_name": target_region}

    profile_name = os.environ.get("AWS_PROFILE")
    if profile_name:
        print(f"  Using profile: {profile_name}")
        boto3_session_kwargs["profile_name"] = profile_name

    session = boto3.Session(**boto3_session_kwargs)

    # Create the client
    boto3_client_kwargs = {"region_name": target_region}
    if assumed_role:
        print(f"  Using role: {assumed_role}", end='')
        sts = session.client("sts")
        response = sts.assume_role(
            RoleArn=str(assumed_role),
            RoleSessionName="langchain-llm-1"
        )
        print(" ... successful!")
        boto3_client_kwargs["aws_access_key_id"] = response["Credentials"]["AccessKeyId"]
        boto3_client_kwargs["aws_secret_access_key"] = response["Credentials"]["SecretAccessKey"]
        boto3_client_kwargs["aws_session_token"] = response["Credentials"]["SessionToken"]

    if endpoint_url:
        boto3_client_kwargs["endpoint_url"] = endpoint_url

    retry_config = Config(
        region_name=target_region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
    bedrock_client = session.client(
        service_name="bedrock",
        config=retry_config,
        **boto3_client_kwargs
    )

    print("boto3 Bedrock client successfully created!")
    print(bedrock_client._endpoint)
    return bedrock_client
