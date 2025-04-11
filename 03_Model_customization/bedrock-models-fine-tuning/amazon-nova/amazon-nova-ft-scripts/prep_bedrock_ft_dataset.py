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
import sys

# Reading JSON file and writing to JSONL
def json_to_jsonl(json_file, jsonl_file):
    with open(json_file, 'r', encoding="utf-8") as f:
        data = json.load(f)
        
    # Write to JSONL file
    with open(jsonl_file, 'w', encoding="utf-8") as f:
        for item in data:
            json_line = json.dumps(item)
            f.write(json_line + '\n')


def prep_ft_jsonl(input_file, 
                  output_file, 
                  prompt_column,
                  completion_column,
                  system_string = None):
    
    """ This function takes in an jsonl file and convert it into the correct format for Nova finetuning. Please refer to https://docs.aws.amazon.com/nova/latest/userguide/customize-fine-tune-examples.html for the latest Amazon Nova FT data format. """
    
    with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
        for line in f_in:
            data = json.loads(line.strip())
            
            ## Construct system, user and assistant prompt 
            prompt = data[prompt_column]
            # print(type(prompt))
            if type(prompt) is list:
                prompt = prompt[0]

            completion = data[completion_column]
            if type(completion) is list:
                completion = completion[0]

            new_data = {}
            new_data["schemaVersion"] = "bedrock-conversation-2024"
            
            if system_string:
                new_data["system"] = [
                    {
                     "text": system_string
                    }
                ]
                
            new_data["messages"] = [
                {
                    "role": "user", 
                     "content": [
                         {
                         "text": prompt
                         }
                     ]
                },
                {
                    "role": "assistant", 
                     "content": [
                         {
                         "text": completion
                         }
                     ]
                }
            ]

            f_out.write(json.dumps(new_data) + "\n")

    print("Conversion completed!")
    
    
## Define the system string, leave it empty if not needed
#sys_prompt =  "You are an AI assistant who is well-versed in AWS knowledge. Please accurately answer the question.\n"

# sys_prompt =  "You are an AI assistant who is well-versed in solving diverse grade school math word problems. Please accurately answer the question.\n"

# sys_prompt =  "You are an AI assistant who is well-versed in answering commonsense qustions. Please accurately answer the question.\n"

sys_prompt = "You are an AI assistant who is well-versed in answering medical questions"




