#!/usr/bin/env python3
"""
Test script to generate sample screenshots without pygame
"""
from src.weather.weather_fetcher import WeatherFetcher
from src.graphics.renderer import DisplayRenderer

def main():
    print("Generating test screenshots...")

    # Create fetcher and renderer
    fetcher = WeatherFetcher()
    renderer = DisplayRenderer(64, 64)

    # Get demo weather data
    metar_data = fetcher.get_metar('KJFK')
    taf_data = fetcher.get_taf('KJFK')

    print("\nMETAR Data:")
    print(f"  Station: {metar_data.get('station')}")
    print(f"  Flight Rules: {metar_data.get('flight_rules')}")
    print(f"  Temperature: {metar_data.get('temperature')}°C")
    print(f"  Dewpoint: {metar_data.get('dewpoint')}°C")
    print(f"  Wind: {metar_data.get('wind_direction')}° @ {metar_data.get('wind_speed')} kt")
    print(f"  Visibility: {metar_data.get('visibility')} SM")
    print(f"  Ceiling: {metar_data.get('ceiling')} ft")

    print("\nTAF Data:")
    print(f"  Station: {taf_data.get('station')}")
    print(f"  Forecast periods: {len(taf_data.get('forecast', []))}")
    for i, period in enumerate(taf_data.get('forecast', [])[:5]):
        print(f"  Period {i+1}:")
        print(f"    Time: {period.get('start_time')} UTC")
        print(f"    Flight Rules: {period.get('flight_rules')}")
        print(f"    Wind: {period.get('wind_direction')}° @ {period.get('wind_speed')} kt")
        print(f"    Ceiling: {period.get('ceiling')} ft")
        print(f"    Visibility: {period.get('visibility')} SM")

    # Generate METAR display
    metar_img = renderer.create_metar_display(
        station=metar_data.get('station', 'KJFK'),
        temperature=metar_data.get('temperature'),
        dewpoint=metar_data.get('dewpoint'),
        wind_speed=metar_data.get('wind_speed'),
        wind_direction=metar_data.get('wind_direction'),
        visibility=metar_data.get('visibility'),
        ceiling=metar_data.get('ceiling'),
        flight_rules=metar_data.get('flight_rules', 'UNKNOWN'),
        conditions=metar_data.get('conditions', []),
        frame=0
    )

    # Scale up for better viewing (10x)
    metar_img_large = metar_img.resize((640, 640), 0)  # NEAREST neighbor
    metar_img_large.save('test_metar_display.png')
    print("\nSaved: test_metar_display.png")

    # Generate TAF display
    taf_img = renderer.create_taf_display(
        station=metar_data.get('station', 'KJFK'),
        taf_data=taf_data,
        flight_rules=metar_data.get('flight_rules', 'UNKNOWN'),
        frame=0
    )

    # Scale up for better viewing (10x)
    taf_img_large = taf_img.resize((640, 640), 0)  # NEAREST neighbor
    taf_img_large.save('test_taf_display.png')
    print("Saved: test_taf_display.png")

    print("\nTest complete! Check the PNG files to see the displays.")

if __name__ == '__main__':
    main()
