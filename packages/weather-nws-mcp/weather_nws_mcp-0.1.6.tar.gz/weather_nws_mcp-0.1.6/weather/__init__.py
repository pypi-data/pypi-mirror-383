"""A Python package for accessing weather data from the National Weather Service (NWS) API."""

from .weather import (
    get_weather_by_city,
    main,
)

__all__ = [
    "get_weather_by_city",
    "main",
]

__version__ = "0.1.6"