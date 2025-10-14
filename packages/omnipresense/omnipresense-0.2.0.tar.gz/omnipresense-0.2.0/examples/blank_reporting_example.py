"""
Blank Reporting Feature Example

This example demonstrates the blank reporting functionality that automatically
sends data when no movement is detected by the radar sensor.

This is useful for applications that need to know when objects (like trucks)
have passed and are no longer detected by the radar.
"""

import time

from omnipresense import BlankReporting, OutputMode, SamplingRate, Units, create_radar


def main():
    # Connect to radar sensor
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Configure sensor
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_sampling_rate(SamplingRate.HZ_1000)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)

        # Configure blank reporting behavior - try different values:
        # radar.set_blank_reporting(BlankReporting.DISABLED)     # No blank reporting (default)
        # radar.set_blank_reporting(BlankReporting.BLANK_LINES)  # Send blank lines when no movement
        radar.set_blank_reporting(BlankReporting.ZERO_VALUES)    # Send zero values when no movement (recommended)

        print("Radar configured with zero value blank reporting.")
        print("Move something in front of the sensor, then stop moving it.")
        print("You should see zero-speed readings when no movement is detected.")
        print()

        def on_detection(reading):
            timestamp = reading.timestamp
            direction = reading.direction.value if reading.direction else "?"
            speed_text = f"Speed: {reading.speed:.1f} km/h" if reading.speed is not None else "No speed"

            # Indicate if this is a blank reporting reading (zero speed from hardware)
            blank_indicator = " [BLANK REPORT]" if reading.speed == 0.0 else ""

            print(f"[{timestamp:.3f}] {speed_text}, Direction: {direction}{blank_indicator}")

            # Show special handling for blank reporting
            if reading.speed == 0.0:
                print("  -> No movement detected (hardware blank reporting)")

        # Start data streaming
        radar.start_streaming(on_detection)

        # Run for 30 seconds
        print("Starting detection for 30 seconds...")
        time.sleep(30)

        print("\nDetection complete.")


def demonstration():
    """
    Demonstrates different blank reporting scenarios
    """
    print("=== Blank Reporting Feature Demonstration ===")
    print()

    scenarios = [
        (BlankReporting.DISABLED, "No blank reporting - only real radar data"),
        (BlankReporting.ZERO_VALUES, "Zero values - report 0 speed when no movement (recommended)"),
        (BlankReporting.BLANK_LINES, "Blank lines - send empty lines when no movement"),
        (BlankReporting.SPACES, "Spaces - send space characters when no movement"),
        (BlankReporting.COMMAS, "Commas - send commas when no movement"),
        (BlankReporting.TIMESTAMPS, "Timestamps - send timestamps when no movement"),
    ]

    for mode, description in scenarios:
        print(f"Mode: {mode.name}")
        print(f"Description: {description}")
        print(f"Command: radar.set_blank_reporting(BlankReporting.{mode.name})")
        print()


if __name__ == "__main__":
    try:
        # Show available scenarios
        demonstration()

        # Run the main example
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")