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

import boto3 
from botocore.config import Config
import sys


my_config = Config(
    region_name = 'us-east-1', 
    signature_version = 'v4',
    retries = {
        'max_attempts': 5,
        'mode': 'standard'
    })

bedrock = boto3.client(service_name="bedrock", config=my_config)

## Specify IAM roles

# US EAST 1
role_name = "genaiic-bedrock-ft-useast1-role"
role_arn = "arn:aws:iam::613305653031:role/service-role/genaiic-bedrock-ft-useast1-role" 


input_s3_uri = sys.argv[1] 
output_s3_uri = sys.argv[2] 

 
job_name = sys.argv[3] 
model_name = job_name 


response_ft = bedrock.create_model_customization_job(
    jobName = job_name,
    customModelName = model_name,
    roleArn = role_arn,
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0:300k", 
    trainingDataConfig={"s3Uri": input_s3_uri},
    outputDataConfig={"s3Uri": output_s3_uri},
    hyperParameters={'epochCount': '1', 
                     'learningRate': '1e-6', 
                     'batchSize': '1'}
)

jobArn = response_ft.get('jobArn')
status = bedrock.get_model_customization_job(jobIdentifier=jobArn)["status"]
print(f'Job status: {status}')


