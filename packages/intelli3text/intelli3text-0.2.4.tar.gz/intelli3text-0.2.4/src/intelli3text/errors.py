class Intelli3Error(Exception):
    """Base exception for all intelli3text-specific errors.

    Use this as the common ancestor for custom exceptions so callers can
    either catch specific error types or handle all library errors at once.

    Example:
        try:
            pipeline.process(source)
        except Intelli3Error as e:
            # Handle any library-specific error
            print(f"intelli3text error: {e}")
    """


class ModelNotFoundError(Intelli3Error):
    """Raised when a required model/resource cannot be found or loaded.

    Typical cases:
        - Missing fastText LID model (e.g., `lid.176.bin`) and auto-download fails
        - Missing spaCy language model (e.g., `pt_core_news_md`) and download fails

    Attributes:
        model_name: A human-readable identifier of the missing model/resource.
        hint: Optional guidance to resolve the issue (e.g., install command, env var).
    """

    def __init__(self, model_name: str, hint: str | None = None):
        self.model_name = model_name
        self.hint = hint
        msg = f"Required model/resource not found: {model_name}"
        if hint:
            msg += f" | hint: {hint}"
        super().__init__(msg)
