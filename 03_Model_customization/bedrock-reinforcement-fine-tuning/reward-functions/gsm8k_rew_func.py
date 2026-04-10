import re

_SOLUTION_CLIP_CHARS = 300


def lambda_handler(event, context):
    """AWS Lambda handler for GSM8K reward function."""
    results = []
    for item in event:
        item_id = item.get("id") or item.get("task_id", "unknown")
        messages = item.get("messages", [])
        metadata = item.get("metadata", {})
        
        # Get ground truth - check both metadata and top-level reference_answer
        ground_truth = metadata.get("reference_answer", {}).get("final_answer")
        if not ground_truth:
            ground_truth = item.get("reference_answer", {}).get("final_answer")
        if not ground_truth:
            print(f"No ground truth found for id: {item_id}")
        
        # Get assistant response
        assistant_response = ""
        for msg in messages:
            if msg.get("role") == "assistant":
                assistant_response = msg.get("content", "")
        
        # Compute score
        score = compute_score(assistant_response, ground_truth) if ground_truth else 0.0
        
        results.append({
            "id": item_id,
            "aggregate_reward_score": score,
            "reward_components": {"correctness": score}
        })
    
    return results


def extract_solution(solution_str, method="strict"):
    assert method in ["strict", "flexible"]

    # Optimization: Regular expression matching on very long strings can be slow.
    # For math problems, the final answer is usually at the end.
    # We only match on the last 300 characters, which is a safe approximation for 300 tokens.
    if len(solution_str) > _SOLUTION_CLIP_CHARS:
        solution_str = solution_str[-_SOLUTION_CLIP_CHARS:]

    if method == "strict":
        # this also tests the formatting of the model
        solutions = re.findall("#### (\\-?[0-9\\.\\,]+)", solution_str)
        if len(solutions) == 0:
            final_answer = None
        else:
            # take the last solution
            final_answer = solutions[-1].replace(",", "").replace("$", "")
    elif method == "flexible":
        answer = re.findall("(\\-?[0-9\\.\\,]+)", solution_str)
        final_answer = None
        if len(answer) == 0:
            # no reward is there is no answer
            pass
        else:
            invalid_str = ["", "."]
            # find the last number that is not '.'
            for final_answer in reversed(answer):
                if final_answer not in invalid_str:
                    break
    return final_answer


def compute_score(
    solution_str, ground_truth, method="strict", format_score=0.0, score=1.0
):
    """The scoring function for GSM8k.

    Reference: Trung, Luong, et al. "Reft: Reasoning with reinforced fine-tuning." Proceedings of the 62nd Annual
    Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). 2024.

    Args:
        solution_str: the solution text
        ground_truth: the ground truth
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_score: the score for the format
        score: the score for the correct answer
    """
    answer = extract_solution(solution_str=solution_str, method=method)
    if answer is None:
        return 0
    else:
        if answer == ground_truth:
            return score
        else:
            return format_score
