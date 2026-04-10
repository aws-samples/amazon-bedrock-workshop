# Bedrock RFT Helpers

Reusable utility functions for Amazon Bedrock Reinforcement Fine-Tuning (RFT) workflows.

## Installation

```python
import sys
sys.path.append("../../helpers")  # Adjust path as needed
from helpers import (
    create_lambda_execution_role,
    create_bedrock_rft_role,
    create_lambda_deployment_package,
    deploy_lambda_function
)
```

## Functions

### IAM Roles

#### create_lambda_execution_role
```python
role_arn = create_lambda_execution_role(
    role_name="MyLambdaRole",
    region="us-east-1",
    description="Lambda execution role",  # optional
    wait_seconds=10  # optional
)
```

#### create_bedrock_rft_role
```python
role_arn = create_bedrock_rft_role(
    role_name="MyBedrockRole",
    region="us-east-1",
    account_id="123456789012",
    s3_bucket="my-bucket",
    lambda_function_name="my-reward-function",
    s3_output_prefix="rft-output",  # optional
    wait_seconds=10  # optional
)
```

### Lambda Deployment

#### create_lambda_deployment_package
```python
zip_content = create_lambda_deployment_package(
    source_file="reward_function.py",
    zip_filename="deployment.zip",  # optional
    archive_name="handler.py"  # optional
)
```

#### deploy_lambda_function
```python
lambda_arn = deploy_lambda_function(
    function_name="my-reward-function",
    zip_content=zip_content,
    role_arn=lambda_role_arn,
    handler="reward_function.lambda_handler",
    region="us-east-1",
    runtime="python3.11",  # optional
    timeout=300,  # optional
    memory_size=512,  # optional
    environment_vars={"KEY": "value"}  # optional
)
```

## Example Usage

```python
import boto3
from helpers import (
    create_lambda_execution_role,
    create_bedrock_rft_role,
    create_lambda_deployment_package,
    deploy_lambda_function
)

REGION = "us-east-1"
S3_BUCKET = "my-bucket"
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']

# 1. Create Lambda role
lambda_role_arn = create_lambda_execution_role(
    role_name="MyLambdaRole",
    region=REGION
)

# 2. Create deployment package
zip_content = create_lambda_deployment_package("my_reward_function.py")

# 3. Deploy Lambda
lambda_arn = deploy_lambda_function(
    function_name="my-reward-function",
    zip_content=zip_content,
    role_arn=lambda_role_arn,
    handler="my_reward_function.lambda_handler",
    region=REGION
)

# 4. Create Bedrock role
bedrock_role_arn = create_bedrock_rft_role(
    role_name="MyBedrockRole",
    region=REGION,
    account_id=ACCOUNT_ID,
    s3_bucket=S3_BUCKET,
    lambda_function_name="my-reward-function"
)
```
