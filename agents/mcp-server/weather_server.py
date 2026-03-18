#!/usr/bin/env python3
"""weather_server.py - MCP server for weather information"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio


# Create server instance
server = Server("weather-server")


# ==================== Weather Tools ====================

@server.tool()
async def get_current_weather(city: str, country_code: Optional[str] = None) -> str:
    """Get current weather for a city.
    
    Args:
        city: City name (e.g., "London")
        country_code: Optional country code (e.g., "UK" for United Kingdom)
    """
    try:
        # Using OpenWeatherMap API (free tier)
        # Note: In production, you should use environment variables for API keys
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo")
        
        if api_key == "demo":
            # Demo mode - return mock data
            return f"""🌤️ Weather for {city}{f', {country_code}' if country_code else ''} (Demo Mode):

Current: 22°C (72°F)
Condition: Partly Cloudy
Humidity: 65%
Wind: 12 km/h
Pressure: 1013 hPa
Visibility: 10 km

Note: Using demo data. Set OPENWEATHER_API_KEY environment variable for real data."""
        
        # Build query
        query = city
        if country_code:
            query += f",{country_code}"
        
        # Make API request
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": query,
            "appid": api_key,
            "units": "metric"  # Use metric units
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Parse response
        temp_c = data["main"]["temp"]
        temp_f = (temp_c * 9/5) + 32
        feels_like_c = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        description = data["weather"][0]["description"].title()
        visibility = data.get("visibility", "N/A")
        
        if visibility != "N/A":
            visibility = f"{visibility/1000:.1f} km"
        
        result = f"""🌤️ Weather for {data['name']}, {data['sys']['country']}:

Current: {temp_c:.1f}°C ({temp_f:.1f}°F)
Feels like: {feels_like_c:.1f}°C
Condition: {description}
Humidity: {humidity}%
Wind: {wind_speed} m/s
Pressure: {pressure} hPa
Visibility: {visibility}"""
        
        return result
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "Error: Invalid API key. Please set OPENWEATHER_API_KEY environment variable."
        elif e.response.status_code == 404:
            return f"Error: City '{city}' not found."
        else:
            return f"HTTP Error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Error getting weather: {e}"


@server.tool()
async def get_weather_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.
    
    Args:
        city: City name
        days: Number of days to forecast (1-5, default: 3)
    """
    try:
        # Limit days to 1-5
        days = max(1, min(5, days))
        
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo")
        
        if api_key == "demo":
            # Demo mode
            forecast_days = []
            for i in range(days):
                date = datetime.now().date()
                forecast_days.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "temp_min": 18 + i,
                    "temp_max": 25 + i,
                    "condition": ["Sunny", "Partly Cloudy", "Cloudy"][i % 3]
                })
            
            result = f"🌤️ {days}-Day Forecast for {city} (Demo Mode):\n\n"
            for day in forecast_days:
                result += f"{day['date']}: {day['condition']}, {day['temp_min']}°C - {day['temp_max']}°C\n"
            
            result += "\nNote: Using demo data. Set OPENWEATHER_API_KEY for real forecast."
            return result
        
        # Get forecast from OpenWeatherMap
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "cnt": days * 8  # 8 forecasts per day
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Group forecasts by day
        forecasts_by_day = {}
        for forecast in data["list"]:
            date = forecast["dt_txt"].split()[0]
            if date not in forecasts_by_day:
                forecasts_by_day[date] = {
                    "temps": [],
                    "conditions": []
                }
            
            forecasts_by_day[date]["temps"].append(forecast["main"]["temp"])
            forecasts_by_day[date]["conditions"].append(forecast["weather"][0]["description"])
        
        # Calculate daily stats
        result = f"🌤️ {days}-Day Forecast for {data['city']['name']}, {data['city']['country']}:\n\n"
        
        for i, (date, stats) in enumerate(list(forecasts_by_day.items())[:days]):
            avg_temp = sum(stats["temps"]) / len(stats["temps"])
            # Get most common condition
            from collections import Counter
            most_common_condition = Counter(stats["conditions"]).most_common(1)[0][0]
            
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            
            result += f"{day_name} ({date}): {most_common_condition.title()}, ~{avg_temp:.1f}°C avg\n"
        
        return result
        
    except Exception as e:
        return f"Error getting forecast: {e}"


@server.tool()
async def convert_temperature(value: float, from_unit: str = "c", to_unit: str = "f") -> str:
    """Convert temperature between units.
    
    Args:
        value: Temperature value
        from_unit: Source unit ("c" for Celsius, "f" for Fahrenheit, "k" for Kelvin)
        to_unit: Target unit ("c" for Celsius, "f" for Fahrenheit, "k" for Kelvin)
    """
    try:
        # Normalize unit names
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Convert to Kelvin first (standard unit)
        if from_unit == "c":
            kelvin = value + 273.15
        elif from_unit == "f":
            kelvin = (value - 32) * 5/9 + 273.15
        elif from_unit == "k":
            kelvin = value
        else:
            return f"Error: Invalid source unit '{from_unit}'. Use 'c', 'f', or 'k'."
        
        # Convert from Kelvin to target unit
        if to_unit == "c":
            result = kelvin - 273.15
            unit_name = "°C"
        elif to_unit == "f":
            result = (kelvin - 273.15) * 9/5 + 32
            unit_name = "°F"
        elif to_unit == "k":
            result = kelvin
            unit_name = "K"
        else:
            return f"Error: Invalid target unit '{to_unit}'. Use 'c', 'f', or 'k'."
        
        from_unit_name = {"c": "°C", "f": "°F", "k": "K"}[from_unit]
        
        return f"{value}{from_unit_name} = {result:.2f}{unit_name}"
        
    except Exception as e:
        return f"Error converting temperature: {e}"


@server.tool()
async def get_air_quality(city: str) -> str:
    """Get air quality information for a city.
    
    Args:
        city: City name
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo")
        
        if api_key == "demo":
            return f"""🌫️ Air Quality for {city} (Demo Mode):

AQI: 45 (Good)
PM2.5: 12 µg/m³
PM10: 25 µg/m³
Ozone: 45 ppb
NO₂: 15 ppb
SO₂: 3 ppb

Note: Using demo data. Set OPENWEATHER_API_KEY for real air quality data."""
        
        # First get city coordinates
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {
            "q": city,
            "limit": 1,
            "appid": api_key
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get coordinates
            geo_response = await client.get(geo_url, params=geo_params)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                return f"Error: City '{city}' not found."
            
            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]
            
            # Get air quality
            aqi_url = "http://api.openweathermap.org/data/2.5/air_pollution"
            aqi_params = {
                "lat": lat,
                "lon": lon,
                "appid": api_key
            }
            
            aqi_response = await client.get(aqi_url, params=aqi_params)
            aqi_response.raise_for_status()
            aqi_data = aqi_response.json()
        
        # Parse AQI data
        aqi = aqi_data["list"][0]["main"]["aqi"]
        components = aqi_data["list"][0]["components"]
        
        # AQI descriptions
        aqi_levels = {
            1: "Good",
            2: "Fair", 
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        
        result = f"""🌫️ Air Quality for {geo_data[0]['name']}, {geo_data[0]['country']}:

AQI: {aqi} ({aqi_levels.get(aqi, "Unknown")})
PM2.5: {components.get('pm2_5', 'N/A')} µg/m³
PM10: {components.get('pm10', 'N/A')} µg/m³
Ozone: {components.get('o3', 'N/A')} µg/m³
NO₂: {components.get('no2', 'N/A')} µg/m³
SO₂: {components.get('so2', 'N/A')} µg/m³
CO: {components.get('co', 'N/A')} µg/m³"""
        
        return result
        
    except Exception as e:
        return f"Error getting air quality: {e}"


@server.tool()
async def compare_weather(city1: str, city2: str) -> str:
    """Compare weather between two cities.
    
    Args:
        city1: First city name
        city2: Second city name
    """
    try:
        # Get weather for both cities
        weather1 = await get_current_weather(city1)
        weather2 = await get_current_weather(city2)
        
        # Extract temperatures (simplified parsing for demo)
        import re
        
        def extract_temp(text):
            match = re.search(r'Current:\s*([\d.-]+)°C', text)
            return float(match.group(1)) if match else None
        
        temp1 = extract_temp(weather1)
        temp2 = extract_temp(weather2)
        
        if temp1 is not None and temp2 is not None:
            diff = temp1 - temp2
            if diff > 0:
                comparison = f"{city1} is {diff:.1f}°C warmer than {city2}"
            elif diff < 0:
                comparison = f"{city1} is {abs(diff):.1f}°C cooler than {city2}"
            else:
                comparison = f"Both cities have the same temperature"
        else:
            comparison = "Could not extract temperature for comparison"
        
        result = f"🌡️ Weather Comparison:\n\n"
        result += f"{city1}:\n{weather1[:200]}...\n\n"
        result += f"{city2}:\n{weather2[:200]}...\n\n"
        result += f"Comparison: {comparison}"
        
        return result
        
    except Exception as e:
        return f"Error comparing weather: {e}"


# ==================== Resources ====================

@server.resource("weather://current/{city}")
async def current_weather_resource(city: str) -> str:
    """Get current weather as a resource."""
    return await get_current_weather(city)


@server.resource("weather://forecast/{city}/{days}")
async def forecast_resource(city: str, days: str) -> str:
    """Get weather forecast as a resource."""
    try:
        return await get_weather_forecast(city, int(days))
    except:
        return await get_weather_forecast(city, 3)


# ==================== Main Server Loop ====================

async def main():
    """Run the MCP server."""
    import sys
    
    print(f"Starting Weather MCP server...", file=sys.stderr)
    print(f"Available tools:", file=sys.stderr)
    
    tools = [
        "get_current_weather",
        "get_weather_forecast",
        "convert_temperature",
        "get_air_quality",
        "compare_weather"
    ]
    
    for tool in tools:
        print(f"  - {tool}", file=sys.stderr)
    
    print(f"\nNote: Set OPENWEATHER_API_KEY environment variable for real data", file=sys.stderr)
    print(f"Server ready. Waiting for connections...", file=sys.stderr)
    
    # Run the server
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    asyncio.run(main())