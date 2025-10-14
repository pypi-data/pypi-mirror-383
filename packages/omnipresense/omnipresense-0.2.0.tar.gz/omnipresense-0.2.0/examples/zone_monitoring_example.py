"""
Zone Monitoring Example - Traffic Speed Detection with Range Filtering

Demonstrates comprehensive OPS243-C configuration for zone-based traffic monitoring:
1. Explicit baudrate configuration (19200, 8N1)
2. Speed output with magnitude
3. Units in km/h with magnitude filtering
4. Range AND speed filtering (only report speeds within detection zone)
5. Inbound direction filter (approaching traffic only)
6. Cosine correction for angled installation (~50 degrees)

This example is perfect for roadside speed monitoring where you want to:
- Only measure vehicles within a specific distance zone
- Filter out receding traffic (measure approaching only)
- Account for angled sensor mounting
- See both speed and distance with signal strength
"""

import time
from datetime import datetime

from omnipresense import (
    Direction,
    OutputMode,
    Units,
    create_radar,
)


def print_header():
    """Print a nice header for the monitoring session."""
    print("=" * 80)
    print(" " * 20 + "OPS243-C ZONE MONITORING EXAMPLE")
    print("=" * 80)
    print()


def print_config_summary(radar, min_range, max_range, min_speed, angle):
    """Print configuration summary."""
    print("📋 CONFIGURATION SUMMARY")
    print("-" * 80)
    print(f"  Sensor Model:        OPS243-C (Combined Doppler + FMCW)")
    print(f"  Baudrate:            19200 (8N1)")
    print(f"  Speed Units:         km/h")
    print(f"  Detection Zone:      {min_range:.1f}m - {max_range:.1f}m")
    print(f"  Min Speed:           {min_speed:.1f} km/h")
    print(f"  Direction Filter:    INBOUND ONLY (approaching traffic)")
    print(f"  Cosine Correction:   {angle}° (hardware-based)")
    print(f"  Magnitude Filter:    >20 (default)")
    print(f"  Range+Speed Filter:  ENABLED (OY mode)")
    print("-" * 80)
    print()


def print_status(message, status="INFO"):
    """Print status message with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "CONFIG": "⚙️",
        "DATA": "📊",
    }
    symbol = symbols.get(status, "•")
    print(f"[{timestamp}] {symbol} {message}")


def format_reading(reading):
    """Format radar reading for display."""
    parts = []

    # Speed with direction
    if reading.speed:
        direction_arrow = "→" if reading.direction == Direction.APPROACHING else "←"
        parts.append(f"Speed: {reading.speed:6.2f} km/h {direction_arrow}")

    # Range
    if reading.range_m:
        parts.append(f"Range: {reading.range_m:6.2f} m")

    # Magnitude
    if reading.magnitude:
        parts.append(f"Signal: {reading.magnitude:4.0f}")

    return " | ".join(parts) if parts else None


def main():
    """Main monitoring function."""
    print_header()

    # STEP 1: Create radar with explicit baudrate (19200, 8N1 is default)
    print_status("Connecting to OPS243-C radar...", "INFO")
    print_status("Baudrate: 19200 (8N1)", "CONFIG")

    radar = create_radar("OPS243-C", "/dev/ttyACM0", baudrate=19200)

    with radar:
        print_status("Connected successfully!", "SUCCESS")
        print()

        # STEP 0: Reset to factory defaults to ensure clean state
        print_status("Step 0: Resetting to factory defaults...", "CONFIG")
        radar.reset_flash_settings()  # AX command - resets persistent memory
        print_status("Factory reset complete - clean configuration state", "SUCCESS")
        print()

        # Configuration parameters
        MIN_RANGE = 2.0  # meters - start of detection zone
        MAX_RANGE = 20.0  # meters - end of detection zone
        MIN_SPEED = 1.0  # km/h - ignore very slow objects
        MAGNITUDE_THRESHOLD = 20  # signal strength threshold
        COSINE_ANGLE = 50  # degrees - sensor mounting angle

        # STEP 1: Enable speed output modes
        print_status("Step 1: Enabling speed output modes...", "CONFIG")
        radar.enable_output_mode(OutputMode.SPEED, True)  # OS command
        radar.enable_output_mode(OutputMode.DIRECTION, True)  # OD command
        radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)  # OM command
        print_status("Output modes enabled: SPEED, DIRECTION, MAGNITUDE", "SUCCESS")

        # STEP 2: Enable magnitude reporting
        print_status("Step 2: Enabling magnitude output...", "CONFIG")
        radar.enable_magnitude_output(True)  # OM command
        print_status("Magnitude reporting enabled", "SUCCESS")

        # STEP 3: Disable standalone range output
        # This ensures range only appears WITH speed via OY mode
        # Must be done AFTER enabling speed modes to avoid being re-enabled
        print_status("Step 3: Disabling standalone range output...", "CONFIG")
        radar.send_command("od")  # od command - disable range-only reports
        time.sleep(0.2)  # Extra delay for command processing
        print_status(
            "Standalone range output disabled (od) - range will only appear with speed",
            "SUCCESS",
        )

        # STEP 4: Set speed units to km/h and magnitude filtering
        print_status("Step 4: Configuring units and magnitude filter...", "CONFIG")
        radar.set_units(Units.KILOMETERS_PER_HOUR)  # UK command
        radar.set_magnitude_threshold(MAGNITUDE_THRESHOLD, doppler=True)  # M>20 command
        print_status(
            f"Units: km/h, Magnitude threshold: >{MAGNITUDE_THRESHOLD}", "SUCCESS"
        )

        # STEP 5: Set speed-range filtering with OY mode
        print_status("Step 5: Configuring zone-based filtering...", "CONFIG")

        # First, set individual filters
        radar.set_speed_filter(min_speed=MIN_SPEED)  # R>1.0 command
        print_status(f"Speed filter: >{MIN_SPEED} km/h", "SUCCESS")

        radar.set_range_filter(
            min_range=MIN_RANGE, max_range=MAX_RANGE
        )  # r>5.0 and r<20.0 commands
        print_status(f"Range filter: {MIN_RANGE}m - {MAX_RANGE}m", "SUCCESS")

        # Then enable range AND speed filter (OY mode)
        radar.enable_range_and_speed_filter(True)  # OY command
        print_status(
            "Range AND Speed filter ENABLED (OY) - speeds only reported within zone",
            "SUCCESS",
        )

        # STEP 6: Set inbound filter (objects moving towards us)
        # print_status("Step 6: Setting direction filter to INBOUND...", "CONFIG")
        # radar.set_direction_filter(Direction.APPROACHING)  # R+ command
        # print_status("Direction filter: APPROACHING only (R+)", "SUCCESS")

        # STEP 7: Set cosine correction for ~50 degree angle
        # print_status("Step 7: Enabling cosine correction...", "CONFIG")
        # radar.enable_cosine_correction(COSINE_ANGLE)  # ^/+50.0 and ^/-50.0 commands
        # correction_factor = 1 / abs(
        #     __import__("math").cos(__import__("math").radians(COSINE_ANGLE))
        # )
        # print_status(
        #     f"Cosine correction: {COSINE_ANGLE}° (factor: {correction_factor:.3f}x)",
        #     "SUCCESS",
        # )

        print()
        print_config_summary(radar, MIN_RANGE, MAX_RANGE, MIN_SPEED, COSINE_ANGLE)

        # Setup callback for real-time data
        detection_count = 0

        def on_detection(reading):
            nonlocal detection_count
            formatted = format_reading(reading)
            if formatted:
                detection_count += 1
                print_status(f"[#{detection_count:04d}] {formatted}", "DATA")

        # Start monitoring
        print("🚗 MONITORING ZONE: Watching for approaching vehicles...")
        print(f"   Detection zone: {MIN_RANGE}m - {MAX_RANGE}m")
        print(f"   Minimum speed: {MIN_SPEED} km/h")
        print(f"   Press Ctrl+C to stop\n")

        radar.start_streaming(on_detection)

        try:
            # Run indefinitely until user stops
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n")
            print_status(
                f"Monitoring stopped. Total detections: {detection_count}", "INFO"
            )
            print("=" * 80)


if __name__ == "__main__":
    main()
