"""
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this
 * software and associated documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
import time
from typing import Optional
import boto3
from botocore.config import Config
import pandas as pd
import matplotlib.pyplot as plt

my_config = Config(
    region_name = 'us-east-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 5,
        'mode': 'standard'
    }
)

bedrock = boto3.client(service_name="bedrock", config=my_config)
bedrock_runtime = boto3.client(service_name="bedrock-runtime",config=my_config)

def get_provisioned_model_id(custom_model_id, provisioned_model_name = 'finetuned_nova'):
    """ This function takes a finetuned/custom model id, creates a provisioned throughput job and returns the provisioned model id """

    provisioned_model_id = bedrock.create_provisioned_model_throughput(
                                        modelUnits=1,
                                        provisionedModelName=provisioned_model_name,
                                        modelId= custom_model_id
                            )

    return provisioned_model_id['provisionedModelArn']
    

def create_nova_messages(prompt):
    """
    Create messages array for Nova models from conversation

    Args:
    conv (object): Conversation object containing messages

    Returns:
    list: List of formatted messages for Nova model
    """
    messages = []
    
    messages.append({
            "role": "user",
            "content": [{"text": prompt}]
        })

    return messages

# API setting constants
API_MAX_RETRY = 16
API_RETRY_SLEEP = 10
API_ERROR_OUTPUT = "$ERROR$"

def chat_completion_aws_bedrock_nova(model, conv, temperature, max_tokens, aws_region="us-east-1"):
    """
    Call AWS Bedrock API for chat completion using Nova models

    Args:
    model (str): Model ID
    conv (object): Conversation object containing messages
    temperature (float): Temperature parameter for response generation
    max_tokens (int): Maximum tokens in response
    api_dict (dict, optional): API configuration dictionary
    aws_region (str, optional): AWS region, defaults to "us-west-2"

    Returns:
    str: Generated response text or error message
    """

    # Configure AWS client 
    bedrock_rt_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region,
        )

    output = API_ERROR_OUTPUT
    
    # Retry logic for API calls
    for _ in range(API_MAX_RETRY):
        try:
            # Create messages from conversation
            messages = create_nova_messages(conv)
            inferenceConfig = {
                "max_new_tokens": max_tokens,
                "temperature": temperature, 
            }

            # Prepare request body
            model_kwargs = {"messages": messages,
                            "inferenceConfig": inferenceConfig}
            body = json.dumps(model_kwargs)

            # Call Bedrock API
            start = time.time()
            
            response = bedrock_rt_client.invoke_model(
                body=body,
                modelId=model,
                accept='application/json',
                contentType='application/json'
            )
            latency_j = time.time() - start

            # Parse response
            response_body = json.loads(response.get('body').read())
            
            res_j_in_tok = response_body[ 'usage' ]['inputTokens']
            
            res_j_out_tok = response_body[ 'usage' ]['outputTokens']   
            
            res_j_tot_tok = response_body[ 'usage' ]['totalTokens']
            
            output = response_body['output']['message']['content'][0]['text']
            break

        except Exception as e:
            print(type(e), e)
            ## Uncomment time.sleep if encounter Bedrock invoke throttling error
            # time.sleep(API_RETRY_SLEEP)

    return output, latency_j, res_j_in_tok, res_j_out_tok, res_j_tot_tok

    
def plot_training_loss(input_file, output_file):
    ''' This function plots training loss using the default model output file 'step_wise_training_metrics.csv' generated from the finetuning job'''
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['step_number'], df['training_loss'], 'b-', linewidth=2)
    
    # Customize the plot
    plt.title('Training Loss vs Step Number', fontsize=14)
    plt.xlabel('Step Number', fontsize=12)
    plt.ylabel('Training Loss', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add some padding to the axes
    plt.margins(x=0.02)
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Plot saved as {output_file}")
