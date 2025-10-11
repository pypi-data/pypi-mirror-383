
# MCP-compliant server using FastMCP
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

WEATHER_API_URL = "http://temp-ute.home"


async def fetch_weather_data() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_API_URL, timeout=5.0)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def temperature() -> float:
    """Get the current temperature in Celsius."""
    data = await fetch_weather_data()
    return data.get("TemperatureC")


@mcp.tool()
async def humidity() -> float:
    """Get the current humidity percentage."""
    data = await fetch_weather_data()
    return data.get("Humidity%")


@mcp.tool()
async def pressure() -> float:
    """Get the current pressure in hPa."""
    data = await fetch_weather_data()
    return data.get("Pressure_hPa")


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
