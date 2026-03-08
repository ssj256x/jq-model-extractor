class ResolutionError(Exception):
    pass


class JqResolutionError(ResolutionError):
    pass


class TransformError(ResolutionError):
    pass


class ComputationError(ResolutionError):
    pass


class ModelResolutionError(ResolutionError):
    pass


class MissingValueError(ResolutionError):
    def __init__(self, expression: str):
        super().__init__(f"No value found for jq expression: \"{expression}\"")
        self.expression = expression
