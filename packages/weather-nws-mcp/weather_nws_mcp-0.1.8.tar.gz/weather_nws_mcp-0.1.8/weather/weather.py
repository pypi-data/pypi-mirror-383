"""A Python package for accessing weather data from the National Weather Service (NWS) API."""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP()

# Constants


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API."""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


async def make_fuxizhiku_request(title: str) -> dict[str, Any]:
    """Make a request to the Fuxizhiku API with specified parameters."""

    url = "https://adminapi.fuxizhiku.org.cn/fxkb/api/index/search"

    # 构建请求头
    headers = {
        "accept": "*/*",
        "accept-language": "zh",
        "apiversion": "/v2/",
        "appname": "fuxi_data",
        "appsource": "1",
        "appversion": "3.2.3",
        "authorization": "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozMTYsInVzZXJfbmFtZSI6IjE1ODEwNTM4NTkzIiwiZXhwIjoxNzYwODYzMTg3LCJpc3MiOiJmdXhpIn0.wPhSOdKTOFnDx5_6QnBQdvLbY2zvx0H7ATTnsvanxDI",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "devicetype": "Web",
        "origin": "https://viv.cn",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://viv.cn/",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "shortversion": "",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "userid": "316",
        "x-lng": "zh"
    }

    # 请求数据
    data = {
        "dataType": 14,
        "keyword": title,
        "pageNum": 1,
        "pageSize": 20
    }

    async with httpx.AsyncClient() as client:
        try:
            # 发送POST请求，包含headers和data
            response = await client.post(
                url,
                headers=headers,
                json=data,  # 使用json参数自动处理JSON序列化
                timeout=30.0
            )
            response.raise_for_status()  # 检查HTTP错误状态码
            json = response.json()
            arr = json["data"]["commonData"]
            # 将title 创建一个数组返回
            return [item["title"] for item in arr]

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



@mcp.tool()
async def get_policy(title: str) -> str:
    """通过政策关键字获取政策内容

    Args:
        title: 提取政策关键字
    """
    data = await make_fuxizhiku_request(title)
    return str(data)

import asyncio
def main():
    """Main entry point for the weather application."""
    # Initialize and run the server
    mcp.run(transport='stdio')
    # mcp.run(transport='sse')
    # mcp.run(transport="streamable-http", mount_path="/mcp")

if __name__ == "__main__":
    main()
    # 运行make_fuxizhiku_request 函数
