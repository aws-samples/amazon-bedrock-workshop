class Schema:
    Converse = {
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
                },
            },
            "messages": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "enum": ["user", "assistant"]},
                        "content": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "image": {
                                        "type": "object",
                                        "properties": {
                                            "format": {"type": "string"},
                                            "source": {
                                                "type": "object",
                                                "properties": {
                                                    "s3Location": {
                                                        "type": "object",
                                                        "properties": {
                                                            "uri": {
                                                                "type": "string",
                                                                "pattern": "^s3://.*",
                                                            },
                                                            "bucketOwner": {
                                                                "type": "string"
                                                            },
                                                        },
                                                        "additionalProperties": True,
                                                        "required": ["uri"],
                                                    }
                                                },
                                                "additionalProperties": True,
                                                "required": ["s3Location"],
                                            },
                                        },
                                        "additionalProperties": True,
                                        "required": ["format", "source"],
                                    },
                                    "video": {
                                        "type": "object",
                                        "properties": {
                                            "format": {"type": "string"},
                                            "source": {
                                                "type": "object",
                                                "properties": {
                                                    "s3Location": {
                                                        "type": "object",
                                                        "properties": {
                                                            "uri": {
                                                                "type": "string",
                                                                "pattern": "^s3://.*",
                                                            },
                                                            "bucketOwner": {
                                                                "type": "string"
                                                            },
                                                        },
                                                        "additionalProperties": True,
                                                        "required": ["uri"],
                                                    }
                                                },
                                                "additionalProperties": True,
                                                "required": ["s3Location"],
                                            },
                                        },
                                        "additionalProperties": True,
                                        "required": ["format", "source"],
                                    },
                                },
                                "additionalProperties": True,
                            },
                        },
                    },
                    "additionalProperties": True,
                    "required": ["role", "content"],
                },
            },
        },
        "additionalProperties": True,
        "required": ["messages"],
    }

    PROMPT_COMPLETION = {
        "type": "object",
        "required": ["prompt", "completion"],
        "properties": {"prompt": {"type": "string"}, "completion": {"type": "string"}},
        "additionalProperties": True,
    }
