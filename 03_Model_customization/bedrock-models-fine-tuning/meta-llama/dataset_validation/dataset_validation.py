import argparse
import json
from jsonschema import validate, ValidationError

from utils.constants import *
from utils.model_config.models_registry import MODELS
from utils.model_config.input_type import InputType
from utils.exceptions.invalid_row_exception import InvalidRowException
from utils.schema import Schema


def validate_record_count(record_count, dataset_type):
    """
    Validates that the dataset size does not exceed the maximum allowed records.

    Args:
        record_count (int): The number of records in the dataset
        dataset_type (str): Type of dataset ('train' or 'validation')

    Raises:
        Exception: If the record count exceeds MAX_TRAIN_RECORDS for training datasets
                  or MAX_VALIDATION_RECORDS for validation datasets
    """
    if dataset_type == TRAIN and record_count > MAX_TRAIN_RECORDS:
        raise Exception(
            f"The {dataset_type} dataset contains {record_count} records, which exceeds the maximum allowed limit of {MAX_TRAIN_RECORDS}."
        )

    if dataset_type == VALIDATION and record_count > MAX_VALIDATION_RECORDS:
        raise Exception(
            f"The {dataset_type} dataset contains {record_count} records, which exceeds the maximum allowed limit of {MAX_VALIDATION_RECORDS}."
        )


def validate_converse(row, index):
    """
    Validates a single row of conversational data against the Converse schema.

    Checks for:
    - Compliance with Schema.Converse JSON schema
    - Valid message roles
    - Proper image handling (assistants cannot include images)

    Args:
        row (dict): A dictionary containing the conversation data
        index (int): The row index in the dataset for error reporting

    Raises:
        InvalidRowException: If the row fails validation, with details about the error
        ValidationError: If the JSON schema validation fails
    """
    try:
        validate(row, Schema.Converse)
        dialogue = row[Keys.MESSAGES]
        for message in dialogue:
            role = message[Keys.ROLE]
            supported_roles = [member.value for member in list(Roles)]
            if role not in supported_roles:
                raise InvalidRowException(
                    f"The role '{role}' is not supported. Supported roles are: {supported_roles}. ",
                    index,
                )

            for content in message[Keys.CONTENT]:
                if Keys.IMAGE in content:
                    if role == Roles.ASSISTANT:
                        raise InvalidRowException(
                            f"A message with the role '{Roles.ASSISTANT}' should not contain any images. ",
                            index,
                        )
    except ValidationError as e:
        raise InvalidRowException(f"{e}\n\n", index)


def validate_prompt_completion(row, index):
    """
    Validates a single row of prompt-completion data against the PROMPT_COMPLETION schema.

    Args:
        row (dict): A dictionary containing the prompt-completion data
        index (int): The row index in the dataset for error reporting

    Raises:
        InvalidRowException: If the row fails validation, with details about the error
        ValidationError: If the JSON schema validation fails

    """
    try:
        validate(row, Schema.PROMPT_COMPLETION)
    except ValidationError as e:
        raise InvalidRowException(f"{e}\n\n", index)


def main():
    parser = argparse.ArgumentParser(description="A script for dataset validation.")
    parser.add_argument(
        "-d",
        "--dataset-type",
        type=str,
        choices=[TRAIN, VALIDATION],
        required=True,
        help="Specify the dataset type.",
    )
    parser.add_argument(
        "-f",
        "--file-path",
        type=str,
        required=True,
        help="Provide the local path to your JSONL file.",
    )
    parser.add_argument(
        "-m",
        "--model-name",
        type=str,
        choices=list(MODELS.keys()),
        required=True,
        help="Specify the model name.",
    )

    args = parser.parse_args()
    dataset_type, file_path, model_name = (
        args.dataset_type,
        args.file_path,
        args.model_name,
    )

    model = MODELS[model_name]

    with open(file_path, "r") as file:
        dataset = [json.loads(line) for line in file]
        validate_record_count(len(dataset), dataset_type)
        for index, row in enumerate(dataset):
            if model.input_type == InputType.CONVERSE:
                validate_converse(row, index)
            if model.input_type == InputType.PROMPT_COMPLETION:
                validate_prompt_completion(row, index)

    print("Validation complete.")


if __name__ == "__main__":
    main()
