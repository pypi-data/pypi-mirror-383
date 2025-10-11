"""A Python package for accessing weather data from the National Weather Service (NWS) API."""

from .weather import (
    get_alerts,
    get_forecast,
    main,
)

__all__ = [
    "get_alerts",
    "get_forecast",
    "main",
]

__version__ = "0.1.0"