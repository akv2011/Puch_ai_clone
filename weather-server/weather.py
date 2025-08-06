import logging
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    try:
        # Get grid point from NWS API
        async with httpx.AsyncClient() as client:
            # First, get the grid point
            grid_response = await client.get(
                f"https://api.weather.gov/points/{latitude},{longitude}",
                headers={"User-Agent": "WeatherMCP/1.0"}
            )
            grid_response.raise_for_status()
            grid_data = grid_response.json()
            
            # Get the forecast URL
            forecast_url = grid_data["properties"]["forecast"]
            
            # Get the actual forecast
            forecast_response = await client.get(
                forecast_url,
                headers={"User-Agent": "WeatherMCP/1.0"}
            )
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Format the forecast
            periods = forecast_data["properties"]["periods"][:5]  # Get first 5 periods
            
            result = f"🌤️ Weather Forecast for {latitude}, {longitude}\n\n"
            for period in periods:
                result += f"**{period['name']}**\n"
                result += f"🌡️ {period['temperature']}°{period['temperatureUnit']}\n"
                result += f"📝 {period['shortForecast']}\n"
                result += f"💨 {period.get('windSpeed', 'N/A')} {period.get('windDirection', '')}\n\n"
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        return f"❌ Error getting weather forecast: {str(e)}"

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.weather.gov/alerts/active?area={state.upper()}",
                headers={"User-Agent": "WeatherMCP/1.0"}
            )
            response.raise_for_status()
            data = response.json()
            
            alerts = data.get("features", [])
            
            if not alerts:
                return f"✅ No active weather alerts for {state.upper()}"
            
            result = f"⚠️ Active Weather Alerts for {state.upper()}\n\n"
            
            for alert in alerts[:5]:  # Limit to 5 alerts
                properties = alert["properties"]
                result += f"🚨 **{properties.get('event', 'Unknown')}**\n"
                result += f"📍 Area: {properties.get('areaDesc', 'Unknown')}\n"
                result += f"⏰ Effective: {properties.get('effective', 'Unknown')}\n"
                result += f"📝 {properties.get('headline', 'No details available')}\n\n"
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting weather alerts: {e}")
        return f"❌ Error getting weather alerts: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting Weather MCP Server")
    mcp.run(transport='stdio')
