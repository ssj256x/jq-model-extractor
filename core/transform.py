class Transform:
    def __init__(self, fn, description: str = ""):
        self.fn = fn
        self.description = description

    def apply(self, data):
        try:
            return Ok(self.fn(data))
        except Exception as e:
            return Err(TransformError(str(e)))