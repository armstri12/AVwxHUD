# Aviation Weather HUD - Setup Guide

Complete setup instructions for both simulator (desktop) and hardware (Raspberry Pi) installations.

## Table of Contents
- [Simulator Setup (Desktop)](#simulator-setup-desktop)
- [Hardware Setup (Raspberry Pi)](#hardware-setup-raspberry-pi)
- [Wiring Guide](#wiring-guide)
- [First Run](#first-run)
- [Auto-start on Boot](#auto-start-on-boot)

---

## Simulator Setup (Desktop)

Perfect for testing and development without hardware!

### Requirements
- Python 3.7 or higher
- Internet connection
- Windows, macOS, or Linux

### Installation Steps

1. **Install Python** (if not already installed)
   - Download from https://python.org
   - Verify: `python --version` or `python3 --version`

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/AVwxHUD.git
   cd AVwxHUD
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or on some systems:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Run the Simulator**
   ```bash
   python simulator.py KJFK
   ```

   Replace `KJFK` with your preferred airport code!

### Troubleshooting Simulator

**ImportError: No module named 'pygame'**
```bash
pip install pygame --upgrade
```

**Display window doesn't appear**
- Check if your system has a display/GUI environment
- On WSL, you may need an X server

---

## Hardware Setup (Raspberry Pi)

### Requirements
- Raspberry Pi (Model 3B+, 4, or Zero 2W recommended)
- 64x32 RGB LED Matrix (HUB75 interface)
- Adafruit RGB Matrix HAT or Bonnet
- MicroSD card (8GB+, Class 10)
- 5V 4A+ power supply
- Female-to-female jumper wires (if not using HAT)

### Step 1: Raspberry Pi OS Setup

1. **Flash Raspberry Pi OS**
   - Use Raspberry Pi Imager: https://www.raspberrypi.org/software/
   - Choose "Raspberry Pi OS Lite" or "Desktop" version
   - Enable SSH in settings before flashing

2. **Boot and Update**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

### Step 2: Install Dependencies

1. **Install Python and Tools**
   ```bash
   sudo apt install -y python3-pip python3-dev git
   ```

2. **Clone Repository**
   ```bash
   cd ~
   git clone https://github.com/yourusername/AVwxHUD.git
   cd AVwxHUD
   ```

3. **Install Python Requirements**
   ```bash
   sudo pip3 install -r requirements.txt
   ```

### Step 3: Install RGB Matrix Library

**Option A: Using Installer Script (Recommended)**
```bash
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh > rgb-matrix.sh
sudo bash rgb-matrix.sh
```
- Say YES to continuing
- Select your HAT/Bonnet type
- Say YES to reboot when asked

**Option B: Manual Installation**
```bash
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```

### Step 4: Configure

1. **Edit Configuration**
   ```bash
   cd ~/AVwxHUD
   nano config/config.json
   ```

2. **Set Your Airport**
   ```json
   {
     "airport": "KSFO",
     "brightness": 75,
     "update_interval": 300
   }
   ```

3. **Save and Exit**
   - Press `Ctrl+X`, then `Y`, then `Enter`

### Step 5: Test

```bash
sudo python3 main.py KJFK
```

You should see the display light up with weather data!

---

## Wiring Guide

### Using Adafruit RGB Matrix HAT/Bonnet
Simply plug the HAT onto the Raspberry Pi GPIO pins. No wiring needed!

### Manual Wiring (Without HAT)

**Important:** Follow the wiring diagram for rpi-rgb-led-matrix carefully.

**Typical connections for 64x32 matrix:**

| Matrix Pin | GPIO Pin | Physical Pin |
|------------|----------|--------------|
| R1         | GPIO 17  | 11           |
| G1         | GPIO 18  | 12           |
| B1         | GPIO 22  | 15           |
| R2         | GPIO 23  | 16           |
| G2         | GPIO 24  | 18           |
| B2         | GPIO 25  | 22           |
| A          | GPIO 15  | 10           |
| B          | GPIO 16  | 36           |
| C          | GPIO 20  | 38           |
| D          | GPIO 21  | 40           |
| CLK        | GPIO 11  | 23           |
| LAT        | GPIO 26  | 37           |
| OE         | GPIO 27  | 13           |
| GND        | GND      | 6, 9, 14, 20 |

**Power:**
- Connect matrix 5V and GND to external power supply (4-8A)
- **DO NOT** power matrix from Raspberry Pi!

---

## First Run

### Test Different Airports

```bash
# Los Angeles
sudo python3 main.py KLAX

# London Heathrow
sudo python3 main.py EGLL

# Tokyo Haneda
sudo python3 main.py RJTT

# Your local airport (find ICAO code)
sudo python3 main.py XXXX
```

### Adjust Brightness

```bash
sudo python3 main.py KJFK --brightness 50
```

Values: 0-100 (lower = dimmer, saves power)

### Change Update Frequency

```bash
sudo python3 main.py KJFK --update 120
```

Updates every 120 seconds (2 minutes)

---

## Auto-start on Boot

Make the display start automatically when Raspberry Pi boots.

### Method 1: Systemd Service (Recommended)

1. **Create Service File**
   ```bash
   sudo nano /etc/systemd/system/avwxhud.service
   ```

2. **Add This Content**
   ```ini
   [Unit]
   Description=Aviation Weather HUD
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/home/pi/AVwxHUD
   ExecStart=/usr/bin/python3 /home/pi/AVwxHUD/main.py --config /home/pi/AVwxHUD/config/config.json
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable avwxhud.service
   sudo systemctl start avwxhud.service
   ```

4. **Check Status**
   ```bash
   sudo systemctl status avwxhud.service
   ```

5. **View Logs**
   ```bash
   sudo journalctl -u avwxhud.service -f
   ```

### Method 2: rc.local

1. **Edit rc.local**
   ```bash
   sudo nano /etc/rc.local
   ```

2. **Add Before `exit 0`**
   ```bash
   # Start Aviation Weather HUD
   cd /home/pi/AVwxHUD
   /usr/bin/python3 /home/pi/AVwxHUD/main.py --config config/config.json > /var/log/avwxhud.log 2>&1 &
   ```

3. **Make Executable**
   ```bash
   sudo chmod +x /etc/rc.local
   ```

### Stop Auto-start

**If using systemd:**
```bash
sudo systemctl stop avwxhud.service
sudo systemctl disable avwxhud.service
```

**If using rc.local:**
Remove the lines you added from `/etc/rc.local`

---

## Performance Tuning

### Reduce CPU Usage

Edit `src/display/matrix_display.py`, adjust:
```python
options.pwm_lsb_nanoseconds = 130  # Increase to reduce CPU load
options.gpio_slowdown = 4          # Increase if flickering
```

### Improve Stability

```bash
# Disable audio (reduces interference)
sudo nano /boot/config.txt
# Add: dtparam=audio=off

# Disable Bluetooth (if not needed)
# Add: dtoverlay=disable-bt
```

---

## Tips and Best Practices

1. **Power Supply**: Use a quality 5V power supply with enough amperage
2. **Cooling**: Consider a heatsink or small fan for 24/7 operation
3. **Updates**: Keep weather update interval at 5 minutes (300s) or more
4. **API Token**: Get free token from AVWX.rest for better reliability
5. **Backup**: Keep a backup of your config file

---

## Getting Help

**Still having issues?**

1. Check `/var/log/syslog` for errors
2. Run manually to see error messages: `sudo python3 main.py KJFK`
3. Verify RGB matrix works with example programs
4. Check GitHub issues
5. Verify airport code at https://www.world-airport-codes.com/

---

## Next Steps

Once working:
- Customize colors and icons
- Add multiple airports (modify code to cycle through them)
- Build an enclosure
- Add physical buttons to change airports
- Integrate with flight tracking APIs

Enjoy your Aviation Weather HUD! ✈️
