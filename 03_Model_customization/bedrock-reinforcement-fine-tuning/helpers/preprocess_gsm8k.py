# Preprocess GSM8K from HuggingFace into Bedrock RFT format

from datasets import load_dataset
import json, re

def preprocess_gsm8k(hf_path="openai/gsm8k", train_size=256, test_size=256, output_dir="."):
    ds = load_dataset(hf_path, "main")
    
    def extract_answer(answer_text):
        match = re.search(r'####\s*(-?\d+(?:,\d+)*)', answer_text)
        return match.group(1).replace(',', '') if match else ""
    
    def extract_steps(answer_text):
        return [s.strip() for s in answer_text.split('\n') if s.strip() and not s.strip().startswith('####')]
    
    def format_row(row, idx, split):
        return {
            "messages": [
                {"role": "system", "content": "You are a helpful math tutor who solves word problems step by step."},
                {"role": "user", "content": f"{row['question']} Let's think step by step and output the final answer after \"####\"."}
            ],
            "reference_answer": {
                "final_answer": extract_answer(row['answer']),
                "steps": extract_steps(row['answer'])
            },
            "task_id": f"gsm8k_{split}_{idx}",
            "domain": "math",
            "difficulty_level": "grade_school",
            "data_source": hf_path,
            "original_question": row['question'],
            "original_answer": row['answer']
        }
    
    for split, size, filename in [("train", train_size, "train.jsonl"), ("test", test_size, "test.jsonl")]:
        with open(f"{output_dir}/{filename}", "w") as f:
            for i, row in enumerate(ds[split].select(range(min(size, len(ds[split]))))):
                f.write(json.dumps(format_row(row, i, split)) + "\n")
        print(f"Wrote {filename}")

if __name__ == "__main__":
    preprocess_gsm8k(output_dir=".")
