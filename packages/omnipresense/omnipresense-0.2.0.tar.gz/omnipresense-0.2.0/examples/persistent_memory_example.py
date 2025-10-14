"""
Persistent Memory Example

This example demonstrates the persistent memory functionality that allows saving
configuration settings to flash memory. These settings are retained even after
power loss or power cycling.

This is useful for applications that need consistent sensor configuration
without having to reconfigure the sensor every time.
"""

import time

from omnipresense import (
    BlankReporting,
    OutputMode,
    PowerMode,
    SamplingRate,
    Units,
    create_radar,
)


def main():
    # Connect to radar sensor
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        print("=== Persistent Memory Demonstration ===")
        print()

        # 1. Read current flash settings
        print("1. Reading current flash settings...")
        try:
            flash_settings = radar.read_flash_settings()
            print(f"Current flash settings: {flash_settings}")
        except Exception as e:
            print(f"Error reading flash settings: {e}")
        print()

        # 2. Get persistent memory settings
        print("2. Getting persistent memory settings...")
        try:
            memory_settings = radar.get_persistent_memory_settings()
            print(f"Persistent memory settings: {memory_settings}")
        except Exception as e:
            print(f"Error getting persistent memory settings: {e}")
        print()

        # 3. Configure sensor with custom settings
        print("3. Configuring sensor with custom settings...")
        radar.set_power_mode(PowerMode.ACTIVE)
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_sampling_rate(SamplingRate.HZ_5000)
        radar.set_data_precision(1)
        radar.set_magnitude_threshold(25)
        radar.set_blank_reporting(BlankReporting.ZERO_VALUES)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)
        radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)

        print("Custom configuration applied:")
        print("  - Units: kilometers per hour")
        print("  - Sampling rate: 5000 Hz")
        print("  - Data precision: 1 decimal place")
        print("  - Magnitude threshold: 25")
        print("  - Blank reporting: zero values")
        print("  - Output modes: speed, direction, magnitude")
        print()

        # 4. Save configuration to flash memory
        print("4. Saving configuration to flash memory...")
        print("   (This will take ~1 second due to required delay)")
        try:
            radar.save_config_to_memory()
            print("✓ Configuration successfully saved to flash memory!")
            print("   Settings will persist across power cycles.")
        except Exception as e:
            print(f"✗ Error saving configuration: {e}")
        print()

        # 5. Read flash settings again to confirm
        print("5. Reading flash settings again to confirm save...")
        try:
            new_flash_settings = radar.read_flash_settings()
            print(f"Updated flash settings: {new_flash_settings}")
        except Exception as e:
            print(f"Error reading updated flash settings: {e}")
        print()

        # 6. Demonstrate configuration persistence simulation
        print("6. Configuration persistence demonstration:")
        print("   The settings are now saved to flash memory.")
        print("   If you power cycle the sensor, it will start with these settings.")
        print("   No need to reconfigure the sensor in your application!")
        print()

        # 7. Optional: Reset to factory defaults
        print("7. Optional: Reset to factory defaults")
        print("   Uncomment the following lines to reset flash to factory defaults:")
        print("   # radar.reset_flash_settings()  # or radar.reset_sensor()")
        print("   # print('✓ Flash settings reset to factory defaults')")
        print()

        # Demonstrate the configured sensor working
        print("8. Testing configured sensor (5 seconds)...")

        def on_detection(reading):
            speed_text = (
                f"Speed: {reading.speed:.1f} km/h"
                if reading.speed is not None
                else "No speed"
            )
            direction = reading.direction.value if reading.direction else "?"
            magnitude_text = (
                f", Magnitude: {reading.magnitude:.0f}"
                if reading.magnitude is not None
                else ""
            )

            # Show if this is a blank report (zero speed from hardware)
            blank_indicator = " [BLANK]" if reading.speed == 0.0 else ""

            print(f"{speed_text}, Direction: {direction}{magnitude_text}{blank_indicator}")

        radar.start_streaming(on_detection)
        time.sleep(5)

        print()
        print("=== Demonstration Complete ===")
        print()
        print("Summary:")
        print("• Custom configuration has been saved to flash memory")
        print("• Settings will persist across power cycles")
        print("• Use radar.reset_flash_settings() to restore factory defaults")
        print("• Use radar.read_flash_settings() to check current saved settings")


def factory_reset_example():
    """
    Example of how to reset sensor to factory defaults
    """
    print("=== Factory Reset Example ===")
    print()

    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        print("Resetting sensor to factory defaults...")
        print("(This will take ~1 second due to required delay)")

        try:
            # Option 1: Use reset_sensor() (resets everything)
            radar.reset_sensor()
            print("✓ Sensor reset to factory defaults!")

            # Option 2: Use reset_flash_settings() (same effect, more explicit)
            # radar.reset_flash_settings()
            # print("✓ Flash settings reset to factory defaults!")

        except Exception as e:
            print(f"✗ Error resetting sensor: {e}")

        print()
        print("Factory reset complete. All custom settings have been cleared.")


if __name__ == "__main__":
    try:
        # Run main demonstration
        main()

        # Uncomment to run factory reset example
        # print("\n" + "="*50 + "\n")
        # factory_reset_example()

    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("• Ensure radar sensor is connected")
        print("• Check the correct port name (/dev/ttyACM0)")
        print("• Verify sensor is powered on")