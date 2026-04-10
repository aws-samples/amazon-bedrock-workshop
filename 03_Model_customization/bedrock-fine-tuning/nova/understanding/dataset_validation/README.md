## Dataset Validation for Fine-tuning Nova Understanding models
Before you create a fine-tuning job in the Amazon Bedrock console or using API, utilize the provided script to validate your dataset first. This would allow you to identify formatting errors (if any) faster and save costs.

### Usage

Install the last version of python [here](https://www.python.org/downloads/) if you haven't already.

Download the `dataset_validation` folder, `cd` into the root directory, and run the dataset validation script:

```
python3 nova_ft_dataset_validator.py -i <file path> -m <model name>
```

- Model name options
    - micro: Nova Micro Model
    - lite: Nova Lite Model
    - pro: Nova Pro Model

### Features
1. Validates the `JSONL` format
2. Collects all the client errors so
    - This ensures that all the errors are reported once rather than in an iterative manner
3. For each line
    - required keys exists
    - `messages` field is not null
    - given `role` for each message is supported
    - messages with the `assistant` role do not contain an image/video
    - `role` alternates between `user` and `assistant`
    - there are no more than 10 images per line
    - number of samples supported by model type
    - image/video is from the supported formats

### Limitations

This script cannot perform the following validations, as the logic is proprietary to Nova model customization:
    - Image size validation 
    - Video length validation
    - Checking whether the service has access to S3 paths

However, these details can be found in the Nova model customization documentation: https://docs.aws.amazon.com/nova/latest/userguide/customize-fine-tune-prepare.html
