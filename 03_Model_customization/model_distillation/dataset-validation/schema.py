from enum import Enum


class Schema(Enum):
    CONVERSE = {
        "type": "object",
        "properties": {
            "schemaVersion": {"type": "string", "const": "bedrock-conversation-2024"},
            "system": {
                "type": "array",
                "maxItems": 1,
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                    "additionalProperties": False,
                },
            },
            "messages": {
                "type": "array",
                "minItems": 1,
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "enum": ["user", "assistant"]},
                        "content": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 1,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "type": {"type": "string"},
                                },
                                "required": ["text"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["role", "content"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["schemaVersion", "messages"],
        "additionalProperties": False,
    }
