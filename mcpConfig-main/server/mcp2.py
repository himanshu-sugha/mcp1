from typing import Any, List, Optional, Generator, Union, Dict
import httpx
import json
import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime

# Initialize FastMCP server with basic configuration
mcp = FastMCP(name="mcp-integration")

# Constants with increased timeout
API_TIMEOUT = 60.0  # 60 seconds timeout for all API calls
API_SLOW_ENDPOINT_TIMEOUT = 120.0  # 2 minutes for slow endpoints
WEATHER_API_KEY = "174c5941cd1842f58d475356242605"
WEATHER_API_BASE = "http://api.weatherapi.com/v1"
NWS_API_BASE = "https://api.weather.gov"
MCP2_BASE_URL = "http://34.31.55.189:8080"
PLAYWRIGHT_MCP_URL = "https://playwright-mcp-nttc25y22a-uc.a.run.app"
PROPHET_SERVICE_URL = "http://34.45.252.228:8000"
CODE_EXECUTOR_URL = "http://34.66.53.176:8002"
USER_AGENT = "mcp-integration/1.0"

# Custom progress notification handler
async def send_progress(message: str):
    """Send progress notification in a way compatible with the current FastMCP version."""
    # Log progress to stdout for debugging
    print(f"PROGRESS: {message}")
    # In newer versions of FastMCP, we would use mcp.progress here
    # For now, we'll just log the progress

async def make_api_request(
    url: str, 
    method: str = "GET", 
    json_data: Optional[dict] = None,
    params: Optional[dict] = None,
    progress_callback: Optional[callable] = None
) -> Optional[dict]:
    """Make an API request with extended timeout and error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    
    # Determine if this is a potentially slow endpoint
    is_slow_endpoint = any(keyword in url for keyword in ["enhance", "playwright", "masa", "search", "execute"])
    current_timeout = API_SLOW_ENDPOINT_TIMEOUT if is_slow_endpoint else API_TIMEOUT
    
    # Send initial progress notification
    if progress_callback:
        await progress_callback(f"Starting request to {url}")
    
    # Implementation of exponential backoff for retries
    max_retries = 3 if is_slow_endpoint else 1
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            if retry_count > 0 and progress_callback:
                await progress_callback(f"Retry attempt {retry_count}/{max_retries} for {url}")
            
            async with httpx.AsyncClient(timeout=current_timeout) as client:
                if progress_callback:
                    await progress_callback(f"Connecting to {url}")
                    
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                else:
                    response = await client.post(url, headers=headers, json=json_data)
                
                if progress_callback:
                    await progress_callback(f"Received response from {url} with status {response.status_code}")
                    
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException as e:
            last_error = e
            print(f"Request to {url} timed out after {current_timeout}s on attempt {retry_count + 1}/{max_retries + 1}")
            
            # Increase timeout for next retry
            current_timeout *= 1.5
            
            if retry_count == max_retries:
                print(f"Maximum retries reached for {url}. Last error: {str(e)}")
                break
                
        except httpx.HTTPStatusError as e:
            last_error = e
            print(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
            
            # Don't retry for client errors (4xx)
            if e.response.status_code >= 400 and e.response.status_code < 500:
                break
                
        except Exception as e:
            last_error = e
            print(f"Error making request to {url}: {str(e)}")
            
            # For other errors, we'll retry as well
        
        retry_count += 1
        
        if retry_count <= max_retries:
            # Wait before retrying with exponential backoff
            backoff_time = 2 ** retry_count
            if progress_callback:
                await progress_callback(f"Waiting {backoff_time}s before retry")
            await asyncio.sleep(backoff_time)
    
    if last_error:
        print(f"Final error for {url}: {str(last_error)}")
    
    return None

# Weather API specific request function with progress support
async def weather_api_request(endpoint: str, params: dict) -> Optional[dict]:
    """Make a direct API request to the WeatherAPI.com with minimal overhead and error handling."""
    url = f"{WEATHER_API_BASE}/{endpoint}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    
    # Add API key to params
    params["key"] = WEATHER_API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Weather API error for {url}: {str(e)}")
        return None

# Health Check Endpoints

async def check_mcp2_health() -> str:
    pass

async def check_playwright_health() -> str:
    pass

async def check_prophet_health() -> str:
    pass

async def check_code_executor_health() -> str:
    pass

# MCP-2 Server Endpoints

async def twitter_search(query: str, max_results: int = 5) -> str:
    pass

async def enhance_tweets_masa(query: str, max_results: int = 10, enhance_top_x: int = 5, custom_instruction: Optional[str] = None) -> str:
    pass

async def extract_search_terms(query: str, max_results: int = 10, enhance_top_x: int = 5, custom_instruction: Optional[str] = None) -> str:
    pass

async def enhance_tweets_playwright(tweets: List[dict], custom_instruction: Optional[str] = None) -> str:
    pass

async def enhance_tweets_playright(query: str, max_results: int = 8, enhance_top_x: int = 3, custom_instruction: Optional[str] = None) -> str:
    pass

# Code Executor Endpoints

async def execute_python_code(code: str) -> str:
    pass

async def generate_and_execute(query: str) -> str:
    pass

# Prophet Service Endpoints

async def store_engagement_data(topic: str, platform: str, value: float, source: str = "api", additional_metadata: Optional[dict] = None) -> str:
    pass

async def store_platform_engagements(topic: str, platform_engagements: List[dict]) -> str:
    pass

async def generate_engagement_forecast(topic: str, platform: str = "twitter", periods: int = 7, include_history: bool = True) -> str:
    pass

async def get_topic_history(topic: str, platform: Optional[str] = None) -> str:
    pass

# Original Weather Tools (kept for compatibility)

@mcp.tool()
async def get_weather_forecast(q: str, days: int = 3) -> str:
    """Get a multi-day weather forecast for a location (1-7 days)."""
    if not (1 <= days <= 7):
        return "Days parameter must be between 1 and 7."
    await send_progress(f"Requesting {days}-day forecast for: {q}")
    data = await weather_api_request("forecast.json", {"q": q, "days": days, "aqi": "no", "alerts": "no"})
    if not data or "forecast" not in data or "forecastday" not in data["forecast"]:
        return f"Could not retrieve forecast for '{q}'."
    loc = data.get("location", {})
    days_data = data["forecast"]["forecastday"]
    header = f"Forecast for {loc.get('name', '')}, {loc.get('region', '')}, {loc.get('country', '')}"
    lines = [header, ""]
    for day in days_data:
        d = day.get("date", "?")
        info = day.get("day", {})
        cond = info.get("condition", {})
        lines.append(f"Date: {d}")
        lines.append(f"  - Avg Temp: {info.get('avgtemp_c', 'N/A')}°C / {info.get('avgtemp_f', 'N/A')}°F")
        lines.append(f"  - Condition: {cond.get('text', '')}")
        lines.append(f"  - Max Wind: {info.get('maxwind_kph', 'N/A')} kph")
        lines.append(f"  - Humidity: {info.get('avghumidity', 'N/A')}%")
        lines.append(f"  - Rain: {info.get('daily_chance_of_rain', 'N/A')}% chance")
        lines.append("")
    return "\n".join(lines)

@mcp.tool()
async def get_current_weather(q: str) -> str:
    """Fetches the current weather for a given location using WeatherAPI.com."""
    await send_progress(f"Requesting current weather for: {q}")
    data = await weather_api_request("current.json", {"q": q})
    if not data or "location" not in data or "current" not in data:
        return f"Could not retrieve weather for '{q}'. Please check the location and try again."
    loc = data["location"]
    cur = data["current"]
    cond = cur.get("condition", {})
    summary = [
        f"Weather for {loc.get('name', '')}, {loc.get('region', '')}, {loc.get('country', '')}",
        f"Time: {loc.get('localtime', '')}",
        f"Temperature: {cur.get('temp_c', 'N/A')}°C / {cur.get('temp_f', 'N/A')}°F",
        f"Condition: {cond.get('text', '')}",
        f"Feels Like: {cur.get('feelslike_c', 'N/A')}°C / {cur.get('feelslike_f', 'N/A')}°F",
        f"Wind: {cur.get('wind_kph', 'N/A')} kph ({cur.get('wind_dir', '')})",
        f"Humidity: {cur.get('humidity', 'N/A')}%",
        f"Cloud Cover: {cur.get('cloud', 'N/A')}%",
        f"Precipitation: {cur.get('precip_mm', 'N/A')} mm",
        f"UV Index: {cur.get('uv', 'N/A')}"
    ]
    return "\n".join(summary)

@mcp.tool()
async def get_weather_alerts(area: str) -> str:
    """Get active weather alerts for a location, if any."""
    await send_progress(f"Checking weather alerts for: {area}")
    data = await weather_api_request("forecast.json", {"q": area, "days": 1, "alerts": "yes"})
    alerts = data.get("alerts", {}).get("alert", []) if data else []
    if not alerts:
        return f"No weather alerts for '{area}'."
    lines = [f"Weather Alerts for {area}:"]
    for alert in alerts:
        lines.append(f"- Event: {alert.get('event', 'Unknown')}")
        lines.append(f"  Severity: {alert.get('severity', 'Unknown')}")
        lines.append(f"  Areas: {alert.get('areas', 'Unknown')}")
        lines.append(f"  Effective: {alert.get('effective', 'Unknown')}")
        lines.append(f"  Expires: {alert.get('expires', 'Unknown')}")
        lines.append(f"  Description: {alert.get('desc', 'No description')}")
        lines.append("---")
    return "\n".join(lines)

async def search_locations(q: str) -> str:
    pass

async def get_time_zone(q: str) -> str:
    pass

# Playwright MCP Endpoints

async def get_topic_latest(topic: str) -> str:
    pass

# Debugging

async def debug_last_request() -> str:
    pass

    """
    Get current weather for a location.
    
    Parameters:
    - q: Location query (city name, lat/lon, IP address, US zip, UK postcode, etc.)
    """
    await send_progress(f"Fetching current weather for {q}")
    data = await weather_api_request("current.json", {"q": q})
    
    if not data:
        await send_progress(f"Failed to get current weather for {q}")
        return f"Failed to get current weather for {q}"
    
    await send_progress("Formatting weather data")
    
    location = data.get("location", {})
    weather_info = data.get("current", {})
    weather_desc = weather_info.get("condition", {})

    def format_weather_report(loc, info, desc):
        lines = [
            "Weather Report for {city}, {region}, {country}".format(
                city=loc.get('name', ''), region=loc.get('region', ''), country=loc.get('country', '')),
            "Time: {time}".format(time=loc.get('localtime', '')),
            "Temp: {c}°C | {f}°F".format(c=info.get('temp_c', ''), f=info.get('temp_f', '')),
            "Status: {cond}".format(cond=desc.get('text', '')),
            "Feels Like: {c}°C | {f}°F".format(c=info.get('feelslike_c', ''), f=info.get('feelslike_f', '')),
            "Wind: {kph} kph | {mph} mph ({dirn})".format(kph=info.get('wind_kph', ''), mph=info.get('wind_mph', ''), dirn=info.get('wind_dir', '')),
            "Humidity: {humidity}%".format(humidity=info.get('humidity', '')),
            "Clouds: {cloud}%".format(cloud=info.get('cloud', '')),
            "Rain: {mm} mm | {inch} in".format(mm=info.get('precip_mm', ''), inch=info.get('precip_in', '')),
            "UV: {uv}".format(uv=info.get('uv', ''))
        ]
        return "\n".join(lines)

    report = format_weather_report(location, weather_info, weather_desc)
    await send_progress("Completed")
    return report


    """
    Get weather forecast for a location.
    
    Parameters:
    - q: Location query (city name, lat/lon, IP address, US zip, UK postcode, etc.)
    - days: Number of days for forecast (1-14)
    """
    if days < 1 or days > 14:
        await send_progress("Invalid days parameter")
        return "Days parameter must be between 1 and 14"
    
    await send_progress(f"Fetching {days}-day forecast for {q}")
    data = await weather_api_request("forecast.json", {"q": q, "days": days, "aqi": "yes", "alerts": "yes"})
    
    if not data:
        await send_progress(f"Failed to get weather forecast for {q}")
        return f"Failed to get weather forecast for {q}"
    
    await send_progress("Processing forecast data")
    
    location = data.get("location", {})
    current = data.get("current", {})
    forecast = data.get("forecast", {})
    alerts = data.get("alerts", {})
    
    # Format current weather
    await send_progress("Formatting current weather")
    current_condition = current.get("condition", {})
    current_weather = f"""Current Weather for {location.get('name', '')}, {location.get('region', '')}, {location.get('country', '')}:
Local Time: {location.get('localtime', '')}
Temperature: {current.get('temp_c', '')}°C / {current.get('temp_f', '')}°F
Condition: {current_condition.get('text', '')}
Feels Like: {current.get('feelslike_c', '')}°C / {current.get('feelslike_f', '')}°F
Wind: {current.get('wind_kph', '')} kph / {current.get('wind_mph', '')} mph, direction {current.get('wind_dir', '')}
Humidity: {current.get('humidity', '')}%
"""
    
    # Format forecast days
    await send_progress("Formatting forecast days")
    forecast_days = []
    for day in forecast.get("forecastday", []):
        day_date = day.get("date", "")
        day_data = day.get("day", {})
        day_condition = day_data.get("condition", {})
        
        forecast_days.append(f"""Date: {day_date}
Min/Max Temp: {day_data.get('mintemp_c', '')}°C to {day_data.get('maxtemp_c', '')}°C / {day_data.get('mintemp_f', '')}°F to {day_data.get('maxtemp_f', '')}°F
Condition: {day_condition.get('text', '')}
Chance of Rain: {day_data.get('daily_chance_of_rain', '')}%
Max Wind: {day_data.get('maxwind_kph', '')} kph / {day_data.get('maxwind_mph', '')} mph
Avg Humidity: {day_data.get('avghumidity', '')}%
UV Index: {day_data.get('uv', '')}
""")
    
    # Format alerts if any
    await send_progress("Checking for weather alerts")
    alert_text = ""
    alert_list = alerts.get("alert", [])
    if alert_list:
        alert_items = []
        for alert in alert_list:
            alert_items.append(f"""Alert: {alert.get('headline', '')}
Category: {alert.get('category', '')}
Severity: {alert.get('severity', '')}
Urgency: {alert.get('urgency', '')}
Areas: {alert.get('areas', '')}
Effective: {alert.get('effective', '')}
Expires: {alert.get('expires', '')}
Description: {alert.get('desc', '')}
""")
        alert_text = "Weather Alerts:\n" + "\n".join(alert_items)
    
    await send_progress("Forecast data ready")
    return current_weather + "\n\nForecast:\n" + "\n".join(forecast_days) + "\n\n" + alert_text


    """
    Search for locations using Weather API.
    
    Parameters:
    - q: Location search query (city or partial name)
    """
    await send_progress(f"Searching for locations matching '{q}'")
    data = await weather_api_request("search.json", {"q": q})
    
    if not data:
        await send_progress(f"No locations found for '{q}'")
        return f"No locations found for '{q}'"
    
    if not isinstance(data, list):
        await send_progress(f"Invalid response format: {data}")
        return f"Invalid response format for location search: {data}"
    
    if not data:
        await send_progress(f"No locations found matching '{q}'")
        return f"No locations found matching '{q}'"
    
    await send_progress(f"Found {len(data)} locations, formatting results")
    
    locations = []
    for location in data:
        locations.append(f"""{location.get('name', '')}, {location.get('region', '')}, {location.get('country', '')}
Coordinates: {location.get('lat', '')}, {location.get('lon', '')}
ID: {location.get('id', '')}
""")
    
    await send_progress("Search completed")
    return f"Found {len(locations)} locations matching '{q}':\n\n" + "\n".join(locations)


    """
    Get timezone information for a location.
    
    Parameters:
    - q: Location query (city name, lat/lon, IP address, US zip, UK postcode, etc.)
    """
    await send_progress(f"Fetching timezone data for {q}")
    data = await weather_api_request("timezone.json", {"q": q})
    
    if not data:
        await send_progress(f"Failed to get timezone information for {q}")
        return f"Failed to get timezone information for {q}"
    
    await send_progress("Formatting timezone data")
    
    location = data.get("location", {})
    
    result = f"""Timezone Information for {location.get('name', '')}, {location.get('region', '')}, {location.get('country', '')}:
Timezone: {location.get('tz_id', '')}
Local Time: {location.get('localtime', '')}
Latitude: {location.get('lat', '')}
Longitude: {location.get('lon', '')}
"""
    
    await send_progress("Timezone data ready")
    return result

if __name__ == "__main__":
    print("Starting MCP Integration Server with stdio transport...")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error with stdio transport: {e}")
        print("Trying HTTP transport...")
        try:
            mcp.run(transport="http", port=8000)
        except Exception as e2:
            print(f"Error with HTTP transport: {e2}")
            print("Trying WebSocket transport...")
            mcp.run(transport="ws", port=8001)