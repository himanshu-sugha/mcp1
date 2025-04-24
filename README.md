# MCP Integration Server

A FastMCP server plugin providing real-time weather data via WeatherAPI.com.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/antoniogarrote/uv) package manager
- Windows OS (Linux/macOS also supported)

## Installation

1. Create and activate a virtual environment:

```bash
uv venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate   # macOS/Linux
```

2. Install dependencies:

```bash
uv add "mcp[cli]" httpx
```

## Features

### Weather Tools

- `get_current_weather(q: str) -> str`
  Fetch current weather for a given location.

- `get_weather_forecast(q: str, days: int) -> str`
  Retrieve a multi-day forecast (1–7 days).

- `get_weather_alerts(area: str) -> str`
  List active weather alerts for a location.

## Usage

### Development (with MCP Inspector)

```bash
uv run mcp dev server/mcp2.py
```

Open your MCP client (e.g., VS Code extension) and click **Tool List** to view and invoke the weather tools.

### Production

```bash
uv run mcp run server/mcp2.py
```

## Configuration

- `WEATHER_API_KEY` is defined in `server/mcp2.py` for WeatherAPI.com.
- Other service endpoints (`PLAYWRIGHT_MCP_URL`, `PROPHET_SERVICE_URL`, `CODE_EXECUTOR_URL`) live in `server/mcp2.py`.

