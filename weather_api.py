""" A SIMPLE Weather API service for fetching weather data in the program."""

import requests
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from config.settings import API_CONFIG
from utils.constants import WEATHER_CODES


class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""
    pass


class WeatherAPI:
    """Service class for interacting with OpenWeatherMap API."""
    
    def __init__(self):
        self.api_key = API_CONFIG["OPENWEATHER_API_KEY"]
        self.base_url = API_CONFIG["BASE_URL"]
        self.timeout = API_CONFIG["TIMEOUT"]
        self.units = API_CONFIG["UNITS"]
        self._cache = {}
    
    def get_weather_by_city(self, city: str) -> Dict:
        """Get weather data for a specific city."""
        if not city.strip():
            raise WeatherAPIError("City name cannot be empty")
        
        cache_key = f"city_{city.lower()}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "units": self.units,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get("cod") == 200:
                processed_data = self._process_weather_data(data)
                self._cache_data(cache_key, processed_data)
                return processed_data
            else:
                raise WeatherAPIError(f"API Error: {data.get('message', 'Unknown error')}")
                
        except requests.exceptions.Timeout:
            raise WeatherAPIError("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("No internet connection.")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """Get weather data for specific coordinates."""
        cache_key = f"coords_{lat}_{lon}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "units": self.units,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            processed_data = self._process_weather_data(data)
            self._cache_data(cache_key, processed_data)
            return processed_data
            
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Failed to get weather data: {str(e)}")
    
    def _process_weather_data(self, raw_data: Dict) -> Dict:
        """Process raw API data into a clean format."""
        weather = raw_data["weather"][0]
        main = raw_data["main"]
        wind = raw_data.get("wind", {})
        
        return {
            "city": raw_data.get("name", "Unknown"),
            "country": raw_data.get("sys", {}).get("country", ""),
            "temperature": round(main["temp"]),
            "feels_like": round(main["feels_like"], 1),
            "humidity": main["humidity"],
            "pressure": main.get("pressure", 0),
            "wind_speed": wind.get("speed", 0),
            "wind_direction": wind.get("deg", 0),
            "description": weather["description"].title(),
            "weather_id": weather["id"],
            "icon": weather["icon"],
            "timestamp": datetime.now()
        }
    
    def _cache_data(self, key: str, data: Dict):
        """Cache weather data with timestamp."""
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data if it's still valid."""
        if key not in self._cache:
            return None
        
        cache_entry = self._cache[key]
        cache_age = datetime.now() - cache_entry["timestamp"]
        
        if cache_age > timedelta(seconds=300):  # 5 minutes
            del self._cache[key]
            return None
        
        return cache_entry["data"]
