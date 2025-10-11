import logging
from typing import Any

# Custom log level: THOUGHT
THOUGHT = 25
logging.addLevelName(THOUGHT, "THOUGHT")


def thought(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
    if self.isEnabledFor(THOUGHT):
        self._log(THOUGHT, message, args, **kwargs)


setattr(logging.Logger, "thought", thought)


# RichHandler for UI output (stub, real implementation in handlers.py)
class RichHandler(logging.Handler):
    def emit(self, _record):
        # Actual implementation in handlers.py
        pass


def setup_logging(config_path=None):
    """
    Set up logging configuration from YAML file.
    """
    from .config import LogConfig

    LogConfig.load(config_path)
