"""
Bedrock tutor tools - FastAPI version (no Streamlit dependency)
"""
from strands import tool
from typing import List, Dict, Any
from pathlib import Path
import yaml


@tool
def update_scratchpad(code: str, highlight_lines: str = None) -> str:
    """
    Updates the code scratchpad with new Python code and optionally highlights specific lines.

    Args:
        code: Complete Python code to display in the scratchpad
        highlight_lines: Optional line numbers to highlight (e.g., "5-7" or "3,5,8-10")

    Returns:
        Confirmation message
    """
    if highlight_lines:
        return f"✓ Code updated in scratchpad (highlighted lines: {highlight_lines})"
    return "✓ Code updated in scratchpad"


@tool
def highlight_code(line_range: str, explanation: str = None) -> str:
    """
    Highlights and scrolls to specific lines in the current code scratchpad.
    Use this to draw attention to relevant code sections when explaining concepts.

    Args:
        line_range: Line numbers to highlight (e.g., "5-7" or "3,5,8-10")
        explanation: Optional brief explanation of what you're highlighting

    Returns:
        Confirmation message
    """
    if explanation:
        return f"✓ Highlighted lines {line_range}: {explanation}"
    return f"✓ Highlighted lines {line_range}"


@tool
def give_user_task(task_description: str, hint: str = None) -> str:
    """
    Give the user a hands-on task to try in the code scratchpad.
    Use this to make learning interactive - ask them to modify code, try different parameters, etc.

    Args:
        task_description: Clear description of what the user should try
        hint: Optional hint to help them succeed

    Returns:
        Confirmation that task was presented
    """
    if hint:
        return f"✓ Task presented to user with hint"
    return f"✓ Task presented to user"


@tool
def ask_multiple_choice(
    question: str,
    options: List[str],
    correct_answer: str,
    explanation: str = None
) -> str:
    """
    Ask the user a multiple choice question to test their knowledge.
    Creates interactive buttons that validate answers and provide feedback.

    Args:
        question: The question to ask
        options: List of answer choices (e.g., ["max_tokens", "temperature", "top_p"])
        correct_answer: The correct answer (must match one option exactly)
        explanation: Optional explanation shown after answering

    Returns:
        Confirmation that question was presented

    Example:
        ask_multiple_choice(
            question="Which parameter controls response randomness?",
            options=["max_tokens", "temperature", "top_p"],
            correct_answer="temperature",
            explanation="Temperature controls randomness. Higher = more creative, lower = more focused."
        )
    """
    return f"✓ Multiple choice question presented with {len(options)} options"


@tool
def update_learning_progress(
    path_id: str,
    steps_completed: List[str],
    total_steps: int
) -> str:
    """
    Update the visual progress indicator for a learning path.
    Call this whenever you cover a concept from the active learning path.

    Args:
        path_id: The learning path ID (e.g., "distributed-inference")
        steps_completed: List of step names/numbers covered (e.g., ["Step 1: Setup", "Step 3: Streaming"])
        total_steps: Total number of steps in this learning path

    Returns:
        Confirmation of progress update
    """
    progress_pct = int((len(steps_completed) / total_steps) * 100) if total_steps > 0 else 0
    return f"✓ Progress updated: {len(steps_completed)}/{total_steps} steps completed ({progress_pct}%)"


@tool
def read_scratchpad() -> str:
    """
    Read the current code in the user's scratchpad.
    Use this to:
    - See what code the user has written or modified
    - Debug errors in their code
    - Acknowledge their changes
    - Help them with their modifications

    Returns:
        The current code in the scratchpad
    """
    # Note: In a real implementation, this would retrieve code from session state
    # For now, agent should ask user to share code if needed
    return "Note: To see your code, please share it in chat or describe what you changed."


@tool
def find_learning_paths(query: str) -> List[Dict[str, str]]:
    """
    Search for relevant learning paths based on keywords or topics.

    Args:
        query: Search query (keywords or topic to find)

    Returns:
        List of matching learning paths with id, title, and description
    """
    learning_paths = _load_learning_paths()
    query_lower = query.lower()
    matches = []

    for path_id, path_data in learning_paths.items():
        keywords = [k.lower() for k in path_data.get('keywords', [])]
        title = path_data.get('title', '').lower()
        description = path_data.get('description', '').lower()

        if (query_lower in title or query_lower in description or
            any(query_lower in kw or kw in query_lower for kw in keywords)):
            matches.append({
                'id': path_id,
                'title': path_data['title'],
                'description': path_data['description']
            })

    return matches


@tool
def load_learning_path(path_id: str) -> Dict[str, Any]:
    """
    Load a specific learning path by ID.

    Args:
        path_id: The ID of the learning path

    Returns:
        Learning path content
    """
    learning_paths = _load_learning_paths()

    if path_id in learning_paths:
        path_data = learning_paths[path_id]
        return {
            'id': path_id,
            'title': path_data['title'],
            'description': path_data['description'],
            'content': path_data['content'][:5000]
        }
    else:
        return {"error": f"Learning path '{path_id}' not found"}


def _load_learning_paths():
    """Helper to load learning paths from markdown files"""
    learning_paths = {}
    learning_paths_dir = Path(__file__).parent.parent.parent / "tutor" / "learning_paths"

    if learning_paths_dir.exists():
        for md_file in learning_paths_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        learning_paths[frontmatter['id']] = {
                            **frontmatter,
                            'content': parts[2].strip()
                        }
            except Exception:
                pass

    return learning_paths
