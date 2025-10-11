"""
Django Logging Modules for django_cfg.

Auto-configuring logging utilities.
"""

from .django_logger import DjangoLogger, get_logger
from .logger import logger

__all__ = [
    "logger",
    "DjangoLogger",
    "get_logger",
]
