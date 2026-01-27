"""
Graphics renderer for LED matrix display
Handles drawing weather information with aviation-themed graphics
"""
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from .icons import AviationIcons, Font5x7


class DisplayRenderer:
    """Renders aviation weather information to LED matrix"""

    def __init__(self, width: int = 64, height: int = 32):
        """
        Initialize renderer
        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self.width = width
        self.height = height
        self.icons = AviationIcons()
        self.font = Font5x7()

    def create_weather_display(
        self,
        station: str,
        temperature: Optional[int],
        wind_speed: Optional[int],
        wind_direction: Optional[int],
        flight_rules: str,
        weather_icon: str,
        frame: int = 0
    ) -> Image.Image:
        """
        Create complete weather display
        Args:
            station: Airport code (e.g., 'KJFK')
            temperature: Temperature in Celsius
            wind_speed: Wind speed in knots
            wind_direction: Wind direction in degrees
            flight_rules: VFR, MVFR, IFR, or LIFR
            weather_icon: Icon name (clear, cloudy, rain, snow, etc.)
            frame: Animation frame number
        Returns:
            PIL Image ready for display
        """
        # Create RGB image
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Get flight category color for background accent
        color = self._get_flight_rules_color(flight_rules)

        # Draw status bar at top with flight category color
        draw.rectangle([(0, 0), (self.width, 2)], fill=color)

        # Draw station code (top left)
        self._draw_text(img, station[:4], 2, 4, (255, 255, 255))

        # Draw temperature (top right)
        if temperature is not None:
            temp_str = f"{temperature}°"
            self._draw_text(img, temp_str, self.width - len(temp_str) * 4 - 2, 4, (255, 200, 0))

        # Draw weather icon (left side, center)
        self._draw_weather_icon(img, weather_icon, 4, 14, frame)

        # Draw wind information (right side)
        if wind_speed is not None and wind_direction is not None:
            self._draw_wind(img, wind_speed, wind_direction, 40, 14, frame)

        # Draw flight category text at bottom
        self._draw_text(img, flight_rules[:4], 2, self.height - 8, color)

        return img

    def create_info_display(
        self,
        station: str,
        visibility: Optional[float],
        altimeter: Optional[float],
        clouds: list,
        flight_rules: str,
        frame: int = 0
    ) -> Image.Image:
        """
        Create information display with visibility, altimeter, and clouds
        """
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        color = self._get_flight_rules_color(flight_rules)

        # Status bar
        draw.rectangle([(0, 0), (self.width, 2)], fill=color)

        # Station
        self._draw_text(img, station[:4], 2, 4, (255, 255, 255))

        y_pos = 12

        # Visibility
        if visibility is not None:
            vis_text = f"VIS {visibility}SM"
            self._draw_text(img, vis_text[:10], 2, y_pos, (100, 200, 255))
            y_pos += 8

        # Altimeter
        if altimeter is not None:
            alt_text = f"ALT {altimeter:.2f}"
            self._draw_text(img, alt_text[:10], 2, y_pos, (200, 255, 100))
            y_pos += 8

        # Clouds (first layer)
        if clouds and len(clouds) > 0:
            cloud = clouds[0]
            cloud_text = f"{cloud.get('type', 'SKC')}"
            if cloud.get('altitude'):
                cloud_text += f"{cloud['altitude']}"
            self._draw_text(img, cloud_text[:10], 2, y_pos, (200, 200, 200))

        return img

    def create_startup_display(self, message: str = "AVWX HUD") -> Image.Image:
        """Create startup/splash screen"""
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))

        # Draw airplane in center
        airplane = self.icons.get_airplane(0)
        x_offset = (self.width - 8) // 2
        y_offset = 8
        self._draw_icon(img, airplane, x_offset, y_offset, (0, 200, 255))

        # Draw text below
        self._draw_text(img, message[:10], (self.width - len(message) * 4) // 2, 20, (255, 255, 255))

        return img

    def _draw_weather_icon(
        self,
        img: Image.Image,
        icon_name: str,
        x: int,
        y: int,
        frame: int
    ):
        """Draw animated weather icon"""
        color = (255, 255, 255)

        if icon_name == 'clear':
            icon = self.icons.get_sun(frame)
            color = (255, 200, 0)
        elif icon_name == 'cloudy':
            icon = self.icons.get_cloud('small')
            color = (180, 180, 180)
        elif icon_name == 'rain':
            # Draw cloud
            cloud = self.icons.get_cloud('small')
            self._draw_icon(img, cloud, x, y - 2, (150, 150, 150))
            # Draw rain below
            icon = self.icons.get_rain(frame)
            y += 4
            color = (100, 100, 255)
        elif icon_name == 'snow':
            # Draw cloud
            cloud = self.icons.get_cloud('small')
            self._draw_icon(img, cloud, x, y - 2, (200, 200, 200))
            # Draw snow below
            icon = self.icons.get_snow(frame)
            y += 4
            color = (200, 220, 255)
        elif icon_name == 'thunderstorm':
            # Draw cloud
            cloud = self.icons.get_cloud('small')
            self._draw_icon(img, cloud, x, y - 2, (100, 100, 100))
            # Draw lightning below
            icon = self.icons.get_thunderstorm(frame)
            y += 3
            color = (255, 255, 0)
        elif icon_name == 'fog':
            icon = self.icons.get_fog()
            color = (150, 150, 150)
        else:
            icon = self.icons.get_cloud('small')
            color = (128, 128, 128)

        self._draw_icon(img, icon, x, y, color)

    def _draw_wind(
        self,
        img: Image.Image,
        speed: int,
        direction: int,
        x: int,
        y: int,
        frame: int
    ):
        """Draw wind speed and direction"""
        # Draw wind speed text
        speed_text = f"{speed}KT"
        self._draw_text(img, speed_text, x, y, (0, 255, 200))

        # Draw wind arrow below
        arrow_points = self.icons.get_wind_arrow(direction)
        center_x = x + 10
        center_y = y + 10

        pixels = img.load()
        for px, py in arrow_points:
            draw_x = center_x + px
            draw_y = center_y + py
            if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                pixels[draw_x, draw_y] = (255, 100, 0)

    def _draw_icon(
        self,
        img: Image.Image,
        icon: list,
        x: int,
        y: int,
        color: Tuple[int, int, int]
    ):
        """Draw a pixel icon at specified position"""
        pixels = img.load()
        for row_idx, row in enumerate(icon):
            for col_idx, pixel in enumerate(row):
                if pixel:
                    draw_x = x + col_idx
                    draw_y = y + row_idx
                    if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                        pixels[draw_x, draw_y] = color

    def _draw_text(
        self,
        img: Image.Image,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int]
    ):
        """Draw text using simple font (4 pixels wide per char + 1 spacing)"""
        draw = ImageDraw.Draw(img)

        # Use PIL's default font for simplicity (tiny font)
        try:
            # Try to use a small built-in font
            draw.text((x, y), text, fill=color)
        except:
            # Fallback to basic drawing
            draw.text((x, y), text, fill=color)

    def _draw_number(
        self,
        img: Image.Image,
        number: str,
        x: int,
        y: int,
        color: Tuple[int, int, int]
    ):
        """Draw number using custom 5x7 font"""
        pixels = img.load()
        x_offset = 0

        for char in str(number):
            if char in self.font.DIGITS:
                digit = self.font.DIGITS[char]
                for row_idx, row in enumerate(digit):
                    for col_idx, pixel in enumerate(row):
                        if pixel:
                            draw_x = x + x_offset + col_idx
                            draw_y = y + row_idx
                            if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                                pixels[draw_x, draw_y] = color
                x_offset += 6  # 5 pixels + 1 spacing

    def _get_flight_rules_color(self, flight_rules: str) -> Tuple[int, int, int]:
        """Get color for flight rules"""
        colors = {
            'VFR': (0, 255, 0),
            'MVFR': (0, 0, 255),
            'IFR': (255, 0, 0),
            'LIFR': (255, 0, 255),
        }
        return colors.get(flight_rules.upper(), (128, 128, 128))
