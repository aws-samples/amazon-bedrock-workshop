import json
import re
from dataclasses import dataclass, asdict
from typing import List
 
_SOLUTION_CLIP_CHARS = 300
 
 
@dataclass
class RewardOutput:
    id: str
    aggregate_reward_score: float
    score: float
    metrics_list: List[dict]
 
 
def extract_solution(solution_str, method="strict"):
    assert method in ["strict", "flexible"]
 
    if len(solution_str) > _SOLUTION_CLIP_CHARS:
        solution_str = solution_str[-_SOLUTION_CLIP_CHARS:]
 
    if method == "strict":
        solutions = re.findall(r"#### (\-?[0-9\.\,]+)", solution_str)
        if not solutions:
            return None
        return solutions[-1].replace(",", "").replace("$", "")
    else:
        answers = re.findall(r"(\-?[0-9\.\,]+)", solution_str)
        invalid_str = ["", "."]
        for answer in reversed(answers):
            if answer not in invalid_str:
                return answer
        return None
 
 
def compute_score(trajectory_id, solution_str, ground_truth, method="strict", format_score=0.0, score=1.0):
    answer = extract_solution(solution_str=solution_str, method=method)
    if answer is not None and answer == ground_truth:
        final_score = score
    elif answer is not None:
        final_score = format_score
    else:
        final_score = 0.0
 
    return RewardOutput(
        id=trajectory_id,
        aggregate_reward_score=float(final_score),
        score=float(final_score),
        metrics_list=[],
    )
 
 
def lambda_handler(event, context):
    """
    Receives a batch of trajectory objects as a JSON array.
    Each trajectory has: id, messages, reference_answer.
    Returns a JSON array of: [{"id": "...", "aggregate_reward_score": float, "metrics_list": [...]}, ...]
    """
    print("Event: ", json.dumps(event))

    trajectories = event if isinstance(event, list) else event.get("trajectories", [])
 
    scores = []
    for trajectory in trajectories:
        trajectory_id = trajectory.get("id", "no-id")
 
        # Response is in the last assistant message
        response = ""
        for msg in reversed(trajectory.get("messages", [])):
            if msg.get("role") == "assistant":
                response = msg.get("content", "")
                break
 
        reference_answer = trajectory.get("reference_answer", {})
        reference_text = reference_answer.get('text', '') if isinstance(reference_answer, dict) else ''
        
        # Extract ground truth using the #### pattern from reference answer
        gt_match = re.findall(r"#### (\-?[0-9\.\,]+)", reference_text)
        ground_truth = gt_match[-1].replace(",", "") if gt_match else ''
 
        result = compute_score(
            trajectory_id=trajectory_id,
            solution_str=response,
            ground_truth=ground_truth,
        )
        scores.append(result)
        print(f"id={trajectory_id} answer={extract_solution(response)} truth={ground_truth} score={result.aggregate_reward_score}")
 
    return [asdict(s) for s in scores]