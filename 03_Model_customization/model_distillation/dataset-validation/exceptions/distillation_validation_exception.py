import json


class DistillationValidationException(Exception):
    def __init__(self, error_message=None):
        self.errorMessage = error_message
        super().__init__(error_message)

    def serialize(self):
        """Convert exception to string format"""
        return json.dumps(self.__dict__)
