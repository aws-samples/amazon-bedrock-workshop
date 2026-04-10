#!/usr/bin/env python3
"""
Batch Inference Simulator for Amazon Bedrock

This script simulates calling batch inference by:
1. Reading records from a JSONL file
2. Making Bedrock invoke calls for each record
3. Recording responses with corresponding record IDs in an output file

The output format matches the AWS Bedrock Batch Inference output format.
"""

import os
import json
import time
import logging
import argparse
import secrets
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from tqdm import tqdm


# Configure logging
def setup_logging(log_level: str = "INFO") -> Tuple[logging.Logger, logging.Logger]:
    """
    Set up logging with two loggers: one for general logs and one for errors
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Tuple of (main_logger, error_logger)
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Set up main logger
    main_logger = logging.getLogger("batch_inference")
    main_logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    main_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(f"logs/batch_inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    main_logger.addHandler(file_handler)
    
    # Set up error logger
    error_logger = logging.getLogger("batch_inference_errors")
    error_logger.setLevel(logging.ERROR)
    
    # Error file handler
    error_file_handler = logging.FileHandler(f"logs/batch_inference_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    error_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - %(recordId)s'))
    error_logger.addHandler(error_file_handler)
    
    return main_logger, error_logger


class BatchInferenceSimulator:
    """
    Simulates batch inference for Amazon Bedrock models
    """
    
    def __init__(
        self,
        input_file: str,
        output_file: str,
        model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
        region: str = "us-east-1",
        max_retries: int = 5,
        initial_backoff: float = 1.0,
        backoff_factor: float = 2.0,
        jitter: float = 0.1,
        logger: Optional[logging.Logger] = None,
        error_logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the batch inference simulator
        
        Args:
            input_file: Path to input JSONL file
            output_file: Path to output JSONL file
            model_id: Bedrock model ID to use
            region: AWS region
            max_retries: Maximum number of retries for failed requests
            initial_backoff: Initial backoff time in seconds
            backoff_factor: Multiplicative factor for backoff
            jitter: Random jitter factor to add to backoff
            logger: Logger for general logs
            error_logger: Logger for error logs
        """
        self.input_file = input_file
        self.output_file = output_file
        self.model_id = model_id
        self.region = region
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        
        # Set up loggers if not provided
        if logger is None or error_logger is None:
            self.logger, self.error_logger = setup_logging()
        else:
            self.logger = logger
            self.error_logger = error_logger
        
        # Initialize Bedrock client
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region
        )
        
        # Statistics
        self.stats = {
            "total_records": 0,
            "successful_records": 0,
            "failed_records": 0,
            "retried_records": 0,
            "total_tokens": {
                "input": 0,
                "output": 0
            },
            "start_time": None,
            "end_time": None
        }
    
    def read_jsonl(self) -> List[Dict[str, Any]]:
        """
        Read records from JSONL file
        
        Returns:
            List of records as dictionaries
        """
        records = []
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        record = json.loads(line)
                        records.append(record)
            
            self.logger.info(f"Read {len(records)} records from {self.input_file}")
            self.stats["total_records"] = len(records)
            return records
        
        except FileNotFoundError:
            self.logger.error(f"Input file not found: {self.input_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON: {str(e)}")
            raise

    def format_model_input(self, model_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the model input according to model requirements
        
        Args:
            model_input: Raw model input from JSONL file
            
        Returns:
            Formatted model input according to AWS Bedrock invoke request schema
        """
        formatted_input = {}
        
        # Add system message if present
        if "system" in model_input:
            # System should be an array with objects containing text field
            if isinstance(model_input["system"], str):
                # Convert string to proper format
                formatted_input["system"] = [{"text": model_input["system"]}]
            elif isinstance(model_input["system"], list):
                # Ensure each item in the list has the correct format
                formatted_input["system"] = []
                for item in model_input["system"]:
                    if isinstance(item, str):
                        formatted_input["system"].append({"text": item})
                    elif isinstance(item, dict) and "text" in item:
                        formatted_input["system"].append(item)
                    else:
                        # Default case - wrap in proper structure
                        formatted_input["system"].append({"text": str(item)})
            else:
                # Default case - wrap in proper structure
                formatted_input["system"] = [{"text": str(model_input["system"])}]
        
        # Add messages
        if "messages" in model_input:
            # Ensure messages follow the required format
            messages = model_input["messages"]
            if isinstance(messages, list):
                formatted_messages = []
                for msg in messages:
                    if isinstance(msg, dict) and "role" in msg:
                        # Message already has the correct structure
                        if "content" in msg:
                            # Ensure content is properly formatted
                            if not isinstance(msg["content"], list):
                                # Convert content to list of objects with text field
                                msg["content"] = [{"text": str(msg["content"])}]
                            else:
                                # Ensure each content item has the correct format
                                formatted_content = []
                                for content_item in msg["content"]:
                                    if isinstance(content_item, str):
                                        formatted_content.append({"text": content_item})
                                    elif isinstance(content_item, dict):
                                        # Keep as is if it's already a dict
                                        formatted_content.append(content_item)
                                    else:
                                        formatted_content.append({"text": str(content_item)})
                                msg["content"] = formatted_content
                        else:
                            # Add empty content if missing
                            msg["content"] = []
                        formatted_messages.append(msg)
                    else:
                        # Skip invalid messages
                        self.logger.warning(f"Skipping invalid message format: {msg}")
                formatted_input["messages"] = formatted_messages
            else:
                self.logger.warning("Messages must be a list. Skipping messages.")
        
        # Add inference configuration parameters if present
        if "inferenceConfig" in model_input:
            config = model_input["inferenceConfig"]
            formatted_input["inferenceConfig"] = {
                "maxTokens": config.get("maxTokens", 5000),
                "temperature": config.get("temperature", 0.7),
                "topP": config.get("topP", 0.9),
                "topK": config.get("topK", 50),
                "stopSequences": config.get("stopSequences", [])
            }
        
        # Add tool configuration if present
        if "toolConfig" in model_input:
            formatted_input["toolConfig"] = model_input["toolConfig"]
        
        return formatted_input
    
    def invoke_model(self, model_input: Dict[str, Any], record_id: str) -> Dict[str, Any]:
        """
        Invoke Bedrock model with retry logic
        
        Args:
            model_input: Model input parameters
            record_id: Record ID for logging
            
        Returns:
            Model response
        """
        retry_count = 0
        backoff_time = self.initial_backoff
        
        # Format the input for nova lite
        self.logger.debug("model input", model_input)
        formatted_input = self.format_model_input(model_input)
        # print("formatted_input", formatted_input)
        
        while True:
            try:
                self.logger.debug(f"Invoking model for record {record_id}")
                
                # Invoke the model
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(formatted_input)
                )
                
                
                # Parse the response
                response_body = json.loads(response.get('body').read().decode('utf-8'))
                
                # Extract metrics
                input_tokens = response.get('inputTokenCount', 0)
                output_tokens = response.get('outputTokenCount', 0)
                
                # Update token statistics
                self.stats["total_tokens"]["input"] += input_tokens
                self.stats["total_tokens"]["output"] += output_tokens
                
                # Format response in batch inference format matching the desired structure
                formatted_response = {
                    "modelInput": model_input,
                    "modelOutput": response_body,
                    "recordId": record_id
                }
                
                self.stats["successful_records"] += 1
                return formatted_response
                
            except ClientError as e:
                error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
                
                # Don't retry ModelErrorException
                if error_code == "ModelErrorException" and "unexpected error" in str(e):
                    self.logger.warning(f"{error_code} encountered for record {record_id}, not retrying.\n{str(e.response)}")
                    
                    # Format error response
                    error_response = {
                        "recordId": record_id,
                        "errorMessage": str(e),
                        "errorCode": error_code
                    }
                    
                    self.stats["failed_records"] += 1
                    return error_response
                
                # For other errors, continue with retry logic
                retry_count += 1
                self.stats["retried_records"] += 1
                
                if retry_count > self.max_retries:
                    self.logger.error(f"Max retries exceeded for record {record_id}")
                    self.error_logger.error(
                        f"Failed to invoke model after {self.max_retries} retries",
                        extra={"recordId": record_id}
                    )
                    
                    # Format error response
                    error_response = {
                        "recordId": record_id,
                        "errorMessage": str(e),
                        "errorCode": error_code
                    }
                    
                    self.stats["failed_records"] += 1
                    return error_response
            except Exception as e:
                # For general exceptions, continue with retry logic
                retry_count += 1
                self.stats["retried_records"] += 1
                
                if retry_count > self.max_retries:
                    self.logger.error(f"Max retries exceeded for record {record_id}")
                    self.error_logger.error(
                        f"Failed to invoke model after {self.max_retries} retries",
                        extra={"recordId": record_id}
                    )
                    
                    # Format error response
                    error_response = {
                        "recordId": record_id,
                        "errorMessage": str(e),
                        "errorCode": "UnknownError"
                    }
                    
                    self.stats["failed_records"] += 1
                    return error_response
                
                # Calculate backoff with jitter
                # Generate cryptographically secure random number between -jitter and jitter
                rand_int = secrets.randbelow(2**32)  # Using 32 bits for sufficient precision
                normalized = (rand_int / (2**32 - 1)) * 2 - 1  # Convert to [-1, 1]
                jitter_amount = normalized * self.jitter * backoff_time
                sleep_time = backoff_time + jitter_amount
                
                self.logger.warning(
                    f"Error invoking model for record {record_id}. "
                    f"Retry {retry_count}/{self.max_retries} in {sleep_time:.2f}s: {str(e)}"
                )
                
                time.sleep(sleep_time)
                backoff_time *= self.backoff_factor
    
    def process_records(self, records: List[Dict[str, Any]]) -> None:
        """
        Process all records and write results to output file
        
        Args:
            records: List of records to process
        """
        self.stats["start_time"] = datetime.now()
        self.logger.info(f"Starting batch inference with {len(records)} records")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        with open(self.output_file, 'w') as f:
            for record in tqdm(records, desc="Processing records"):
                # Extract record ID and model input
                record_id = record.get("recordId", f"record_{hash(json.dumps(record))}")
                model_input = record.get("modelInput", {})
                
                
                # Invoke model
                result = self.invoke_model(model_input, record_id)
                
                # Write result to output file
                f.write(json.dumps(result) + '\n')
        
        self.stats["end_time"] = datetime.now()
        self.logger.info(f"Batch inference completed. Results written to {self.output_file}")
    
    def print_summary(self) -> None:
        """
        Print summary statistics
        """
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        else:
            duration = 0
        
        self.logger.info("=" * 50)
        self.logger.info("BATCH INFERENCE SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total records processed: {self.stats['total_records']}")
        self.logger.info(f"Successful records: {self.stats['successful_records']}")
        self.logger.info(f"Failed records: {self.stats['failed_records']}")
        self.logger.info(f"Records with retries: {self.stats['retried_records']}")
        self.logger.info(f"Total input tokens: {self.stats['total_tokens']['input']}")
        self.logger.info(f"Total output tokens: {self.stats['total_tokens']['output']}")
        self.logger.info(f"Total duration: {duration:.2f} seconds")
        
        if self.stats['total_records'] > 0 and duration > 0:
            self.logger.info(f"Average processing time per record: {duration / self.stats['total_records']:.2f} seconds")
        
        self.logger.info("=" * 50)
    
    def run(self) -> None:
        """
        Run the batch inference simulation
        """
        try:
            # Read records
            records = self.read_jsonl()
            
            # Process records
            self.process_records(records)
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            self.logger.error(f"Error running batch inference: {str(e)}")
            raise


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Batch Inference Simulator for Amazon Bedrock")
    
    parser.add_argument("--input", "-i", required=True, help="Input JSONL file path")
    parser.add_argument("--output", "-o", required=True, help="Output JSONL file path")
    parser.add_argument("--model", "-m", default="anthropic.claude-3-haiku-20240307-v1:0", 
                        help="Bedrock model ID (default: anthropic.claude-3-haiku-20240307-v1:0)")
    parser.add_argument("--region", "-r", default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum retries for failed requests (default: 5)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level (default: INFO)")
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Set up logging
    main_logger, error_logger = setup_logging(args.log_level)
    
    # Create and run simulator
    simulator = BatchInferenceSimulator(
        input_file=args.input,
        output_file=args.output,
        model_id=args.model,
        region=args.region,
        max_retries=args.max_retries,
        logger=main_logger,
        error_logger=error_logger
    )
    
    simulator.run()


if __name__ == "__main__":
    main()