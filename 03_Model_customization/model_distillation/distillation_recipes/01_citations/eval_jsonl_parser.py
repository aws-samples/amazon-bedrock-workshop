import boto3
import pandas as pd
import json
import re
from typing import List, Dict, Any, Optional
# import numpy as np
import time

def parse_jsonl_to_df(file_path: str) -> pd.DataFrame:
    """
    Parse a JSONL file containing conversation data into a pandas DataFrame.
    
    Args:
        file_path (str): Path to the JSONL file
        
    Returns:
        pd.DataFrame: DataFrame containing the parsed data with appropriate data types
    """
    # Read the JSONL file line by line
    records = []
    with open(file_path, 'r') as f:
        line_no = 1
        for line in f:
            record = json.loads(line.strip())
            # Process each conversation turn
            for turn in record.get('conversationTurns', []):
                # Validate citations for this turn
                validation_results = validate_citation_coverage(turn, model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0")
                
                # Extract relevant fields
                processed_record = {
                    'prompt': turn.get('inputRecord', {}).get('prompt', {}).get('content', [{}])[0].get('text', ''),
                    'reference_response': turn.get('inputRecord', {}).get('referenceResponses', [{}])[0].get('content', [{}])[0].get('text', ''),
                    'model_identifier': turn.get('output', {}).get('modelIdentifier', ''),
                    'kb_identifier': turn.get('output', {}).get('knowledgeBaseIdentifier', ''),
                    'model_output': turn.get('output', {}).get('text', ''),
                }
                
                # Extract metrics
                metrics = {}
                for result in turn.get('results', []):
                    metric_name = result.get('metricName', '').replace('Builtin.', '')
                    metric_value = result.get('result')
                    metrics[f'metric_{metric_name.lower()}'] = metric_value
                
                processed_record.update(metrics)
                
                # Add citation validation results
                citation_fields = {
                    'citation_validation_rate': validation_results.get('validation_rate', 0.0),
                    'total_citations': validation_results.get('total_citations', 0),
                    'valid_citations': validation_results.get('valid_citations', 0),
                    'all_citations_valid': validation_results.get('all_citations_valid', False),
                    'citation_coverage': validation_results.get('citation_coverage', 0)
                }
                processed_record.update(citation_fields)
                
                records.append(processed_record)
                print(f"Processed line {str(line_no)}")
                line_no+=1
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Set data types
    dtype_mapping = {
        'prompt': 'string',
        'reference_response': 'string',
        'model_identifier': 'string',
        'kb_identifier': 'string',
        'model_output': 'string',
        'citation_validation_rate': 'float64',
        'total_citations': 'int64',
        'valid_citations': 'int64',
        'all_citations_valid': 'bool',
        'citation_coverage': 'int64'
    }
    
    # Add metric columns to dtype mapping
    metric_columns = [col for col in df.columns if col.startswith('metric_')]
    for col in metric_columns:
        dtype_mapping[col] = 'float64'
    
    # Apply data types
    for col, dtype in dtype_mapping.items():
        if col in df.columns:
            if dtype == 'float64':
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                df[col] = df[col].astype(dtype)
    
    return df

def aggregate_metrics_by_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate metric columns by model_identifier, computing the mean for each metric.
    
    Args:
        df (pd.DataFrame): DataFrame containing the parsed data from parse_jsonl_to_df
        
    Returns:
        pd.DataFrame: DataFrame with metrics aggregated by model_identifier
    """
    # add 1 to the citation coverage column given coverage_map is zero-based, and it should be a scale from 1 to 5
    df['citation_coverage'] = df['citation_coverage'] + 1
    
    # Identify metric columns
    filter_columns = ['metric_correctness', 'metric_completeness',
       'metric_helpfulness', 'metric_logicalcoherence', 'metric_faithfulness',
       'all_citations_valid', 'citation_coverage']
    metric_columns = [col for col in df.columns if col in filter_columns]

    
    # Group by model_identifier and calculate mean of metrics
    aggregated_df = df.groupby('model_identifier')[metric_columns].agg({
        col: 'mean' for col in metric_columns
    }).reset_index()
    
    # Round metric values to 4 decimal places for readability
    for col in metric_columns:
        aggregated_df[col] = aggregated_df[col].round(4)
    
    return aggregated_df

def validate_citation_coverage(
    turn: Dict[str, Any],
    xml_pattern: Optional[str] = None,
    model_id: Optional[str] = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
) -> Dict[str, Any]:
    """
    Parse model output XML from a conversation turn to extract citations
    and validate if they exist in retrieved passages. Also evaluates citation coverage
    using a Claude model.
    
    Args:
        turn (Dict[str, Any]): The conversation turn containing model output and retrieved passages
        xml_pattern (Optional[str]): Regex pattern to extract citation text from XML, defaults to answer_part tags
        model_id (Optional[str]): The Claude model ID to use for citation coverage evaluation
        
    Returns:
        Dict[str, Any]: Dictionary containing validation results including:
                       - citation_validation_rate: Ratio of valid citations
                       - total_citations: Number of citations found
                       - valid_citations: Number of valid citations
                       - all_citations_valid: Boolean indicating if all citations are valid
                       - citation_coverage: Numeric score (0-4) indicating citation coverage
    """
    # Extract model output and retrieved passages from the turn
    model_output = turn.get('output', {}).get('text', '')
    retrieved_passages = turn.get('output', {}).get('retrievedPassages', {})
    
    # Compile the regex pattern
    if not xml_pattern:
        xml_pattern = r'<answer_part>\n(.*?)\n<\/answer_part>'
    answers_pattern = re.compile(xml_pattern, re.DOTALL)
    
    # Extract all matches from the model output
    answers = answers_pattern.findall(model_output)
    
    # Extract text from retrieved passages
    passage_texts = []
    for passage in retrieved_passages.get('retrievalResults', []):
        if passage.get('content') and passage['content'].get('text'):
            passage_texts.append(passage['content']['text'])
    
    # Validate each citation
    validation_results = {
        'citations': [],
        'all_citations_valid': True,
        'total_citations': len(answers),
        'valid_citations': 0,
        'model_output': model_output
    }
    
    for answer in answers:
        citation_found = False
        
        # Check if the citation text exists in any of the retrieved passages
        answer_text_pattern = re.compile(r'<text>\n(.*?)\n</text>', re.DOTALL)
        sources_pattern = re.compile(r'<source>(.*?)</source>', re.DOTALL)

        citation_texts = answer_text_pattern.findall(answer)
        sources_texts = sources_pattern.findall(answer)

        for passage_text in passage_texts:
            for cited_text in citation_texts:
                if cited_text in passage_text:
                    citation_found = True
                    break
        
        # Add result to the validation results
        validation_results['citations'].append({
            'text': answer,
            'found_in_passages': citation_found
        })
        
        # Update validation stats
        if citation_found:
            validation_results['valid_citations'] += 1
        else:
            validation_results['all_citations_valid'] = False

        coverage_map = {
            "none is present in context": 0,
            "some is present in context": 1,
            "approximately half is present in context": 2,
            "most is present in context": 3,
            "all is present in context": 4
        }
        related_passages = "\n".join(sources_texts)
        candidate_response = "\n".join(citation_texts)
        if 'I could not find an exact answer to the question' in candidate_response and len(sources_texts) < 1:
            print("justified non answer, marking 'all is present in context'")
            validation_results['citation_coverage'] = coverage_map["all is present in context"] # this means the answer is justified - no llm call needed
        else:
            # print(f"sending prompt with the following:\nrelated passages: {related_passages}\ncandidate response: {candidate_response}\n\n")
            # Call send_prompt_to_claude with the validation results
            prompt = f"""
                For a given task, you are provided with a set of related passages, and a candidate answer.

                Does the candidate answer contain information that is not included in the passages, or that cannot be easily inferred from them via common sense knowledge?

                Related Passages:{related_passages}

                Candidate Response: {candidate_response}

                Evaluate how much of the information in the answer is contained in the available context passages (or can be inferred from them via common sense knowledge). Ignore any other mistakes, such as missing information, untruthful answers, grammar issues etc; only evaluate whether the information in the candidate answer is in the related passages.


                Firstly explain your response, followed by your final answer. You should follow the format 
                Explanation: [Explanation], Answer: [Answer], 
                where '[Answer]' can be one of the following:
                ```
                none is present in context
                some is present in context
                approximately half is present in context
                most is present in the context
                all is present in the context
                ```
                """
            eval_answer = send_prompt_to_claude(
                model_id=model_id,
                prompt=prompt,
                max_tokens=500,
                temperature=0.1
            )
        
            try:
                cleansed_answer = eval_answer.split('Answer:')[1].lower().strip()
                for ans in coverage_map.keys():
                    if ans in cleansed_answer:
                        print(f"found citation coverage: {ans}")
                        validation_results['citation_coverage'] = coverage_map[ans]
                        break
                
            except:
                print(f"error parsing citation value: {eval_answer}\nmarking as 0")
                validation_results['citation_coverage'] = 0
    
    # Calculate validation rate
    if validation_results['total_citations'] > 0:
        validation_results['validation_rate'] = validation_results['valid_citations'] / validation_results['total_citations']
    else:
        validation_results['validation_rate'] = 0.0
    
   
    
    return validation_results

def send_prompt_to_claude(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    stop_sequences: Optional[List[str]] = None,
    model_id: Optional[str] = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
) -> str:
    """
    Send a prompt to Claude via Amazon Bedrock and return the response.
    
    Args:
        prompt (str): The prompt text to send to Claude
        system (str, optional): System message to set context for the model
        max_tokens (int, optional): Maximum number of tokens to generate
        temperature (float, optional): Controls randomness in the response (0-1)
        top_p (float, optional): Controls diversity via nucleus sampling (0-1)
        stop_sequences (List[str], optional): List of sequences where the model should stop generating
        model_id (str, optional): The Claude model ID to use, defaults to Claude 3.5 Haiku
        
    Returns:
        str: The model's response text
        
    Raises:
        Exception: If the API call fails
    """
    # Initialize Bedrock Runtime client
    bedrock_runtime = boto3.client('bedrock-runtime')

    # Add a small delay to avoid rate limiting
    time.sleep(.1)
    
    try:
        # Prepare the request payload for the Bedrock converse API
        request = {
            "modelId": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        # Add system message if provided to set context for the model
        if system:
            request["system"] = [{"text": system}]

        # Add inference configuration parameters if provided
        inference_config = {}
        if max_tokens is not None:
            inference_config["maxTokens"] = max_tokens
        if temperature is not None:
            inference_config["temperature"] = temperature
        if top_p is not None:
            inference_config["topP"] = top_p
        if stop_sequences:
            inference_config["stopSequences"] = stop_sequences

        # Only include inference config in request if parameters were provided
        if inference_config:
            request["inferenceConfig"] = inference_config
        
        # Call the Bedrock API with the prepared request
        response = bedrock_runtime.converse(**request)
        
        # Extract the response text from the nested structure
        response_content = response['output']['message']['content'][0]['text']
        
        return response_content
        
    except Exception as e:
        raise Exception(f"Error calling Bedrock API: {str(e)}")

# Functions are used in the data processing pipeline:
# 1. parse_jsonl_to_df - Parses JSONL evaluation data into DataFrame
# 2. validate_citation_coverage - Validates citations in model responses
# 3. send_prompt_to_claude - Evaluates citation coverage using Claude
# 4. aggregate_metrics_by_model - Summarizes metrics by model for comparison