import os
import json
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError, model_validator

# Constants
MIN_LINES = 32
MAX_TRAINING_LINES = 10000
MAX_VALIDATION_LINES = 1000
MAX_TOTAL_LINES = 10000
MAX_TOKENS = 32000
CHARS_PER_TOKEN = 3 
MAX_TRAINING_SIZE_GB = 10
MAX_VALIDATION_SIZE_GB = 1
RESERVED_KEYWORDS = ["\nHuman:", "\nAssistant:"]

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str

class DataEntry(BaseModel):
    system: Optional[str] = None
    messages: List[Message] = Field(..., min_items=2)
        
    @model_validator(mode='after')
    def check_message_structure(self) -> 'DataEntry':
        messages = self.messages
        if not messages:
            raise ValueError("Messages list cannot be empty")
            
        if messages[0].role != 'user' or messages[-1].role != 'assistant':
            raise ValueError("Messages must start with user and end with assistant")
            
        for i in range(len(messages) - 1):
            if messages[i].role == messages[i+1].role:
                raise ValueError("Messages must alternate between user and assistant")
                
        for keyword in RESERVED_KEYWORDS:
            if self.system and keyword in self.system:
                raise ValueError(f"Reserved keyword '{keyword}' found in system prompt")
            for message in messages:
                if keyword in message.content:
                    raise ValueError(f"Reserved keyword '{keyword}' found in message content")
                
        return self

def validate_data_entry(entry: dict) -> Tuple[bool, List[str]]:
    try:
        DataEntry(**entry)
        return True, []
    except ValidationError as e:
        errors = []
        for error in e.errors():
            if error["type"] == "value_error":
                errors.append(f"Structure error: {error['msg']}")
            else:
                location = ".".join(str(loc) for loc in error["loc"])
                errors.append(f"Field '{location}': {error['msg']}")
        return False, errors     

def count_tokens(text: str) -> int:
    """Estimate the number of tokens in a given text."""
    return len(text) // CHARS_PER_TOKEN

def validate_file(file_path: str, is_training: bool = True) -> Tuple[List[str], int]:
    """Validate a JSONL file"""
    errors = []
    line_count = 0
    
    file_size_gb = os.path.getsize(file_path)/(1024*1024*1024)
    if is_training:
        if file_size_gb > MAX_TRAINING_SIZE_GB:
            errors.append(f"Training file size ({file_size_gb:.2f} GB) exceeds the maximum allowed size ({MAX_TRAINING_SIZE_GB} GB)")
    else:
        if file_size_gb > MAX_VALIDATION_SIZE_GB:
            errors.append(f"Validation file size ({file_size_gb:.2f} GB) exceeds the maximum allowed size ({MAX_VALIDATION_SIZE_GB} GB)")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line_count += 1
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"Line {line_num}: Invalid JSON")
                continue
            is_valid, entry_errors = validate_data_entry(data)
            if not is_valid:
                for error in entry_errors:
                    errors.append(f"Line {line_num}: {error}")
            total_tokens = (count_tokens(data.get('system', '')) + 
                        sum(count_tokens(msg['content']) for msg in data['messages']))
            if total_tokens > MAX_TOKENS:
                errors.append(f"Line {line_num}: Exceeds maximum token count ({total_tokens} > {MAX_TOKENS})")

    if is_training:
        if line_count > MAX_TRAINING_LINES or line_count < MIN_LINES:
            errors.append(f"File has {line_count} lines. Training data should have between {MIN_LINES} and {MAX_TRAINING_LINES} lines.")
    else:
        if line_count > MAX_VALIDATION_LINES or line_count < MIN_LINES:
            errors.append(f"File has {line_count} lines. Validation data should have between {MIN_LINES} and {MAX_VALIDATION_LINES} lines.")

    return errors, line_count

def print_validation_results(file_path: str, errors: List[str]) -> None:
    """Print the validation results."""
    if errors:
        print(f"Validation FAILED for {file_path}. Errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"Validation SUCCESSFUL for {file_path}.")

def validate_data(training_path: str, validation_path: Optional[str] = None) -> None:
    """Validate training data and optionally validation data."""
    print("Validating Training Data...")
    training_errors, training_lines = validate_file(training_path)
    print_validation_results(training_path, training_errors)
    
    total_lines = training_lines
    if validation_path:
        print("\nValidating Validation Data...")
        validation_errors, validation_lines = validate_file(validation_path)
        print_validation_results(validation_path, validation_errors)
        total_lines = total_lines + validation_lines
        
    if total_lines > MAX_TOTAL_LINES:
        print(f"\nError: Total number of lines ({total_lines}) exceeds the maximum allowed ({MAX_TOTAL_LINES}.")
    elif not training_errors and (not validation_path or not validation_errors):
        print("\nAll data passed validation!")
    else:
        print("\nPlease correct the errors and run the validation again.")