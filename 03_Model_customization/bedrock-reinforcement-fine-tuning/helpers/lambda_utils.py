"""
Lambda deployment utilities for Bedrock RFT reward functions.
"""

import os
import zipfile
from typing import Optional
import boto3


def create_lambda_deployment_package(
    source_file: str,
    zip_filename: str = "lambda_deployment.zip",
    archive_name: Optional[str] = None,
) -> bytes:
    """
    Create a Lambda deployment package from a Python file.

    Args:
        source_file: Path to the Python source file
        zip_filename: Name for the output zip file
        archive_name: Name for the file inside the archive (defaults to source filename)

    Returns:
        Zip file contents as bytes
    """
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file not found: {source_file}")

    archive_name = archive_name or os.path.basename(source_file)

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(source_file, archive_name)

    print(f"✓ Created {zip_filename}")

    with open(zip_filename, "rb") as f:
        content = f.read()

    print(f"✓ Package size: {len(content) / 1024:.1f} KB")
    return content


def cleanup_lambda_deployment_package(
    zip_filename: str = "lambda_deployment.zip",
) -> None:
    """Remove the Lambda deployment zip file."""
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        print(f"✓ Cleaned up {zip_filename}")


def deploy_lambda_function(
    function_name: str,
    zip_content: bytes,
    role_arn: str,
    handler: str,
    region: str,
    runtime: str = "python3.11",
    description: str = "RFT reward function",
    timeout: int = 300,
    memory_size: int = 512,
    environment_vars: Optional[dict] = None,
) -> str:
    """
    Deploy or update a Lambda function.

    Args:
        function_name: Name for the Lambda function
        zip_content: Deployment package as bytes
        role_arn: IAM role ARN for Lambda execution
        handler: Lambda handler (e.g., 'module.function_name')
        region: AWS region
        runtime: Python runtime version
        description: Function description
        timeout: Function timeout in seconds
        memory_size: Memory allocation in MB
        environment_vars: Environment variables dict

    Returns:
        Lambda function ARN
    """
    lambda_client = boto3.client("lambda", region_name=region)
    environment_vars = environment_vars or {}

    print(f"Deploying Lambda function: {function_name}...")

    # Check if function exists
    try:
        lambda_client.get_function(FunctionName=function_name)
        function_exists = True
    except lambda_client.exceptions.ResourceNotFoundException:
        function_exists = False

    if function_exists:
        print("Function exists, updating code...")
        lambda_client.update_function_code(
            FunctionName=function_name, ZipFile=zip_content
        )
        print("✓ Lambda function code updated")
    else:
        print("Creating new Lambda function...")
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": zip_content},
            Description=description,
            Timeout=timeout,
            MemorySize=memory_size,
            Environment={"Variables": environment_vars},
        )
        print("✓ Lambda function created")

    # Wait for function to be active
    print("Waiting for function to be active...")
    waiter = lambda_client.get_waiter("function_active_v2")
    waiter.wait(FunctionName=function_name)

    function_info = lambda_client.get_function(FunctionName=function_name)
    lambda_arn = function_info["Configuration"]["FunctionArn"]

    print(f"✓ Lambda deployed: {lambda_arn}")
    print(f"  Runtime: {function_info['Configuration']['Runtime']}")
    print(f"  Memory: {function_info['Configuration']['MemorySize']} MB")
    print(f"  Timeout: {function_info['Configuration']['Timeout']}s")

    return lambda_arn
