# Weather Package

A Python package for accessing weather data from the National Weather Service (NWS) API.

## Features

- Get weather alerts for US states
- Get weather forecasts for any location by latitude and longitude
- Easy-to-use asynchronous API

## Installation

```bash
pip install weather
```

## Usage

```python
from weather import get_alerts, get_forecast

# Get weather alerts for California
alerts = get_alerts("CA")

# Get forecast for a specific location (latitude, longitude)
forecast = get_forecast(34.0522, -118.2437)  # Los Angeles, CA
```

## Requirements

- Python 3.11+
- httpx
- mcp
