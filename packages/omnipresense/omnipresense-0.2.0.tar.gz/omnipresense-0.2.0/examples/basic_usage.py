"""
Basic Usage Example

A minimal example showing how to get started with OmniPreSense radar sensors.
This example uses kilometers per hour and shows speed, direction, and distance detection.

Demonstrates baudrate configuration options:
- Automatic detection (default, recommended)
- Manual baudrate specification
- Persistent baudrate settings
"""

import time

from omnipresense import BaudRate, BlankReporting, OutputMode, PowerMode, SamplingRate, Units, create_radar


def main():
    # Connect to radar sensor with automatic baudrate detection (recommended)
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    # Alternative connection methods:

    # Specify exact baudrate (useful if you know the sensor's current setting)
    # radar = create_radar("OPS243-C", "/dev/ttyACM0", baudrate=19200)

    # Use BaudRate enum for type safety
    # radar = create_radar("OPS243-C", "/dev/ttyACM0", baudrate=BaudRate.BAUD_19200)

    # Disable auto-detection (faster connection if you're sure about baudrate)
    # radar = create_radar("OPS243-C", "/dev/ttyACM0", baudrate=19200, auto_detect_baudrate=False)

    with radar:
        # Configure sensor for speed detection in km/h
        radar.set_power_mode(PowerMode.ACTIVE)
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_data_precision(2)
        radar.set_sampling_rate(SamplingRate.HZ_1000)
        radar.set_duty_cycle(5, 0)

        # Enable output modes (required for data transmission)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)
        radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)

        # Optional: Set blank reporting to get zero-speed readings when movement stops
        radar.set_blank_reporting(BlankReporting.ZERO_VALUES)  # Report zero values when no movement detected
        # radar.set_blank_reporting(BlankReporting.DISABLED)    # No blank reporting (default)
        # radar.set_blank_reporting(BlankReporting.TIMESTAMPS)  # Report timestamps when no movement

        # Optional: Save configuration to flash memory (persists across power cycles)
        # radar.save_config_to_memory()  # Uncomment to save current settings to flash
        # radar.save_config_to_memory(save_baudrate=True)  # Also save current baudrate
        # print("Configuration saved to persistent memory!")

        # Show current connection info
        print(f"Connected at {radar.get_current_baud_rate()} baud")

        # Optional: Query sensor's baudrate setting
        try:
            sensor_baud, response = radar.query_baud_rate()
            print(f"Sensor reports baudrate: {sensor_baud}")
        except Exception as e:
            print(f"Could not query sensor baudrate: {e}")

        print("Radar configured. Move something in front of the sensor...")

        # Define callback for radar readings
        def on_detection(reading):
            print(f"Raw data: '{reading.raw_data}'")
            direction = reading.direction.value if reading.direction else "?"
            distance = f", Distance: {reading.range_m:.1f}m" if reading.range_m else ""
            speed_text = (
                f"Speed: {reading.speed:.1f} km/h" if reading.speed is not None else "No speed"
            )
            print(f"{speed_text}, Direction: {direction}{distance}")

        # Start data streaming
        radar.start_streaming(on_detection)

        # Run for 10 seconds
        time.sleep(10)

        print("Detection complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
