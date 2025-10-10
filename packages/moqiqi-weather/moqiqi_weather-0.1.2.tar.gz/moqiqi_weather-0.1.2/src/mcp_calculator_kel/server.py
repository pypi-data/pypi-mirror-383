from mcp.server.fastmcp.server import FastMCP
import requests

mcp = FastMCP("WeatherService")

@mcp.tool()
def weather(city: str = "Beijing") -> str:
    """
    获取指定城市的实时天气信息
    Args:
        city: 城市名称（支持中文/英文，例如 Beijing 或 北京）
    Returns:
        天气情况的简要文本
    """
    url = f"https://wttr.in/{city}?format=3"  # 只返回简短天气，例如 "Beijing: 🌦 +20°C"
    headers = {"User-Agent": "curl/7.68.0"}   # wttr.in 推荐使用 curl UA
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return f"查询失败: {res.status_code}"
    return res.text.strip()

if __name__ == "__main__":
    mcp.run(transport="stdio")



