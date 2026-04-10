## Dataset Validation for Model Distillation
Before you create a model distillation job in the Amazon Bedrock console, utilize the provided script to validate your dataset first. This would allow you to identify formatting errors (if any) faster and save costs.
More details about the accepted format for prompts and invocation logs can be found here: https://docs.aws.amazon.com/bedrock/latest/userguide/prequisites-model-distillation.html
### Prompt Format
Below are 2 examples of valid prompts for model distillation.
```
{
    "schemaVersion": "bedrock-conversation-2024",
    "system": [
        {
            "text": "A chat between a curious User and an artificial intelligence Bot. The Bot gives helpful, detailed, and polite answers to the User's questions."
        }
    ],    
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": "why is the sky blue"
                }
            ]
        },
        {
            "role": "assistant"
            "content": [
               {
                   "text": "The sky is blue because molecules in the air scatter blue light from the Sun more than other colors."
               }
            ]
        }
    ]
}
```
`System` is optional, and so is the `assistant` content within `messages`. An example of a valid prompt without those is shown below
```
{
    "schemaVersion": "bedrock-conversation-2024",    
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": "why is the sky blue"
                }
            ]
        }
    ]
}

```
### Dataset constraints
- Dataset size must be less than 1 Gb
- Dataset must contain at least 100 valid prompts. Invalid prompts that do not conform to the format will be dropped.
### Invocation Logs Format
```
{
  "schemaType": "ModelInvocationLog",
  "schemaVersion": "1.0",
  "timestamp": "<timestamp>",
  "accountId": "<accountId>",
  "identity": {
    "arn": "<arn>"
  },
  "region": "<region>",
  "requestId": "<requestId>",
  "operation": "InvokeModel",
  "modelId": "<modelId>",
  "input": {
    "inputContentType": "application/json",
    "inputBodyJson": {
      "prompt": "<|begin_of_text|><|start_header_id|>user<|end_header_id|>What is the capital of Sudan?<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
      "temperature": 0.1,
      "max_gen_len": 2048,
      "top_p": 0.9
    },
    "inputTokenCount": 15
  },
  "output": {
    "outputContentType": "application/json",
    "outputBodyJson": {
      "generation": "\n\nThe capital of Sudan is Khartoum.",
      "prompt_token_count": 15,
      "generation_token_count": 12,
      "stop_reason": "stop"
    },
    "outputTokenCount": 12
  },
  "requestMetadata": {
    "<key>": "<value>",
    "<key>": "<value>"
    ...
  }
}
```
### Invocation Logs Constraints
- If a filter is provided and the invocation log does not match the filter, the record will be dropped
- Minimum of 100 invocation logs that match the given filter
### Usage

Install the last version of python [here](https://www.python.org/downloads/) if you haven't already.

Download the `dataset-validation` folder, `cd` into the root directory, and run the dataset validation script:

```
pip install -r requirements.txt -U
python3 dataset_validator.py -p <path>

# Specifying an output file for detailed validation logs
python3 dataset_validator.py -p <path> -o <log file>

# Specifying the given path is for invocation logs
python3 dataset_validator.py -p <path> -i
```

- Path options
    - file: /path/to/file.jsonl or /path/to/file.gz (with invocation logs flag)
    - folder: /path/to/folder
    - S3: s3://bucket/key

### Features
1. Validates prompts in the given path satisfy the `bedrock-conversation-2024` format
2. If an output file is given, validation errors for each prompt would be logged in the output file
3. If the invocation logs flag is present, the validator will validate for the invocation logs use-case instead

### Limitations

This script currently does not support the following features:
- Invocation logs validation with filters
- Validating prompts do not contain invalid tags
