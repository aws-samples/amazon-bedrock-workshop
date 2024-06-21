import boto3
import json
import time
import zipfile
import logging
import pprint
from io import BytesIO

iam_client = boto3.client('iam')
sts_client = boto3.client('sts')
session = boto3.session.Session()
region = session.region_name
account_id = sts_client.get_caller_identity()["Account"]
dynamodb_client = boto3.client('dynamodb')
dynamodb_resource = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
bedrock_agent_client = boto3.client('bedrock-agent')
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def create_dynamodb(table_name):
    try:
        table = dynamodb_resource.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'booking_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'booking_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # Use on-demand capacity mode
        )

        # Wait for the table to be created
        print(f'Creating table {table_name}...')
        table.wait_until_exists()
        print(f'Table {table_name} created successfully!')
    except dynamodb_client.Client.exceptions.ResourceInUseException:
        print(f'Table {table_name} already exists, skipping table creation step')


def create_lambda(lambda_function_name, lambda_iam_role):
    # add to function

    # Package up the lambda function code
    s = BytesIO()
    z = zipfile.ZipFile(s, 'w')
    z.write("lambda_function.py")
    z.close()
    zip_content = s.getvalue()
    try:
        # Create Lambda Function
        lambda_function = lambda_client.create_function(
            FunctionName=lambda_function_name,
            Runtime='python3.12',
            Timeout=60,
            Role=lambda_iam_role['Role']['Arn'],
            Code={'ZipFile': zip_content},
            Handler='lambda_function.lambda_handler'
        )
    except lambda_client.Client.exceptions.ResourceConflictException:
        print("Lambda function already exists, retrieving it")
        lambda_function = lambda_client.get_function(
            FunctionName=lambda_function_name
        )
        lambda_function = lambda_function['Configuration']

    return lambda_function


def create_lambda_role(agent_name, dynamodb_table_name):
    lambda_function_role = f'{agent_name}-lambda-role'
    dynamodb_access_policy_name = f'{agent_name}-dynamodb-policy'
    # Create IAM Role for the Lambda function
    try:
        assume_role_policy_document = {
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
        }

        assume_role_policy_document_json = json.dumps(assume_role_policy_document)

        lambda_iam_role = iam_client.create_role(
            RoleName=lambda_function_role,
            AssumeRolePolicyDocument=assume_role_policy_document_json
        )

        # Pause to make sure role is created
        time.sleep(10)
    except iam_client.exceptions.EntityAlreadyExistsException:
        lambda_iam_role = iam_client.get_role(RoleName=lambda_function_role)

    # Attach the AWSLambdaBasicExecutionRole policy
    iam_client.attach_role_policy(
        RoleName=lambda_function_role,
        PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    )

    # Create a policy to grant access to the DynamoDB table
    dynamodb_access_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:DeleteItem"
                ],
                "Resource": "arn:aws:dynamodb:{}:{}:table/{}".format(
                    region, account_id, dynamodb_table_name
                )
            }
        ]
    }

    # Create the policy
    dynamodb_access_policy_json = json.dumps(dynamodb_access_policy)
    try:
        dynamodb_access_policy = iam_client.create_policy(
            PolicyName=dynamodb_access_policy_name,
            PolicyDocument=dynamodb_access_policy_json
        )
    except iam_client.exceptions.EntityAlreadyExistsException:
        dynamodb_access_policy = iam_client.get_policy(
            PolicyArn=f"arn:aws:iam::{account_id}:policy/{dynamodb_access_policy_name}"
        )

    # Attach the policy to the Lambda function's role
    iam_client.attach_role_policy(
        RoleName=lambda_function_role,
        PolicyArn=dynamodb_access_policy['Policy']['Arn']
    )
    return lambda_iam_role


def invoke_agent_helper(query, session_id, agent_id, alias_id, enable_trace=False, session_state=None):
    end_session: bool = False
    if not session_state:
        session_state = {}

    # invoke the agent API
    agent_response = bedrock_agent_runtime_client.invoke_agent(
        inputText=query,
        agentId=agent_id,
        agentAliasId=alias_id,
        sessionId=session_id,
        enableTrace=enable_trace,
        endSession=end_session,
        sessionState=session_state
    )

    if enable_trace:
        logger.info(pprint.pprint(agent_response))

    event_stream = agent_response['completion']
    try:
        for event in event_stream:
            if 'chunk' in event:
                data = event['chunk']['bytes']
                if enable_trace:
                    logger.info(f"Final answer ->\n{data.decode('utf8')}")
                agent_answer = data.decode('utf8')
                return agent_answer
                # End event indicates that the request finished successfully
            elif 'trace' in event:
                if enable_trace:
                    logger.info(json.dumps(event['trace'], indent=2))
            else:
                raise Exception("unexpected event.", event)
    except Exception as e:
        raise Exception("unexpected event.", e)


def create_agent_role(agent_name, agent_foundation_model, kb_id=None):
    agent_bedrock_allow_policy_name = f"{agent_name}-ba"
    agent_role_name = f'AmazonBedrockExecutionRoleForAgents_{agent_name}'
    # Create IAM policies for agent
    statements = [
        {
            "Sid": "AmazonBedrockAgentBedrockFoundationModelPolicy",
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": [
                f"arn:aws:bedrock:{region}::foundation-model/{agent_foundation_model}"
            ]
        }
    ]
    # add Knowledge Base retrieve and retrieve and generate permissions if agent has KB attached to it
    if kb_id:
        statements.append(
            {
                "Sid": "QueryKB",
                "Effect": "Allow",
                "Action": [
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate"
                ],
                "Resource": [
                    f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_id}"
                ]
            }
        )

    bedrock_agent_bedrock_allow_policy_statement = {
        "Version": "2012-10-17",
        "Statement": statements
    }

    bedrock_policy_json = json.dumps(bedrock_agent_bedrock_allow_policy_statement)
    try:
        agent_bedrock_policy = iam_client.create_policy(
            PolicyName=agent_bedrock_allow_policy_name,
            PolicyDocument=bedrock_policy_json
        )
    except iam_client.exceptions.EntityAlreadyExistsException:
        agent_bedrock_policy = iam_client.get_policy(
            PolicyArn=f"arn:aws:iam::{account_id}:policy/{agent_bedrock_allow_policy_name}"
        )
                    
    # Create IAM Role for the agent and attach IAM policies
    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }

    assume_role_policy_document_json = json.dumps(assume_role_policy_document)
    try:
        agent_role = iam_client.create_role(
            RoleName=agent_role_name,
            AssumeRolePolicyDocument=assume_role_policy_document_json
        )

        # Pause to make sure role is created
        time.sleep(10)
    except iam_client.Client.exceptions.EntityAlreadyExistsException:
        agent_role = iam_client.get_role(
            RoleName=agent_role_name,
        )

    iam_client.attach_role_policy(
        RoleName=agent_role_name,
        PolicyArn=agent_bedrock_policy['Policy']['Arn']
    )
    return agent_role


def delete_agent_roles_and_policies(agent_name, kb_policy_name):
    agent_bedrock_allow_policy_name = f"{agent_name}-ba"
    agent_role_name = f'AmazonBedrockExecutionRoleForAgents_{agent_name}'
    dynamodb_access_policy_name = f'{agent_name}-dynamodb-policy'
    lambda_function_role = f'{agent_name}-lambda-role'

    for policy in [agent_bedrock_allow_policy_name, kb_policy_name]:
        try:
            iam_client.detach_role_policy(
                RoleName=agent_role_name,
                PolicyArn=f'arn:aws:iam::{account_id}:policy/{policy}'
            )
        except Exception as e:
            print(f"Could not detach {policy} from {agent_role_name}")
            print(e)

    for policy in [dynamodb_access_policy_name]:
        try:
            iam_client.detach_role_policy(
                RoleName=lambda_function_role,
                PolicyArn=f'arn:aws:iam::{account_id}:policy/{policy}'
            )
        except Exception as e:
            print(f"Could not detach {policy} from {lambda_function_role}")
            print(e)

    try:
        iam_client.detach_role_policy(
            RoleName=lambda_function_role,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
    except Exception as e:
        print(f"Could not detach AWSLambdaBasicExecutionRole from {lambda_function_role}")
        print(e)

    for role_name in [agent_role_name, lambda_function_role]:
        try:
            iam_client.delete_role(
                RoleName=role_name
            )
        except Exception as e:
            print(f"Could not delete role {role_name}")
            print(e)

    for policy in [agent_bedrock_allow_policy_name, kb_policy_name, dynamodb_access_policy_name]:
        try:
            iam_client.delete_policy(
                PolicyArn=f'arn:aws:iam::{account_id}:policy/{policy}'
            )
        except Exception as e:
            print(f"Could not delete policy {policy}")
            print(e)


def clean_up_resources(
        table_name, lambda_function, lambda_function_name, agent_action_group_response, agent_functions,
        agent_id, kb_id, alias_id
):
    action_group_id = agent_action_group_response['agentActionGroup']['actionGroupId']
    action_group_name = agent_action_group_response['agentActionGroup']['actionGroupName']
    # Delete Agent Action Group, Agent Alias, and Agent
    try:
        bedrock_agent_client.update_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupId= action_group_id,
            actionGroupName=action_group_name,
            actionGroupExecutor={
                'lambda': lambda_function['FunctionArn']
            },
            functionSchema={
                'functions': agent_functions
            },
            actionGroupState='DISABLED',
        )
        bedrock_agent_client.disassociate_agent_knowledge_base(
            agentId=agent_id,
            agentVersion='DRAFT',
            knowledgeBaseId=kb_id
        )
        bedrock_agent_client.delete_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupId=action_group_id
        )
        bedrock_agent_client.delete_agent_alias(
            agentAliasId=alias_id,
            agentId=agent_id
        )
        bedrock_agent_client.delete_agent(agentId=agent_id)
        print(f"Agent {agent_id}, Agent Alias {alias_id}, and Action Group have been deleted.")
    except Exception as e:
        print(f"Error deleting Agent resources: {e}")

    # Delete Lambda function
    try:
        lambda_client.delete_function(FunctionName=lambda_function_name)
        print(f"Lambda function {lambda_function_name} has been deleted.")
    except Exception as e:
        print(f"Error deleting Lambda function {lambda_function_name}: {e}")

    # Delete DynamoDB table
    try:
        dynamodb_client.delete_table(TableName=table_name)
        print(f"Table {table_name} is being deleted...")
        waiter = dynamodb_client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name)
        print(f"Table {table_name} has been deleted.")
    except Exception as e:
        print(f"Error deleting table {table_name}: {e}")