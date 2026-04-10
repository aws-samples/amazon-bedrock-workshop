# Data Validation Tool for Claude-3 Haiku Fine-Tuning Training and Validation Datasets

This tool provides a simple and efficient way to validate JSONL format data for Claude-3 Haiku Fine-Tuning training and validation datasets. It supports both local files and data stored in Amazon S3.

## Contents

1. `data_validator.py`: The core Python script containing validation logic

2. `Claude-3 Haiku Fine-Tuning Training and Validation Data Validator.ipynb`: A Jupyter notebook interface for easy use of the validation tool

## Features

1. Validates `JSONL` format for training and validation datasets

2. Supports both local files and S3 stored data

3. Checks for file size limits:
   - Training data: Max 10GB
   - Validation data: Max 1GB
   
4. Validates line counts:
   - Training data: 32 to 10,000 lines
   - Validation data: 32 to 1,000 lines
   - Total (training + validation): Max 10,000 lines
   
5. Validates data structure and content for each entry

6. Estimates and checks token counts per entry: Max 32,000 tokens

7. Checks for Anthropic's reserved keywords in prompts:
   - Ensures "\nHuman:" and "\nAssistant:" do not appear in prompts
   - Note: Variations without colons (e.g., "\nHuman" or "\nAssistant") are allowed