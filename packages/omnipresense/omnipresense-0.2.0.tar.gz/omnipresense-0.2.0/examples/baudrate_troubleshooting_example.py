"""
Baudrate Troubleshooting and Configuration Example

This example demonstrates how to work with different baudrates, troubleshoot
connection issues, and configure the radar's UART settings for optimal communication.

Key features covered:
- Automatic baudrate detection
- Manual baudrate configuration
- Connection troubleshooting
- Persistent baudrate settings
- UART control commands
"""

import time
import logging

from omnipresense import (
    BaudRate,
    OutputMode,
    RadarConnectionError,
    RadarCommandError,
    Units,
    create_radar,
)

# Enable debug logging to see connection attempts
logging.basicConfig(level=logging.INFO)


def automatic_detection_example():
    """
    Example of automatic baudrate detection (default behavior).

    This is the recommended approach for most users.
    """
    print("=== Automatic Baudrate Detection Example ===")
    print()

    try:
        # Create radar with auto-detection enabled (default)
        print("Attempting connection with automatic baudrate detection...")
        radar = create_radar("OPS243-C", "/dev/ttyACM0")

        with radar:
            print(f"✅ Successfully connected at {radar.get_current_baud_rate()} baud")

            # Get sensor's actual baudrate setting
            try:
                sensor_baud, response = radar.query_baud_rate()
                print(f"📡 Sensor reports baudrate: {sensor_baud}")
                print(f"   Raw response: {response}")
            except RadarCommandError as e:
                print(f"⚠️  Could not query sensor baudrate: {e}")

            # Test basic functionality
            radar.set_units(Units.KILOMETERS_PER_HOUR)
            radar.enable_output_mode(OutputMode.SPEED, True)
            print("✅ Basic configuration successful")

    except RadarConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting suggestions:")
        print("1. Check that the sensor is powered on")
        print("2. Verify the port name (/dev/ttyACM0, /dev/ttyUSB0, COM3, etc.)")
        print("3. Check permissions (Linux: add user to dialout group)")
        print("4. Try the manual baudrate examples below")


def manual_baudrate_example():
    """
    Example of manually specifying baudrate.

    Use this when you know the exact baudrate or when auto-detection fails.
    """
    print("\n=== Manual Baudrate Configuration Example ===")
    print()

    # List of common baudrates to try
    baudrates_to_try = [
        (BaudRate.BAUD_19200, "19200 (radar default)"),
        (BaudRate.BAUD_115200, "115200 (common for USB)"),
        (BaudRate.BAUD_9600, "9600 (most reliable)"),
        (BaudRate.BAUD_57600, "57600 (medium speed)"),
        (BaudRate.BAUD_230400, "230400 (fastest)"),
    ]

    for baudrate, description in baudrates_to_try:
        print(f"Trying {description}...")

        try:
            # Disable auto-detection and specify exact baudrate
            radar = create_radar(
                "OPS243-C",
                "/dev/ttyACM0",
                baudrate=baudrate.value,
                auto_detect_baudrate=False
            )

            with radar:
                print(f"✅ Connected successfully at {baudrate.value} baud")

                # Verify connection works
                radar.set_units(Units.METERS_PER_SECOND)
                print("✅ Connection verified - basic commands work")
                break

        except RadarConnectionError:
            print(f"❌ Failed at {baudrate.value} baud")
            continue
    else:
        print("❌ Could not connect at any baudrate")


def baudrate_change_example():
    """
    Example of changing the sensor's baudrate setting.

    ⚠️ WARNING: This changes the sensor's configuration permanently
    until reset or changed again.
    """
    print("\n=== Baudrate Change Example ===")
    print()
    print("⚠️  WARNING: This will change the sensor's baudrate setting!")
    print("   You will need to reconnect after the change.")
    print()

    # Get user confirmation
    confirm = input("Continue? (y/N): ").lower().strip()
    if confirm != 'y':
        print("Skipping baudrate change example")
        return

    try:
        # Connect with current settings
        radar = create_radar("OPS243-C", "/dev/ttyACM0")

        with radar:
            # Check current baudrate
            current_baud = radar.get_current_baud_rate()
            print(f"📡 Current connection baudrate: {current_baud}")

            try:
                sensor_baud, _ = radar.query_baud_rate()
                print(f"📡 Sensor reports baudrate: {sensor_baud}")
            except:
                print("📡 Could not query sensor baudrate")

            # Change to a different baudrate
            new_baudrate = BaudRate.BAUD_57600
            print(f"\n🔄 Changing sensor baudrate to {new_baudrate.value}...")

            radar.set_baud_rate(new_baudrate)
            print("✅ Baudrate change command sent")

        print("\n🔌 Reconnecting with new baudrate...")
        time.sleep(1)  # Give sensor time to switch

        # Reconnect with new baudrate
        new_radar = create_radar(
            "OPS243-C",
            "/dev/ttyACM0",
            baudrate=new_baudrate.value,
            auto_detect_baudrate=False
        )

        with new_radar:
            print(f"✅ Successfully reconnected at {new_baudrate.value} baud")

            # Verify connection
            new_radar.set_units(Units.KILOMETERS_PER_HOUR)
            print("✅ New connection verified")

    except Exception as e:
        print(f"❌ Baudrate change failed: {e}")


def persistent_baudrate_example():
    """
    Example of saving baudrate to persistent memory.

    This ensures the baudrate setting survives power cycles.
    """
    print("\n=== Persistent Baudrate Example ===")
    print()

    try:
        radar = create_radar("OPS243-C", "/dev/ttyACM0")

        with radar:
            current_baud = radar.get_current_baud_rate()
            print(f"📡 Current baudrate: {current_baud}")

            # Save current configuration including baudrate to flash memory
            print("\n💾 Saving configuration to persistent memory...")
            radar.save_config_to_memory(save_baudrate=True)
            print("✅ Configuration and baudrate saved to flash memory")
            print("   This will be used as default after power cycling")

            # Alternative: save only baudrate
            print("\n💾 Alternative: saving only baudrate...")
            radar.save_baudrate_to_memory()
            print("✅ Baudrate saved to persistent memory")

    except Exception as e:
        print(f"❌ Failed to save persistent settings: {e}")


def connection_diagnostics():
    """
    Comprehensive connection diagnostics and troubleshooting.
    """
    print("\n=== Connection Diagnostics ===")
    print()

    port = "/dev/ttyACM0"  # Change as needed

    print(f"🔍 Diagnosing connection to {port}...")
    print()

    # Test 1: Check if port exists (basic check)
    import os
    if not os.path.exists(port):
        print(f"❌ Port {port} does not exist")
        print("   Try: ls /dev/tty* (Linux) or check Device Manager (Windows)")
        return
    else:
        print(f"✅ Port {port} exists")

    # Test 2: Try auto-detection with detailed logging
    print("\n🔍 Testing auto-detection...")
    try:
        radar = create_radar("OPS243-C", port, auto_detect_baudrate=True)
        with radar:
            baud = radar.get_current_baud_rate()
            print(f"✅ Auto-detection successful at {baud} baud")

            # Test sensor info
            try:
                info = radar.get_sensor_info()
                print(f"✅ Sensor info: {info.model}, FW: {info.firmware_version}")
            except:
                print("⚠️  Connected but could not get sensor info")

    except RadarConnectionError as e:
        print(f"❌ Auto-detection failed: {e}")

        # Test 3: Try each baudrate individually
        print("\n🔍 Testing individual baudrates...")
        for baudrate in BaudRate:
            print(f"   Testing {baudrate.value} baud...", end=" ")
            try:
                test_radar = create_radar(
                    "OPS243-C",
                    port,
                    baudrate=baudrate.value,
                    auto_detect_baudrate=False
                )
                with test_radar:
                    print("✅ Success")
                    break
            except:
                print("❌ Failed")
        else:
            print("\n❌ No baudrate worked")
            print("\nPossible issues:")
            print("1. Wrong port name")
            print("2. Sensor not powered")
            print("3. USB cable issue")
            print("4. Permissions (Linux: sudo usermod -a -G dialout $USER)")
            print("5. Sensor in different mode")


def main():
    """
    Main demonstration of baudrate troubleshooting.
    """
    print("OPS Radar Baudrate Troubleshooting and Configuration")
    print("=" * 60)
    print()
    print("This example demonstrates various aspects of UART/baudrate handling:")
    print("• Automatic detection (recommended)")
    print("• Manual configuration")
    print("• Changing sensor baudrate")
    print("• Persistent memory settings")
    print("• Connection diagnostics")
    print()

    # Run all examples
    try:
        automatic_detection_example()
        manual_baudrate_example()
        baudrate_change_example()
        persistent_baudrate_example()
        connection_diagnostics()

    except KeyboardInterrupt:
        print("\n\nDemo stopped by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")

    print("\n" + "=" * 60)
    print("Baudrate troubleshooting complete!")
    print()
    print("Key takeaways:")
    print("• Use auto-detection for most cases")
    print("• Default radar baudrate is 19200")
    print("• USB connections often use 115200")
    print("• Save baudrate to persistent memory if changed")
    print("• Check logs for detailed connection attempts")


if __name__ == "__main__":
    main()