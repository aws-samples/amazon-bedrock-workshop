## Dataset Validation for Fine-tuning Meta Llama Models
Before you create a fine-tuning job in the Amazon Bedrock console, utilize the provided script to validate your dataset first, which would allow you to identify formatting errors (if any) faster and save costs.

### Usage

Install the latest version of python [here](https://www.python.org/downloads/) if you haven't already.

Download the `dataset_validation` folder, `cd` into the root directory, then run the following command to install the necessary dependencies:
```
python3 -m venv .venv && source .venv/bin/activate && pip install jsonschema
```
Then, use the following command to validate your dataset:
```
python3 dataset_validation.py -d <dataset type> -f <file path> -m <model name>
```

1. Dataset type options
    - train
    - validation

2. Model name options
    - llama3-1-8b
    - llama3-1-70b
    - llama3-2-1b
    - llama3-2-3b
    - llama3-2-11b
    - llama3-2-90b


### Features
1. Validates the `JSONL` format
2. Checks that the `train` dataset has $\leq$ 10k rows and `validation` dataset has $\leq$ 1k rows
    - Each conversation should only take up 1 row
3. For each row
    - Validates conversation format for models using conversational input
        - Checks if roles are supported
        - Prevents assistant messages from containing images
    - Validates prompt-completion format for models using prompt-completion input
    

### Limitations Not Validated by the Script
1. Images
    - Size $\leq$ 10 MB
    - Format must be one of `png`, `jpeg`, `gif`, `webp`
    - Dimensions $\leq$ 8192 x 8192 pixels
2. Input token length of each dataset row $\leq$ 16K (10K for Llama 3.2 90B model)