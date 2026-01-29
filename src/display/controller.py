"""
Display controller
Manages weather data updates and display modes
"""
import time
from typing import Optional
from ..weather.weather_fetcher import WeatherFetcher, get_weather_icon
from ..graphics.renderer import DisplayRenderer


class DisplayController:
    """Controls the weather display and updates"""

    def __init__(
        self,
        display,
        airport_code: str,
        api_token: Optional[str] = None,
        update_interval: int = 300
    ):
        """
        Initialize display controller
        Args:
            display: Display instance (hardware or simulator)
            airport_code: ICAO airport code
            api_token: Optional AVWX API token
            update_interval: Seconds between weather updates
        """
        self.display = display
        self.airport_code = airport_code.upper()
        self.update_interval = update_interval

        self.weather_fetcher = WeatherFetcher(api_token)
        self.renderer = DisplayRenderer()

        self.current_weather = None
        self.current_taf = None
        self.last_update = 0
        self.animation_frame = 0
        self.display_mode = 0  # 0 = METAR, 1 = TAF
        self.mode_timer = 0

    def update(self):
        """Update weather data if needed"""
        current_time = time.time()

        # Check if we need to update weather data
        if current_time - self.last_update >= self.update_interval:
            print(f"Fetching weather for {self.airport_code}...")
            self.current_weather = self.weather_fetcher.get_metar(self.airport_code)
            self.current_taf = self.weather_fetcher.get_taf(self.airport_code)
            self.last_update = current_time

            if self.current_weather:
                print(f"Weather updated: {self.current_weather.get('flight_rules', 'N/A')}")
            else:
                print("Failed to fetch weather data")

            if self.current_taf:
                print(f"TAF updated: {len(self.current_taf.get('forecast', []))} periods")

    def render(self):
        """Render current display - alternates between METAR and TAF"""
        if not self.current_weather:
            # Show loading/startup screen
            img = self.renderer.create_startup_display(f"LOADING {self.airport_code}")
            self.display.show_image(img)
            return

        # Alternate between METAR and TAF every 5 seconds
        self.mode_timer += 1
        if self.mode_timer >= 150:  # 5 seconds at 30fps
            self.display_mode = 1 - self.display_mode
            self.mode_timer = 0

        # Render appropriate screen
        if self.display_mode == 0:
            # METAR screen
            img = self.renderer.create_metar_display(
                station=self.current_weather.get('station', self.airport_code),
                temperature=self.current_weather.get('temperature'),
                dewpoint=self.current_weather.get('dewpoint'),
                wind_speed=self.current_weather.get('wind_speed'),
                wind_direction=self.current_weather.get('wind_direction'),
                visibility=self.current_weather.get('visibility'),
                ceiling=self.current_weather.get('ceiling'),
                flight_rules=self.current_weather.get('flight_rules', 'UNKNOWN'),
                conditions=self.current_weather.get('conditions', []),
                frame=self.animation_frame
            )
        else:
            # TAF screen
            img = self.renderer.create_taf_display(
                station=self.current_weather.get('station', self.airport_code),
                taf_data=self.current_taf,
                flight_rules=self.current_weather.get('flight_rules', 'UNKNOWN'),
                frame=self.animation_frame
            )

        self.display.show_image(img)

        # Increment animation frame
        self.animation_frame = (self.animation_frame + 1) % 60

    def run(self):
        """Main run loop"""
        print(f"Starting Aviation Weather HUD for {self.airport_code}")

        # Show startup screen
        startup_img = self.renderer.create_startup_display("AVWX HUD")
        self.display.show_image(startup_img)
        time.sleep(2)

        # Initial weather fetch
        self.update()

        running = True
        try:
            while running:
                # Check for quit events (simulator only)
                if hasattr(self.display, 'check_events'):
                    if not self.display.check_events():
                        running = False
                        break

                # Update weather data if needed
                self.update()

                # Render display
                self.render()

                # Control frame rate
                if hasattr(self.display, 'tick'):
                    self.display.tick(30)  # 30 FPS
                else:
                    time.sleep(1/30)  # 30 FPS fallback

        except KeyboardInterrupt:
            print("\nShutting down...")

        finally:
            # Clean up
            self.display.clear()
            if hasattr(self.display, 'close'):
                self.display.close()

    def set_airport(self, airport_code: str):
        """
        Change airport
        Args:
            airport_code: New ICAO airport code
        """
        self.airport_code = airport_code.upper()
        self.current_weather = None
        self.last_update = 0
        print(f"Airport changed to {self.airport_code}")
