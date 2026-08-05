import logging
import sys
from typing import Optional, Callable

class QueueLogHandler(logging.Handler):
    """Custom logging handler that routes log messages to a queue callback or queue."""
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.callback:
                self.callback(msg)
        except Exception:
            self.handleError(record)

_logger_instance: Optional[logging.Logger] = None

def setup_logger(name: str = "AudioOverImageProducer", level: int = logging.INFO, queue_callback: Optional[Callable[[str], None]] = None) -> logging.Logger:
    global _logger_instance
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()
        
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # Queue callback handler if provided
    if queue_callback:
        qh = QueueLogHandler(queue_callback)
        qh.setFormatter(formatter)
        logger.addHandler(qh)
        
    _logger_instance = logger
    return logger

def get_logger() -> logging.Logger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = setup_logger()
    return _logger_instance
