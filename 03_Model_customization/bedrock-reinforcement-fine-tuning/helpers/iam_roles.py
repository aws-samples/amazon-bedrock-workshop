"""
IAM Role utilities for Bedrock RFT training.
"""

import json
import time
import boto3


def create_lambda_execution_role(
    role_name: str,
    region: str,
    description: str = "Lambda execution role for RFT reward function",
    wait_seconds: int = 10,
) -> str:
    """
    Create or retrieve an IAM role for Lambda function execution.

    Args:
        role_name: Name for the IAM role
        region: AWS region
        description: Role description
        wait_seconds: Seconds to wait for role propagation

    Returns:
        Role ARN
    """
    iam_client = boto3.client("iam", region_name=region)

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description,
        )
        role_arn = response["Role"]["Arn"]
        print(f"✓ Created role: {role_name}")

        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        )
        print("✓ Attached AWSLambdaBasicExecutionRole policy")

    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Role {role_name} already exists, using existing role")
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response["Role"]["Arn"]

    print(f"✓ Lambda role ready: {role_arn}")
    return role_arn


def create_bedrock_rft_role(
    role_name: str,
    region: str,
    account_id: str,
    s3_bucket: str,
    lambda_function_name: str,
    s3_output_prefix: str = "rft-output",
    description: str = "Execution role for Bedrock RFT training jobs",
    wait_seconds: int = 10,
) -> str:
    """
    Create or retrieve an IAM role for Bedrock RFT training.

    Args:
        role_name: Name for the IAM role
        region: AWS region
        account_id: AWS account ID
        s3_bucket: S3 bucket name for training data
        lambda_function_name: Name of the Lambda reward function
        s3_output_prefix: S3 prefix for output data
        description: Role description
        wait_seconds: Seconds to wait for role propagation

    Returns:
        Role ARN
    """
    iam_client = boto3.client("iam", region_name=region)

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "S3ReadAccess",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{s3_bucket}/*",
                    f"arn:aws:s3:::{s3_bucket}",
                ],
            },
            {
                "Sid": "S3WriteAccess",
                "Effect": "Allow",
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{s3_bucket}/{s3_output_prefix}/*",
            },
            {
                "Sid": "LambdaInvokeAccess",
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:{region}:{account_id}:function:{lambda_function_name}",
            },
        ],
    }

    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description,
        )
        role_arn = response["Role"]["Arn"]
        print(f"✓ Created role: {role_name}")

        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName="BedrockRFTPermissions",
            PolicyDocument=json.dumps(permissions_policy),
        )
        print("✓ Attached permissions policy")

    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Role {role_name} already exists, updating policy...")
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName="BedrockRFTPermissions",
            PolicyDocument=json.dumps(permissions_policy),
        )
        print("✓ Updated permissions policy")
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response["Role"]["Arn"]

    print(f"✓ Bedrock role ready: {role_arn}")
    return role_arn
