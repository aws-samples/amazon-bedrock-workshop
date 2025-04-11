from .input_type import InputType
from .model_type import ModelType


class Model:
    def __init__(
        self,
        model_type: ModelType,
        input_type: list[InputType],
    ):
        self.model_type = model_type
        self.input_type = input_type
