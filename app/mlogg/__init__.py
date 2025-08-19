"""Initialization logic for mlogg logging configuration."""

from app.mlogg.setup import init_logging, logger

from app.mlogg.utils import logger_wraps, log_and_time

__all__ = ["init_logging", "logger", "logger_wraps", "log_and_time"]
