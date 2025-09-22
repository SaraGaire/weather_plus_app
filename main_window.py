"""Main window UI for the Weather App."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QCompleter, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont
from typing import Dict

from services.weather_api import WeatherAPI, WeatherAPIError
from services.location_service import LocationService, LocationServiceError
from config.settings import get_config
from utils.helpers import get_weather_emoji
from ui.styles import get_stylesheet


class WeatherWorker(QThread):
    """Worker thread for API calls to prevent UI freezing."""
    
    weather_data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api: WeatherAPI, city: str = None, coordinates: tuple = None):
        super().__init__()
        self.api = api
        self.city = city
        self.coordinates = coordinates
    
    def run(self):
        """Run the weather API call in background."""
        try:
            if self.city:
                data = self.api.get_weather_by_city(self.city)
            elif self.coordinates:
                lat, lon = self.coordinates
                data = self.api.get_weather_by_coordinates(lat, lon)
            else:
                raise WeatherAPIError("No city or coordinates provided")
                
            self.weather_data_ready.emit(data)
            
        except WeatherAPIError as e:
            self.error_occurred.emit(str(e))


class WeatherMainWindow(QWidget):
    """Main window for the Weather App."""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.api = WeatherAPI()
        self.location_service = LocationService()
        self.worker = None
        
        self.init_ui()
        self.setup_auto_refresh()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.config["ui"]["WINDOW_TITLE"])
        self.setFixedSize(*self.config["ui"]["WINDOW_SIZE"])
        
        # Set application icon
        icon_path = self.config["ui"]["ICON_PATH"]
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Create widgets
        self.create_widgets()
        self.setup_layout()
        self.setup_styles()
        self.connect_signals()
    
    def create_widgets(self):
        """Create all UI widgets."""
        # Input section
        self.city_label = QLabel("Enter City Name:")
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., London, Tokyo, New York...")
        
        # Setup autocomplete
        completer = QCompleter(self.config["cities"])
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.city_input.setCompleter(completer)
        
        # Buttons
        self.search_button = QPushButton("🔍 Get Weather")
        self.location_button = QPushButton("📍 My Location")
        self.refresh_button = QPushButton("🔄 Refresh")
        
        # Display section
        self.city_display = QLabel("Weather Anytime")
        self.temperature_label = QLabel("--°C")
        self.emoji_label = QLabel("🌤️")
        self.description_label = QLabel("Select a city to see weather")
        self.details_label = QLabel("")
        
        # Status
        self.status_label = QLabel("Ready")
    
    def setup_layout(self):
        """Setup the widget layout."""
        layout = QVBoxLayout()
        
        # Header
        layout.addWidget(self.city_display)
        layout.addSpacing(20)
        
        # Input section
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.city_label)
        input_layout.addWidget(self.city_input)
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.location_button)
        button_layout.addWidget(self.refresh_button)
        
        # Weather display
        weather_layout = QVBoxLayout()
        weather_layout.addWidget(self.temperature_label)
        weather_layout.addWidget(self.emoji_label)
        weather_layout.addWidget(self.description_label)
        weather_layout.addWidget(self.details_label)
        
        # Add to main layout
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addSpacing(30)
        layout.addLayout(weather_layout)
        layout.addStretch()
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Center align labels
        for label in [self.city_display, self.temperature_label, 
                     self.emoji_label, self.description_label]:
            label.setAlignment(Qt.AlignCenter)
    
    def setup_styles(self):
        """Apply styles to the application."""
        self.setStyleSheet(get_stylesheet())
        
        # Set object names for CSS targeting
        self.city_display.setObjectName("cityDisplay")
        self.temperature_label.setObjectName("temperatureLabel")
        self.emoji_label.setObjectName("emojiLabel")
        self.description_label.setObjectName("descriptionLabel")
        self.status_label.setObjectName("statusLabel")
    
    def connect_signals(self):
        """Connect widget signals to methods."""
        self.search_button.clicked.connect(self.search_weather)
        self.location_button.clicked.connect(self.get_location_weather)
        self.refresh_button.clicked.connect(self.refresh_current)
        self.city_input.returnPressed.connect(self.search_weather)
    
    def setup_auto_refresh(self):
        """Setup automatic refresh timer."""
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.auto_refresh)
        # Refresh every 10 minutes
        self.auto_refresh_timer.start(600000)
        
        self.current_weather_data = None
    
    def search_weather(self):
        """Search for weather by city name."""
        city = self.city_input.text().strip()
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.set_loading_state("Searching for weather...")
        self.worker = WeatherWorker(self.api, city=city)
        self.worker.weather_data_ready.connect(self.display_weather)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()
    
    def get_location_weather(self):
        """Get weather for user's current location."""
        self.set_loading_state("Getting your location...")
        
        try:
            lat, lon, city = self.location_service.get_current_location()
            self.worker = WeatherWorker(self.api, coordinates=(lat, lon))
            self.worker.weather_data_ready.connect(self.display_weather)
            self.worker.error_occurred.connect(self.show_error)
            self.worker.start()
            
        except LocationServiceError as e:
            self.show_error(f"Location error: {str(e)}")
    
    def refresh_current(self):
        """Refresh current weather data."""
        if self.current_weather_data:
            city = self.current_weather_data.get("city")
            if city:
                self.city_input.setText(city)
                self.search_weather()
    
    def auto_refresh(self):
        """Auto refresh current weather silently."""
        if self.current_weather_data:
            city = self.current_weather_data.get("city")
            if city:
                # Silent refresh without loading state
                worker = WeatherWorker(self.api, city=city)
                worker.weather_data_ready.connect(self.display_weather)
                worker.start()
    
    def display_weather(self, data: Dict):
        """Display weather data on the UI."""
        self.current_weather_data = data
        
        # Update city display
        city_text = data["city"]
        if data["country"]:
            city_text += f", {data['country']}"
        self.city_display.setText(city_text)
        
        # Update temperature
        self.temperature_label.setText(f"{data['temperature']}°C")
        
        # Update emoji
        emoji = get_weather_emoji(data["weather_id"])
        self.emoji_label.setText(emoji)
        
        # Update description
        self.description_label.setText(data["description"])
        
        # Update details
        details = (
            f"Feels like: {data['feels_like']}°C\n"
            f"Humidity: {data['humidity']}%\n"
            f"Wind: {data['wind_speed']} m/s"
        )
        if data.get("pressure"):
            details += f"\nPressure: {data['pressure']} hPa"
        
        self.details_label.setText(details)
        
        # Update status
        timestamp = data["timestamp"].strftime("%H:%M")
        self.status_label.setText(f"Last updated: {timestamp}")
        
        self.set_normal_state()
    
    def show_error(self, error_message: str):
        """Display error message."""
        self.temperature_label.setText("Error")
        self.temperature_label.setStyleSheet("color: #ff6b6b;")
        self.emoji_label.setText("❌")
        self.description_label.setText(error_message)
        self.details_label.clear()
        self.status_label.setText("Error occurred")
        
        self.set_normal_state()
    
    def set_loading_state(self, message: str):
        """Set UI to loading state."""
        self.search_button.setEnabled(False)
        self.location_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.status_label.setText(message)
    
    def set_normal_state(self):
        """Reset UI to normal state."""
        self.search_button.setEnabled(True)
        self.location_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        self.temperature_label.setStyleSheet("")  # Reset error color
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()
