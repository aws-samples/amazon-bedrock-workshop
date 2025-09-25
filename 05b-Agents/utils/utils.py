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
    return kb_id


def get_db_table(kb_name):
    smm_client = boto3.client("ssm")
    dynamodb = boto3.resource("dynamodb")
    table_name = smm_client.get_parameter(
        Name=f"{kb_name}-table-name", WithDecryption=False
    )
    table = dynamodb.Table(table_name["Parameter"]["Value"])
    print("DynamoDB table:", table_name["Parameter"]["Value"])
    return table


def create_agentcore_execution_role(role_name="agentcore-execution-role", aws_region="us-east-1"):
    """
    Create an AgentCore Runtime execution role with DynamoDB and Bedrock Knowledge Base access.

    Args:
        role_name (str): Name of the IAM role to create
        aws_account_id (str): AWS Account ID (will be auto-detected if not provided)
        aws_region (str): AWS Region
    """

    iam_client = boto3.client('iam', region_name=aws_region)
    sts_client = boto3.client('sts', region_name=aws_region)

    # Get AWS Account ID if not provided
    aws_account_id = sts_client.get_caller_identity()['Account']

    print(f"Creating AgentCore Runtime execution role: {role_name}")
    print(f"AWS Account ID: {aws_account_id}")
    print(f"AWS Region: {aws_region}")

    # Load and prepare trust policy
    try:
        with open('utils/agentcore-execution-role-trust-policy.json', 'r') as f:
            trust_policy = json.load(f)

        # Replace placeholder with actual account ID
        trust_policy_str = json.dumps(trust_policy).replace(
            '${AWS_ACCOUNT_ID}', aws_account_id)
        trust_policy = json.loads(trust_policy_str)

    except FileNotFoundError:
        print("❌ Error: agentcore-execution-role-trust-policy.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing trust policy JSON: {e}")
        return False

    # Load execution policy
    try:
        with open('utils/agentcore-execution-role-policy.json', 'r') as f:
            execution_policy = json.load(f)
    except FileNotFoundError:
        print("❌ Error: agentcore-execution-role-policy.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing execution policy JSON: {e}")
        return False

    try:
        # Create the IAM role
        print("Creating IAM role...")

        try:
            iam_client.get_role(RoleName=role_name)
            print(f"⚠️ Role '{role_name}' already exists. Skipping creation.")
            return True  # or return the ARN if you want to reuse it
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchEntity':
                raise  # real error, re-raise

        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Execution role for AgentCore Runtime with DynamoDB and Bedrock Knowledge Base access"
        )
        print(f"✅ Successfully created role: {role_name}")

        # Attach the execution policy
        print("Attaching execution policy...")
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName="AgentCoreExecutionPolicy",
            PolicyDocument=json.dumps(execution_policy)
        )
        print("✅ Successfully attached execution policy")

        role_arn = f"arn:aws:iam::{aws_account_id}:role/{role_name}"
        print(f"\n🎉 Role created successfully!")
        print(f"Role ARN: {role_arn}")
        print("\nYou can now use this role when creating your AgentCore Runtime.")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'EntityAlreadyExists':
            print(
                f"❌ Role '{role_name}' already exists. Choose a different name or delete the existing role.")
        else:
            print(f"❌ Error creating role: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def create_gateway_lambda(lambda_function_code_path) -> dict[str, int]:
    boto_session = Session()
    region = boto_session.region_name

    return_resp = {"lambda_function_arn": "Pending", "exit_code": 1}

    # Initialize Cognito client
    lambda_client = boto3.client('lambda', region_name=region)
    iam_client = boto3.client('iam', region_name=region)

    role_name = 'gateway_lambda_iamrole'
    role_arn = ''
    lambda_function_name = 'gateway_lambda'

    print("Reading code from zip file")
    with open(lambda_function_code_path, 'rb') as f:
        lambda_function_code = f.read()

    try:
        print("Creating IAM role for lambda function")

        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }),
            Description="IAM role to be assumed by lambda function"
        )

        role_arn = response['Role']['Arn']

        print("Attaching policy to the IAM role")

        response = iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )

        print(f"Role '{role_name}' created successfully: {role_arn}")
        time.sleep(100)
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == "EntityAlreadyExists":
            response = iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            print(
                f"IAM role {role_name} already exists. Using the same ARN {role_arn}")
        else:
            error_message = error.response['Error']['Code'] + \
                "-" + error.response['Error']['Message']
            print(f"Error creating role: {error_message}")
            return_resp['lambda_function_arn'] = error_message

    if role_arn != "":
        print("Creating lambda function")
        # Create lambda function
        try:
            lambda_response = lambda_client.create_function(
                FunctionName=lambda_function_name,
                Role=role_arn,
                Runtime='python3.12',
                Handler='lambda_handler.lambda_handler',
                Code={'ZipFile': lambda_function_code},
                Description='Lambda function example for Bedrock AgentCore Gateway',
                PackageType='Zip'
            )

            return_resp['lambda_function_arn'] = lambda_response['FunctionArn']
            return_resp['exit_code'] = 0
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == "ResourceConflictException":
                response = lambda_client.get_function(
                    FunctionName=lambda_function_name)
                lambda_arn = response['Configuration']['FunctionArn']
                print(
                    f"AWS Lambda function {lambda_function_name} already exists. Using the same ARN {lambda_arn}")
                return_resp['lambda_function_arn'] = lambda_arn
            else:
                error_message = error.response['Error']['Code'] + \
                    "-" + error.response['Error']['Message']
                print(f"Error creating lambda function: {error_message}")
                return_resp['lambda_function_arn'] = error_message

    return return_resp


def create_agentcore_gateway_role(gateway_name):
    iam_client = boto3.client('iam')
    agentcore_gateway_role_name = f'agentcore-{gateway_name}-role'
    boto_session = Session()
    region = boto_session.region_name
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    role_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:*",
                "bedrock:*",
                "agent-credential-provider:*",
                "iam:PassRole",
                "secretsmanager:GetSecretValue",
                "lambda:InvokeFunction"
            ],
            "Resource": "*"
        }
        ]
    }

    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AssumeRolePolicy",
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": f"{account_id}"
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"
                    }
                }
            }
        ]
    }

    assume_role_policy_document_json = json.dumps(
        assume_role_policy_document
    )

    role_policy_document = json.dumps(role_policy)
    # Create IAM Role for the Lambda function
    try:
        agentcore_iam_role = iam_client.create_role(
            RoleName=agentcore_gateway_role_name,
            AssumeRolePolicyDocument=assume_role_policy_document_json
        )

        # Pause to make sure role is created
        time.sleep(10)
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("Role already exists -- deleting and creating it again")
        policies = iam_client.list_role_policies(
            RoleName=agentcore_gateway_role_name,
            MaxItems=100
        )
        print("policies:", policies)
        for policy_name in policies['PolicyNames']:
            iam_client.delete_role_policy(
                RoleName=agentcore_gateway_role_name,
                PolicyName=policy_name
            )
        print(f"deleting {agentcore_gateway_role_name}")
        iam_client.delete_role(
            RoleName=agentcore_gateway_role_name
        )
        print(f"recreating {agentcore_gateway_role_name}")
        agentcore_iam_role = iam_client.create_role(
            RoleName=agentcore_gateway_role_name,
            AssumeRolePolicyDocument=assume_role_policy_document_json
        )

    # Attach the AWSLambdaBasicExecutionRole policy
    print(f"attaching role policy {agentcore_gateway_role_name}")
    try:
        iam_client.put_role_policy(
            PolicyDocument=role_policy_document,
            PolicyName="AgentCorePolicy",
            RoleName=agentcore_gateway_role_name
        )
    except Exception as e:
        print(e)

    return agentcore_iam_role


def get_or_create_user_pool(cognito, USER_POOL_NAME):
    response = cognito.list_user_pools(MaxResults=60)
    for pool in response["UserPools"]:
        if pool["Name"] == USER_POOL_NAME:
            user_pool_id = pool["Id"]
            response = cognito.describe_user_pool(
                UserPoolId=user_pool_id
            )

            # Get the domain from user pool description
            user_pool = response.get('UserPool', {})
            domain = user_pool.get('Domain')

            if domain:
                region = user_pool_id.split(
                    '_')[0] if '_' in user_pool_id else REGION
                domain_url = f"https://{domain}.auth.{region}.amazoncognito.com"
                print(
                    f"Found domain for user pool {user_pool_id}: {domain} ({domain_url})")
            else:
                print(f"No domains found for user pool {user_pool_id}")
            return pool["Id"]
    print('Creating new user pool')
    created = cognito.create_user_pool(PoolName=USER_POOL_NAME)
    user_pool_id = created["UserPool"]["Id"]
    user_pool_id_without_underscore_lc = user_pool_id.replace("_", "").lower()
    cognito.create_user_pool_domain(
        Domain=user_pool_id_without_underscore_lc,
        UserPoolId=user_pool_id
    )
    print("Domain created as well")
    return created["UserPool"]["Id"]


def get_or_create_resource_server(cognito, user_pool_id, RESOURCE_SERVER_ID, RESOURCE_SERVER_NAME, SCOPES):
    try:
        existing = cognito.describe_resource_server(
            UserPoolId=user_pool_id,
            Identifier=RESOURCE_SERVER_ID
        )
        return RESOURCE_SERVER_ID
    except cognito.exceptions.ResourceNotFoundException:
        print('creating new resource server')
        cognito.create_resource_server(
            UserPoolId=user_pool_id,
            Identifier=RESOURCE_SERVER_ID,
            Name=RESOURCE_SERVER_NAME,
            Scopes=SCOPES
        )
        return RESOURCE_SERVER_ID


def get_or_create_m2m_client(cognito, user_pool_id, CLIENT_NAME, RESOURCE_SERVER_ID):
    response = cognito.list_user_pool_clients(
        UserPoolId=user_pool_id, MaxResults=60)
    for client in response["UserPoolClients"]:
        if client["ClientName"] == CLIENT_NAME:
            describe = cognito.describe_user_pool_client(
                UserPoolId=user_pool_id, ClientId=client["ClientId"])
            return client["ClientId"], describe["UserPoolClient"]["ClientSecret"]
    print('creating new m2m client')
    created = cognito.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=CLIENT_NAME,
        GenerateSecret=True,
        AllowedOAuthFlows=["client_credentials"],
        AllowedOAuthScopes=[
            f"{RESOURCE_SERVER_ID}/gateway:read", f"{RESOURCE_SERVER_ID}/gateway:write"],
        AllowedOAuthFlowsUserPoolClient=True,
        SupportedIdentityProviders=["COGNITO"],
        ExplicitAuthFlows=["ALLOW_REFRESH_TOKEN_AUTH"]
    )
    return created["UserPoolClient"]["ClientId"], created["UserPoolClient"]["ClientSecret"]


def get_token(user_pool_id: str, client_id: str, client_secret: str, scope_string: str, REGION: str) -> dict:
    try:
        user_pool_id_without_underscore = user_pool_id.replace("_", "")
        url = f"https://{user_pool_id_without_underscore}.auth.{REGION}.amazoncognito.com/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope_string,

        }
        print(client_id)
        print(client_secret)
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as err:
        return {"error": str(err)}


def create_lambda_zip():
    # Create temp directory for dependencies
    temp_dir = "utils/lambda_package"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # Install dependencies
    subprocess.run([
        "pip", "install", "python-weather",
        "--target", temp_dir
    ], check=True)

    # Copy lambda handler
    shutil.copy("utils/lambda_handler.py", temp_dir)

    # Create zip file
    with zipfile.ZipFile("utils/weather_lambda.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # Cleanup
    shutil.rmtree(temp_dir)
    print("✅ Created weather_lambda.zip")
