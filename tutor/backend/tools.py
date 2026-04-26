"""
Bedrock tutor tools - FastAPI version (no Streamlit dependency)
"""
from strands import tool
from typing import List, Dict, Any
from pathlib import Path
import yaml


@tool
def update_scratchpad(code: str) -> str:
    """
    Updates the code scratchpad with new Python code.

    Args:
        code: Complete Python code to display in the scratchpad

    Returns:
        Confirmation message
    """
    return "✓ Code updated in scratchpad"


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
