import time
import json
import requests
from boto3.session import Session
from botocore.exceptions import ClientError
import botocore
import boto3
import zipfile
import subprocess
import shutil

import os


def get_kb_id(kb_name):
    smm_client = boto3.client("ssm")
    kb_id = smm_client.get_parameter(
        Name=f"{kb_name}-kb-id", WithDecryption=False)
    print("Knowledge Base Id:", kb_id["Parameter"]["Value"])
    return kb_id["Parameter"]["Value"]


def get_db_table_name(kb_name):
    smm_client = boto3.client("ssm")
    table_name = smm_client.get_parameter(
        Name=f"{kb_name}-table-name", WithDecryption=False
    )
    print("DynamoDB table:", table_name["Parameter"]["Value"])
    return table_name["Parameter"]["Value"]

def attach_inline_policy(role_arn, policy_file, policy_name: str = "InlinePolicy") -> None:
    """
    Attaches an inline IAM policy (from a JSON file) to the specified IAM role.

    Args:
        role_arn (str): The ARN of the IAM role.
        policy_file (str): Path to the JSON file containing the policy definition.
        policy_name (str): Name for the inline policy. Defaults to "InlinePolicy".
    """
    # Extract role name from ARN
    if ":role/" not in role_arn:
        raise ValueError("Invalid IAM role ARN format.")
    role_name = role_arn.split(":role/")[-1].split("/")[-1]

    # Read policy from JSON file
    with open(policy_file, "r", encoding="utf-8") as f:
        policy_doc = json.load(f)

    # Attach inline policy
    iam = boto3.client("iam")
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_doc)
    )

    print(f"✅ Inline policy '{policy_name}' attached to role '{role_name}'.")