import json
import os
import sys
import argparse
import boto3
import logging
import numpy as np
from schema import Schema
from constants import *
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from urllib.parse import urlparse
from path_type import PathType
from file_utils import FileUtils
from concurrent.futures import as_completed, ProcessPoolExecutor
from exceptions.distillation_validation_exception import DistillationValidationException

sys.tracebacklimit = -1

log = logging.getLogger(__name__)


# Set up logging configuration
def setup_logging(output_file=None):
    """Set up logging to write INFO and higher to both console and output file."""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Console handler - logs INFO level messages and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    log.addHandler(console_handler)
    log.setLevel(logging.INFO)

    # File handler - logs DEBUG level messages and above
    file_handler = logging.FileHandler(output_file) if output_file else None
    if file_handler:
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))
        log.addHandler(file_handler)
        log.setLevel(logging.DEBUG)


def validate_prompt(json_data, is_invocation_log):
    """Validate a single JSON object against the schema."""
    if is_invocation_log:
        validate_invocation_log(json_data)
    else:
        validate(instance=json_data, schema=Schema.CONVERSE.value)
        validate_alternating_messages(json_data.get(MESSAGES_FIELD, []))


def validate_invocation_log(line):
    """Validates a single JSON object against invocation logs requirements"""
    for required_key in REQUIRED_INVOCATION_LOG_KEYS:
        if required_key not in line:
            raise ValidationError(f"Missing required key '{required_key}' in invocation log.")
    is_invocation_log_entry_supported(line)


def is_invocation_log_entry_supported(entry):
    is_multi_modal = False
    user_messages = [
        u
        for u in entry.get("input", {}).get("inputBodyJson", {}).get("messages", [])
        if u["role"] == "user"
    ]

    is_multi_turn = len(user_messages) > 1
    if is_multi_turn:
        # Multi-turn is not supported in this validation
        raise ValidationError(
            "Multi-turn prompts are not supported for invocation logs."
        )

    # Converse schema only allows one entry in content which has key with name "text".
    # Two possible formats for content are below:
    # 1. "content": [{"text": "Hello"}, {image: "image_content"}]
    # 2. "content": [{"type": "text", "text": "Hello"}, {"type": "image", "image": "image_content"}]
    # Below logic will identify any multi-modal prompt for any use_messages
    for message in user_messages:
        user_messages_content = message.get("content", [])
        # If more than one content then classify as multi-modal including multiple occurrences of "text" type
        if len(user_messages_content) > 1:
            is_multi_modal = True
        # Else check if only content type present is "text"
        elif len(user_messages_content) == 1:
            text_content = user_messages_content[0].get("text")
            if not text_content:
                is_multi_modal = True
    if is_multi_modal:
        raise ValidationError(
            "Multi-modal prompts are not supported for invocation logs."
        )

    has_input_output = "input" in entry and "output" in entry
    if not has_input_output:
        raise ValidationError("Invocation logs must contain both input and output")


def validate_alternating_messages(messages):
    """Validates that messages are alternating between the user and the assistant role,
     beginning with the user role.

    Args:
      messages: A list of objects that contain a "role" field and a "content" field.
    """
    # Validation for alternating roles
    expected_role = USER_ROLE

    for message in messages:
        role = message.get(ROLE_FIELD)

        # Check if the role alternates as expected
        if role != expected_role:
            raise ValidationError(
                error_message=f"Messages must alternate between '{USER_ROLE}' and '{ASSISTANT_ROLE}' roles,"
                              f" starting with '{USER_ROLE}'."
            )

        expected_role = (
            ASSISTANT_ROLE if expected_role == USER_ROLE else USER_ROLE
        )


def validate_file(file_path, is_invocation_logs, is_file_only):
    """Process a single file and validate each JSON object."""
    total_prompts = 0
    total_valid_prompts = 0

    file_extension = GZ_EXTENSION if is_invocation_logs else JSONL_EXTENSION
    if not file_path.endswith(file_extension):
        log.debug(f"Skipping file {file_path} as it does not have a {file_extension} extension.")
        return total_valid_prompts, total_prompts

    log.info(f"Validating file: {file_path}")

    if not FileUtils.validate_file_size(file_path, is_invocation_logs):
        max_size_gb = FileUtils.convert_bytes_to_Gb(MAX_SIZE)
        log.error(f"{file_path} exceeds {max_size_gb:.2f} Gb.")

    with FileUtils.open_file(file_path, is_invocation_logs) as file:
        prompts = file.readlines()
        total_prompts += len(prompts)
        total_valid_prompts += validate_prompts_in_parallel(prompts, file_path, is_invocation_logs)

    if total_valid_prompts < MIN_NUM_PROMPTS and is_file_only:
        error_msg = f"Total number of valid prompts is less than {MIN_NUM_PROMPTS} for file {file_path}"
        raise DistillationValidationException(error_msg)

    return total_valid_prompts, total_prompts


def validate_folder(folder_path, is_invocation_logs):
    """Process files in a folder."""
    if not os.path.exists(folder_path):
        log.info(f"Folder not found: {folder_path}")
        return

    total_size = 0
    total_valid_prompts = 0
    total_prompts = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            if total_size > MAX_SIZE and not is_invocation_logs:
                max_size_gb = FileUtils.convert_bytes_to_Gb(MAX_SIZE)
                error_msg = f"Total size of files exceeds {max_size_gb:.2f} Gb."
                log.error(error_msg)
                raise DistillationValidationException(error_msg)

            is_file_only = False
            total_valid_prompts_for_file, total_prompts_for_file = validate_file(file_path, is_invocation_logs,
                                                                                 is_file_only)
            total_valid_prompts += total_valid_prompts_for_file
            total_prompts += total_prompts_for_file

    log.info(f"{total_valid_prompts} out of {total_prompts} prompts are valid for path: {folder_path}")

    if total_valid_prompts < MIN_NUM_PROMPTS:
        error_msg = f"Total number of valid prompts is less than {MIN_NUM_PROMPTS}."
        log.error(error_msg)
        raise DistillationValidationException(error_msg)


def process_s3_path(path, is_invocation_logs):
    """Process files in an S3 path."""
    s3_client = boto3.client('s3')
    bucket_name, prefix = parse_s3_path(path)

    files = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if 'Contents' not in files:
        log.info(f"No files found in the S3 path {path}")
        return

    total_size = 0
    total_prompts = 0
    total_valid_prompts = 0

    for file in files['Contents']:
        file_key = file['Key']
        file_extension = GZ_EXTENSION if is_invocation_logs else JSONL_EXTENSION
        file_path = f"s3://{bucket_name}/{file_key}"

        if not file_key.endswith(file_extension):
            log.debug(f"Skipping file {file_path} as it does not have a {file_extension} extension.")
            continue

        file_size = file['Size']
        total_size += file_size
        if total_size > MAX_SIZE and not is_invocation_logs:
            max_size_gb = FileUtils.convert_bytes_to_Gb(MAX_SIZE)
            error_msg = f"Total size of files exceeds {max_size_gb} Gb."
            log.error(error_msg)
            raise DistillationValidationException(error_msg)

        log.info(f"Validating file from S3: {file_path}")
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        lines = file_obj['Body'].readlines()
        total_prompts += len(lines)
        total_valid_prompts += validate_prompts_in_parallel(lines, file_path, is_invocation_logs)

    is_file_path = path.endswith(GZ_EXTENSION) or path.endswith(JSONL_EXTENSION)
    if not is_file_path:
        log.info(f"{total_valid_prompts} out of {total_prompts} prompts are valid for S3 path: {path}")

    if total_valid_prompts < MIN_NUM_PROMPTS:
        error_msg = f"Total number of valid prompts is less than {MIN_NUM_PROMPTS}."
        log.error(f"Total number of valid prompts is less than {MIN_NUM_PROMPTS}.")
        raise DistillationValidationException(error_msg)


def validate_prompts_in_parallel(prompts, file_path, is_invocation_logs):
    """Validates the given prompts in parallel"""
    max_workers = os.process_cpu_count()

    # Create a thread pool to process chunks in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        chunks = np.array_split(np.array(prompts), max_workers)
        starting_line = 1
        for lines in chunks:
            futures.append(executor.submit(validate_lines, lines, starting_line, file_path, is_invocation_logs))
            starting_line += lines.size

        # Wait for all tasks to complete
        total_valid_prompts = 0
        for future in as_completed(futures):
            num_valid_prompts, errors = future.result()
            total_valid_prompts += num_valid_prompts
            if errors:
                for error in errors:
                    log.debug(error)

        if total_valid_prompts < len(prompts):
            log.info("Prompts with invalid format detected. Specify an output file for more details."
                     " Visit the following link for correct format."
                     " \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/prequisites-model-distillation.html ")

        log.info(f"{total_valid_prompts} out of {len(prompts)} prompts are valid for file: {file_path}")
        return total_valid_prompts


def validate_lines(lines, starting_line, file_path, is_invocation_logs):
    """Process a chunk of prompts."""
    line_num = starting_line
    num_valid_prompts = 0
    errors = []
    for line in lines:
        try:
            json_data = json.loads(line)
            validate_prompt(json_data, is_invocation_logs)
            num_valid_prompts += 1
        except json.JSONDecodeError:
            errors.append(f"Invalid JSON. This occurred on line {line_num} for file {file_path}")
        except ValidationError as e:
            errors.append(f"Validation error: {e.message}. This occurred on line {line_num} for file {file_path}")
        line_num += 1
    return num_valid_prompts, errors


def parse_s3_path(path):
    """Parse an S3 URL into bucket name and object key."""
    parsed_url = urlparse(path)
    bucket_name = parsed_url.netloc
    key = parsed_url.path.lstrip('/')
    return bucket_name, key


def get_path_type(path):
    """Determine if the given path is a file, folder, or S3 path."""
    if path.startswith(S3_PREFIX):
        return PathType.S3
    elif os.path.isfile(path):
        return PathType.FILE
    elif os.path.isdir(path):
        return PathType.FOLDER
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description="Validate files for model distillation.")
    parser.add_argument(
        "-p", "--path",
        type=str,
        required=True,
        help="File, folder, or S3 path."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=False,
        help="Output file for more detailed validation error messages (optional)."
    )
    parser.add_argument(
        "-i", "--invocation_logs",
        action="store_true",
        help="Flag to indicate that the files are invocation log files."
    )

    args = parser.parse_args()
    path = args.path
    output_file = args.output
    is_invocation_logs = args.invocation_logs

    # Set up logging to console and to file if specified
    setup_logging(output_file)

    # Determine whether the provided path is a file or folder
    path_type = get_path_type(path)

    log.debug(f"Given input path: {path}")

    if path_type == PathType.FILE:
        is_file_only = True
        validate_file(path, is_invocation_logs, is_file_only)
    elif path_type == PathType.FOLDER:
        validate_folder(path, is_invocation_logs)
    elif path_type == PathType.S3:
        process_s3_path(path, is_invocation_logs)
    else:
        log.info(f"The provided path '{path}' is not a valid file or folder or S3 path.")
        sys.exit(1)

    log.info("Validation complete.")


if __name__ == "__main__":
    main()
