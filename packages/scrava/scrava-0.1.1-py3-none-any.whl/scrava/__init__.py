"""
Scrava - A powerful, composable web scraping framework for Python.

Scrava provides a unified API for building scalable web scrapers by orchestrating
the best tools in the Python ecosystem.
"""

__version__ = "0.1.1"

# Initialize default logging configuration (before any imports)
import logging
import structlog

# Set default log level to WARNING (silent by default)
# Logs only shown when --debug or --verbose flags are used
logging.basicConfig(
    format="%(message)s",
    level=logging.WARNING,
)

# Configure structlog with WARNING level by default (silent)
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,  # Allow reconfiguration
)

# Core data structures
from scrava.http.request import Request
from scrava.http.response import Response
from scrava.bot import BaseBot

# Core components
from scrava.core.crawler import Crawler
from scrava.core.main import Core

# Queue implementations
from scrava.queue.base import BaseQueue
from scrava.queue.memory import MemoryQueue
from scrava.queue.redis import RedisQueue

# Fetcher implementations
from scrava.fetchers.base import BaseFetcher
from scrava.fetchers.httpx import HttpxFetcher
from scrava.fetchers.playwright import PlaywrightFetcher

# Hook system
from scrava.hooks.request import RequestHook
from scrava.hooks.bot import BotHook
from scrava.hooks.cache import CacheHook

# Pipeline system
from scrava.pipelines.base import BasePipeline
from scrava.pipelines.json import JsonPipeline
from scrava.pipelines.mongo import MongoPipeline

# Configuration
from scrava.config.settings import Settings, load_settings

# Logging
from scrava.logging import setup_logging, get_logger

# Formatters
from scrava.formatters import (
    clean_html,
    clean_text,
    DataCleaner,
    CSVFormatter,
    ExcelFormatter,
    JSONFormatter
)

__all__ = [
    # Version
    "__version__",
    
    # Core data structures
    "Request",
    "Response",
    "BaseBot",
    
    # Core components
    "Crawler",
    "Core",
    
    # Queue
    "BaseQueue",
    "MemoryQueue",
    "RedisQueue",
    
    # Fetchers
    "BaseFetcher",
    "HttpxFetcher",
    "PlaywrightFetcher",
    
    # Hooks
    "RequestHook",
    "BotHook",
    "CacheHook",
    
    # Pipelines
    "BasePipeline",
    "JsonPipeline",
    "MongoPipeline",
    
    # Configuration
    "Settings",
    "load_settings",
    
    # Logging
    "setup_logging",
    "get_logger",
    
    # Formatters
    "clean_html",
    "clean_text",
    "DataCleaner",
    "CSVFormatter",
    "ExcelFormatter",
    "JSONFormatter",
]

