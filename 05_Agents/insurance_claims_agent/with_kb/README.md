# Lab 5.3 - Integrating Knowledge Bases to your Agents

## Overview
In this lab we will demonstrate how to integrate a [Knowledge Base for Amazon Bedrock](https://aws.amazon.com/bedrock/knowledge-bases/) to your Agents via [AWS Boto3 SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

Knowledge bases for Amazon Bedrock allows you to aggregate 
data sources into a repository of information. With knowledge bases, you 
can easily build an application that takes advantage of retrieval 
augmented generation (RAG), a technique in which the retrieval of 
information from data sources augments the generation of model responses. 
Once set up, you can take advantage of a knowledge base in the following 
ways.

Configure your RAG application to use the RetrieveAndGenerate API to query 
your knowledge base and generate responses from the information it 
retrieves.

Associate your knowledge base with an agent (for more information, see 
Agents for Amazon Bedrock) to add RAG capability to the agent by helping 
it reason through the steps it can take to help end users.

Create a custom orchestration flow in your application by using the 
Retrieve API to retrieve information directly from the knowledge base.

In this lab you will:

1. Create an [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) vector database 
2. Create an [index](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector-search.html) for your vector database to perform vector search
3. Create your knowledge base and its required IAM role
4. Create a data source from s3 files and associate it to your knowledge base
5. Ingest the data from S3 to your knowledge base
6. Associate your knowledge base to your agent
7. Invoke your agent with a query that requires knowledge base access

This folder contains the API schema, AWS Lambda function and notebook, 
`create_and_invoke_agent_with_kb` with the code for the use case.

You can find detailed instructions on the [Bedrock Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/en-US/90-agents).