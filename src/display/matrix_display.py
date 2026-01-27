"""
RGB LED Matrix display driver
Interfaces with rpi-rgb-led-matrix library for Raspberry Pi
"""
from PIL import Image
from typing import Optional


class MatrixDisplay:
    """Driver for RGB LED matrix hardware"""

    def __init__(self, width: int = 64, height: int = 32):
        """
        Initialize LED matrix
        Args:
            width: Matrix width
            height: Matrix height
        """
        self.width = width
        self.height = height
        self.matrix = None

        try:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions

            # Configuration for the matrix
            options = RGBMatrixOptions()
            options.rows = height
            options.cols = width
            options.chain_length = 1
            options.parallel = 1
            options.hardware_mapping = 'regular'
            options.gpio_slowdown = 4
            options.brightness = 75
            options.pwm_lsb_nanoseconds = 130

            # Create matrix instance
            self.matrix = RGBMatrix(options=options)
            self.canvas = self.matrix.CreateFrameCanvas()
            print(f"RGB LED Matrix initialized: {width}x{height}")

        except ImportError:
            print("Warning: rgbmatrix library not found. Hardware display disabled.")
            print("Install with: sudo pip3 install rgbmatrix")
            self.matrix = None
        except Exception as e:
            print(f"Error initializing matrix: {e}")
            self.matrix = None

    def show_image(self, image: Image.Image):
        """
        Display an image on the matrix
        Args:
            image: PIL Image to display (will be resized if needed)
        """
        if not self.matrix:
            return

        try:
            # Ensure image is RGB and correct size
            if image.size != (self.width, self.height):
                image = image.resize((self.width, self.height), Image.NEAREST)

            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Set the image
            self.canvas.SetImage(image)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

        except Exception as e:
            print(f"Error displaying image: {e}")

    def clear(self):
        """Clear the display"""
        if self.matrix:
            try:
                self.canvas.Clear()
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
            except:
                pass

    def set_brightness(self, brightness: int):
        """
        Set display brightness
        Args:
            brightness: 0-100
        """
        if self.matrix:
            try:
                self.matrix.brightness = max(0, min(100, brightness))
            except:
                pass

    def is_available(self) -> bool:
        """Check if hardware display is available"""
        return self.matrix is not None
