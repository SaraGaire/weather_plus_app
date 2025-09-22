"""Location service for getting user's current location."""

import requests
from typing import Tuple, Dict
from config.settings import API_CONFIG


class LocationServiceError(Exception):
    """Custom exception for location service errors."""
    pass


class LocationService:
    """Service for getting user's location from IP."""
    
    @staticmethod
    def get_current_location() -> Tuple[float, float, str]:
        """
        Get current location from IP.
        Returns: (latitude, longitude, city_name)
        """
        try:
            response = requests.get(
                "https://ipinfo.io/json",
                timeout=API_CONFIG["TIMEOUT"]
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse location
            location = data.get("loc", "0,0")
            lat, lon = map(float, location.split(","))
            city = data.get("city", "Unknown")
            
            return lat, lon, city
            
        except requests.exceptions.RequestException as e:
            raise LocationServiceError(f"Failed to get location: {str(e)}")
        except (ValueError, KeyError) as e:
            raise LocationServiceError(f"Invalid location data: {str(e)}")
