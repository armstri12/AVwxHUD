"""
Graphics renderer for LED matrix display
Handles drawing weather information with aviation-themed graphics
"""
from typing import Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont
from .icons import AviationIcons, Font5x7


class DisplayRenderer:
    """Renders aviation weather information to LED matrix"""

    def __init__(self, width: int = 64, height: int = 64):
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

    def create_metar_display(
        self,
        station: str,
        temperature: Optional[int],
        dewpoint: Optional[int],
        wind_speed: Optional[int],
        wind_direction: Optional[int],
        visibility: Optional[float],
        ceiling: Optional[int],
        flight_rules: str,
        conditions: list,
        frame: int = 0
    ) -> Image.Image:
        """
        Create METAR display screen (64x64)
        Shows: Temp, Dewpoint, Wind, Visibility, Ceiling, Conditions, Flight Rules
        """
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        color = self._get_flight_rules_color(flight_rules)

        # Header bar (rows 0-2)
        draw.rectangle([(0, 0), (self.width, 2)], fill=color)

        # "METAR" label (rows 3-10) - large and clear
        self._draw_text(img, "METAR", 2, 3, (255, 255, 255))

        # Station code (top right)
        self._draw_text(img, station[:4], self.width - 26, 3, (200, 200, 200))

        # Flight rules badge (below METAR)
        self._draw_text(img, flight_rules[:4], 2, 11, color)

        # Data section starts at row 19
        y = 19

        # Temperature / Dewpoint
        if temperature is not None and dewpoint is not None:
            temp_text = f"T {temperature:3d} D{dewpoint:3d}"
            self._draw_text(img, temp_text, 2, y, (255, 200, 0))
        y += 8

        # Wind
        if wind_speed is not None and wind_direction is not None:
            wind_text = f"W{wind_direction:03d}/{wind_speed:02d}KT"
            self._draw_text(img, wind_text, 2, y, (0, 255, 200))
        y += 8

        # Visibility
        if visibility is not None:
            if visibility >= 10:
                vis_text = f"V 10SM"
            else:
                vis_text = f"V {visibility:.1f}SM"
            self._draw_text(img, vis_text, 2, y, (100, 200, 255))
        y += 8

        # Ceiling
        if ceiling is not None:
            # Display in hundreds of feet
            ceil_hund = ceiling // 100
            ceil_text = f"C {ceil_hund:03d}"
            self._draw_text(img, ceil_text, 2, y, (255, 150, 255))
        else:
            self._draw_text(img, "C CLR", 2, y, (100, 100, 100))
        y += 8

        # Conditions
        if conditions:
            cond_text = ' '.join(conditions[:2])  # Max 2 conditions
            self._draw_text(img, cond_text[:10], 2, y, (200, 200, 200))

        return img

    def create_taf_display(
        self,
        station: str,
        taf_data: Dict,
        flight_rules: str,
        frame: int = 0
    ) -> Image.Image:
        """
        Create TAF forecast display screen (64x64)
        Shows multiple forecast periods with clear time blocks
        """
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        color = self._get_flight_rules_color(flight_rules)

        # Header bar
        draw.rectangle([(0, 0), (self.width, 2)], fill=color)

        # "TAF" label - large and clear
        self._draw_text(img, "TAF", 2, 3, (255, 255, 255))

        # Station code (top right)
        self._draw_text(img, station[:4], self.width - 26, 3, (200, 200, 200))

        # TAF data starts at row 11
        if not taf_data or not taf_data.get('forecast'):
            self._draw_text(img, "NO TAF", 2, 20, (150, 150, 150))
            return img

        y = 11
        forecast = taf_data.get('forecast', [])

        # Show up to 5 forecast periods
        for i, period in enumerate(forecast[:5]):
            if y + 10 > self.height:
                break

            # Flight category color bar (left edge, full block height)
            fr = period.get('flight_rules', 'UNKN')
            period_color = self._get_flight_rules_color(fr)
            draw.rectangle([(0, y), (1, y + 9)], fill=period_color)

            # Convert time from UTC to CST (UTC-6)
            start_time = period.get('start_time', '')
            time_str = self._convert_to_cst_24hr(start_time)

            # Time in 24hr CST format (row 1 of block)
            if time_str:
                self._draw_text(img, time_str, 3, y, (200, 200, 255))

            # Wind direction/speed (row 2 of block)
            wind_dir = period.get('wind_direction')
            wind_spd = period.get('wind_speed')
            ceiling = period.get('ceiling')

            if wind_dir is not None and wind_spd is not None:
                wind_text = f"W{wind_dir:03d}/{wind_spd:02d}"
                self._draw_text(img, wind_text, 3, y + 5, (100, 200, 255))

            # Ceiling on same line (right side)
            if ceiling is not None:
                ceil_hund = ceiling // 100
                ceil_text = f"C{ceil_hund:03d}"
                self._draw_text(img, ceil_text, 38, y + 5, (255, 150, 255))

            y += 10  # Move to next time block

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
        self._draw_text(img, message[:10], (self.width - len(message[:10]) * 6) // 2, 20, (255, 255, 255))

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

    def _draw_wind_large(
        self,
        img: Image.Image,
        speed: int,
        direction: int,
        x: int,
        y: int,
        frame: int
    ):
        """Draw wind with large arrow and direction in degrees"""
        # Wind speed
        speed_text = f"{speed}KT"
        self._draw_text(img, speed_text, x, y, (0, 255, 200))

        # Wind direction in degrees
        dir_text = f"{direction:03d}"
        self._draw_text(img, dir_text, x, y + 8, (255, 150, 0))

        # Large wind arrow
        arrow_points = self.icons.get_wind_arrow(direction)
        center_x = x + 12
        center_y = y + 18

        pixels = img.load()
        for px, py in arrow_points:
            draw_x = center_x + px
            draw_y = center_y + py
            if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                # Brighter orange for better visibility
                pixels[draw_x, draw_y] = (255, 120, 0)

    def _draw_taf_forecast(
        self,
        img: Image.Image,
        taf_data: Dict,
        x: int,
        y: int,
        frame: int
    ):
        """Draw TAF forecast information"""
        # TAF header
        self._draw_text(img, "TAF", 2, y, (200, 200, 255))

        forecast = taf_data.get('forecast', [])
        y_offset = y + 8

        # Draw up to 2 forecast periods
        for i, period in enumerate(forecast[:2]):
            if y_offset + 8 > self.height:
                break

            # Flight category indicator
            fr = period.get('flight_rules', 'UNKN')
            color = self._get_flight_rules_color(fr)

            # Draw small colored square for flight category
            draw = ImageDraw.Draw(img)
            draw.rectangle([(2, y_offset), (4, y_offset + 6)], fill=color)

            # Wind info
            wind_dir = period.get('wind_direction')
            wind_spd = period.get('wind_speed')

            if wind_dir is not None and wind_spd is not None:
                wind_text = f"{wind_dir:03d}/{wind_spd:02d}"
                self._draw_text(img, wind_text[:9], 6, y_offset, (100, 200, 255))

            y_offset += 8

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
        color: Tuple[int, int, int],
        scale: int = 1
    ):
        """Draw text using custom pixel font (5 pixels wide per char + 1 spacing)"""
        pixels = img.load()
        x_offset = 0

        for char in str(text):
            char_pattern = self.font.get_char(char)

            if char_pattern:
                # Draw each pixel of the character
                for row_idx, row in enumerate(char_pattern):
                    for col_idx, pixel in enumerate(row):
                        if pixel:
                            for sy in range(scale):
                                for sx in range(scale):
                                    draw_x = x + x_offset + col_idx * scale + sx
                                    draw_y = y + row_idx * scale + sy
                                    if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                                        pixels[draw_x, draw_y] = color
                x_offset += 6 * scale  # 5 pixels + 1 spacing

    def _draw_number(
        self,
        img: Image.Image,
        number: str,
        x: int,
        y: int,
        color: Tuple[int, int, int]
    ):
        """Draw number using custom 5x7 font (deprecated, use _draw_text instead)"""
        # Just call _draw_text now
        self._draw_text(img, number, x, y, color)

    def _convert_to_cst_24hr(self, utc_time_str: str) -> str:
        """
        Convert UTC time string to CST 24-hour format
        Args:
            utc_time_str: Time string like "1823" (HHMM in UTC)
        Returns:
            Time string in CST 24hr format like "12:23"
        """
        if not utc_time_str or len(utc_time_str) < 4:
            return ""

        try:
            # Extract hours and minutes from HHMM format
            utc_hour = int(utc_time_str[:2])
            utc_min = int(utc_time_str[2:4])

            # Convert to CST (UTC-6)
            cst_hour = utc_hour - 6
            if cst_hour < 0:
                cst_hour += 24

            # Format as HH:MM
            return f"{cst_hour:02d}:{utc_min:02d}"
        except (ValueError, IndexError):
            return ""

    def _get_flight_rules_color(self, flight_rules: str) -> Tuple[int, int, int]:
        """Get color for flight rules"""
        colors = {
            'VFR': (0, 255, 0),
            'MVFR': (0, 0, 255),
            'IFR': (255, 0, 0),
            'LIFR': (255, 0, 255),
        }
        return colors.get(flight_rules.upper(), (128, 128, 128))
