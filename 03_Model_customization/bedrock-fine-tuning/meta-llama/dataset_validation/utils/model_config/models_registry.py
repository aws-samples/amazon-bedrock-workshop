from .model import Model
from .model_type import ModelType
from .input_type import InputType

MODELS = {
    "llama3-1-8b": Model(
        model_type=ModelType.TEXT,
        input_type=InputType.PROMPT_COMPLETION,
    ),
    "llama3-1-70b": Model(
        model_type=ModelType.TEXT,
        input_type=InputType.PROMPT_COMPLETION,
    ),
    "llama3-2-1b": Model(
        model_type=ModelType.TEXT,
        input_type=InputType.CONVERSE,
    ),
    "llama3-2-3b": Model(
        model_type=ModelType.TEXT,
        input_type=InputType.CONVERSE,
    ),
    "llama3-2-11b": Model(
        model_type=ModelType.MULTIMODAL,
        input_type=InputType.CONVERSE,
    ),
    "llama3-2-90b": Model(
        model_type=ModelType.MULTIMODAL,
        input_type=InputType.CONVERSE,
    ),
}
