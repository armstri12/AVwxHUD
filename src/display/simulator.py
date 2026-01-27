"""
Pygame-based simulator for LED matrix display
Allows testing on desktop without hardware
"""
import pygame
import math
from PIL import Image
from typing import Optional, Tuple


class SimulatorDisplay:
    """Pygame-based LED matrix simulator with realistic LED rendering"""

    def __init__(self, width: int = 64, height: int = 32, pixel_size: int = 10, led_style: str = 'round'):
        """
        Initialize simulator
        Args:
            width: Matrix width in pixels
            height: Matrix height in pixels
            pixel_size: Size of each LED pixel on screen (for 5mm pitch, use 19)
            led_style: 'round' for circular LEDs, 'square' for square LEDs
        """
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.led_style = led_style

        # LED rendering parameters
        self.gap_ratio = 0.25  # 25% gap between LEDs
        self.gap = max(2, int(pixel_size * self.gap_ratio))
        self.led_size = pixel_size - self.gap

        # Calculate window size with padding
        padding = 20
        self.window_width = width * pixel_size + padding * 2
        self.window_height = height * pixel_size + padding * 2
        self.offset_x = padding
        self.offset_y = padding

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"Aviation Weather HUD Simulator ({width}x{height}) - {pixel_size//2}mm pitch")

        # Create clock for frame rate control
        self.clock = pygame.time.Clock()

        # Background colors
        self.bg_color = (15, 15, 15)  # Dark background
        self.off_led_color = (8, 8, 8)  # Very dark for OFF LEDs

        # Current image
        self.current_image = None

        # Pre-render LED templates for performance
        self._create_led_cache()

        print(f"Simulator initialized: {width}x{height} @ {pixel_size}px per LED (~{pixel_size//2}mm pitch)")
        print(f"Window size: {self.window_width}x{self.window_height}, LED style: {led_style}")

    def _create_led_cache(self):
        """Pre-create LED surfaces for better performance"""
        # Create a surface for one LED that we can reuse
        self.led_surface = pygame.Surface((self.pixel_size, self.pixel_size), pygame.SRCALPHA)

    def _draw_led(self, x: int, y: int, color: Tuple[int, int, int]):
        """
        Draw a single LED with realistic appearance
        Args:
            x: Matrix x coordinate
            y: Matrix y coordinate
            color: RGB color tuple
        """
        # Calculate screen position with padding
        screen_x = self.offset_x + x * self.pixel_size
        screen_y = self.offset_y + y * self.pixel_size

        # Skip if LED is off (black)
        if color == (0, 0, 0):
            # Draw very dim LED to show it's off
            if self.led_style == 'round':
                pygame.draw.circle(
                    self.screen,
                    self.off_led_color,
                    (screen_x + self.pixel_size // 2, screen_y + self.pixel_size // 2),
                    self.led_size // 2
                )
            else:
                pygame.draw.rect(
                    self.screen,
                    self.off_led_color,
                    (screen_x + self.gap // 2, screen_y + self.gap // 2, self.led_size, self.led_size)
                )
            return

        # Calculate brightness for glow effect
        brightness = sum(color) / 3

        if self.led_style == 'round':
            # Draw circular LED with gradient effect
            center_x = screen_x + self.pixel_size // 2
            center_y = screen_y + self.pixel_size // 2
            radius = self.led_size // 2

            # Outer glow (if bright)
            if brightness > 100:
                glow_radius = radius + 2
                glow_intensity = int(brightness * 0.3)
                glow_color = tuple(min(255, c + glow_intensity) for c in color)
                pygame.draw.circle(self.screen, glow_color, (center_x, center_y), glow_radius)

            # Main LED body
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

            # Highlight (makes it look 3D)
            if brightness > 50:
                highlight_color = tuple(min(255, c + 60) for c in color)
                highlight_radius = max(1, radius // 3)
                highlight_offset = radius // 3
                pygame.draw.circle(
                    self.screen,
                    highlight_color,
                    (center_x - highlight_offset, center_y - highlight_offset),
                    highlight_radius
                )

        else:
            # Square LED style
            led_x = screen_x + self.gap // 2
            led_y = screen_y + self.gap // 2

            # Outer glow
            if brightness > 100:
                glow_size = self.led_size + 3
                glow_intensity = int(brightness * 0.3)
                glow_color = tuple(min(255, c + glow_intensity) for c in color)
                pygame.draw.rect(
                    self.screen,
                    glow_color,
                    (led_x - 1, led_y - 1, glow_size, glow_size),
                    border_radius=2
                )

            # Main LED
            pygame.draw.rect(
                self.screen,
                color,
                (led_x, led_y, self.led_size, self.led_size),
                border_radius=2
            )

            # Highlight
            if brightness > 50:
                highlight_color = tuple(min(255, c + 60) for c in color)
                highlight_size = max(2, self.led_size // 3)
                pygame.draw.rect(
                    self.screen,
                    highlight_color,
                    (led_x + 2, led_y + 2, highlight_size, highlight_size)
                )

    def show_image(self, image: Image.Image):
        """
        Display an image in the simulator
        Args:
            image: PIL Image to display
        """
        # Ensure image is RGB and correct size
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.NEAREST)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        self.current_image = image

        # Clear screen with background
        self.screen.fill(self.bg_color)

        # Draw border/frame around the matrix
        border_color = (40, 40, 40)
        pygame.draw.rect(
            self.screen,
            border_color,
            (self.offset_x - 5, self.offset_y - 5,
             self.width * self.pixel_size + 10,
             self.height * self.pixel_size + 10),
            2
        )

        # Get pixel data
        pixels = image.load()

        # Draw each LED pixel with new rendering
        for y in range(self.height):
            for x in range(self.width):
                color = pixels[x, y]
                self._draw_led(x, y, color)

        # Update display
        pygame.display.flip()

    def clear(self):
        """Clear the display"""
        black_image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        self.show_image(black_image)

    def check_events(self) -> bool:
        """
        Check for pygame events (window close, etc.)
        Returns:
            True if should continue, False if should quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_s:
                    # Save screenshot
                    self._save_screenshot()

        return True

    def _save_screenshot(self):
        """Save current display as image file"""
        if self.current_image:
            filename = f"screenshot_{pygame.time.get_ticks()}.png"
            # Save at 10x scale for better quality
            scaled = self.current_image.resize(
                (self.width * 10, self.height * 10),
                Image.NEAREST
            )
            scaled.save(filename)
            print(f"Screenshot saved: {filename}")

    def tick(self, fps: int = 30):
        """
        Control frame rate
        Args:
            fps: Target frames per second
        """
        self.clock.tick(fps)

    def is_available(self) -> bool:
        """Check if simulator is available"""
        return True

    def close(self):
        """Close the simulator"""
        pygame.quit()


def create_display(use_hardware: bool = False, width: int = 64, height: int = 32):
    """
    Factory function to create appropriate display
    Args:
        use_hardware: If True, try to use hardware; otherwise use simulator
        width: Display width
        height: Display height
    Returns:
        Display instance (MatrixDisplay or SimulatorDisplay)
    """
    if use_hardware:
        from .matrix_display import MatrixDisplay
        display = MatrixDisplay(width, height)
        if display.is_available():
            return display
        else:
            print("Hardware not available, falling back to simulator")
            return SimulatorDisplay(width, height)
    else:
        return SimulatorDisplay(width, height)
