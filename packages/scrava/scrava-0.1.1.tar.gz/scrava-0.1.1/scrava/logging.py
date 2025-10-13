"""scrava/logging.py"""
import sys
import logging
from typing import Optional
import structlog


def setup_logging(
    level: str = "WARNING",
    format: str = "console",
    use_colors: bool = True
) -> structlog.BoundLogger:
    """
    Setup structured logging for Scrava.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Output format ('console' for dev, 'json' for production)
        use_colors: Whether to use colored output (console format only)
        
    Returns:
        Configured logger instance
    """
    # Set log level
    log_level = getattr(logging, level.upper(), logging.WARNING)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Configure processors based on format
    if format == "json":
        # Production: JSON output
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Console output
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        
        if use_colors:
            processors.append(structlog.dev.ConsoleRenderer())
        else:
            processors.append(structlog.processors.KeyValueRenderer(
                key_order=["timestamp", "log_level", "event"]
            ))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,  # Allow reconfiguration
    )
    
    return structlog.get_logger()


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Logger instance
    """
    logger = structlog.get_logger()
    if name:
        logger = logger.bind(logger_name=name)
    return logger
