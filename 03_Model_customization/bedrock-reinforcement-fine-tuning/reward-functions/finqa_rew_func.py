from typing import List
import json
import random

from dataclasses import asdict, dataclass

import re
from typing import Optional


def extract_number(text: str) -> Optional[float]:
    """Extract numerical answer from text, prioritizing structured format."""
    # First, try to extract from structured format: ANSWER: <number>
    # Handle various formats: ANSWER: 66.65%, ANSWER: [66.65%], ANSWER: **66.65%**
    answer_match = re.search(
        r"ANSWER:\s*[\[\*]*([\d,.-]+%?)[\]\*]*", text, re.IGNORECASE
    )
    if answer_match:
        num_str = (
            answer_match.group(1)
            .replace("$", "")
            .replace("%", "")
            .replace(",", "")
            .strip()
        )
        try:
            return float(num_str)
        except ValueError:
            pass

    # Fallback: Prioritize currency amounts (financial data)
    multipliers = {'thousand': 1e3, 'k': 1e3, 'million': 1e6, 'm': 1e6, 'billion': 1e9, 'b': 1e9}
    currency_match = re.search(
        r'\$\s*(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+\.?\d*)\s*(thousand|million|billion|k|m|b)?',
        text, re.IGNORECASE
    )
    if currency_match:
        num_str = currency_match.group(1).replace(',', '')
        try:
            value = float(num_str)
            suffix = currency_match.group(2)
            if suffix:
                value *= multipliers.get(suffix.lower(), 1)
            return value
        except ValueError:
            pass

    # Fallback: last number found
    matches = re.findall(r'-?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?|-?\d+\.?\d*%?', text)
    if matches:
        num_str = matches[-1].replace('%', '').replace(',', '').strip()
        try:
            return float(num_str)
        except ValueError:
            pass

    return None


def normalize_number(num: float, tolerance: float = 0.01) -> float:
    """Normalize number for comparison."""
    return round(num, 2)


def compute_score(
    solution_str: str,
    ground_truth: str,
    format_score: float = 0.0,
    score: float = 1.0,
    data_source: str = "finqa",
    extra_info: Optional[dict] = None,
) -> float:
    """FinQA scoring function for numerical and yes/no answers."""
    gt_answer = ground_truth.get("answer", ground_truth)
    gt_str = str(gt_answer).lower().strip()

    # Check if ground truth is yes/no
    if gt_str in ["yes", "no"]:
        # Extract answer from structured format
        answer_match = re.search(r"ANSWER:\s*(\w+)", solution_str, re.IGNORECASE)
        if answer_match:
            predicted_answer = answer_match.group(1).lower().strip()
            if predicted_answer == gt_str:
                return score
        return 0.0

    # Handle numerical answers
    predicted_num = extract_number(solution_str)
    if predicted_num is None:
        return 0.0

    # Try to parse ground truth as number
    try:
        gt_num = float(
            str(gt_answer).replace(",", "").replace("$", "").replace("%", "")
        )
    except (ValueError, AttributeError):
        return 0.0

    # Handle decimal vs percentage mismatch BEFORE normalizing (e.g., 0.098 vs 9.8)
    # If one is ~100x the other, try converting decimal to percentage
    if abs(predicted_num * 100 - gt_num) < abs(predicted_num - gt_num):
        predicted_num = predicted_num * 100
    elif abs(predicted_num - gt_num * 100) < abs(predicted_num - gt_num):
        gt_num = gt_num * 100

    # Normalize both numbers after conversion
    pred_normalized = normalize_number(predicted_num)
    gt_normalized = normalize_number(gt_num)

    # Exact match
    if pred_normalized == gt_normalized:
        return score

    # Check absolute difference with adaptive tolerance
    abs_diff = abs(pred_normalized - gt_normalized)

    # For small values (< 2), use tighter absolute tolerance (0.1)
    # For larger values, use 0.9
    abs_tolerance = 0.1 if abs(gt_normalized) < 2 else 0.9

    if abs_diff < abs_tolerance:
        return score * 0.95

    # Check relative error for larger values
    relative_error = abs_diff / max(abs(gt_normalized), 1e-10)
    if relative_error < 0.01:  # 1% tolerance
        return score * 0.95

    return format_score


@dataclass
class RewardOutput:
    """Reward service."""

    id: str
    aggregate_reward_score: float


def lambda_handler(event, context):

    scores: List[RewardOutput] = []

    samples = event

    for sample in samples:
        # Extract the ground truth key. In the current dataset it's answer
        print("Sample: ", json.dumps(sample, indent=2))
        ground_truth = sample["reference_answer"]

        idx = "no id"
        # print(sample)
        if not "id" in sample:
            print(f"ID is None/empty for sample: {sample}")
        else:
            idx = sample["id"]

        ro = RewardOutput(id=idx, aggregate_reward_score=0.0)

        if not "messages" in sample:
            print(f"Messages is None/empty for id: {idx}")
            scores.append(RewardOutput(id="0", aggregate_reward_score=0.0))
            continue

        # Extract answer from ground truth dict
        if ground_truth is None:
            print(f"No answer found in ground truth for id: {idx}")
            scores.append(RewardOutput(id="0", aggregate_reward_score=0.0))
            continue

        # Get completion from last message (assistant message)
        last_message = sample["messages"][-1]
        completion_text = last_message["content"]

        if last_message["role"] not in ["assistant", "nova_assistant"]:
            print(f"Last message is not from assistant for id: {idx}")
            scores.append(RewardOutput(id="0", aggregate_reward_score=0.0))
            continue

        if not "content" in last_message:
            print(f"Completion text is empty for id: {idx}")
            scores.append(RewardOutput(id="0", aggregate_reward_score=0.0))
            continue

        random_score = compute_score(
            solution_str=completion_text, ground_truth=ground_truth
        )
        ro = RewardOutput(id=idx, aggregate_reward_score=random_score)

        print(f"Response for id: {idx} is {ro}")
        scores.append(ro)

    return [asdict(score) for score in scores]
