"""A simple configuration setting for the app."""

import os
from pathlib import Path
from typing import Dict, Any

# Base directory
BASE_DIR = Path(__file__).parent.parent

# API Configuration
API_CONFIG = {
    "OPENWEATHER_API_KEY": os.getenv("OPENWEATHER_API_KEY", ""),
    "BASE_URL": "https://api.openweathermap.org/data/2.5",
    "TIMEOUT": 10,
    "UNITS": "metric"  # metric, imperial, kelvin
}

# UI Configuration
UI_CONFIG = {
    "WINDOW_TITLE": "Weather Anytime",
    "WINDOW_SIZE": (500, 600),
    "THEME": "dark",  # dark, light
    "FONT_FAMILY": "Arial",
    "ICON_PATH": BASE_DIR / "assets" / "icons" / "weather_icon.png"
}

# Default cities for autocomplete
DEFAULT_CITIES = [
    "New York", "Los Angeles", "London", "Tokyo", 
    "Delhi", "Sydney", "Paris", "Berlin", "Moscow"
]

# Cache settings
CACHE_CONFIG = {
    "ENABLED": True,
    "CACHE_DURATION": 300,  # 5 minutes in seconds
    "MAX_CACHE_SIZE": 100
}

def get_config() -> Dict[str, Any]:
    """Get all configuration settings."""
    return {
        "api": API_CONFIG,
        "ui": UI_CONFIG,
        "cities": DEFAULT_CITIES,
        "cache": CACHE_CONFIG
    }
