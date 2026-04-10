import json
import boto3
import re
from typing import List, Dict, Any
from dataclasses import asdict, dataclass
from botocore.exceptions import ClientError

# Configuration - Update these values as needed
JUDGE_MODEL_ARN = "openai.gpt-oss-120b-1:0"
EVALUATION_PROMPT_TEMPLATE = """You are an expert evaluation system grader.

Given: evaluation task with instruction, input, two responses, and reference solution.
Goal: assess quality of model's evaluation and reference generation.

Scoring rubric (start at 0.0, then add or subtract):

Core Components:
1. Evaluation Component (0.5 max)
   - Correct better/worse/tie judgment: +0.3
   - Valid reasoning provided: +0.2

2. Reference Generation (0.5 max)
   - Complete information coverage: +0.3
   - Appropriate structure/format: +0.2

Deductions:
A. Incorrect evaluation: -0.4
B. Missing/poor reasoning: -0.3
C. Incomplete reference: -0.2
D. Poor structure/format: -0.1

Instructions:
- Compare model's evaluation and reference against ground truth
- Consider both accuracy and completeness
- Apply deductions as needed
- Cap final score to [0.0, 1.0] range

Return EXACTLY this JSON (no extra text):
{
    "score": <numerical score 0.0-1.0>,
    "reasoning": "<explain which rules applied and why, show your scoring steps>"
}

## Current Evaluation Task

### Question
{prompt}

### Model's Response
{completion}"""

# Initialize Bedrock Runtime client
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")


@dataclass
class RewardOutput:
    id: str
    aggregate_reward_score: float
    metrics_list: List[dict]


def format_evaluation_prompt(prompt: str, completion: str, reference: str) -> str:
    """Format the evaluation prompt using the template."""
    eval_prompt = EVALUATION_PROMPT_TEMPLATE.replace("{prompt}", prompt)
    eval_prompt = eval_prompt.replace("{completion}", completion)

    if reference:
        eval_prompt += f"\n\n### Reference Answer (Ground Truth)\n{reference}"

    return eval_prompt


def parse_score_from_text(score_text: str) -> float:
    """Extract a numerical score from the judge model's response."""
    try:
        if score_text.strip().startswith("{"):
            try:
                response_json = json.loads(score_text.strip())
                for field in ["score", "reward", "rating", "value"]:
                    if field in response_json:
                        score = float(response_json[field])
                        if score > 1.0:
                            score = score / 100.0 if score > 10 else score / 10.0
                        return max(0.0, min(1.0, score))
            except (json.JSONDecodeError, ValueError):
                pass

        patterns = [
            r"(\d+\.\d+)",
            r"(\d+)%",
            r"(\d+)/10",
            r"(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, score_text.strip())
            if match:
                score = float(match.group(1))
                if score > 10:
                    score = score / 100.0
                elif score > 1.0:
                    score = score / 10.0
                return max(0.0, min(1.0, score))

        print(f"Warning: Could not parse score from: {score_text[:200]}")
        return 0.5

    except (ValueError, TypeError) as e:
        print(f"Warning: Error parsing score: {e}")
        return 0.5


def evaluate_sample(sample: Dict[str, Any]) -> float:
    """Evaluate a single sample using the judge model."""
    try:
        completion = get_assistant_message(sample)
        reference = get_reference(sample)
        prompt = get_user_message(sample)

        evaluation_text = format_evaluation_prompt(prompt, completion, reference)

        response = bedrock_runtime.converse(
            modelId=JUDGE_MODEL_ARN,
            messages=[{"role": "user", "content": [{"text": evaluation_text}]}],
            inferenceConfig={"maxTokens": 500, "temperature": 0.0},
        )

        output_message = response.get("output", {}).get("message", {})
        content_blocks = output_message.get("content", [])

        if not content_blocks:
            print(
                f"Warning: Empty response from judge model for sample {sample.get('id')}"
            )
            return 0.5

        score_text = find_text_from_content_blocks(content_blocks)
        score = parse_score_from_text(score_text)

        print(
            f"Sample {sample.get('id')}: Judge response: {score_text[:100]}... -> Score: {score}"
        )
        return score

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        print(
            f"Bedrock API Error for sample {sample.get('id')} ({error_code}): {error_message}"
        )
        return 0.5

    except Exception as e:
        print(
            f"Error evaluating sample {sample.get('id')}: {type(e).__name__}: {str(e)}"
        )
        return 0.0


def lambda_handler(event, context):
    """
    Lambda handler for PandaLM evaluation - BATCH PROCESSING.

    Expected event structure (RFT batch format):
    [
        {
            "id": "sample-001",
            "messages": [
                {"role": "user", "content": "Original training prompt"},
                {"role": "assistant", "content": "Model response to evaluate"}
            ],
            "reference_answer": {"answer": "..."}
        },
        ...
    ]

    Returns (RFT batch format):
    [
        {"id": "sample-001", "aggregate_reward_score": 0.85, "metrics_list": [...]},
        ...
    ]
    """
    scores: List[RewardOutput] = []
    samples = event

    if not isinstance(samples, list):
        print(f"Error: Expected list of samples, got {type(samples)}")
        return []

    print(f"Processing batch of {len(samples)} samples")

    for sample in samples:
        sample_id = sample.get("id", "no-id")

        try:
            if not isinstance(sample, dict):
                print(f"Error: Sample {sample_id} is not a dict")
                scores.append(
                    RewardOutput(
                        id=sample_id,
                        aggregate_reward_score=0.0,
                        metrics_list=[
                            {"name": "error", "value": 0.0, "type": "Metric"}
                        ],
                    )
                )
                continue

            if not sample.get("messages", []):
                print(f"Messages field missing or empty for id: {sample_id}")
                scores.append(
                    RewardOutput(
                        id=sample_id,
                        aggregate_reward_score=0.0,
                        metrics_list=[
                            {"name": "error", "value": 0.0, "type": "Metric"}
                        ],
                    )
                )
                continue

            if not is_assistant_message_in_sample(sample):
                print(f"Error: Empty response for sample {sample_id}")
                scores.append(
                    RewardOutput(
                        id=sample_id,
                        aggregate_reward_score=0.0,
                        metrics_list=[
                            {"name": "error", "value": 0.0, "type": "Metric"}
                        ],
                    )
                )
                continue

            if not is_user_message_in_sample(sample):
                print(f"Error: Empty prompt for sample {sample_id}")
                scores.append(
                    RewardOutput(
                        id=sample_id,
                        aggregate_reward_score=0.0,
                        metrics_list=[
                            {"name": "error", "value": 0.0, "type": "Metric"}
                        ],
                    )
                )
                continue

            reward = evaluate_sample(sample)

            scores.append(
                RewardOutput(
                    id=sample_id,
                    aggregate_reward_score=reward,
                    metrics_list=[
                        {"name": "judge_score", "value": reward, "type": "Reward"}
                    ],
                )
            )

        except Exception as e:
            print(f"Error processing sample {sample_id}: {type(e).__name__}: {str(e)}")
            scores.append(
                RewardOutput(
                    id=sample_id,
                    aggregate_reward_score=0.0,
                    metrics_list=[{"name": "error", "value": 0.0, "type": "Metric"}],
                )
            )

    print(f"Completed batch processing: {len(scores)} results")
    return [asdict(score) for score in scores]


def get_reference(sample):
    """Extract the reference answer from the sample."""
    reference = sample.get("reference_answer", "")
    if reference and isinstance(reference, dict):
        if "answer" in reference:
            reference = reference.get("answer")
        elif "expectedAnswer" in reference:
            reference = reference.get("expectedAnswer")
        elif "ground_truth" in reference:
            reference = reference.get("ground_truth")
    return reference


def get_user_message(sample):
    """Search for a user message in the sample's messages."""
    messages = sample.get("messages", [])
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content")
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                return "".join(text_parts)
            return content
    return ""


def get_assistant_message(sample):
    """Search for an assistant message in the sample's messages."""
    messages = sample.get("messages", [])
    for msg in reversed(messages):
        if msg.get("role") in ["assistant", "nova_assistant"]:
            content = msg.get("content")
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                return "".join(text_parts)
            return content
    return ""


def is_assistant_message_in_sample(sample):
    """Check if an assistant message is present in the sample's messages."""
    messages = sample.get("messages", [])
    sample_id = sample.get("id", "no-id")

    if not messages:
        print(f"Messages field missing for id: {sample_id}")
        return False

    last_message = messages[-1]
    if last_message.get("role") not in ["assistant", "nova_assistant"]:
        print(
            f"Last message is not from assistant for id: {sample_id}, role: {last_message.get('role')}"
        )
        return False

    content = last_message.get("content", "")
    if not content:
        print(f"Content field missing in last assistant message for id: {sample_id}")
        return False

    return True


def is_user_message_in_sample(sample):
    """Check if a user message is present in the sample's messages."""
    messages = sample.get("messages", [])
    sample_id = sample.get("id", "no-id")

    if not messages:
        print(f"Messages field missing for id: {sample_id}")
        return False

    first_message = messages[0]
    if first_message.get("role") not in ["user", "system"]:
        print(
            f"First message is not from user for id: {sample_id}, role: {first_message.get('role')}"
        )
        return False

    content = first_message.get("content", "")
    if not content:
        print(f"Content field missing in first user message for id: {sample_id}")
        return False

    return True


def find_text_from_content_blocks(content_blocks):
    """Find text from content blocks."""
    for block in content_blocks:
        if block.get("text", ""):
            return block.get("text")
    return ""
