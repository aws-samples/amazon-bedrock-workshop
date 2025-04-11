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

"""Generate answers with Bedrock models

Usage:
python3 gen_answer.py --model aws_nova_lite_v1 --question-begin 0 --question-end 100 

Reference: 
https://github.com/lm-sys/FastChat/blob/main/fastchat/llm_judge/gen_model_answer.py
"""
import argparse
import json
import os
import time
import concurrent.futures
import shortuuid
import tqdm
from helper import chat_completion_aws_bedrock_nova

# Provide provisioned model ids once hosted customized Nova models through provisioned throughput

AWS_BEDROCK_NOVA_MODEL_LIST = {
    "aws_nova_lite_v1": "amazon.nova-lite-v1:0",
    "aws_nova_pro_v1": "amazon.nova-pro-v1:0",
    "aws_nova_micro_v1": "amazon.nova-micro-v1:0",
    "ft_model_name": # replace with your provisioned model id
}


def get_answer(
    question: dict, model: str, num_choices: int, max_tokens: int, temperature: float, answer_file: str
):

    choices = []

    for i in range(num_choices):
        conv = ""
        turns = []
        
        # Calculate latency and cost
        res_in_tok = 0
        res_out_tok = 0
        res_tot_tok = 0
        res_latency = 0
        
        for j in range(len(question["turns"])):
            conv += question["turns"][j]
            
            if model in AWS_BEDROCK_NOVA_MODEL_LIST:
                model_id = AWS_BEDROCK_NOVA_MODEL_LIST[model]
                output, latency_j, res_j_in_tok, res_j_out_tok, res_j_tot_tok = chat_completion_aws_bedrock_nova(model_id, conv, temperature+0.01, max_tokens, aws_region="us-east-1")
                
                # total the latencies ad tokens
                res_latency += latency_j
                res_in_tok += res_j_in_tok
                res_out_tok += res_j_out_tok
                res_tot_tok += res_j_tot_tok
                
            turns.append(output)

        choices.append({"index": i, "turns": turns})

    # Dump answers
    ans = {
        "question_id": question["question_id"],
        "answer_id": shortuuid.uuid(),
        "model_id": model,
        'use_rag': False,
        "choices": choices,
        "tstamp": time.time(),
        'latency': res_latency,
        'in_token': res_in_tok,
        'out_token': res_out_tok,
        'total_token': res_tot_tok,
    }

    os.makedirs(os.path.dirname(answer_file), exist_ok=True)
    with open(answer_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ans) + "\n")


if __name__ == "__main__":

    ## Load questions 
    question_file = f"dataset/test_set/question_short.jsonl"

    questions = []
    with open(question_file, "r", encoding="utf-8") as ques_file:
        for line in ques_file:
            if line:
                questions.append(json.loads(line))

    ## Run inference and save model output
    model = 'aws_nova_lite_v1'
    num_choices = 1 
    max_tokens = 1024
    temperature = 0.2
    
    answer_file = f"dataset/model_answer/{model}.jsonl"
    print(f"Output to {answer_file}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

        futures = []
        for question in questions:
            future = executor.submit(
                get_answer,
                question,
                model,
                num_choices,
                max_tokens,
                temperature,
                answer_file,
            )
            futures.append(future)

        for future in tqdm.tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            future.result()
        
