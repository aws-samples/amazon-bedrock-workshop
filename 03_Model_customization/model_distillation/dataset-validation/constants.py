USER_ROLE = "user"
ASSISTANT_ROLE = "assistant"
MESSAGES_FIELD = "messages"
ROLE_FIELD = "role"
REQUIRED_INVOCATION_LOG_KEYS = [
    "modelId",
]
MIN_NUM_PROMPTS = 100
JSONL_EXTENSION = ".jsonl"
GZ_EXTENSION = ".gz"
S3_PREFIX = "s3://"
MAX_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB in bytes
