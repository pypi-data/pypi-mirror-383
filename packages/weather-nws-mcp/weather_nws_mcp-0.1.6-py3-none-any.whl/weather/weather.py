"""A Python package for accessing weather data from the National Weather Service (NWS) API."""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP()

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API."""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None



@mcp.tool()
async def get_weather_by_city(cityName: str) -> str:
    """通过国内城市名称获取天气.

    Args:
        cityName: 国内城市名称 (例如: 北京, 上海)
    """
    url = f"https://gfeljm.tianqiapi.com/api?unescape=1&version=v63&appid=62421198&appsecret=9OIbgLuO&city={cityName}"
    data = await make_nws_request(url)
    return str(data)


def main():
    """Main entry point for the weather application."""
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()