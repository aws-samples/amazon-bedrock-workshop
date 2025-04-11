from enum import StrEnum

MAX_TRAIN_RECORDS = 10000
MAX_VALIDATION_RECORDS = 1000
TRAIN = "train"
VALIDATION = "validation"


class Keys(StrEnum):
    PROMPT = "prompt"
    COMPLETION = "completion"
    SYSTEM = "system"
    MESSAGES = "messages"
    ROLE = "role"
    CONTENT = "content"
    TEXT = "text"
    IMAGE = "image"
    SOURCE = "source"
    S3_LOCATION = "s3Location"
    URI = "uri"


class Roles(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
