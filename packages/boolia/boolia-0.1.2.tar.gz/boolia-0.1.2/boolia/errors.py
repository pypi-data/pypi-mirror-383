class MissingVariableError(NameError):
    """Raised when a required variable/path is missing."""

    def __init__(self, parts):
        super().__init__(f"Missing variable/path: {'.'.join(parts)}")
        self.parts = parts
