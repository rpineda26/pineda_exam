import logging
import colorlog

def setup_logger(name=None):
    """
    Set up a colored logger that can be used across your project
    """
    # Create logger
    logger = logging.getLogger(name or __name__)
    
    # Don't add handlers if they already exist (prevents duplicate logs)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Create console handler with color formatting
    handler = colorlog.StreamHandler()
    handler.setLevel(logging.DEBUG)
    
    # Define color scheme
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s: %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    
    handler.setFormatter(color_formatter)
    logger.addHandler(handler)
    
    return logger

# Create a default logger instance
default_logger = setup_logger('MyApp')