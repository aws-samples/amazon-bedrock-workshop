class InvalidRowException(Exception):
    def __init__(self, message, index):
        super().__init__(message)
        self.message = message
        self.line_error_message = (
            f"This error occured on line {index + 1} in the JSONL file."
        )

    def __str__(self):
        return self.message + self.line_error_message
