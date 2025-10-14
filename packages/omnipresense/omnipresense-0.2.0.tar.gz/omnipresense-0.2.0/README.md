# OmniPreSense Radar

<div align="center">

[![PyPI version](https://badge.fury.io/py/omnipresense.svg)](https://badge.fury.io/py/omnipresense)
[![Python versions](https://img.shields.io/pypi/pyversions/omnipresense.svg)](https://pypi.org/project/omnipresense/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/omnipresense)](https://pepy.tech/project/omnipresense)

**A comprehensive, type-safe Python interface for OmniPreSense radar sensors**

_Supports all OPS241/OPS242/OPS243 radar models with full API coverage_

> **⚠️ DISCLAIMER**: This is an **unofficial**, community-developed library. The
> author is **not affiliated** with OmniPreSense Corp. This library provides a
> Python interface for OmniPreSense radar sensors but is not endorsed or
> supported by the company.

[🚀 Quick Start](#quick-start) • [📚 Examples](#examples) • [🛠️ Troubleshooting](TROUBLESHOOTING.md) • [🤝 Contributing](CONTRIBUTING.md)

</div>

---

## ✨ Features

- 📋 **Complete API Coverage** - All commands from the [official API documentation](https://omnipresense.com/wp-content/uploads/2019/10/AN-010-Q_API_Interface.pdf)
- 🔒 **Type-Safe** - Full typing support with comprehensive enums and data classes
- 📡 **Multiple Sensor Support** - Doppler (-A), FMCW (-B), and combined (-C) sensor types
- 🧵 **Thread-Safe** - Robust serial communication with proper synchronization
- 🔧 **Context Managers** - Automatic resource cleanup with `with` statements
- 📊 **Rich Data Structures** - Structured radar readings with timestamps and metadata
- ⚡ **High Performance** - Efficient data streaming with configurable callbacks
- 🛡️ **Error Handling** - Comprehensive exception hierarchy with detailed messages

## 📡 Supported Models

| Model        | Type     | Features                            | Detection Range | Max Speed |
| ------------ | -------- | ----------------------------------- | --------------- | --------- |
| **OPS241-A** | Doppler  | Motion, Speed, Direction, Magnitude | 20-25m          | 31.1 m/s  |
| **OPS242-A** | Doppler  | Enhanced sensitivity                | 20-25m          | 31.1 m/s  |
| **OPS243-A** | Doppler  | Advanced + Range\*                  | 75-100m         | 31.1 m/s  |
| **OPS241-B** | FMCW     | Range, Magnitude                    | 15-20m          | N/A       |
| **OPS243-C** | Combined | All features                        | 50-60m          | 31.1 m/s  |

\*Range measurement pending in firmware

## 🚀 Quick Start

### Installation

```bash
pip install omnipresense
```

### Basic Usage

```python
from omnipresense import create_radar, Units, OutputMode
import time

# Create radar sensor
radar = create_radar('OPS243-C', '/dev/ttyACM0')

# Use context manager for automatic cleanup
with radar:
    # Configure sensor
    radar.set_units(Units.KILOMETERS_PER_HOUR)
    
    # Enable output modes (required for data transmission)
    radar.enable_output_mode(OutputMode.SPEED, True)
    radar.enable_output_mode(OutputMode.DIRECTION, True)
    radar.enable_output_mode(OutputMode.MAGNITUDE, True)

    # Define callback for radar data
    def on_detection(reading):
        if reading.speed and reading.speed > 1.0:
            direction = reading.direction.value if reading.direction else "?"
            distance = f", Distance: {reading.range_m:.1f}m" if reading.range_m else ""
            print(f"Speed: {reading.speed:.1f} km/h, Direction: {direction}{distance}")

    # Start streaming data
    print("Move something in front of the radar...")
    radar.start_streaming(on_detection)
    time.sleep(10)  # Stream for 10 seconds
```

> **Important**: Always enable appropriate output modes (`OutputMode.SPEED`, `OutputMode.DIRECTION`, `OutputMode.MAGNITUDE_SPEED`) for data transmission. Without these, the radar will not send any data.

## 📋 Requirements

- **Python**: 3.8.1+
- **Dependencies**: `pyserial` >= 3.4

## 📁 Examples

The [`examples/`](examples/) directory contains working scripts for different use cases:

- **[`basic_usage.py`](examples/basic_usage.py)** - Simple km/h speed detection with distance
- **[`basic_usage_raw.py`](examples/basic_usage_raw.py)** - PySerial version showing raw protocol
- **[`simple_doppler.py`](examples/simple_doppler.py)** - Doppler radar with direction detection
- **[`simple_range.py`](examples/simple_range.py)** - FMCW range measurement
- **[`combined_example.py`](examples/combined_example.py)** - OPS243-C combined features
- **[`debug_usage.py`](examples/debug_usage.py)** - Comprehensive debugging tool
- **[`raw_data_test.py`](examples/raw_data_test.py)** - Raw data inspection utility
- **[`baudrate_troubleshooting_example.py`](examples/baudrate_troubleshooting_example.py)** - UART/baudrate configuration and troubleshooting
- **[`cosine_correction_example.py`](examples/cosine_correction_example.py)** - Cosine error correction for angled installations
- **[`water_height_averaging_example.py`](examples/water_height_averaging_example.py)** - Water level monitoring with averaging
- **[`vehicle_speed_averaging_example.py`](examples/vehicle_speed_averaging_example.py)** - Vehicle/traffic speed monitoring

Run any example:

```bash
python examples/basic_usage.py
```

## ⚙️ Key Configuration

### Output Modes (Required)

```python
# Enable data transmission (essential!)
radar.enable_output_mode(OutputMode.SPEED, True)
radar.enable_output_mode(OutputMode.DIRECTION, True)
radar.enable_output_mode(OutputMode.MAGNITUDE_SPEED, True)  # Doppler magnitude

# For OPS243-C (combined sensor), you can also enable range magnitude:
# radar.enable_output_mode(OutputMode.MAGNITUDE_RANGE, True)  # FMCW magnitude
```

### Units and Sensitivity

```python
# Set measurement units
radar.set_units(Units.KILOMETERS_PER_HOUR)  # or METERS_PER_SECOND, MILES_PER_HOUR

# Adjust sensitivity (lower = more sensitive)
radar.set_magnitude_threshold(20)  # Default: 20, Range: 1-200+
```

### Filtering

```python
# Filter readings by speed and range
radar.set_speed_filter(min_speed=1.0, max_speed=50.0)
radar.set_range_filter(min_range=0.5, max_range=25.0)

# Range AND Speed Filter (OPS243-C only)
# Only report speeds when objects are within the range filter boundaries
radar.enable_range_and_speed_filter(True)
# Perfect for traffic monitoring with a specific detection zone
```

### Baudrate Configuration

```python
from omnipresense import create_radar, BaudRate

# Automatic detection (recommended - works in most cases)
radar = create_radar('OPS243-C', '/dev/ttyUSB0')

# Specify exact baudrate for faster connection
radar = create_radar('OPS243-C', '/dev/ttyUSB0', baudrate=19200)

# Use BaudRate enum for type safety
radar = create_radar('OPS243-C', '/dev/ttyUSB0', baudrate=BaudRate.BAUD_19200)

# Disable auto-detection (fastest, but requires correct baudrate)
radar = create_radar('OPS243-C', '/dev/ttyUSB0', baudrate=19200, auto_detect_baudrate=False)
```

**Supported Baudrates**: 9600, 19200 (default), 57600, 115200, 230400

**UART Control Commands**:
```python
# Query current sensor baudrate
baud_rate, response = radar.query_baud_rate()

# Change sensor baudrate (requires reconnection)
radar.set_baud_rate(BaudRate.BAUD_57600)

# Save baudrate to persistent memory
radar.save_baudrate_to_memory()  # Survives power cycles
```

### Cosine Error Correction

Cosine error occurs when radar is not perpendicular to the target's motion. The radar measures radial velocity: `v_radial = v_actual × cos(θ)`, causing underestimation of actual speed/range.

**Hardware-based correction**: The sensor applies correction internally using the `^/+` and `^/-` commands. Corrected values are transparent to your application.

**When to use:**
- Side-mounted traffic monitoring
- Angled overhead installations
- Installation constraints requiring non-perpendicular placement

**Basic usage:**
```python
# Enable correction for 30° angled installation (same angle for both directions)
radar.enable_cosine_correction(30)

# Hardware correction is applied by sensor - readings are pre-corrected
def on_detection(reading):
    print(f"Speed: {reading.speed:.1f} km/h")  # Already corrected by hardware

radar.start_streaming(on_detection)
```

**Correction factors by angle:**
- 15° → 1.035x (3.5% increase)
- 30° → 1.155x (15.5% increase)
- 45° → 1.414x (41.4% increase)
- 60° → 2.000x (100% increase) - **unreliable**

**Important notes:**
- Angles > 45° produce unreliable corrections
- Library validates angles (0-89°) and warns for large corrections
- Correction applied by sensor hardware (transparent to application)
- Both speed and range are corrected by hardware

**Advanced configuration - Separate inbound/outbound angles:**
```python
# For traffic monitoring with lanes at different distances
radar.enable_cosine_correction(
    angle_inbound_degrees=25,   # Approaching traffic
    angle_outbound_degrees=35   # Receding traffic
)

# Disable correction
radar.disable_cosine_correction()

# Query current hardware correction settings
config = radar.get_cosine_correction()
print(f"Enabled: {config.enabled}")
print(f"Inbound angle: {config.angle_inbound_degrees}°")
print(f"Outbound angle: {config.angle_outbound_degrees}°")
```

See `examples/cosine_correction_example.py` for detailed demonstrations including traffic monitoring scenarios.

## 📊 Data Structure

Each radar reading provides:

```python
@dataclass
class RadarReading:
    timestamp: float                    # Unix timestamp
    speed: Optional[float]              # Speed in configured units
    direction: Optional[Direction]      # APPROACHING/RECEDING
    range_m: Optional[float]           # Range in meters
    magnitude: Optional[float]         # Signal strength
    raw_data: Optional[str]            # Original data string
```

## 🛡️ Error Handling

```python
from omnipresense import RadarError, RadarConnectionError

try:
    with create_radar('OPS243-C', '/dev/ttyACM0') as radar:
        radar.set_units(Units.METERS_PER_SECOND)
        # ... use radar

except RadarConnectionError:
    print("Could not connect to radar sensor")
except RadarError as e:
    print(f"Radar error: {e}")
```

## Missing Features

The following features from the OmniPreSense API are not yet implemented in this release:

- **Hibernation Mode (OPS243 devices)** - Low-power hibernation functionality for battery-powered applications
- **Rolling Buffer (OPS243-A)** - Capturing large sample set from very fast events

## 🔧 Quick Troubleshooting

### No Data Received?

1. **Enable output modes**: `radar.enable_output_mode(OutputMode.SPEED, True)`
2. **Create motion**: Wave your hand in front of the sensor
3. **Check distance**: Ensure objects are within 0.5m-25m range
4. **Lower threshold**: `radar.set_magnitude_threshold(10)`

### Permission Denied (Linux)?

```bash
sudo usermod -a -G dialout $USER  # Add user to dialout group
# Then logout and login again
```

### Port Not Found?

- **Linux**: Try `/dev/ttyUSB0`, `/dev/ttyACM0`, `/dev/ttyACM1`
- **macOS**: Try `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`
- **Windows**: Try `COM3`, `COM4`, `COM5`, etc.

### Connection Failed / Wrong Baudrate?

1. **Use auto-detection**: `create_radar('OPS243-C', '/dev/ttyUSB0')` (default)
2. **Try common rates**: 19200 (default), 115200 (USB), 9600 (reliable)
3. **Run diagnostics**: `python examples/baudrate_troubleshooting_example.py`
4. **Check logs**: Enable logging to see detection attempts

```python
import logging
logging.basicConfig(level=logging.INFO)  # Shows connection attempts
```

**Need more help?** See the comprehensive [**Troubleshooting Guide**](TROUBLESHOOTING.md).

## 📚 Documentation & Support

- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Detailed issue resolution
- **[Contributing Guide](CONTRIBUTING.md)** - Development and contribution info
- **[Examples Directory](examples/)** - Working code examples
- **[GitHub Issues](https://github.com/yourusername/OmnipresenseRadar/issues)** - Bug reports and feature requests

## 🤝 Contributing

We welcome contributions! Please see our [**Contributing Guide**](CONTRIBUTING.md) for:

- Development environment setup
- Code quality standards
- Testing guidelines  
- Pull request process

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

This project is an **independent, unofficial** implementation developed by the community. It is **not affiliated with, endorsed by, or supported by OmniPreSense Corp.**

- **Trademark**: "OmniPreSense" is a trademark of OmniPreSense Corp.
- **Hardware**: This library is designed to work with OmniPreSense radar sensors
- **Support**: For hardware issues, contact [OmniPreSense directly](https://omnipresense.com/support/). For library issues, use our GitHub Issues.
- **Warranty**: This software comes with no warranty. Use at your own risk.

---

<div align="center">

**⭐ Star this repo if it helps you build amazing radar applications! ⭐**

_Made with ❤️ for the radar sensing community_

</div>

