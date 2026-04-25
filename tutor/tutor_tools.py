"""Tools for the Bedrock tutor agent using strands framework."""

import streamlit as st
from strands import tool
from typing import List, Dict, Any


@tool
def update_scratchpad(code: str) -> str:
    """
    Updates the code scratchpad with new Python code.

    Args:
        code: Complete Python code to display in the scratchpad

    Returns:
        Confirmation message
    """
    print(f"[DEBUG] update_scratchpad called with {len(code)} chars")
    print(f"[DEBUG] First 100 chars: {code[:100]}")
    print(f"[DEBUG] Current session_state.code: {len(st.session_state.code)} chars")

    st.session_state.code = code
    st.session_state.code_generated_count = st.session_state.get('code_generated_count', 0) + 1

    print(f"[DEBUG] After update, session_state.code: {len(st.session_state.code)} chars")
    return "✓ Code updated in scratchpad"


@tool
def find_learning_paths(query: str) -> List[Dict[str, str]]:
    """
    Search for relevant learning paths based on keywords or topics.
    Use this when the user asks about a specific topic (e.g., 'responses API', 'embeddings', 'RAG').

    Args:
        query: Search query (keywords or topic to find)

    Returns:
        List of matching learning paths with id, title, and description
    """
    from streamlit_app import LEARNING_PATHS

    query_lower = query.lower()
    matches = []

    for path_id, path_data in LEARNING_PATHS.items():
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
    Load a specific learning path by ID to get the full teaching content.
    Use this after finding a relevant path with find_learning_paths.

    Args:
        path_id: The ID of the learning path to load (e.g., 'text-generation', 'embeddings', 'rag', 'distributed-inference')

    Returns:
        Learning path content with id, title, and full teaching curriculum
    """
    from streamlit_app import LEARNING_PATHS

    if path_id in LEARNING_PATHS:
        path_data = LEARNING_PATHS[path_id]

        # Set as current learning path
        st.session_state.current_learning_path = path_id

        return {
            'id': path_id,
            'title': path_data['title'],
            'description': path_data['description'],
            'content': path_data['content'][:5000]  # Limit content size
        }
    else:
        return {"error": f"Learning path '{path_id}' not found"}
