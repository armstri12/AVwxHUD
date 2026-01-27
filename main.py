#!/usr/bin/env python3
"""
Aviation Weather HUD - Hardware Version
Run this on Raspberry Pi with RGB LED matrix
"""
import sys
import argparse
import json
import os
from src.display.matrix_display import MatrixDisplay
from src.display.controller import DisplayController


def load_config(config_file: str = 'config/config.json'):
    """Load configuration from file"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}


def main():
    parser = argparse.ArgumentParser(
        description='Aviation Weather HUD for RGB LED Matrix',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python main.py KJFK              # Display weather for JFK airport
  sudo python main.py KSFO --config config/config.json
  sudo python main.py EGLL --token YOUR_TOKEN

Note: Requires root/sudo to access GPIO pins on Raspberry Pi

Flight Categories (color coded):
  VFR (Green)    - Visual Flight Rules (good weather)
  MVFR (Blue)    - Marginal VFR (moderate weather)
  IFR (Red)      - Instrument Flight Rules (poor weather)
  LIFR (Magenta) - Low IFR (very poor weather)
        """
    )

    parser.add_argument(
        'airport',
        type=str,
        nargs='?',
        default=None,
        help='ICAO airport code (e.g., KJFK, KSFO, EGLL)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/config.json',
        help='Configuration file path'
    )

    parser.add_argument(
        '--token',
        type=str,
        default=None,
        help='AVWX API token (optional, for higher rate limits)'
    )

    parser.add_argument(
        '--update',
        type=int,
        default=300,
        help='Weather update interval in seconds (default: 300)'
    )

    parser.add_argument(
        '--width',
        type=int,
        default=64,
        help='Matrix width (default: 64)'
    )

    parser.add_argument(
        '--height',
        type=int,
        default=32,
        help='Matrix height (default: 32)'
    )

    parser.add_argument(
        '--brightness',
        type=int,
        default=75,
        help='LED brightness 0-100 (default: 75)'
    )

    args = parser.parse_args()

    # Load config file
    config = load_config(args.config)

    # Get airport code from args or config
    airport = args.airport or config.get('airport')
    if not airport:
        print("Error: Airport code required (provide as argument or in config file)")
        parser.print_help()
        sys.exit(1)

    # Get API token from args or config
    api_token = args.token or config.get('api_token')

    # Get settings from config or args
    width = config.get('width', args.width)
    height = config.get('height', args.height)
    update_interval = config.get('update_interval', args.update)
    brightness = config.get('brightness', args.brightness)

    # Validate airport code
    if len(airport) < 3 or len(airport) > 4:
        print("Error: Airport code should be 3-4 characters (ICAO format)")
        sys.exit(1)

    print("=" * 60)
    print("Aviation Weather HUD")
    print("=" * 60)
    print(f"Airport: {airport.upper()}")
    print(f"Display: {width}x{height}")
    print(f"Brightness: {brightness}%")
    print(f"Update interval: {update_interval} seconds")
    print()
    print("Press Ctrl+C to exit")
    print("=" * 60)
    print()

    try:
        # Create hardware display
        display = MatrixDisplay(width=width, height=height)

        if not display.is_available():
            print("ERROR: RGB LED Matrix hardware not available!")
            print("Make sure you:")
            print("  1. Are running on a Raspberry Pi")
            print("  2. Have the rgbmatrix library installed")
            print("  3. Are running with sudo/root privileges")
            print()
            print("To install rgbmatrix: sudo pip3 install rgbmatrix")
            print()
            print("Alternatively, use simulator.py for testing without hardware")
            sys.exit(1)

        # Set brightness
        display.set_brightness(brightness)

        # Create controller
        controller = DisplayController(
            display=display,
            airport_code=airport,
            api_token=api_token,
            update_interval=update_interval
        )

        # Run
        controller.run()

    except KeyboardInterrupt:
        print("\nShutdown requested")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("Display stopped")


if __name__ == '__main__':
    main()
