# edubaseid/logging.py
"""
Logging and metrics module.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, Optional

logger = logging.getLogger('edubaseid')
logger.setLevel(logging.INFO)

_metrics: Dict[str, int] = defaultdict(int)

def enable_debug() -> None:
    """Enable debug logging."""
    logger.setLevel(logging.DEBUG)

def log_event(event_name: str, user: Optional[Any] = None, data: Optional[Dict] = None) -> None:
    """
    Log an event.

    :param event_name: Event name
    :param user: Optional user
    :param data: Optional data
    """
    msg = f"Event: {event_name}"
    if user:
        msg += f" User: {user.id}"
    if data:
        msg += f" Data: {data}"
    logger.info(msg)
    _metrics[event_name] += 1

def metrics() -> Dict[str, int]:
    """Get usage metrics."""
    return dict(_metrics)