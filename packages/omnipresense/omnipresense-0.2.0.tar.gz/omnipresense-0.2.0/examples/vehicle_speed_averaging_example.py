"""
Vehicle Speed Averaging Example (OPS243 Only)

This example demonstrates speed averaging functionality for vehicle/traffic monitoring
applications. Speed averaging provides stable, noise-free speed readings by averaging
measurements over configurable time periods.

Use cases:
- Traffic speed monitoring
- Vehicle detection and classification
- Speed enforcement systems
- Traffic flow analysis

The OPS243 supports both time-based averaging and moving average modes for vehicle monitoring.
"""

import time

from omnipresense import (
    Direction,
    OutputMode,
    SamplingRate,
    Units,
    create_radar,
)


def traffic_monitoring_example():
    """
    Example configuration for traffic speed monitoring.

    This setup uses speed averaging to provide stable vehicle speed readings,
    reducing noise from radar fluctuations and providing reliable measurements.
    """
    print("=== Traffic Speed Monitoring Example ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")  # OPS243-C supports averaging

    with radar:
        # Configure sensor for speed measurement
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_sampling_rate(SamplingRate.HZ_10000)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)
        radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)

        # Set filters to focus on vehicle speeds (exclude walking pedestrians)
        radar.set_speed_filter(min_speed=5.0, max_speed=120.0)  # 5-120 km/h range
        radar.set_magnitude_threshold(30)  # Higher threshold for vehicles

        # Configure speed averaging for traffic monitoring
        print("Configuring speed averaging for traffic monitoring...")
        radar.configure_speed_averaging(
            period=3,     # Average over 3 seconds per vehicle
            delay=0,      # No delay - report each vehicle immediately after averaging
            enable=True
        )

        print("Speed averaging configured:")
        print("  - Averaging period: 3 seconds per vehicle")
        print("  - No delay between reports")
        print("  - Filters: 5-120 km/h vehicle speed range")
        print("  - This provides stable speed readings for each vehicle")
        print()

        vehicle_count = 0

        def on_vehicle_detection(reading):
            nonlocal vehicle_count

            if reading.speed is not None and reading.speed > 0:
                vehicle_count += 1
                timestamp = time.strftime("%H:%M:%S", time.localtime(reading.timestamp))
                direction = reading.direction.value if reading.direction else "?"
                magnitude = f", Signal: {reading.magnitude:.0f}" if reading.magnitude else ""

                # Determine direction description
                direction_desc = {
                    "+": "Approaching",
                    "-": "Receding"
                }.get(direction, "Unknown")

                print(f"[{timestamp}] Vehicle #{vehicle_count}: {reading.speed:.1f} km/h {direction_desc}{magnitude}")

                # Vehicle classification based on speed
                if reading.speed < 25:
                    vehicle_type = "🚲 Bicycle/Slow vehicle"
                elif reading.speed < 50:
                    vehicle_type = "🚗 City traffic"
                elif reading.speed < 80:
                    vehicle_type = "🚗 Highway traffic"
                else:
                    vehicle_type = "🚛 Fast vehicle/Highway"

                print(f"         Type: {vehicle_type}")

                # Speed compliance check
                speed_limit = 50  # km/h
                if reading.speed > speed_limit + 10:
                    print(f"         ⚠️  SPEEDING: {reading.speed - speed_limit:.1f} km/h over limit!")

                print()

        print("Starting traffic monitoring (30 seconds)...")
        print("Point the radar at a road or drive vehicles past the sensor...")
        print()

        radar.start_streaming(on_vehicle_detection)
        time.sleep(30)

        print(f"\nTraffic monitoring complete. Total vehicles detected: {vehicle_count}")


def moving_average_vehicle_tracking():
    """
    Example using moving average for real-time vehicle tracking.

    Moving average provides immediate response while smoothing out noise,
    perfect for continuous vehicle tracking applications.
    """
    print("\n=== Real-Time Vehicle Tracking with Moving Average ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Configure for real-time tracking
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_20000)  # High sample rate for responsiveness
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)

        # Configure moving average for smooth tracking
        print("Configuring moving average for real-time tracking...")
        radar.configure_moving_average(
            points=8,     # Average over last 8 readings for smooth tracking
            enable=True
        )

        print("Moving average configured:")
        print("  - 8-point moving average")
        print("  - Real-time smoothed vehicle tracking")
        print("  - Responsive to speed changes while reducing noise")
        print()

        last_speed = 0
        readings_count = 0

        def on_vehicle_tracking(reading):
            nonlocal last_speed, readings_count

            if reading.speed is not None:
                readings_count += 1
                speed_kmh = reading.speed * 3.6  # Convert m/s to km/h
                direction = reading.direction.value if reading.direction else "?"

                # Detect significant speed changes
                speed_change = abs(speed_kmh - last_speed)
                change_indicator = ""
                if speed_change > 5:  # Significant change
                    if speed_kmh > last_speed:
                        change_indicator = " ↗️ Accelerating"
                    else:
                        change_indicator = " ↘️ Decelerating"

                print(f"Reading #{readings_count:2d}: {speed_kmh:5.1f} km/h ({reading.speed:4.1f} m/s) {direction}{change_indicator}")

                last_speed = speed_kmh

        print("Starting real-time vehicle tracking (20 seconds)...")
        print("Move a vehicle in front of the sensor to see smooth tracking...")
        print()

        radar.start_streaming(on_vehicle_tracking)
        time.sleep(20)


def speed_enforcement_example():
    """
    Example for speed enforcement applications.

    Uses precise averaging to ensure accurate speed measurements
    for enforcement purposes.
    """
    print("\n=== Speed Enforcement Example ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Configure for enforcement accuracy
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_sampling_rate(SamplingRate.HZ_10000)
        radar.set_data_precision(2)  # High precision for legal accuracy
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)
        radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)

        # Strict filtering for enforcement
        radar.set_speed_filter(min_speed=10.0, max_speed=200.0)
        radar.set_magnitude_threshold(50)  # High threshold for clear detections

        # Configure for enforcement-grade averaging
        print("Configuring enforcement-grade speed measurement...")
        radar.configure_speed_averaging(
            period=2,     # 2-second averaging for accuracy
            delay=0,      # Immediate reporting
            enable=True
        )

        print("Enforcement configuration:")
        print("  - 2-second averaging period for accuracy")
        print("  - High precision measurements")
        print("  - Strict filtering: 10-200 km/h, high signal threshold")
        print("  - Suitable for legal speed enforcement")
        print()

        speed_limit = 50  # km/h
        violation_count = 0

        def on_enforcement_reading(reading):
            nonlocal violation_count

            if reading.speed is not None and reading.speed > 0:
                timestamp = time.strftime("%H:%M:%S", time.localtime(reading.timestamp))
                direction = reading.direction.value if reading.direction else "?"
                magnitude = reading.magnitude if reading.magnitude else 0

                print(f"[{timestamp}] Vehicle Speed: {reading.speed:.2f} km/h, Direction: {direction}, Signal: {magnitude:.0f}")

                # Check for speed violations
                if reading.speed > speed_limit:
                    violation_count += 1
                    excess_speed = reading.speed - speed_limit
                    severity = "MINOR" if excess_speed <= 10 else "MAJOR" if excess_speed <= 20 else "SEVERE"

                    print(f"         🚨 VIOLATION #{violation_count}: {excess_speed:.2f} km/h over limit ({severity})")
                    print(f"         Recommended Action: {'Warning' if severity == 'MINOR' else 'Citation' if severity == 'MAJOR' else 'Court Summons'}")
                else:
                    print(f"         ✅ Compliant: {speed_limit - reading.speed:.2f} km/h under limit")

                print()

        print(f"Starting speed enforcement monitoring (speed limit: {speed_limit} km/h)...")
        print("High-precision averaging ensures legally defensible measurements...")
        print()

        radar.start_streaming(on_enforcement_reading)
        time.sleep(25)

        print(f"\nEnforcement session complete. Total violations: {violation_count}")


def main():
    """
    Main vehicle speed monitoring demonstration.
    """
    try:
        print("OPS243 Vehicle Speed Averaging Demonstration")
        print("=" * 55)
        print()
        print("This example demonstrates speed averaging for vehicle monitoring applications.")
        print("Speed averaging provides stable, accurate readings for traffic analysis.")
        print()

        # Run vehicle monitoring demonstrations
        traffic_monitoring_example()
        moving_average_vehicle_tracking()
        speed_enforcement_example()

        print("\n" + "=" * 55)
        print("Vehicle speed monitoring demonstration complete!")
        print()
        print("Key applications:")
        print("• Traffic flow monitoring with stable speed readings")
        print("• Real-time vehicle tracking with moving averages")
        print("• Speed enforcement with legally defensible accuracy")
        print("• Vehicle classification based on speed patterns")

    except Exception as e:
        if "OPS243" in str(e):
            print("Error: Speed averaging features require an OPS243 device")
            print("Available OPS243 models: OPS243-A, OPS243-C")
        else:
            print(f"Error: {e}")

        print("\nTroubleshooting:")
        print("• Ensure you have an OPS243-A or OPS243-C sensor")
        print("• Position sensor to detect vehicle traffic")
        print("• Check sensor connection and power")
        print("• Verify vehicles are within detection range")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")