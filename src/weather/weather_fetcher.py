"""
Aviation Weather Data Fetcher
Fetches METAR and TAF data from aviation weather sources
"""
import requests
from typing import Dict, Optional
from datetime import datetime


class WeatherFetcher:
    """Fetches aviation weather data from AVWX API"""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize weather fetcher
        Args:
            api_token: Optional AVWX API token for higher rate limits
        """
        self.base_url = "https://avwx.rest/api"
        self.api_token = api_token
        self.headers = {}
        if api_token:
            self.headers['Authorization'] = f'Bearer {api_token}'

    def get_metar(self, airport_code: str) -> Optional[Dict]:
        """
        Fetch METAR data for an airport
        Args:
            airport_code: ICAO airport code (e.g., 'KJFK')
        Returns:
            Dictionary with parsed METAR data or None if error
        """
        try:
            url = f"{self.base_url}/metar/{airport_code.upper()}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._parse_metar(data)
            elif response.status_code == 401:
                print(f"Error fetching METAR: 401 Unauthorized")
                print(f"API token required. Get free token at: https://avwx.rest")
                print(f"Using DEMO mode with sample data...")
                return self._get_demo_data(airport_code.upper())
            else:
                print(f"Error fetching METAR: {response.status_code}")
                print(f"Using DEMO mode with sample data...")
                return self._get_demo_data(airport_code.upper())
        except Exception as e:
            print(f"Exception fetching METAR: {e}")
            print(f"Using DEMO mode with sample data...")
            return self._get_demo_data(airport_code.upper())

    def _parse_metar(self, data: Dict) -> Dict:
        """Parse METAR API response into simplified format"""
        try:
            # Extract key information
            result = {
                'station': data.get('station', 'N/A'),
                'time': data.get('time', {}).get('repr', 'N/A'),
                'flight_rules': data.get('flight_rules', 'UNKNOWN'),
                'raw': data.get('raw', ''),
            }

            # Temperature
            if 'temperature' in data and data['temperature']:
                result['temperature'] = data['temperature'].get('value', None)
            else:
                result['temperature'] = None

            # Dew point
            if 'dewpoint' in data and data['dewpoint']:
                result['dewpoint'] = data['dewpoint'].get('value', None)
            else:
                result['dewpoint'] = None

            # Wind
            if 'wind_direction' in data and data['wind_direction']:
                result['wind_direction'] = data['wind_direction'].get('value', None)
            else:
                result['wind_direction'] = None

            if 'wind_speed' in data and data['wind_speed']:
                result['wind_speed'] = data['wind_speed'].get('value', None)
            else:
                result['wind_speed'] = None

            # Visibility
            if 'visibility' in data and data['visibility']:
                result['visibility'] = data['visibility'].get('value', None)
            else:
                result['visibility'] = None

            # Ceiling (lowest broken or overcast layer)
            result['ceiling'] = None
            if 'clouds' in data and data['clouds']:
                for cloud in data['clouds']:
                    if cloud and cloud.get('type') in ['BKN', 'OVC']:
                        if cloud.get('altitude') is not None:
                            result['ceiling'] = cloud['altitude'] * 100  # Convert to feet AGL
                            break

            # Altimeter
            if 'altimeter' in data and data['altimeter']:
                result['altimeter'] = data['altimeter'].get('value', None)
            else:
                result['altimeter'] = None

            # Cloud layers
            result['clouds'] = []
            if 'clouds' in data and data['clouds']:
                for cloud in data['clouds']:
                    if cloud:
                        result['clouds'].append({
                            'type': cloud.get('type', ''),
                            'altitude': cloud.get('altitude', None),
                            'repr': cloud.get('repr', '')
                        })

            # Weather conditions
            result['conditions'] = []
            if 'wx_codes' in data and data['wx_codes']:
                for wx in data['wx_codes']:
                    if wx and 'repr' in wx:
                        result['conditions'].append(wx['repr'])

            return result

        except Exception as e:
            print(f"Error parsing METAR: {e}")
            return {
                'station': data.get('station', 'N/A'),
                'error': str(e),
                'raw': data.get('raw', '')
            }

    def get_taf(self, airport_code: str) -> Optional[Dict]:
        """
        Fetch TAF data for an airport
        Args:
            airport_code: ICAO airport code (e.g., 'KJFK')
        Returns:
            Dictionary with parsed TAF data or None if error
        """
        try:
            url = f"{self.base_url}/taf/{airport_code.upper()}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._parse_taf(data)
            elif response.status_code == 401:
                print(f"Error fetching TAF: 401 Unauthorized")
                return self._get_demo_taf(airport_code.upper())
            else:
                print(f"Error fetching TAF: {response.status_code}")
                return self._get_demo_taf(airport_code.upper())
        except Exception as e:
            print(f"Exception fetching TAF: {e}")
            return self._get_demo_taf(airport_code.upper())

    def _parse_taf(self, data: Dict) -> Dict:
        """Parse TAF API response into simplified format"""
        try:
            result = {
                'station': data.get('station', 'N/A'),
                'time': data.get('time', {}).get('repr', 'N/A'),
                'raw': data.get('raw', ''),
                'forecast': []
            }

            # Get forecast periods
            if 'forecast' in data and data['forecast']:
                for period in data['forecast'][:3]:  # First 3 periods
                    forecast_item = {
                        'type': period.get('type', 'FM'),
                        'wind_direction': None,
                        'wind_speed': None,
                        'visibility': None,
                        'flight_rules': period.get('flight_rules', 'UNKNOWN')
                    }

                    if 'wind_direction' in period and period['wind_direction']:
                        forecast_item['wind_direction'] = period['wind_direction'].get('value')
                    if 'wind_speed' in period and period['wind_speed']:
                        forecast_item['wind_speed'] = period['wind_speed'].get('value')
                    if 'visibility' in period and period['visibility']:
                        forecast_item['visibility'] = period['visibility'].get('value')

                    result['forecast'].append(forecast_item)

            return result
        except Exception as e:
            print(f"Error parsing TAF: {e}")
            return {
                'station': data.get('station', 'N/A'),
                'error': str(e),
                'raw': data.get('raw', ''),
                'forecast': []
            }

    def _get_demo_taf(self, airport_code: str) -> Dict:
        """Generate demo TAF data"""
        return {
            'station': airport_code,
            'time': 'DEMO',
            'raw': f'{airport_code} DEMO TAF',
            'forecast': [
                {'type': 'FM', 'wind_direction': 270, 'wind_speed': 10, 'visibility': 10.0, 'flight_rules': 'VFR'},
                {'type': 'FM', 'wind_direction': 180, 'wind_speed': 15, 'visibility': 5.0, 'flight_rules': 'MVFR'},
                {'type': 'FM', 'wind_direction': 90, 'wind_speed': 20, 'visibility': 3.0, 'flight_rules': 'IFR'},
            ]
        }

    def _get_demo_data(self, airport_code: str) -> Dict:
        """
        Generate demo weather data for testing without API
        Args:
            airport_code: Airport code to display
        Returns:
            Dictionary with sample weather data
        """
        import random

        # Cycle through different weather conditions for demo
        weather_scenarios = [
            {
                'flight_rules': 'VFR',
                'temperature': 22,
                'dewpoint': 14,
                'wind_speed': 8,
                'wind_direction': 270,
                'visibility': 10.0,
                'ceiling': None,
                'altimeter': 30.12,
                'conditions': [],
                'clouds': [{'type': 'FEW', 'altitude': 50, 'repr': 'FEW050'}]
            },
            {
                'flight_rules': 'MVFR',
                'temperature': 15,
                'dewpoint': 12,
                'wind_speed': 12,
                'wind_direction': 180,
                'visibility': 5.0,
                'ceiling': 2500,
                'altimeter': 29.92,
                'conditions': ['BR'],
                'clouds': [{'type': 'BKN', 'altitude': 25, 'repr': 'BKN025'}]
            },
            {
                'flight_rules': 'IFR',
                'temperature': 8,
                'dewpoint': 7,
                'wind_speed': 18,
                'wind_direction': 90,
                'visibility': 2.0,
                'ceiling': 1200,
                'altimeter': 29.75,
                'conditions': ['RA'],
                'clouds': [{'type': 'OVC', 'altitude': 12, 'repr': 'OVC012'}]
            },
            {
                'flight_rules': 'VFR',
                'temperature': 28,
                'dewpoint': 18,
                'wind_speed': 5,
                'wind_direction': 45,
                'visibility': 10.0,
                'ceiling': None,
                'altimeter': 30.25,
                'conditions': [],
                'clouds': [{'type': 'SCT', 'altitude': 80, 'repr': 'SCT080'}]
            },
            {
                'flight_rules': 'MVFR',
                'temperature': -2,
                'dewpoint': -4,
                'wind_speed': 15,
                'wind_direction': 360,
                'visibility': 4.0,
                'ceiling': 2000,
                'altimeter': 30.05,
                'conditions': ['SN'],
                'clouds': [{'type': 'OVC', 'altitude': 20, 'repr': 'OVC020'}]
            },
        ]

        # Select a scenario based on time (changes slowly)
        import time
        scenario_index = int(time.time() / 30) % len(weather_scenarios)
        scenario = weather_scenarios[scenario_index]

        return {
            'station': airport_code,
            'time': 'DEMO',
            'flight_rules': scenario['flight_rules'],
            'raw': f'{airport_code} DEMO MODE',
            'temperature': scenario['temperature'],
            'dewpoint': scenario['dewpoint'],
            'wind_direction': scenario['wind_direction'],
            'wind_speed': scenario['wind_speed'],
            'visibility': scenario['visibility'],
            'ceiling': scenario['ceiling'],
            'altimeter': scenario['altimeter'],
            'clouds': scenario['clouds'],
            'conditions': scenario['conditions']
        }

    def get_flight_category_color(self, flight_rules: str) -> tuple:
        """
        Get RGB color for flight category
        Args:
            flight_rules: VFR, MVFR, IFR, or LIFR
        Returns:
            RGB tuple (r, g, b)
        """
        colors = {
            'VFR': (0, 255, 0),      # Green - Visual Flight Rules
            'MVFR': (0, 0, 255),     # Blue - Marginal VFR
            'IFR': (255, 0, 0),      # Red - Instrument Flight Rules
            'LIFR': (255, 0, 255),   # Magenta - Low IFR
            'UNKNOWN': (128, 128, 128)  # Gray
        }
        return colors.get(flight_rules.upper(), colors['UNKNOWN'])


def get_weather_icon(conditions: list, flight_rules: str) -> str:
    """
    Determine weather icon based on conditions
    Args:
        conditions: List of weather condition codes
        flight_rules: Flight category (VFR, MVFR, IFR, LIFR)
    Returns:
        Icon name string
    """
    if not conditions:
        if flight_rules == 'VFR':
            return 'clear'
        else:
            return 'cloudy'

    # Check for severe weather
    for cond in conditions:
        if 'TS' in cond:  # Thunderstorm
            return 'thunderstorm'
        if 'SN' in cond or 'SG' in cond:  # Snow
            return 'snow'
        if 'RA' in cond or 'DZ' in cond:  # Rain
            return 'rain'
        if 'FG' in cond or 'BR' in cond:  # Fog/Mist
            return 'fog'

    # Default based on flight rules
    if flight_rules == 'VFR':
        return 'clear'
    elif flight_rules in ['MVFR', 'IFR', 'LIFR']:
        return 'cloudy'

    return 'unknown'
