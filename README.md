# Aviation Weather HUD ✈️

A beautiful aviation weather heads-up display for 64x32 RGB LED matrices, featuring real-time METAR data, animated weather icons, and a desktop simulator for testing.

![Flight Categories](https://img.shields.io/badge/VFR-Green-success)
![MVFR](https://img.shields.io/badge/MVFR-Blue-blue)
![IFR](https://img.shields.io/badge/IFR-Red-red)
![LIFR](https://img.shields.io/badge/LIFR-Magenta-purple)

## Features

- **Real-time Aviation Weather**: Fetches METAR data from AVWX API
- **Color-coded Flight Categories**:
  - 🟢 **VFR** (Green) - Visual Flight Rules (good weather)
  - 🔵 **MVFR** (Blue) - Marginal VFR (moderate weather)
  - 🔴 **IFR** (Red) - Instrument Flight Rules (poor weather)
  - 🟣 **LIFR** (Magenta) - Low IFR (very poor weather)
- **Animated Weather Icons**: Clear skies, clouds, rain, snow, thunderstorms, and fog
- **Multiple Display Modes**:
  - Main: Temperature, wind speed/direction, weather icon
  - Info: Visibility, altimeter setting, cloud layers
- **Desktop Simulator**: Test and develop without hardware using Pygame
- **Auto-updating**: Configurable weather data refresh interval

## Hardware Requirements

### For LED Matrix Display
- Raspberry Pi (any model with GPIO pins)
- 64x32 RGB LED Matrix Panel (HUB75 interface)
- RGB LED Matrix HAT or adapter
- 5V power supply (4-8A depending on brightness)

### For Simulator (Testing)
- Any computer with Python 3.7+
- No special hardware required!

## Quick Start

### 1. Simulator (Test on Your Computer)

```bash
# Clone the repository
git clone https://github.com/yourusername/AVwxHUD.git
cd AVwxHUD

# Install dependencies
pip install -r requirements.txt

# Run the simulator
python simulator.py KJFK
```

**Simulator Controls:**
- `ESC` or `Q` - Quit
- `S` - Save screenshot

**Note:** The AVWX API requires a free token. If you don't have one, the display will automatically run in **DEMO MODE** with simulated weather data that cycles through different conditions. See [API Token](#api-token-optional) section below to get a free token for real weather data.

### 2. Hardware (Raspberry Pi)

```bash
# Install dependencies
sudo pip3 install -r requirements.txt

# Install RGB matrix library
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh >rgb-matrix.sh
sudo bash rgb-matrix.sh

# Run on hardware (requires root for GPIO access)
sudo python3 main.py KJFK
```

## Configuration

Edit `config/config.json` to customize settings:

```json
{
  "airport": "KJFK",
  "api_token": null,
  "width": 64,
  "height": 32,
  "brightness": 75,
  "update_interval": 300
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `airport` | ICAO airport code | KJFK |
| `api_token` | AVWX API token (optional) | null |
| `width` | Matrix width in pixels | 64 |
| `height` | Matrix height in pixels | 32 |
| `brightness` | LED brightness (0-100) | 75 |
| `update_interval` | Seconds between updates | 300 |

## Usage Examples

### Simulator

```bash
# Basic usage
python simulator.py KSFO

# Larger display (bigger pixels)
python simulator.py EGLL --size 15

# Custom update interval (every 2 minutes)
python simulator.py KATL --update 120

# With API token for higher rate limits
python simulator.py KJFK --token YOUR_API_TOKEN
```

### Hardware

```bash
# Using command line arguments
sudo python3 main.py KSFO --brightness 50

# Using config file
sudo python3 main.py --config config/config.json

# Custom matrix size
sudo python3 main.py EGLL --width 128 --height 64
```

## Display Modes

The display automatically alternates between two modes every 10 seconds:

### Mode 1: Main Weather Display
- Airport code
- Current temperature
- Wind speed and direction (with arrow indicator)
- Animated weather icon
- Flight category color bar

### Mode 2: Information Display
- Airport code
- Visibility (statute miles)
- Altimeter setting (inHg)
- Cloud layer information
- Flight category

## Weather Icons

The display features animated pixel art icons:
- ☀️ **Clear/Sunny** - Yellow sun with rotating rays
- ☁️ **Cloudy** - Gray clouds
- 🌧️ **Rain** - Cloud with falling rain drops
- ❄️ **Snow** - Cloud with falling snowflakes
- ⛈️ **Thunderstorm** - Cloud with flashing lightning bolt
- 🌫️ **Fog** - Horizontal fog layers

## API Token (Required for Real Weather Data)

**UPDATE:** The AVWX API now requires authentication. Without a token, the display runs in **DEMO MODE** with simulated weather data.

### Get Your Free API Token

Get a free API token from [AVWX.rest](https://avwx.rest):

1. Visit https://avwx.rest
2. Click "Sign Up" and create a free account
3. Go to your dashboard and copy your API token
4. Add to `config/config.json`:
   ```json
   {
     "airport": "KJFK",
     "api_token": "YOUR_TOKEN_HERE"
   }
   ```

   OR use `--token` flag:
   ```bash
   python simulator.py KJFK --token YOUR_TOKEN_HERE
   ```

**Free tier:** 4000 requests/day (more than enough for this project!)

### Demo Mode

Without a token, the display automatically enters demo mode which:
- Cycles through 5 different weather scenarios every 30 seconds
- Shows VFR, MVFR, IFR conditions with different weather
- Demonstrates all animations (sun, clouds, rain, snow, lightning)
- Perfect for testing and development!

## Project Structure

```
AVwxHUD/
├── src/
│   ├── weather/           # Weather data fetching
│   │   └── weather_fetcher.py
│   ├── graphics/          # Icons and rendering
│   │   ├── icons.py
│   │   └── renderer.py
│   └── display/           # Display drivers
│       ├── matrix_display.py    # Hardware driver
│       ├── simulator.py         # Pygame simulator
│       └── controller.py        # Main controller
├── config/
│   └── config.json        # Configuration file
├── simulator.py           # Simulator entry point
├── main.py               # Hardware entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Troubleshooting

### Simulator Issues

**Black screen or no display:**
- Make sure pygame is installed: `pip install pygame`
- Check that the airport code is valid (4-letter ICAO)

**No weather data:**
- Verify internet connection
- Check airport code is correct
- Wait a few seconds for initial data fetch
- Consider getting an API token if rate limited

### Hardware Issues

**"Permission denied" or GPIO errors:**
- Run with sudo: `sudo python3 main.py KJFK`
- Ensure you're on a Raspberry Pi

**Display not working:**
- Verify matrix is properly connected
- Check power supply is adequate (5V, 4-8A)
- Ensure RGB matrix library is installed
- Check HAT/adapter compatibility

**Flickering or artifacts:**
- Try adjusting `gpio_slowdown` in matrix_display.py
- Reduce brightness
- Check power supply quality

## Customization

### Adding More Airports

Simply run with different airport codes:
```bash
python simulator.py KSEA  # Seattle
python simulator.py EDDF  # Frankfurt
python simulator.py RJTT  # Tokyo
```

Find ICAO codes at: https://www.world-airport-codes.com/

### Changing Display Colors

Edit color values in `src/graphics/renderer.py`:
```python
def _get_flight_rules_color(self, flight_rules: str):
    colors = {
        'VFR': (0, 255, 0),    # Change to your preferred RGB
        'MVFR': (0, 0, 255),
        # ...
    }
```

### Creating Custom Icons

Add new icons in `src/graphics/icons.py` using pixel art:
```python
@staticmethod
def get_your_icon() -> List[List[int]]:
    return [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        # ... 1 = draw pixel, 0 = skip
    ]
```

## Contributing

Contributions are welcome! Feel free to:
- Add new weather icons
- Improve animations
- Add new display modes
- Support additional matrix sizes
- Enhance documentation

## License

MIT License - feel free to use and modify for your projects!

## Acknowledgments

- Weather data from [AVWX.rest](https://avwx.rest)
- RGB LED Matrix library by [hzeller](https://github.com/hzeller/rpi-rgb-led-matrix)
- Inspired by aviation weather displays at airports worldwide

## Support

Having issues? Please check:
1. The troubleshooting section above
2. Existing GitHub issues
3. AVWX API status
4. RGB matrix wiring guides

---

Made with ❤️ for aviation enthusiasts and pilots

**Remember:** This is for informational purposes only. Always use official aviation weather sources for flight planning and operations.
