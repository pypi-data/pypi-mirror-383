"""Template Tags."""

import datetime as dt
from typing import Optional

from django import template

from moonmining.constants import DATETIME_FORMAT

register = template.Library()


@register.filter
def formatisk(value, magnitude: str = None) -> Optional[str]:
    """Return the formatted ISK value or None if input was invalid.

    Args:
    - magnitude: use the given magnitude to format the number, e.g. "b"
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return None
    power_map = {"t": 12, "b": 9, "m": 6, "k": 3, "": 0}
    if magnitude not in power_map:
        if value >= 10**12:
            magnitude = "t"
        elif value >= 10**9:
            magnitude = "b"
        elif value >= 10**6:
            magnitude = "m"
        elif value >= 10**3:
            magnitude = "k"
        else:
            magnitude = ""
    return f"{value / 10 ** power_map[magnitude]:,.1f}{magnitude}"


@register.filter
def datetime(value: dt.datetime) -> Optional[str]:
    """Render as datetime if possible or return None."""
    try:
        return value.strftime(DATETIME_FORMAT)
    except AttributeError:
        return None
