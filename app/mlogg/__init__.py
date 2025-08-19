"""Initialization logic for mlogg logging configuration."""

from app.mlogg.setup import init_logging, logger

from app.mlogg.utils import logger_wraps, log_and_time

__all__ = ["init_logging", "logger", "logger_wraps", "log_and_time"]

"""
Here’s a concise comparison for your logging strategy:

1. logger_wraps Decorator (Entry/Exit Logging)
Best for: Service and UoW methods where you want automatic, consistent entry/exit logs.
Pros: DRY, easy to apply, ensures every method call is logged with args/results.
Cons: Can be verbose if applied everywhere, but great for business logic and transaction boundaries.
2. log_and_time Decorator (Entry/Exit + Timing)
Best for: Performance-critical paths or places where you want to monitor execution time.
Pros: Adds timing info to entry/exit logs.
Cons: Slightly more verbose logs, but useful for profiling.
3. logger.bind (Manual Logging)
Best for: Repos and lower-level code where you want to log specific events, errors, or context.
Pros: Flexible, can log only what matters (e.g., errors, data changes).
Cons: Requires manual log calls, less DRY.
Recommended Pattern for Your Project
Service/UoW Layer: Use logger_wraps (or log_and_time if you want timing) for entry/exit logging.
Repository Layer: Use logger.bind for contextual, event-driven logs (e.g., errors, data changes).
Avoid double-logging: Don’t use both decorators and manual logs for the same event unless you need both.
"""
