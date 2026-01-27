"""
Pygame-based simulator for LED matrix display
Allows testing on desktop without hardware
"""
import pygame
from PIL import Image
from typing import Optional, Tuple


class SimulatorDisplay:
    """Pygame-based LED matrix simulator"""

    def __init__(self, width: int = 64, height: int = 32, pixel_size: int = 10):
        """
        Initialize simulator
        Args:
            width: Matrix width in pixels
            height: Matrix height in pixels
            pixel_size: Size of each LED pixel on screen
        """
        self.width = width
        self.height = height
        self.pixel_size = pixel_size

        # Calculate window size
        self.window_width = width * pixel_size
        self.window_height = height * pixel_size

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"Aviation Weather HUD Simulator ({width}x{height})")

        # Create clock for frame rate control
        self.clock = pygame.time.Clock()

        # Background color (dark gray to simulate OFF LEDs)
        self.bg_color = (20, 20, 20)

        # Current image
        self.current_image = None

        print(f"Simulator initialized: {width}x{height} @ {pixel_size}px per LED")

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

        # Clear screen
        self.screen.fill(self.bg_color)

        # Get pixel data
        pixels = image.load()

        # Draw each LED pixel
        for y in range(self.height):
            for x in range(self.width):
                color = pixels[x, y]

                # Calculate screen position
                screen_x = x * self.pixel_size
                screen_y = y * self.pixel_size

                # Draw LED pixel with slight gap between pixels for realism
                gap = max(1, self.pixel_size // 10)
                led_size = self.pixel_size - gap

                # Draw the LED
                pygame.draw.rect(
                    self.screen,
                    color,
                    (screen_x + gap // 2, screen_y + gap // 2, led_size, led_size)
                )

                # Optional: Add LED glow effect for brighter pixels
                if sum(color) > 200:  # Bright pixels get a subtle glow
                    glow_color = tuple(min(255, c + 30) for c in color)
                    pygame.draw.rect(
                        self.screen,
                        glow_color,
                        (screen_x + gap // 2, screen_y + gap // 2, led_size, led_size),
                        1
                    )

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
