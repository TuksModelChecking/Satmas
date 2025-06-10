import logging
import os
import sys

# Store loggers to prevent duplicate handlers
_loggers = {}

def get_logger(name: str, 
               level: int = logging.INFO,
               console_output: bool = True, 
               file_output: bool = False,
               log_file: str = None) -> logging.Logger:
    """
    Get a configured logger with the given name.
    
    Args:
        name: The name of the logger
        level: The logging level (default: INFO)
        console_output: Whether to output logs to the console
        file_output: Whether to output logs to a file
        log_file: Path to the log file (if file_output is True)
                  If None, will use <name>.log in the current directory
    
    Returns:
        A configured logger instance
    """
    # Check if we've already created this logger
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding handlers multiple times
    if not logger.handlers:
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if file_output:
            if log_file is None:
                # Default log file is in the directory of the calling script
                try:
                    import inspect
                    frame = inspect.stack()[1]
                    caller_dir = os.path.dirname(os.path.abspath(frame.filename))
                    log_file = os.path.join(caller_dir, f"{name}.log")
                except:
                    # Fallback to current directory
                    log_file = f"{name}.log"
            
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
    
    # Store for future use
    _loggers[name] = logger
    return logger

def set_log_level(level: int):
    """
    Set the log level for all existing loggers.
    
    Args:
        level: The logging level (e.g., logging.DEBUG, logging.INFO)
    """
    for logger in _loggers.values():
        logger.setLevel(level)