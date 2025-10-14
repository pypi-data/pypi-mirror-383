# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-XX

### Added

#### UART Control & Baudrate Management
- **BaudRate enum** with all supported rates (9600, 19200, 57600, 115200, 230400)
- **Automatic baudrate detection** - library now tries multiple baudrates automatically
- **UART control commands**:
  - `query_baud_rate()` - Query sensor's current baudrate (I? command)
  - `set_baud_rate()` - Change sensor baudrate (I1-I5 commands)
  - `get_current_baud_rate()` - Get connection's current baudrate
- **Enhanced create_radar()** with `baudrate` and `auto_detect_baudrate` parameters
- **Persistent baudrate settings**:
  - `save_baudrate_to_memory()` - Save baudrate to flash memory
  - Enhanced `save_config_to_memory()` with optional baudrate saving

#### Blank Reporting & Timeout Management
- **BlankReporting enum** for hardware-based timeout functionality
- **Blank reporting modes**: DISABLED, ZERO_VALUES, BLANK_LINES, SPACES, COMMAS, TIMESTAMPS
- `set_blank_reporting()` and `get_blank_reporting()` methods
- Hardware-native timeout solution using sensor's BZ, BL, BS, BC, BT, BV commands

#### Persistent Memory Management
- **Comprehensive flash memory support**:
  - `save_config_to_memory()` - Save current configuration (A! command)
  - `get_persistent_memory_settings()` - Query settings (A? command)
  - `read_flash_settings()` - Read flash settings (A. command)
  - `reset_flash_settings()` - Reset to factory defaults (AX command)
- All flash operations include required 1-second delays per API specification

#### Speed & Range Averaging (OPS243 Only)
- **AveragingConfig dataclass** for structured averaging configuration
- **Range averaging methods**:
  - `enable_range_averaging()`, `set_range_averaging_period()`, `set_range_averaging_delay()`
  - `configure_range_averaging()` - Convenient setup method
- **Speed averaging methods**:
  - `enable_speed_averaging()`, `set_speed_averaging_period()`, `set_speed_averaging_delay()`
  - `configure_speed_averaging()` - Convenient setup method
- **Moving average support**:
  - `set_moving_average_points()`, `configure_moving_average()`
- `get_averaging_config()` - Get current averaging settings
- Validation for OPS243-only features with clear error messages

#### Cosine Error Correction (Hardware-based)
- **CosineCorrection dataclass** for managing hardware correction configuration
- **Hardware-based correction** using sensor API commands (`^/+n.n`, `^/-n.n`, `^?`)
- **Correction methods**:
  - `enable_cosine_correction(angle_inbound_degrees, angle_outbound_degrees)` - Enable hardware correction with separate angles
  - `disable_cosine_correction()` - Disable hardware correction
  - `get_cosine_correction()` - Query sensor's current hardware correction settings
- **Separate inbound/outbound angles**: Configure different correction angles for approaching and receding traffic
- **Transparent correction**: Sensor applies correction internally - application receives pre-corrected values
- **Validation and warnings**:
  - Angle validation (0-89 degrees)
  - Warnings for angles > 45° (unreliable corrections)
  - Correction factor validation (warns if > 2.0x)
- **Use cases**: Side-mounted traffic monitoring, angled overhead installations, multi-lane traffic with varying distances

#### Peak Speed Averaging
- **Peak speed averaging** (K+/K-) for Doppler sensors
- `enable_peak_speed_averaging(enable)` - Enable/disable peak speed filtering
- Filters multiple speed reports and provides primary (peak) speed of detected object
- Averages three nearest detected speeds around peak signal value

#### Range AND Speed Filter (OPS243-C Only)
- **Combined range and speed filtering** (OY/Oy commands)
- `enable_range_and_speed_filter(enable)` - Enable/disable combined filtering
- Only reports speeds when objects are within configured range filter boundaries
- Perfect for traffic monitoring with specific detection zones
- Requires both Doppler and FMCW capabilities (OPS243-C)

#### New Examples
- **`baudrate_troubleshooting_example.py`** - Comprehensive UART troubleshooting and configuration
- **`cosine_correction_example.py`** - Cosine error correction demonstrations with traffic monitoring scenarios
- **`water_height_averaging_example.py`** - Water level monitoring with range averaging
- **`vehicle_speed_averaging_example.py`** - Vehicle/traffic speed monitoring with averaging
- **`blank_reporting_example.py`** - Blank reporting modes demonstration
- **`persistent_memory_example.py`** - Flash memory configuration management

### Changed

#### Breaking Changes

##### Software Timeout Removal
- **REMOVED: Software timeout mechanism** - The previous `movement_timeout` parameter and software-based zero-value generation has been completely removed
- **MIGRATION REQUIRED**: Replace software timeout with hardware blank reporting:
  ```python
  # OLD (v0.1.0) - NO LONGER WORKS:
  # radar = create_radar('OPS243-C', '/dev/ttyUSB0', movement_timeout=5.0)

  # NEW (v0.2.0) - Use blank reporting instead:
  radar = create_radar('OPS243-C', '/dev/ttyUSB0')
  radar.set_blank_reporting(BlankReporting.ZERO_VALUES)
  ```

##### Cosine Error Correction - Hardware Migration
- **BREAKING**: Cosine correction is now hardware-based, not software-based
- **API signature changed**:
  ```python
  # OLD (early v0.2.0 development):
  # radar.enable_cosine_correction(angle_degrees=30, apply_to_speed=True, apply_to_range=True)

  # NEW (v0.2.0 release):
  radar.enable_cosine_correction(angle_inbound_degrees=30, angle_outbound_degrees=30)
  # Or simply:
  radar.enable_cosine_correction(30)  # Uses same angle for both directions
  ```
- **RadarReading fields removed**:
  - `raw_speed` - Hardware provides no access to uncorrected speed
  - `raw_range_m` - Hardware provides no access to uncorrected range
  - `cosine_corrected` - Correction is always transparent (check config instead)
- **Behavior changes**:
  - Correction applied by sensor hardware, not library software
  - Both speed and range are always corrected (no selective application)
  - Separate angles can be configured for inbound/outbound traffic
- **CosineCorrection dataclass changes**:
  - Removed: `apply_to_speed`, `apply_to_range`, `angle_degrees`
  - Added: `angle_inbound_degrees`, `angle_outbound_degrees`

##### OutputMode Refactoring
- **OutputMode enum refactored** - Fixed to comply with OPS radar API conventions:
  - **BREAKING**: `OutputMode.MAGNITUDE` renamed to `OutputMode.MAGNITUDE_SPEED`
  - **NEW**: `OutputMode.MAGNITUDE_RANGE` added for FMCW range magnitude (OPS243-C only)
  - **INTERNAL CHANGE**: Enum values now store mode letter only (e.g., "M" instead of "OM")
  - **API Convention**: First letter (O/o) = data type, Second letter (uppercase/lowercase) = enable/disable
  - **Migration**: Replace `OutputMode.MAGNITUDE` with `OutputMode.MAGNITUDE_SPEED` in all code

##### Other Breaking Changes
- **Default baudrate behavior**: Now uses 19200 (radar default) instead of 115200
- **OPSRadarSensor.__init__()**: Added `auto_detect_baudrate` parameter, removed `movement_timeout`
- **create_radar()**: Enhanced with baudrate management parameters, removed timeout functionality

#### Enhanced Connection Process
- **Intelligent connection logic**: Tries user-specified baudrate first, then auto-detection
- **Connection testing**: Added `_test_connection()` for reliable baudrate detection
- **Better error handling**: Detailed error messages for connection failures
- **Comprehensive logging**: Debug information for connection attempts

#### Improved Examples
- **basic_usage.py**: Added baudrate configuration examples and connection info
- All examples now demonstrate latest features and best practices

### Removed

#### Software Timeout Mechanism
- **BREAKING**: Removed `movement_timeout` parameter from all radar classes
- **BREAKING**: Removed software-based zero-value generation when no movement detected
- **BREAKING**: Removed internal timeout tracking and synthetic reading generation
- **Reason**: Replaced with superior hardware-native blank reporting functionality
- **Migration Path**: Use `radar.set_blank_reporting(BlankReporting.ZERO_VALUES)` for equivalent functionality

### Documentation

#### Enhanced README
- **New baudrate configuration section** with examples and best practices
- **Updated examples list** including new specialized examples
- **Enhanced troubleshooting section** with baudrate-specific guidance
- **UART control documentation** with command examples

#### API Documentation
- Enhanced docstrings for all new methods
- Clear parameter descriptions and usage examples
- Error handling documentation
- OPS243-specific feature callouts

### Technical Improvements

#### Code Quality
- **Type safety**: All new enums and methods are fully typed
- **Error handling**: Comprehensive exception hierarchy with specific error types
- **Validation**: Input validation for all new parameters and commands
- **Logging**: Structured logging throughout for debugging

#### Backward Compatibility
- All existing code continues to work unchanged
- New parameters have sensible defaults
- Optional features don't affect basic usage

## [0.1.0] - 2025-01-XX

### Added
- Initial release with basic radar sensor support
- Support for OPS241-A, OPS242-A, OPS243-A, OPS241-B, OPS243-C models
- Basic command interface and data streaming
- Context manager support
- Type-safe enums and data classes
- Error handling and validation
- Basic examples and documentation

---

**Legend:**
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements