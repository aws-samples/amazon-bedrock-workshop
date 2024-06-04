import json
import boto3
import time
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, RequestError
import pprint
from retrying import retry

valid_embedding_models = ["cohere.embed-multilingual-v3", "cohere.embed-english-v3", "amazon.titan-embed-text-v1"]
pp = pprint.PrettyPrinter(indent=2)


def interactive_sleep(seconds: int):
    """
    Support functionality to induce an artificial 'sleep' to the code in order to wait for resources to be available
    Args:
        seconds (int): number of seconds to sleep for
    """
    dots = ''
    for i in range(seconds):
        dots += '.'
        print(dots, end='\r')
        time.sleep(1)


class BedrockKnowledgeBase:
    """
    Support class that allows for:
        - creation (or retrieval) of a Knowledge Base for Amazon Bedrock with all its pre-requisites
          (including OSS, IAM roles and Permissions and S3 bucket)
        - Ingestion of data into the Knowledge Base
        - Deletion of all resources created
    """
    def __init__(
            self,
            kb_name,
            kb_description=None,
            data_bucket_name=None,
            embedding_model="amazon.titan-embed-text-v1"
    ):
        """
        Class initializer
        Args:
            kb_name (str): the knowledge base name
            kb_description (str): knowledge base description
            data_bucket_name (str): name of s3 bucket to connect with knowledge base
            embedding_model (str): embedding model to use
        """
        print(f"Creating KB {kb_name}")
        boto3_session = boto3.session.Session()
        self.region_name = boto3_session.region_name
        self.iam_client = boto3_session.client('iam')
        self.account_number = boto3.client('sts').get_caller_identity().get('Account')
        self.suffix = str(self.account_number)[:4]
        self.identity = boto3.client('sts').get_caller_identity()['Arn']
        self.aoss_client = boto3_session.client('opensearchserverless')
        self.s3_client = boto3.client('s3')
        self.bedrock_agent_client = boto3.client('bedrock-agent')
        credentials = boto3.Session().get_credentials()
        self.awsauth = AWSV4SignerAuth(credentials, self.region_name, 'aoss')

        self.kb_name = kb_name
        self.kb_description = kb_description
        if data_bucket_name is not None:
            self.bucket_name = data_bucket_name
        else:
            self.bucket_name = f"{self.kb_name}-{self.suffix}"
        if embedding_model not in valid_embedding_models:
            valid_embeddings_str = str(valid_embedding_models)
            raise ValueError(f"Invalid embedding model. Your embedding model should be one of {valid_embeddings_str}")
        self.embedding_model = embedding_model
        self.encryption_policy_name = f"{self.kb_name}-sp-{self.suffix}"
        self.network_policy_name = f"{self.kb_name}-np-{self.suffix}"
        self.access_policy_name = f'{self.kb_name}-ap-{self.suffix}'
        self.kb_execution_role_name = f'AmazonBedrockExecutionRoleForKnowledgeBase_{self.suffix}'
        self.fm_policy_name = f'AmazonBedrockFoundationModelPolicyForKnowledgeBase_{self.suffix}'
        self.s3_policy_name = f'AmazonBedrockS3PolicyForKnowledgeBase_{self.suffix}'
        self.oss_policy_name = f'AmazonBedrockOSSPolicyForKnowledgeBase_{self.suffix}'

        self.vector_store_name = f'{self.kb_name}-{self.suffix}'
        self.index_name = f"{self.kb_name}-index-{self.suffix}"
        print("========================================================================================")
        print(f"Step 1 - Creating or retrieving {self.bucket_name} S3 bucket for Knowledge Base documents")
        self.create_s3_bucket()
        print("========================================================================================")
        print(f"Step 2 - Creating Knowledge Base Execution Role ({self.kb_execution_role_name}) and Policies")
        self.bedrock_kb_execution_role = self.create_bedrock_kb_execution_role()
        print("========================================================================================")
        print(f"Step 3 - Creating OSS encryption, network and data access policies")
        self.encryption_policy, self.network_policy, self.access_policy = self.create_policies_in_oss()
        print("========================================================================================")
        print(f"Step 4 - Creating OSS Collection (this step takes a couple of minutes to complete)")
        self.host, self.collection, self.collection_id, self.collection_arn = self.create_oss()
        # Build the OpenSearch client
        self.oss_client = OpenSearch(
            hosts=[{'host': self.host, 'port': 443}],
            http_auth=self.awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=300
        )
        print("========================================================================================")
        print(f"Step 5 - Creating OSS Vector Index")
        self.create_vector_index()
        print("========================================================================================")
        print(f"Step 6 - Creating Knowledge Base")
        self.knowledge_base, self.data_source = self.create_knowledge_base()
        print("========================================================================================")

    def create_s3_bucket(self):
        """
        Check if bucket exists, and if not create S3 bucket for knowledge base data source
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f'Bucket {self.bucket_name} already exists - retrieving it!')
        except ClientError as e:
            print(f'Creating bucket {self.bucket_name}')
            if self.region_name == "us-east-1":
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name
                )
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region_name}
                )

    def create_bedrock_kb_execution_role(self):
        """
        Create Knowledge Base Execution IAM Role and its required policies.
        If role and/or policies already exist, retrieve them
        Returns:
            IAM role
        """
        foundation_model_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                    ],
                    "Resource": [
                        f"arn:aws:bedrock:{self.region_name}::foundation-model/{self.embedding_model}"
                    ]
                }
            ]
        }

        s3_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{self.bucket_name}",
                        f"arn:aws:s3:::{self.bucket_name}/*"
                    ],
                    "Condition": {
                        "StringEquals": {
                            "aws:ResourceAccount": f"{self.account_number}"
                        }
                    }
                }
            ]
        }

        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        try:
            # create policies based on the policy documents
            fm_policy = self.iam_client.create_policy(
                PolicyName=self.fm_policy_name,
                PolicyDocument=json.dumps(foundation_model_policy_document),
                Description='Policy for accessing foundation model',
            )
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print(f"{self.fm_policy_name} already exists, retrieving it!")
            fm_policy = self.iam_client.get_policy(
                PolicyArn=f"arn:aws:iam::{self.account_number}:policy/{self.fm_policy_name}"
            )

        try:
            s3_policy = self.iam_client.create_policy(
                PolicyName=self.s3_policy_name,
                PolicyDocument=json.dumps(s3_policy_document),
                Description='Policy for reading documents from s3')
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print(f"{self.s3_policy_name} already exists, retrieving it!")
            s3_policy = self.iam_client.get_policy(
                PolicyArn=f"arn:aws:iam::{self.account_number}:policy/{self.s3_policy_name}"
            )
        # create bedrock execution role
        try:
            bedrock_kb_execution_role = self.iam_client.create_role(
                RoleName=self.kb_execution_role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
                Description='Amazon Bedrock Knowledge Base Execution Role for accessing OSS and S3',
                MaxSessionDuration=3600
            )
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print(f"{self.kb_execution_role_name} already exists, retrieving it!")
            bedrock_kb_execution_role = self.iam_client.get_role(
                RoleName=self.kb_execution_role_name
            )
        # fetch arn of the policies and role created above
        s3_policy_arn = s3_policy["Policy"]["Arn"]
        fm_policy_arn = fm_policy["Policy"]["Arn"]

        # attach policies to Amazon Bedrock execution role
        self.iam_client.attach_role_policy(
            RoleName=bedrock_kb_execution_role["Role"]["RoleName"],
            PolicyArn=fm_policy_arn
        )
        self.iam_client.attach_role_policy(
            RoleName=bedrock_kb_execution_role["Role"]["RoleName"],
            PolicyArn=s3_policy_arn
        )
        return bedrock_kb_execution_role

    def create_oss_policy_attach_bedrock_execution_role(self, collection_id):
        """
        Create OpenSearch Serverless policy and attach it to the Knowledge Base Execution role.
        If policy already exists, attaches it
        """
        # define oss policy document
        oss_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "aoss:APIAccessAll"
                    ],
                    "Resource": [
                        f"arn:aws:aoss:{self.region_name}:{self.account_number}:collection/{collection_id}"
                    ]
                }
            ]
        }

        oss_policy_arn = f"arn:aws:iam::{self.account_number}:policy/{self.oss_policy_name}"
        created = False
        try:
            self.iam_client.create_policy(
                PolicyName=self.oss_policy_name,
                PolicyDocument=json.dumps(oss_policy_document),
                Description='Policy for accessing opensearch serverless',
            )
            created = True
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print(f"Policy {oss_policy_arn} already exists, skipping creation")
        print("Opensearch serverless arn: ", oss_policy_arn)

        self.iam_client.attach_role_policy(
            RoleName=self.bedrock_kb_execution_role["Role"]["RoleName"],
            PolicyArn=oss_policy_arn
        )
        return created

    def create_policies_in_oss(self):
        """
        Create OpenSearch Serverless encryption, network and data access policies.
        If policies already exist, retrieve them
        """
        try:
            encryption_policy = self.aoss_client.create_security_policy(
                name=self.encryption_policy_name,
                policy=json.dumps(
                    {
                        'Rules': [{'Resource': ['collection/' + self.vector_store_name],
                                   'ResourceType': 'collection'}],
                        'AWSOwnedKey': True
                    }),
                type='encryption'
            )
        except self.aoss_client.exceptions.ConflictException:
            print(f"{self.encryption_policy_name} already exists, retrieving it!")
            encryption_policy = self.aoss_client.get_security_policy(
                name=self.encryption_policy_name,
                type='encryption'
            )

        try:
            network_policy = self.aoss_client.create_security_policy(
                name=self.network_policy_name,
                policy=json.dumps(
                    [
                        {'Rules': [{'Resource': ['collection/' + self.vector_store_name],
                                    'ResourceType': 'collection'}],
                         'AllowFromPublic': True}
                    ]),
                type='network'
            )
        except self.aoss_client.exceptions.ConflictException:
            print(f"{self.network_policy_name} already exists, retrieving it!")
            network_policy = self.aoss_client.get_security_policy(
                name=self.network_policy_name,
                type='network'
            )

        try:
            access_policy = self.aoss_client.create_access_policy(
                name=self.access_policy_name,
                policy=json.dumps(
                    [
                        {
                            'Rules': [
                                {
                                    'Resource': ['collection/' + self.vector_store_name],
                                    'Permission': [
                                        'aoss:CreateCollectionItems',
                                        'aoss:DeleteCollectionItems',
                                        'aoss:UpdateCollectionItems',
                                        'aoss:DescribeCollectionItems'],
                                    'ResourceType': 'collection'
                                },
                                {
                                    'Resource': ['index/' + self.vector_store_name + '/*'],
                                    'Permission': [
                                        'aoss:CreateIndex',
                                        'aoss:DeleteIndex',
                                        'aoss:UpdateIndex',
                                        'aoss:DescribeIndex',
                                        'aoss:ReadDocument',
                                        'aoss:WriteDocument'],
                                    'ResourceType': 'index'
                                }],
                            'Principal': [self.identity, self.bedrock_kb_execution_role['Role']['Arn']],
                            'Description': 'Easy data policy'}
                    ]),
                type='data'
            )
        except self.aoss_client.exceptions.ConflictException:
            print(f"{self.access_policy_name} already exists, retrieving it!")
            access_policy = self.aoss_client.get_access_policy(
                name=self.access_policy_name,
                type='data'
            )

        return encryption_policy, network_policy, access_policy

    def create_oss(self):
        """
        Create OpenSearch Serverless Collection. If already existent, retrieve
        """
        try:
            collection = self.aoss_client.create_collection(name=self.vector_store_name, type='VECTORSEARCH')
            collection_id = collection['createCollectionDetail']['id']
            collection_arn = collection['createCollectionDetail']['arn']
        except self.aoss_client.exceptions.ConflictException:
            collection = self.aoss_client.batch_get_collection(names=[self.vector_store_name])['collectionDetails'][0]
            pp.pprint(collection)
            collection_id = collection['id']
            collection_arn = collection['arn']
        pp.pprint(collection)

        # Get the OpenSearch serverless collection URL
        host = collection_id + '.' + self.region_name + '.aoss.amazonaws.com'
        print(host)
        # wait for collection creation
        # This can take couple of minutes to finish
        response = self.aoss_client.batch_get_collection(names=[self.vector_store_name])
        # Periodically check collection status
        while (response['collectionDetails'][0]['status']) == 'CREATING':
            print('Creating collection...')
            interactive_sleep(30)
            response = self.aoss_client.batch_get_collection(names=[self.vector_store_name])
        print('\nCollection successfully created:')
        pp.pprint(response["collectionDetails"])
        # create opensearch serverless access policy and attach it to Bedrock execution role
        try:
            created = self.create_oss_policy_attach_bedrock_execution_role(collection_id)
            if created:
                # It can take up to a minute for data access rules to be enforced
                print("Sleeping for a minute to ensure data access rules have been enforced")
                interactive_sleep(60)
            return host, collection, collection_id, collection_arn
        except Exception as e:
            print("Policy already exists")
            pp.pprint(e)

    def create_vector_index(self):
        """
        Create OpenSearch Serverless vector index. If existent, ignore
        """
        body_json = {
            "settings": {
                "index.knn": "true",
                "number_of_shards": 1,
                "knn.algo_param.ef_search": 512,
                "number_of_replicas": 0,
            },
            "mappings": {
                "properties": {
                    "vector": {
                        "type": "knn_vector",
                        "dimension": 1536,
                        "method": {
                            "name": "hnsw",
                            "engine": "faiss",
                            "space_type": "l2"
                        },
                    },
                    "text": {
                        "type": "text"
                    },
                    "text-metadata": {
                        "type": "text"}
                }
            }
        }

        # Create index
        try:
            response = self.oss_client.indices.create(index=self.index_name, body=json.dumps(body_json))
            print('\nCreating index:')
            pp.pprint(response)

            # index creation can take up to a minute
            interactive_sleep(60)
        except RequestError as e:
            # you can delete the index if its already exists
            # oss_client.indices.delete(index=index_name)
            print(
                f'Error while trying to create the index, with error {e.error}\nyou may unmark the delete above to '
                f'delete, and recreate the index')

    @retry(wait_random_min=1000, wait_random_max=2000, stop_max_attempt_number=7)
    def create_knowledge_base(self):
        """
        Create Knowledge Base and its Data Source. If existent, retrieve
        """
        opensearch_serverless_configuration = {
            "collectionArn": self.collection_arn,
            "vectorIndexName": self.index_name,
            "fieldMapping": {
                "vectorField": "vector",
                "textField": "text",
                "metadataField": "text-metadata"
            }
        }

        # Ingest strategy - How to ingest data from the data source
        chunking_strategy_configuration = {
            "chunkingStrategy": "FIXED_SIZE",
            "fixedSizeChunkingConfiguration": {
                "maxTokens": 512,
                "overlapPercentage": 20
            }
        }

        # The data source to ingest documents from, into the OpenSearch serverless knowledge base index
        s3_configuration = {
            "bucketArn": f"arn:aws:s3:::{self.bucket_name}",
            # "inclusionPrefixes":["*.*"] # you can use this if you want to create a KB using data within s3 prefixes.
        }

        # The embedding model used by Bedrock to embed ingested documents, and realtime prompts
        embedding_model_arn = f"arn:aws:bedrock:{self.region_name}::foundation-model/{self.embedding_model}"
        print(str({
                    "type": "VECTOR",
                    "vectorKnowledgeBaseConfiguration": {
                        "embeddingModelArn": embedding_model_arn
                    }
                }))
        try:
            create_kb_response = self.bedrock_agent_client.create_knowledge_base(
                name=self.kb_name,
                description=self.kb_description,
                roleArn=self.bedrock_kb_execution_role['Role']['Arn'],
                knowledgeBaseConfiguration={
                    "type": "VECTOR",
                    "vectorKnowledgeBaseConfiguration": {
                        "embeddingModelArn": embedding_model_arn
                    }
                },
                storageConfiguration={
                    "type": "OPENSEARCH_SERVERLESS",
                    "opensearchServerlessConfiguration": opensearch_serverless_configuration
                }
            )
            kb = create_kb_response["knowledgeBase"]
            pp.pprint(kb)
        except self.bedrock_agent_client.exceptions.ConflictException:
            kbs = self.bedrock_agent_client.list_knowledge_bases(
                maxResults=100
            )
            kb_id = None
            for kb in kbs['knowledgeBaseSummaries']:
                if kb['name'] == self.kb_name:
                    kb_id = kb['knowledgeBaseId']
            response = self.bedrock_agent_client.get_knowledge_base(knowledgeBaseId=kb_id)
            kb = response['knowledgeBase']
            pp.pprint(kb)

        # Create a DataSource in KnowledgeBase
        try:
            create_ds_response = self.bedrock_agent_client.create_data_source(
                name=self.kb_name,
                description=self.kb_description,
                knowledgeBaseId=kb['knowledgeBaseId'],
                dataDeletionPolicy='RETAIN',
                dataSourceConfiguration={
                    "type": "S3",
                    "s3Configuration": s3_configuration
                },
                vectorIngestionConfiguration={
                    "chunkingConfiguration": chunking_strategy_configuration
                }
            )
            ds = create_ds_response["dataSource"]
            pp.pprint(ds)
        except self.bedrock_agent_client.exceptions.ConflictException:
            ds_id = self.bedrock_agent_client.list_data_sources(
                knowledgeBaseId=kb['knowledgeBaseId'],
                maxResults=100
            )['dataSourceSummaries'][0]['dataSourceId']
            get_ds_response = self.bedrock_agent_client.get_data_source(
                dataSourceId=ds_id,
                knowledgeBaseId=kb['knowledgeBaseId']
            )
            ds = get_ds_response["dataSource"]
            pp.pprint(ds)
        return kb, ds

    def start_ingestion_job(self):
        """
        Start an ingestion job to synchronize data from an S3 bucket to the Knowledge Base
        """
        # Start an ingestion job
        start_job_response = self.bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=self.knowledge_base['knowledgeBaseId'],
            dataSourceId=self.data_source["dataSourceId"]
        )
        job = start_job_response["ingestionJob"]
        pp.pprint(job)
        # Get job
        while job['status'] != 'COMPLETE':
            get_job_response = self.bedrock_agent_client.get_ingestion_job(
                knowledgeBaseId=self.knowledge_base['knowledgeBaseId'],
                dataSourceId=self.data_source["dataSourceId"],
                ingestionJobId=job["ingestionJobId"]
            )
            job = get_job_response["ingestionJob"]
        pp.pprint(job)
        interactive_sleep(40)

    def get_knowledge_base_id(self):
        """
        Get Knowledge Base Id
        """
        pp.pprint(self.knowledge_base["knowledgeBaseId"])
        return self.knowledge_base["knowledgeBaseId"]

    def get_bucket_name(self):
        """
        Get the name of the bucket connected with the Knowledge Base Data Source
        """
        pp.pprint(f"Bucket connected with KB: {self.bucket_name}")
        return self.bucket_name

    def delete_kb(self, delete_s3_bucket=False, delete_iam_roles_and_policies=True):
        """
        Delete the Knowledge Base resources
        Args:
            delete_s3_bucket (bool): boolean to indicate if s3 bucket should also be deleted
            delete_iam_roles_and_policies (bool): boolean to indicate if IAM roles and Policies should also be deleted
        """
        self.bedrock_agent_client.delete_data_source(
            dataSourceId=self.data_source["dataSourceId"],
            knowledgeBaseId=self.knowledge_base['knowledgeBaseId']
        )
        self.bedrock_agent_client.delete_knowledge_base(
            knowledgeBaseId=self.knowledge_base['knowledgeBaseId']
        )
        self.oss_client.indices.delete(index=self.index_name)
        self.aoss_client.delete_collection(id=self.collection_id)
        self.aoss_client.delete_access_policy(
            type="data",
            name=self.access_policy_name
        )
        self.aoss_client.delete_security_policy(
            type="network",
            name=self.network_policy_name
        )
        self.aoss_client.delete_security_policy(
            type="encryption",
            name=self.encryption_policy_name
        )
        if delete_s3_bucket:
            self.delete_s3()
        if delete_iam_roles_and_policies:
            self.delete_iam_roles_and_policies()

    def delete_iam_roles_and_policies(self):
        """
        Delete IAM Roles and policies used by the Knowledge Base
        """
        fm_policy_arn = f"arn:aws:iam::{self.account_number}:policy/{self.fm_policy_name}"
        s3_policy_arn = f"arn:aws:iam::{self.account_number}:policy/{self.s3_policy_name}"
        oss_policy_arn = f"arn:aws:iam::{self.account_number}:policy/{self.oss_policy_name}"
        self.iam_client.detach_role_policy(
            RoleName=self.kb_execution_role_name,
            PolicyArn=s3_policy_arn
        )
        self.iam_client.detach_role_policy(
            RoleName=self.kb_execution_role_name,
            PolicyArn=fm_policy_arn
        )
        self.iam_client.detach_role_policy(
            RoleName=self.kb_execution_role_name,
            PolicyArn=oss_policy_arn
        )
        self.iam_client.delete_role(RoleName=self.kb_execution_role_name)
        self.iam_client.delete_policy(PolicyArn=s3_policy_arn)
        self.iam_client.delete_policy(PolicyArn=fm_policy_arn)
        self.iam_client.delete_policy(PolicyArn=oss_policy_arn)
        return 0

    def delete_s3(self):
        """
        Delete the objects contained in the Knowledge Base S3 bucket.
        Once the bucket is empty, delete the bucket
        """
        objects = self.s3_client.list_objects(Bucket=self.bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
        self.s3_client.delete_bucket(Bucket=self.bucket_name)