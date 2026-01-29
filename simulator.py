#!/usr/bin/env python3
"""
Aviation Weather HUD Simulator
Run this on your computer to test without hardware
"""
import sys
import argparse
from src.display.simulator import SimulatorDisplay
from src.display.controller import DisplayController


def main():
    parser = argparse.ArgumentParser(
        description='Aviation Weather HUD Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simulator.py KJFK                    # Display weather for JFK airport
  python simulator.py KSFO --size 24          # Larger display
  python simulator.py EGLL --style square     # Square LEDs instead of round
  python simulator.py KJFK --token YOUR_TOKEN # Use API token for real weather

Controls:
  ESC or Q - Quit
  S - Save screenshot

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
        help='ICAO airport code (e.g., KJFK, KSFO, EGLL)'
    )

    parser.add_argument(
        '--size',
        type=int,
        default=12,
        help='Size of each LED pixel in pixels (default: 12 for ~3mm pitch)'
    )

    parser.add_argument(
        '--style',
        type=str,
        default='round',
        choices=['round', 'square'],
        help='LED style: round (default) or square'
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
        default=64,
        help='Matrix height (default: 64)'
    )

    args = parser.parse_args()

    # Validate airport code
    if len(args.airport) < 3 or len(args.airport) > 4:
        print("Error: Airport code should be 3-4 characters (ICAO format)")
        sys.exit(1)

    print("=" * 60)
    print("Aviation Weather HUD Simulator")
    print("=" * 60)
    print(f"Airport: {args.airport.upper()}")
    print(f"Display: {args.width}x{args.height} @ {args.size}px per LED (~{args.size//2}mm pitch)")
    print(f"LED Style: {args.style}")
    print(f"Update interval: {args.update} seconds")
    print()
    print("Press ESC or Q to quit, S to save screenshot")
    print("=" * 60)
    print()

    try:
        # Create simulator display
        display = SimulatorDisplay(
            width=args.width,
            height=args.height,
            pixel_size=args.size,
            led_style=args.style
        )

        # Create controller
        controller = DisplayController(
            display=display,
            airport_code=args.airport,
            api_token=args.token,
            update_interval=args.update
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

    print("Simulator stopped")


if __name__ == '__main__':
    main()
