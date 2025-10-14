"""
Cosine Error Correction Example

Demonstrates how to use hardware cosine error correction for angled radar installations.

Cosine error occurs when the radar sensor is not perpendicular to the target's
direction of motion. The radar measures radial velocity (v_radial = v_actual × cos(θ)),
which underestimates actual speed and range.

Common use cases:
- Traffic monitoring with side-mounted radar
- Overhead mounting at an angle
- Installation constraints requiring non-perpendicular placement

This example shows:
- When cosine correction is needed
- How to enable hardware-based correction
- Configuring separate angles for inbound/outbound traffic
- Understanding correction factors
"""

import math
import time

from omnipresense import OutputMode, Units, create_radar


def calculate_correction_factor(angle_degrees):
    """Calculate the correction factor for a given angle."""
    return 1 / math.cos(math.radians(angle_degrees))


def demonstrate_correction_concept():
    """
    Demonstrate the concept of cosine error with examples.
    """
    print("=" * 70)
    print("COSINE ERROR CORRECTION - CONCEPT")
    print("=" * 70)
    print()
    print("When radar is not perpendicular to motion, it measures radial velocity:")
    print("  v_radial = v_actual × cos(angle)")
    print()
    print("Correction applied by hardware: v_actual = v_radial / cos(angle)")
    print()
    print("Example corrections needed:")
    print()

    angles = [0, 15, 30, 45, 60]
    actual_speed = 100  # km/h

    print(f"{'Angle':>6}  {'Measured':>10}  {'Correction':>12}  {'Corrected':>10}")
    print("-" * 50)

    for angle in angles:
        factor = calculate_correction_factor(angle)
        measured = actual_speed * math.cos(math.radians(angle))
        corrected = measured * factor

        print(
            f"{angle:>6}°  {measured:>9.1f}  {factor:>11.3f}x  {corrected:>9.1f}"
        )

    print()
    print("Note: Angles > 45° produce unreliable corrections (factor > 1.41x)")
    print()


def basic_correction_example():
    """
    Basic example of enabling hardware cosine correction for a 30° angled installation.
    """
    print("=" * 70)
    print("BASIC HARDWARE CORRECTION EXAMPLE")
    print("=" * 70)
    print()
    print("Scenario: Radar mounted at 30° angle to traffic flow")
    print("Expected: 30° angle requires 1.155x correction factor")
    print("Correction: Applied by sensor hardware (no software processing)")
    print()

    try:
        radar = create_radar("OPS243-C", "/dev/ttyACM0")

        with radar:
            # Configure basic radar settings
            radar.set_units(Units.KILOMETERS_PER_HOUR)
            radar.enable_output_mode(OutputMode.SPEED, True)
            radar.enable_output_mode(OutputMode.DIRECTION, True)

            # Enable hardware cosine correction for 30° angle
            # Sensor will automatically apply correction to all readings
            radar.enable_cosine_correction(30)

            print("Hardware cosine correction enabled: 30° angle")
            print("All reported speeds are automatically corrected by sensor")
            print()
            print("Monitoring traffic... (10 seconds)")
            print()
            print(f"{'Time':>6}  {'Speed (km/h)':>13}  {'Direction':>10}")
            print("-" * 40)

            readings_count = 0

            def on_detection(reading):
                nonlocal readings_count
                if reading.speed is not None and readings_count < 10:
                    direction = reading.direction.value if reading.direction else "?"

                    print(
                        f"{reading.timestamp % 1000:>6.1f}  "
                        f"{reading.speed:>12.1f}  "
                        f"{direction:>10}"
                    )

                    readings_count += 1

            radar.start_streaming(on_detection)
            time.sleep(10)

            print()
            print("Correction automatically applied by sensor hardware!")

    except Exception as e:
        print(f"Error: {e}")


def traffic_monitoring_example():
    """
    Traffic monitoring with separate angles for inbound/outbound lanes.

    Real-world scenario: Side-mounted radar monitoring two-lane traffic where
    lanes are at different distances from the sensor.
    """
    print()
    print("=" * 70)
    print("TRAFFIC MONITORING - SEPARATE LANE ANGLES")
    print("=" * 70)
    print()
    print("Scenario: Side-mounted radar monitoring two-lane traffic")
    print("  - Inbound lane (closer): 25° angle")
    print("  - Outbound lane (farther): 35° angle")
    print()

    try:
        radar = create_radar("OPS243-C", "/dev/ttyACM0")

        with radar:
            radar.set_units(Units.KILOMETERS_PER_HOUR)
            radar.enable_output_mode(OutputMode.SPEED, True)
            radar.enable_output_mode(OutputMode.DIRECTION, True)
            radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)

            # Configure separate angles for approaching (inbound) and receding (outbound) traffic
            radar.enable_cosine_correction(
                angle_inbound_degrees=25,
                angle_outbound_degrees=35
            )

            print("Hardware correction configured:")
            print("  Inbound (approaching): 25° → 1.103x correction")
            print("  Outbound (receding):  35° → 1.221x correction")
            print()
            print("Monitoring traffic... (15 seconds)")
            print()
            print(f"{'Time':>6}  {'Speed':>6}  {'Direction':>11}  {'Magnitude':>9}")
            print("-" * 45)

            def on_vehicle_detection(reading):
                if reading.speed is not None and reading.speed > 5:  # Filter slow objects
                    direction_str = "Approaching" if reading.direction and reading.direction.value == "+" else "Receding"
                    magnitude = f"{reading.magnitude:.0f}" if reading.magnitude else "N/A"

                    print(
                        f"{reading.timestamp % 1000:>6.1f}  "
                        f"{reading.speed:>5.1f}  "
                        f"{direction_str:>11}  "
                        f"{magnitude:>9}"
                    )

            radar.start_streaming(on_vehicle_detection)
            time.sleep(15)

            print()
            print("Each lane automatically gets its configured correction!")

    except Exception as e:
        print(f"Error: {e}")


def query_correction_settings():
    """
    Example of querying current cosine correction settings from sensor.
    """
    print()
    print("=" * 70)
    print("QUERY CORRECTION SETTINGS")
    print("=" * 70)
    print()

    try:
        radar = create_radar("OPS243-C", "/dev/ttyACM0")

        with radar:
            # Query current settings from sensor hardware
            config = radar.get_cosine_correction()

            print("Current hardware correction settings:")
            print(f"  Enabled: {config.enabled}")
            print(f"  Inbound angle: {config.angle_inbound_degrees}°")
            print(f"  Outbound angle: {config.angle_outbound_degrees}°")
            print()

            if config.enabled:
                inbound_factor = calculate_correction_factor(config.angle_inbound_degrees)
                outbound_factor = calculate_correction_factor(config.angle_outbound_degrees)
                print("Correction factors:")
                print(f"  Inbound: {inbound_factor:.3f}x")
                print(f"  Outbound: {outbound_factor:.3f}x")

    except Exception as e:
        print(f"Error: {e}")


def disable_correction_example():
    """
    Example of disabling cosine correction.
    """
    print()
    print("=" * 70)
    print("DISABLE CORRECTION")
    print("=" * 70)
    print()

    try:
        radar = create_radar("OPS243-C", "/dev/ttyACM0")

        with radar:
            # Disable hardware correction
            radar.disable_cosine_correction()

            print("Hardware cosine correction disabled")
            print("Sensor will report uncorrected (radial) velocities")

    except Exception as e:
        print(f"Error: {e}")


def main():
    """
    Main demonstration of hardware cosine correction.
    """
    try:
        print("OPS Radar Hardware Cosine Error Correction")
        print("=" * 70)
        print()
        print("This example demonstrates hardware-based cosine correction.")
        print("The sensor applies correction internally - no software processing needed!")
        print()

        # Run demonstrations
        demonstrate_correction_concept()
        basic_correction_example()
        traffic_monitoring_example()
        query_correction_settings()
        disable_correction_example()

        print()
        print("=" * 70)
        print("Hardware cosine correction demonstration complete!")
        print()
        print("Key takeaways:")
        print("• Correction is applied by sensor hardware (transparent to application)")
        print("• Separate angles can be configured for inbound/outbound traffic")
        print("• Ideal for side-mounted traffic monitoring with multiple lanes")
        print("• Corrections are part of persistent memory (survive reboot)")

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("• Ensure you have an OPS241-A, OPS242-A, OPS243-A, or OPS243-C sensor")
        print("• Check sensor connection and port settings")
        print("• Verify sensor is powered on")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
