"""Exception classes for Aviro package."""


class PromptNotFoundError(Exception):
    """Exception raised when a prompt is not found"""
    def __init__(self, prompt_id: str, message: str = None):
        self.prompt_id = prompt_id
        self.message = message or f"Prompt '{prompt_id}' not found"
        super().__init__(self.message)


class EvaluatorNotFoundError(Exception):
    """Exception raised when an evaluator is not found"""
    def __init__(self, evaluator_id: str, message: str = None):
        self.evaluator_id = evaluator_id
        self.message = message or f"Evaluator '{evaluator_id}' not found"
        super().__init__(self.message)


class PromptAlreadyExistsError(Exception):
    """Exception raised when trying to create a prompt that already exists"""
    def __init__(self, prompt_id: str, message: str = None):
        self.prompt_id = prompt_id
        self.message = message or f"Prompt '{prompt_id}' already exists"
        super().__init__(self.message)


class EvaluatorAlreadyExistsError(Exception):
    """Exception raised when trying to create an evaluator that already exists"""
    def __init__(self, evaluator_id: str, message: str = None):
        self.evaluator_id = evaluator_id
        self.message = message or f"Evaluator '{evaluator_id}' already exists"
        super().__init__(self.message)

