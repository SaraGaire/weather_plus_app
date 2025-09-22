import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import WeatherMainWindow


def main():
    """Main function to run the weather application."""
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setApplicationName("Weather App")
    app.setApplicationVersion("2.0")
    
    window = WeatherMainWindow()
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
