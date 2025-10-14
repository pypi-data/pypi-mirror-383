"""
Water Height Monitoring with Range Averaging (OPS243 Only)

This example demonstrates range averaging functionality specifically for water height
and level monitoring applications. Range averaging provides stable, noise-free
measurements by averaging sensor readings over configurable time periods.

Use cases:
- Water level monitoring in tanks, reservoirs, rivers
- Flood monitoring and early warning systems
- Industrial liquid level control
- Environmental water monitoring
- Irrigation system management

The OPS243's range averaging eliminates noise and provides reliable long-term measurements.
"""

import time

from omnipresense import (
    OutputMode,
    SamplingRate,
    Units,
    create_radar,
)


def water_height_monitoring_example():
    """
    Example configuration for water height monitoring application.

    This setup uses range averaging to provide stable water level readings
    over time, reducing noise and providing reliable measurements.
    """
    print("=== Water Height Monitoring Example ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")  # OPS243-C supports averaging

    with radar:
        # Configure sensor for range measurement
        radar.set_units(Units.METERS)
        radar.enable_output_mode(OutputMode.SPEED, False)  # Disable speed output
        radar.enable_output_mode(OutputMode.DIRECTION, False)  # Disable direction output
        radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)  # Enable for signal quality

        # Configure range averaging for water height monitoring
        print("Configuring range averaging for water height monitoring...")
        radar.configure_range_averaging(
            period=10,    # Average over 10 seconds for stable readings
            delay=60,     # Report averaged reading every minute
            enable=True   # Enable range averaging
        )

        print("Range averaging configured:")
        print("  - Averaging period: 10 seconds")
        print("  - Reporting interval: 60 seconds")
        print("  - This provides stable water level readings every minute")
        print()

        # Data callback for water height monitoring
        def on_water_level_reading(reading):
            timestamp = time.strftime("%H:%M:%S", time.localtime(reading.timestamp))

            if reading.range_m is not None:
                # Convert range to water height (assuming sensor is 5m above water)
                sensor_height = 5.0  # meters above water surface
                water_height = sensor_height - reading.range_m

                magnitude_text = f", Signal: {reading.magnitude:.0f}" if reading.magnitude else ""

                print(f"[{timestamp}] Water Height: {water_height:.2f}m (Range: {reading.range_m:.2f}m){magnitude_text}")

                # Alert for unusual water levels
                if water_height > 3.0:
                    print("  ⚠️  WARNING: High water level detected!")
                elif water_height < 0.5:
                    print("  ⚠️  WARNING: Low water level detected!")

        print("Starting water height monitoring (will show averaged readings every minute)...")
        print("Note: In real deployment, you would see readings every 60 seconds")
        print("For demo purposes, we'll run for 2 minutes...")
        print()

        radar.start_streaming(on_water_level_reading)
        time.sleep(120)  # Monitor for 2 minutes

        print("\nWater height monitoring demo complete.")


def speed_averaging_example():
    """
    Example of speed averaging for traffic monitoring.
    """
    print("\n=== Speed Averaging Example ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Configure sensor for speed measurement
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_sampling_rate(SamplingRate.HZ_5000)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)

        # Configure speed averaging
        print("Configuring speed averaging...")
        radar.configure_speed_averaging(
            period=5,     # Average over 5 seconds
            delay=30,     # Report averaged speed every 30 seconds
            enable=True
        )

        print("Speed averaging configured:")
        print("  - Averaging period: 5 seconds")
        print("  - Reporting interval: 30 seconds")
        print("  - Provides stable speed readings for traffic monitoring")
        print()

        def on_averaged_speed(reading):
            timestamp = time.strftime("%H:%M:%S", time.localtime(reading.timestamp))

            if reading.speed is not None and reading.speed > 0:
                direction = reading.direction.value if reading.direction else "?"
                print(f"[{timestamp}] Average Speed: {reading.speed:.1f} km/h, Direction: {direction}")

        print("Starting speed averaging demo (30 seconds)...")
        radar.start_streaming(on_averaged_speed)
        time.sleep(30)


def moving_average_example():
    """
    Example of moving average mode for real-time smoothing.
    """
    print("\n=== Moving Average Example ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Configure sensor
        radar.set_units(Units.METERS_PER_SECOND)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)

        # Configure moving average
        print("Configuring moving average...")
        radar.configure_moving_average(
            points=10,    # Average over last 10 readings
            enable=True
        )

        print("Moving average configured:")
        print("  - Moving average over 10 data points")
        print("  - Provides real-time smoothed readings")
        print("  - Reduces noise while maintaining responsiveness")
        print()

        readings_count = 0

        def on_moving_average(reading):
            nonlocal readings_count
            readings_count += 1

            if reading.speed is not None and reading.speed > 0:
                direction = reading.direction.value if reading.direction else "?"
                print(f"Reading #{readings_count:2d}: Smoothed Speed: {reading.speed:.2f} m/s, Direction: {direction}")

        print("Starting moving average demo (20 seconds)...")
        print("Move something in front of the sensor to see smoothed readings...")
        radar.start_streaming(on_moving_average)
        time.sleep(20)


def configuration_management_example():
    """
    Example of checking and managing averaging configuration.
    """
    print("\n=== Configuration Management Example ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Get current averaging configuration
        config = radar.get_averaging_config()

        print("Current averaging configuration:")
        print(f"  Range averaging enabled: {config.range_averaging_enabled}")
        print(f"  Range averaging period: {config.range_averaging_period}s")
        print(f"  Range averaging delay: {config.range_averaging_delay}s")
        print(f"  Speed averaging enabled: {config.speed_averaging_enabled}")
        print(f"  Speed averaging period: {config.speed_averaging_period}s")
        print(f"  Speed averaging delay: {config.speed_averaging_delay}s")
        print(f"  Moving average points: {config.moving_average_points}")
        print()

        # Demonstrate individual parameter setting
        print("Setting individual averaging parameters...")

        radar.set_range_averaging_period(15)
        radar.set_range_averaging_delay(120)
        radar.enable_range_averaging(True)

        radar.set_speed_averaging_period(8)
        radar.set_moving_average_points(15)

        # Get updated configuration
        updated_config = radar.get_averaging_config()
        print("Updated configuration:")
        print(f"  Range averaging period: {updated_config.range_averaging_period}s")
        print(f"  Range averaging delay: {updated_config.range_averaging_delay}s")
        print(f"  Speed averaging period: {updated_config.speed_averaging_period}s")
        print(f"  Moving average points: {updated_config.moving_average_points}")


def main():
    """
    Main demonstration of water height monitoring with averaging.
    """
    try:
        print("OPS243 Water Height Monitoring with Range Averaging")
        print("=" * 52)
        print()
        print("This example demonstrates range averaging for water height monitoring applications.")
        print("Range averaging provides stable, noise-free water level readings over time.")
        print()

        # Run demonstrations
        water_height_monitoring_example()
        speed_averaging_example()
        moving_average_example()
        configuration_management_example()

        print("\n" + "=" * 52)
        print("Water height monitoring demonstration complete!")
        print()
        print("Key takeaways:")
        print("• Range averaging eliminates noise for stable water level readings")
        print("• Configurable periods allow optimization for different monitoring needs")
        print("• Long-term averaging perfect for flood monitoring and level control")
        print("• All timing parameters can be adjusted for your specific application")

    except Exception as e:
        if "OPS243" in str(e):
            print("Error: Averaging features require an OPS243 device")
            print("Available OPS243 models: OPS243-A, OPS243-C")
        else:
            print(f"Error: {e}")

        print("\nTroubleshooting:")
        print("• Ensure you have an OPS243-A or OPS243-C sensor")
        print("• Check sensor connection and port settings")
        print("• Verify sensor is powered on")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")