"""
OmniPreSense Radar Sensor Interface

A comprehensive, type-safe Python interface for OmniPreSense radar sensors.
Supports all OPS241/OPS242/OPS243 radar models with full API coverage. Based on
https://omnipresense.com/wp-content/uploads/2019/10/AN-010-Q_API_Interface.pdf

Features:
- Type-safe operations with comprehensive enums and data classes
- Support for Doppler (-A), FMCW (-B), and combined (-C) sensor types
- Complete API implementation with all commands
- Thread-safe serial communication
- Context manager support for automatic cleanup
- Comprehensive error handling and validation
- Rich documentation with examples

Example usage:
    ```python
    from new_radar import create_radar, Units, SamplingRate

    # Create radar sensor
    radar = create_radar('OPS243-A', '/dev/ttyACM0')

    # Use context manager for automatic cleanup
    with radar:
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)

        def on_data(reading):
            print(f"Speed: {reading.speed} m/s, Direction: {reading.direction}")

        radar.start_streaming(on_data)
        time.sleep(10)
    ```

Author: Oskar Graeb graeb.oskar@gmail.com
License: MIT
"""

import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Callable, Dict, List, Optional, Type

import serial

# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class RadarError(Exception):
    """Base exception for all radar-related errors."""


class RadarConnectionError(RadarError):
    """Raised when connection to radar fails."""


class RadarCommandError(RadarError):
    """Raised when a radar command fails or returns an error."""


class RadarValidationError(RadarError):
    """Raised when parameter validation fails."""


class RadarTimeoutError(RadarError):
    """Raised when a radar operation times out."""


# =============================================================================
# Enums and Constants
# =============================================================================


class SensorType(Enum):
    """Radar sensor types with their capabilities."""

    DOPPLER_A = "OPS241-A"  # Motion, Speed, Direction
    DOPPLER_A2 = "OPS242-A"  # Enhanced Doppler
    DOPPLER_A3 = "OPS243-A"  # Advanced Doppler with range
    FMCW_B = "OPS241-B"  # Range only
    COMBINED_C = "OPS243-C"  # FMCW + Doppler


class Units(Enum):
    """Output units for speed and range measurements."""

    # Doppler units (speed)
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    FEET_PER_SECOND = "ft/s"
    MILES_PER_HOUR = "mph"
    CENTIMETERS_PER_SECOND = "cm/s"

    # FMCW units (range)
    METERS = "m"
    CENTIMETERS = "cm"
    FEET = "ft"


class SamplingRate(IntEnum):
    """Available sampling rates in Hz."""

    HZ_1000 = 1000  # Max speed: 3.1 m/s, Resolution: 0.006 m/s
    HZ_5000 = 5000  # Max speed: 15.5 m/s, Resolution: 0.030 m/s
    HZ_10000 = 10000  # Max speed: 31.1 m/s, Resolution: 0.061 m/s
    HZ_20000 = 20000  # Max speed: 62.2 m/s, Resolution: 0.121 m/s
    HZ_50000 = 50000  # Max speed: 155.4 m/s, Resolution: 0.304 m/s
    HZ_100000 = 100000  # Max speed: 310.8 m/s, Resolution: 0.608 m/s


class Direction(Enum):
    """Object movement direction."""

    APPROACHING = "+"
    RECEDING = "-"
    UNKNOWN = "?"


class PowerMode(Enum):
    """Sensor power modes."""

    ACTIVE = "PA"  # Full power, continuous operation
    IDLE = "PI"  # Low power, periodic operation
    SLEEP = "PP"  # Minimal power, wake on command


class OutputMode(Enum):
    """
    Data output modes.

    Per OPS radar API conventions:
    - First letter: Uppercase = Speed/Doppler (O), Lowercase = Range/FMCW (o)
    - Second letter: Uppercase = Enable, Lowercase = Disable

    Examples:
    - OM = Enable speed magnitude, Om = Disable speed magnitude
    - oM = Enable range magnitude, om = Disable range magnitude

    This enum stores the mode identifier (second letter). The enable_output_mode()
    method constructs the full command based on enable/disable parameter.
    """

    SPEED = "S"  # Speed data (OS=enable, Os=disable)
    DIRECTION = "D"  # Direction data (OD=enable, Od=disable)
    JSON = "J"  # JSON output (OJ=toggle)
    MAGNITUDE_SPEED = "M"  # Speed magnitude (OM=enable, Om=disable)
    MAGNITUDE_RANGE = "m"  # Range magnitude (oM=enable, om=disable)
    RAW = "R"  # Raw ADC data (OR=enable, Or=disable)
    FFT = "F"  # Post-FFT data (OF=enable, Of=disable)
    TIMESTAMP = "T"  # Timestamps (OT=toggle)
    UNITS = "U"  # Units in output (OU=enable, Ou=disable)


class BlankReporting(Enum):
    """Blank data reporting modes when measured data doesn't meet filtering criteria."""

    DISABLED = "BV"  # Turn off blank reporting (default)
    ZERO_VALUES = "BZ"  # Report zero values (recommended for timeout behavior)
    BLANK_LINES = "BL"  # Report blank lines
    SPACES = "BS"  # Report spaces
    COMMAS = "BC"  # Report commas
    TIMESTAMPS = "BT"  # Report timestamps


class BaudRate(IntEnum):
    """UART baud rates supported by OmniPreSense radar sensors.

    Maps to I1-I5 commands as per the API documentation.
    Default radar baud rate is 19200 (I2).
    """

    BAUD_9600 = 9600  # I1 command
    BAUD_19200 = 19200  # I2 command (default)
    BAUD_57600 = 57600  # I3 command
    BAUD_115200 = 115200  # I4 command
    BAUD_230400 = 230400  # I5 command


# UART control constants
DEFAULT_RADAR_BAUDRATE = 19200  # Default baud rate per API documentation
BAUDRATE_COMMAND_MAP = {
    BaudRate.BAUD_9600: "I1",
    BaudRate.BAUD_19200: "I2",
    BaudRate.BAUD_57600: "I3",
    BaudRate.BAUD_115200: "I4",
    BaudRate.BAUD_230400: "I5",
}

# Auto-detection sequence (try most common first)
BAUDRATE_DETECTION_ORDER = [
    BaudRate.BAUD_19200,  # Default per API
    BaudRate.BAUD_115200,  # Common for USB connections
    BaudRate.BAUD_9600,  # Slowest but most reliable
    BaudRate.BAUD_57600,  # Medium speed
    BaudRate.BAUD_230400,  # Fastest
]


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class RadarReading:
    """
    Represents a single radar measurement.

    Note: If hardware cosine correction is enabled, speed and range_m values
    are already corrected by the sensor.
    """

    timestamp: float = field(default_factory=time.time)
    speed: Optional[float] = None  # Speed in configured units
    direction: Optional[Direction] = None
    range_m: Optional[float] = None  # Range in meters
    magnitude: Optional[float] = None
    raw_data: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"t={self.timestamp:.3f}"]
        if self.speed is not None:
            parts.append(f"speed={self.speed}")
        if self.direction:
            parts.append(f"dir={self.direction.value}")
        if self.range_m is not None:
            parts.append(f"range={self.range_m}m")
        if self.magnitude is not None:
            parts.append(f"mag={self.magnitude}")
        return f"RadarReading({', '.join(parts)})"


@dataclass
class SensorInfo:
    """Radar sensor information and capabilities."""

    model: str
    firmware_version: str
    board_id: str
    frequency: float
    has_doppler: bool
    has_fmcw: bool
    max_range: float
    detection_range: str


@dataclass
class AveragingConfig:
    """Configuration for speed and range averaging on OPS243 devices."""

    range_averaging_enabled: bool = False
    range_averaging_period: int = 5  # seconds
    range_averaging_delay: int = 300  # seconds between averaging cycles

    speed_averaging_enabled: bool = False
    speed_averaging_period: int = 5  # seconds (0 = moving average mode)
    speed_averaging_delay: int = 300  # seconds between averaging cycles
    moving_average_points: int = 5  # number of points for moving average (max 20)


@dataclass
class CosineCorrection:
    """
    Cosine error correction configuration for angled radar installations.

    Cosine error occurs when the radar sensor is not perpendicular to the target's
    direction of motion. The radar measures radial velocity (v_radial = v_actual × cos(θ)),
    causing underestimation of actual speed/range.

    Use this correction when:
    - Radar is mounted at a known angle to traffic flow
    - Side-mounted installations (not perpendicular)
    - Overhead mounting at an angle

    Formula: corrected_value = measured_value / cos(angle)

    Example: Target at 30° angle traveling 60 mph will read as 52 mph.
             Correction: 52 / cos(30°) = 60 mph

    Note: Hardware correction is applied by the sensor. Separate angles can be
    configured for inbound and outbound traffic to account for lane positioning.
    """

    enabled: bool = False
    angle_inbound_degrees: float = 0.0  # Angle for approaching objects (0-89 degrees)
    angle_outbound_degrees: float = 0.0  # Angle for receding objects (0-89 degrees)


@dataclass
class RadarConfig:
    """Complete radar sensor configuration."""

    units: Units = Units.METERS_PER_SECOND
    sampling_rate: SamplingRate = SamplingRate.HZ_10000
    data_precision: int = 2
    magnitude_threshold: int = 20
    speed_filter_min: Optional[float] = None
    speed_filter_max: Optional[float] = None
    range_filter_min: Optional[float] = None
    range_filter_max: Optional[float] = None
    direction_filter: Optional[Direction] = None
    range_and_speed_filter: bool = False
    power_mode: PowerMode = PowerMode.ACTIVE
    output_modes: List[OutputMode] = field(default_factory=lambda: [OutputMode.SPEED])
    buffer_size: int = 1024
    duty_cycle_short: int = 0
    duty_cycle_long: int = 0
    blank_reporting: BlankReporting = BlankReporting.DISABLED
    averaging: AveragingConfig = field(default_factory=AveragingConfig)
    cosine_correction: CosineCorrection = field(default_factory=CosineCorrection)


# =============================================================================
# Base Radar Sensor Class
# =============================================================================


class OPSRadarSensor(ABC):
    """
    Abstract base class for OmniPreSense radar sensors.

    Provides common functionality for serial communication, command handling,
    and data processing that's shared across all sensor types.
    """

    # Command mappings
    SAMPLING_RATE_COMMANDS = {
        SamplingRate.HZ_1000: "SI",
        SamplingRate.HZ_5000: "SV",
        SamplingRate.HZ_10000: "SX",
        SamplingRate.HZ_20000: "S2",
        SamplingRate.HZ_50000: "SL",
        SamplingRate.HZ_100000: "SC",
    }

    POWER_MODE_COMMANDS = {
        PowerMode.ACTIVE: "PA",
        PowerMode.IDLE: "PI",
        PowerMode.SLEEP: "PP",
    }

    # Duty cycle command mappings
    DUTY_CYCLE_COMMANDS = {
        0: "W0",
        1: "WI",
        5: "WV",
        10: "WX",
        20: "W2",
        50: "WL",
        100: "WC",
        200: "W2",
        300: "W3",
        400: "W4",
        500: "WD",
        600: "WM",
        700: "W7",
        800: "W8",
        900: "W9",
        1000: "WT",
    }

    def __init__(
        self,
        port: str,
        baudrate: Optional[int] = None,
        timeout: float = 0.1,
        auto_detect_baudrate: bool = True,
    ):
        """
        Initialize radar sensor.

        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Serial communication speed. If None, uses radar default (19200)
                     or auto-detection if enabled
            timeout: Serial read timeout in seconds (default: 0.1)
            auto_detect_baudrate: Enable automatic baudrate detection if initial connection fails
        """
        self.port_name = port
        self.baudrate = baudrate if baudrate is not None else DEFAULT_RADAR_BAUDRATE
        self.timeout = timeout
        self.auto_detect_baudrate = auto_detect_baudrate
        self._user_specified_baudrate = baudrate  # Track what user specified
        self.ser: Optional[serial.Serial] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callback: Optional[Callable[[RadarReading], None]] = None
        self._config = RadarConfig()
        self._sensor_info: Optional[SensorInfo] = None
        self._lock = threading.RLock()

        logger.info(f"Initialized {self.__class__.__name__} on port {port}")

    # Context manager support
    def __enter__(self) -> "OPSRadarSensor":
        """Context manager entry - opens connection."""
        if not self.open():
            raise RadarConnectionError(f"Failed to open connection to {self.port_name}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - closes connection."""
        self.close()

    def open(self) -> bool:
        """
        Open serial connection to radar sensor with automatic baudrate detection.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            RadarConnectionError: If connection fails after all attempts
        """
        # Determine baudrates to try
        baudrates_to_try = []

        if self._user_specified_baudrate is not None:
            # User specified a baudrate, try it first
            baudrates_to_try.append(self._user_specified_baudrate)
            if self.auto_detect_baudrate:
                # Add auto-detection sequence, excluding the user-specified one
                for rate in BAUDRATE_DETECTION_ORDER:
                    if rate.value != self._user_specified_baudrate:
                        baudrates_to_try.append(rate.value)
        elif self.auto_detect_baudrate:
            # No user preference, use full auto-detection sequence
            baudrates_to_try = [rate.value for rate in BAUDRATE_DETECTION_ORDER]
        else:
            # No auto-detection, just use current baudrate
            baudrates_to_try = [self.baudrate]

        last_error = None

        for try_baudrate in baudrates_to_try:
            logger.debug(f"Attempting connection at {try_baudrate} baud")

            try:
                # Close any existing connection
                if self.ser and self.ser.is_open:
                    self.ser.close()

                # Attempt connection at this baudrate
                self.ser = serial.Serial(
                    port=self.port_name,
                    baudrate=try_baudrate,
                    timeout=self.timeout,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                )

                # Test the connection by trying to get sensor info
                time.sleep(0.1)  # Give sensor time to respond

                # Try a simple command to test connectivity
                test_success = self._test_connection()

                if test_success:
                    # Update our internal baudrate to the successful one
                    self.baudrate = try_baudrate
                    logger.info(
                        f"Successfully connected to radar at {try_baudrate} baud on {self.port_name}"
                    )

                    # Get sensor info on successful connection
                    try:
                        self._sensor_info = self._get_sensor_info()
                    except Exception as e:
                        logger.warning(f"Connected but failed to get sensor info: {e}")
                        # Continue anyway, connection is working

                    return True
                else:
                    # Connection test failed, try next baudrate
                    if self.ser:
                        self.ser.close()
                        self.ser = None
                    continue

            except Exception as e:
                last_error = e
                logger.debug(f"Failed to connect at {try_baudrate} baud: {e}")
                if self.ser:
                    try:
                        self.ser.close()
                    except:
                        pass
                    self.ser = None
                continue

        # All attempts failed
        error_msg = f"Failed to connect to radar on {self.port_name}"
        if len(baudrates_to_try) > 1:
            error_msg += f" (tried baudrates: {baudrates_to_try})"
        if last_error:
            error_msg += f". Last error: {last_error}"

        logger.error(error_msg)
        raise RadarConnectionError(error_msg)

    def _test_connection(self) -> bool:
        """
        Test if the current serial connection is working.

        Returns:
            bool: True if connection appears to be working
        """
        if not self.ser or not self.ser.is_open:
            return False

        try:
            # Clear any pending data
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            # Send a simple query command and wait for response
            self.ser.write(b"?\n")
            self.ser.flush()

            # Give sensor time to respond
            time.sleep(0.2)

            # Try to read some data
            if self.ser.in_waiting > 0:
                response = self.ser.read(self.ser.in_waiting).decode(
                    "utf-8", errors="ignore"
                )
                logger.debug(f"Connection test response: {response.strip()}")
                # Any response indicates the connection is working
                return len(response.strip()) > 0
            else:
                # No response might mean wrong baudrate or sensor issue
                return False

        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False

    def close(self) -> None:
        """Close serial connection and stop reader thread."""
        self.stop_streaming()

        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                logger.info("Closed radar serial connection")
            except Exception as e:
                logger.error(f"Error closing radar serial connection: {e}")
        self.ser = None

    def is_connected(self) -> bool:
        """Check if radar sensor is connected."""
        return self.ser is not None and self.ser.is_open

    def send_command(
        self, command: str, expect_response: bool = False, timeout: float = 1.0
    ) -> Optional[str]:
        """
        Send command to radar sensor.

        Args:
            command: Command string to send
            expect_response: Whether to wait for and return response
            timeout: Response timeout in seconds

        Returns:
            Optional[str]: Response if expect_response=True, None otherwise

        Raises:
            RadarCommandError: If command fails or times out
        """
        if not self.is_connected():
            raise RadarCommandError("Radar not connected")

        with self._lock:
            try:
                # Add newline if not present
                if not command.endswith("\n"):
                    command += "\n"

                if self.ser is not None:
                    self.ser.write(command.encode("ascii"))
                    self.ser.flush()
                else:
                    raise RadarCommandError("Serial connection not available")
                logger.debug(f"Sent radar command: {command.strip()}")

                if expect_response:
                    # Wait for response
                    if self.ser is not None:
                        response = (
                            self.ser.readline().decode("ascii", errors="ignore").strip()
                        )
                    else:
                        raise RadarCommandError("Serial connection not available")
                    if response:
                        logger.debug(f"Received response: {response}")
                        return response
                    else:
                        raise RadarTimeoutError(
                            f"No response to command: {command.strip()}"
                        )

                # Longer delay for commands with numeric parameters that require
                # carriage return to complete (per API documentation)
                cmd_stripped = command.strip()
                if any(cmd_stripped.startswith(prefix) for prefix in ['r>', 'r<', 'R>', 'R<', 'M>', 'm>', 'yp', 'yd', 'Yp', 'Yd', 'Ym']):
                    time.sleep(0.15)  # Extra time for sensor to process numeric filters
                else:
                    time.sleep(0.05)  # Standard delay for other commands
                return None

            except serial.SerialException as e:
                logger.error(f"Serial error sending command '{command.strip()}': {e}")
                raise RadarCommandError(f"Serial communication error: {e}") from e
            except Exception as e:
                logger.error(f"Error sending command '{command.strip()}': {e}")
                raise RadarCommandError(f"Command failed: {e}") from e

    # =============================================================================
    # Module Information Commands
    # =============================================================================

    def get_sensor_info(self) -> SensorInfo:
        """Get comprehensive sensor information."""
        if self._sensor_info is None:
            self._sensor_info = self._get_sensor_info()
        return self._sensor_info

    def _get_sensor_info(self) -> SensorInfo:
        """Internal method to query sensor information."""
        try:
            # Get basic info
            response = self.send_command("??", expect_response=True) or "Unknown"

            # Parse the JSON response if available
            version = "Unknown"
            board_id = "Unknown"
            freq_val = 0.0

            if response and response != "Unknown":
                try:
                    # Handle multiple JSON objects in response
                    lines = response.strip().split("\n")
                    for line in lines:
                        if line.strip().startswith("{"):
                            data = json.loads(line.strip())
                            if "Version" in data:
                                version = data["Version"]
                            elif "rev" in data:
                                board_id = data["rev"]
                            elif "Product" in data and "OPS243-C" in data["Product"]:
                                freq_val = 24.125e9  # 24.125 GHz for OPS243-C
                except (json.JSONDecodeError, ValueError) as e:
                    logger.debug(f"JSON parsing error: {e}")
                    # Fallback to simple parsing
                    version = response[:50] if len(response) > 50 else response

            # Try to get board ID separately if not found
            if board_id == "Unknown":
                board_id = self.send_command("?P", expect_response=True) or "Unknown"

            # Try to get frequency separately if not found
            if freq_val == 0.0:
                frequency = self.send_command("?F", expect_response=True) or "0"
                try:
                    freq_val = float(frequency.split()[-1]) if frequency != "0" else 0.0
                except (ValueError, IndexError):
                    freq_val = 0.0

            # Determine sensor capabilities based on model
            model = self.__class__.__name__
            has_doppler = "Doppler" in model or "Combined" in model
            has_fmcw = "FMCW" in model or "Combined" in model

            # For OPS243C, it has both capabilities
            if "OPS243C" in model:
                has_doppler = True
                has_fmcw = True

            # Set detection ranges based on sensor type
            if "OPS241" in model:
                max_range = 25.0
                detection_range = "20-25m"
            elif "OPS242" in model:
                max_range = 25.0
                detection_range = "20-25m"
            elif "OPS243" in model and has_doppler and not has_fmcw:
                max_range = 100.0
                detection_range = "75-100m"
            elif "OPS241" in model and has_fmcw:
                max_range = 20.0
                detection_range = "15-20m"
            elif "OPS243" in model and has_fmcw:
                max_range = 60.0
                detection_range = "50-60m"
            else:
                max_range = 25.0
                detection_range = "Unknown"

            return SensorInfo(
                model=model,
                firmware_version=version,
                board_id=board_id,
                frequency=freq_val,
                has_doppler=has_doppler,
                has_fmcw=has_fmcw,
                max_range=max_range,
                detection_range=detection_range,
            )

        except Exception as e:
            logger.warning(f"Could not get complete sensor info: {e}")
            return SensorInfo(
                model=self.__class__.__name__,
                firmware_version="Unknown",
                board_id="Unknown",
                frequency=0.0,
                has_doppler="Doppler" in self.__class__.__name__,
                has_fmcw="FMCW" in self.__class__.__name__,
                max_range=25.0,
                detection_range="Unknown",
            )

    def get_firmware_version(self) -> str:
        """Get firmware version string."""
        return self.send_command("??", expect_response=True) or "Unknown"

    def get_board_id(self) -> str:
        """Get board ID."""
        return self.send_command("?P", expect_response=True) or "Unknown"

    def get_frequency(self) -> float:
        """Get operating frequency in Hz."""
        response = self.send_command("?F", expect_response=True)
        try:
            return float(response.split()[-1]) if response else 0.0
        except (ValueError, IndexError):
            return 0.0

    # =============================================================================
    # Configuration Commands
    # =============================================================================

    def set_units(self, units: Units) -> None:
        """
        Set output units for measurements.

        Args:
            units: Units enum value for speed or range

        Raises:
            RadarValidationError: If units not supported by sensor type
        """
        self._validate_units(units)

        # Map units to commands - different for Doppler vs FMCW
        doppler_commands = {
            Units.METERS_PER_SECOND: "UM",
            Units.KILOMETERS_PER_HOUR: "UK",
            Units.FEET_PER_SECOND: "UF",
            Units.MILES_PER_HOUR: "US",
            Units.CENTIMETERS_PER_SECOND: "UC",
        }

        fmcw_commands = {Units.METERS: "uM", Units.CENTIMETERS: "uC", Units.FEET: "uF"}

        if units in doppler_commands and self.get_sensor_info().has_doppler:
            self.send_command(doppler_commands[units])
        elif units in fmcw_commands and self.get_sensor_info().has_fmcw:
            self.send_command(fmcw_commands[units])
        else:
            raise RadarValidationError(f"Units {units} not supported by this sensor")

        self._config.units = units
        logger.info(f"Set units to {units.value}")

    def set_sampling_rate(self, rate: SamplingRate) -> None:
        """
        Set sampling rate.

        Args:
            rate: SamplingRate enum value
        """
        if not self.get_sensor_info().has_doppler:
            raise RadarValidationError("Sampling rate only applies to Doppler sensors")

        command = self.SAMPLING_RATE_COMMANDS[rate]
        self.send_command(command)
        self._config.sampling_rate = rate
        logger.info(f"Set sampling rate to {rate.value} Hz")

    def set_data_precision(self, precision: int) -> None:
        """
        Set data precision (decimal places).

        Args:
            precision: Number of decimal places (0-9)
        """
        if not 0 <= precision <= 9:
            raise RadarValidationError("Precision must be 0-9")

        self.send_command(f"F{precision}")
        self._config.data_precision = precision
        logger.info(f"Set data precision to {precision} decimal places")

    def set_magnitude_threshold(self, threshold: int, doppler: bool = True) -> None:
        """
        Set magnitude threshold for detection.

        Args:
            threshold: Magnitude threshold value
            doppler: True for Doppler threshold, False for FMCW
        """
        if threshold < 0:
            raise RadarValidationError("Threshold must be non-negative")

        if doppler:
            self.send_command(f"M>{threshold}")
        else:
            self.send_command(f"m>{threshold}")

        self._config.magnitude_threshold = threshold
        logger.info(f"Set magnitude threshold to {threshold}")

    def set_power_mode(self, mode: PowerMode) -> None:
        """
        Set sensor power mode.

        Args:
            mode: PowerMode enum value
        """
        command = self.POWER_MODE_COMMANDS[mode]
        self.send_command(command)
        self._config.power_mode = mode
        logger.info(f"Set power mode to {mode.value}")

    def set_buffer_size(self, size: int) -> None:
        """
        Set sampling buffer size.

        Args:
            size: Buffer size (valid values depend on sensor)
        """
        if size <= 0:
            raise RadarValidationError("Buffer size must be positive")

        # Map common sizes to commands
        size_commands = {
            64: "S<",
            128: "S{",
            256: "S}",
            512: "S>",
            1024: "S>",
            2048: "S]",
        }

        # Find closest valid size
        valid_sizes = list(size_commands.keys())
        closest_size = min(valid_sizes, key=lambda x: abs(x - size))

        if abs(closest_size - size) > size * 0.1:  # 10% tolerance
            logger.warning(f"Requested size {size} not available, using {closest_size}")

        self.send_command(size_commands[closest_size])
        self._config.buffer_size = closest_size
        logger.info(f"Set buffer size to {closest_size}")

    def set_duty_cycle(self, short_ms: int, long_ms: int = 0) -> None:
        """
        Set duty cycle timing.

        Args:
            short_ms: Short duty cycle delay in milliseconds
            long_ms: Long duty cycle delay in milliseconds (optional)
        """
        # Find closest valid short duty cycle value
        valid_values = list(self.DUTY_CYCLE_COMMANDS.keys())
        closest_short = min(valid_values, key=lambda x: abs(x - short_ms))

        if closest_short in self.DUTY_CYCLE_COMMANDS:
            self.send_command(self.DUTY_CYCLE_COMMANDS[closest_short])
            self._config.duty_cycle_short = closest_short
            logger.info(f"Set short duty cycle to {closest_short}ms")

        if long_ms > 0:
            # Long duty cycle uses different command format
            self.send_command(f"Z={long_ms}")
            self._config.duty_cycle_long = long_ms
            logger.info(f"Set long duty cycle to {long_ms}ms")

    def set_blank_reporting(self, mode: BlankReporting) -> None:
        """
        Set blank data reporting mode for when measured data doesn't meet filtering criteria.

        Args:
            mode: BlankReporting enum value
                  - DISABLED: Turn off blank reporting (default)
                  - ZERO_VALUES: Report zero values (recommended for timeout behavior)
                  - BLANK_LINES: Report blank lines
                  - SPACES: Report spaces
                  - COMMAS: Report commas
                  - TIMESTAMPS: Report timestamps
        """
        self.send_command(mode.value)
        self._config.blank_reporting = mode

        mode_descriptions = {
            BlankReporting.DISABLED: "disabled",
            BlankReporting.ZERO_VALUES: "zero values",
            BlankReporting.BLANK_LINES: "blank lines",
            BlankReporting.SPACES: "spaces",
            BlankReporting.COMMAS: "commas",
            BlankReporting.TIMESTAMPS: "timestamps",
        }

        logger.info(f"Set blank reporting to {mode_descriptions[mode]}")

    def get_blank_reporting(self) -> BlankReporting:
        """
        Get current blank data reporting mode.

        Returns:
            Current BlankReporting enum value
        """
        response = self.send_command("B?", expect_response=True)
        if not response:
            return BlankReporting.DISABLED

        # Map response back to enum
        response_map = {
            "BV": BlankReporting.DISABLED,
            "BZ": BlankReporting.ZERO_VALUES,
            "BL": BlankReporting.BLANK_LINES,
            "BS": BlankReporting.SPACES,
            "BC": BlankReporting.COMMAS,
            "BT": BlankReporting.TIMESTAMPS,
        }

        # Extract command from response (might include additional text)
        for cmd, mode in response_map.items():
            if cmd in response:
                return mode

        return BlankReporting.DISABLED

    # =============================================================================
    # UART Control Commands
    # =============================================================================

    def query_baud_rate(self) -> tuple[int, str]:
        """
        Query current baud rate and oversampling setting using I? command.

        Returns:
            Tuple of (baud_rate, raw_response)

        Raises:
            RadarCommandError: If query fails
        """
        response = self.send_command("I?", expect_response=True, timeout=2.0)
        if not response:
            raise RadarCommandError("No response to baud rate query")

        logger.debug(f"Baud rate query response: {response}")

        # Try to parse numeric baud rate from response
        # Response format varies, could be just the number or include text
        import re

        numbers = re.findall(r"\d+", response)
        if numbers:
            try:
                baud_rate = int(numbers[0])
                return baud_rate, response.strip()
            except ValueError:
                pass

        raise RadarCommandError(f"Could not parse baud rate from response: {response}")

    def set_baud_rate(self, baudrate: BaudRate) -> bool:
        """
        Set new baud rate using I1-I5 commands.

        Args:
            baudrate: BaudRate enum value

        Returns:
            bool: True if command sent successfully

        Raises:
            RadarValidationError: If baud rate not supported
            RadarCommandError: If command fails

        Note:
            After changing baud rate, you must reconnect with the new baud rate.
            The connection will be disrupted when the sensor switches baud rates.
        """
        if baudrate not in BAUDRATE_COMMAND_MAP:
            raise RadarValidationError(f"Unsupported baud rate: {baudrate}")

        command = BAUDRATE_COMMAND_MAP[baudrate]

        logger.info(f"Setting baud rate to {baudrate.value} using command {command}")

        try:
            # Send the command, but don't expect a response since baud rate will change
            self.send_command(command, expect_response=False)

            # Update our internal state
            self.baudrate = baudrate.value

            logger.warning(
                f"Baud rate changed to {baudrate.value}. You must reconnect."
            )
            return True

        except Exception as e:
            logger.error(f"Failed to set baud rate to {baudrate.value}: {e}")
            raise RadarCommandError(f"Failed to set baud rate: {e}") from e

    def get_current_baud_rate(self) -> int:
        """
        Get the baud rate this connection is currently using.

        Returns:
            int: Current connection baud rate

        Note:
            This returns the baud rate used by the Python serial connection,
            not necessarily the sensor's current setting. Use query_baud_rate()
            to check the sensor's actual baud rate setting.
        """
        return self.baudrate

    # =============================================================================
    # Averaging Commands (OPS243 Only)
    # =============================================================================

    def _validate_ops243_only(self) -> None:
        """Validate that the sensor supports OPS243-only features."""
        sensor_info = self.get_sensor_info()
        if "OPS243" not in sensor_info.model:
            raise RadarValidationError(
                "Averaging features are only supported on OPS243 devices"
            )

    def enable_range_averaging(self, enable: bool = True) -> None:
        """
        Enable or disable range averaging (OPS243 only).

        Args:
            enable: True to enable range averaging, False to disable

        Raises:
            RadarValidationError: If sensor is not OPS243
        """
        self._validate_ops243_only()

        command = "y+" if enable else "y-"
        self.send_command(command)
        self._config.averaging.range_averaging_enabled = enable

        status = "enabled" if enable else "disabled"
        logger.info(f"Range averaging {status}")

    def set_range_averaging_period(self, seconds: int) -> None:
        """
        Set range averaging time period (OPS243 only).

        Args:
            seconds: Time period in seconds to average over (default: 5)

        Raises:
            RadarValidationError: If sensor is not OPS243 or seconds is invalid
        """
        self._validate_ops243_only()

        if seconds <= 0:
            raise RadarValidationError("Range averaging period must be positive")

        self.send_command(f"yp{seconds}")
        self._config.averaging.range_averaging_period = seconds
        logger.info(f"Set range averaging period to {seconds} seconds")

    def set_range_averaging_delay(self, seconds: int) -> None:
        """
        Set delay between range averaging cycles (OPS243 only).

        Args:
            seconds: Delay in seconds between averaging cycles (default: 300)

        Raises:
            RadarValidationError: If sensor is not OPS243 or seconds is invalid
        """
        self._validate_ops243_only()

        if seconds <= 0:
            raise RadarValidationError("Range averaging delay must be positive")

        self.send_command(f"yd{seconds}")
        self._config.averaging.range_averaging_delay = seconds
        logger.info(f"Set range averaging delay to {seconds} seconds")

    def enable_speed_averaging(self, enable: bool = True) -> None:
        """
        Enable or disable speed averaging (OPS243 only).

        Args:
            enable: True to enable speed averaging, False to disable

        Raises:
            RadarValidationError: If sensor is not OPS243
        """
        self._validate_ops243_only()

        command = "Y+" if enable else "Y-"
        self.send_command(command)
        self._config.averaging.speed_averaging_enabled = enable

        status = "enabled" if enable else "disabled"
        logger.info(f"Speed averaging {status}")

    def set_speed_averaging_period(self, seconds: int) -> None:
        """
        Set speed averaging time period (OPS243 only).

        Args:
            seconds: Time period in seconds to average over (default: 5)
                    Set to 0 to enable moving average mode

        Raises:
            RadarValidationError: If sensor is not OPS243 or seconds is invalid
        """
        self._validate_ops243_only()

        if seconds < 0:
            raise RadarValidationError("Speed averaging period must be non-negative")

        self.send_command(f"Yp{seconds}")
        self._config.averaging.speed_averaging_period = seconds

        if seconds == 0:
            logger.info("Set speed averaging to moving average mode")
        else:
            logger.info(f"Set speed averaging period to {seconds} seconds")

    def set_speed_averaging_delay(self, seconds: int) -> None:
        """
        Set delay between speed averaging cycles (OPS243 only).

        Args:
            seconds: Delay in seconds between averaging cycles (default: 300)

        Raises:
            RadarValidationError: If sensor is not OPS243 or seconds is invalid
        """
        self._validate_ops243_only()

        if seconds <= 0:
            raise RadarValidationError("Speed averaging delay must be positive")

        self.send_command(f"Yd{seconds}")
        self._config.averaging.speed_averaging_delay = seconds
        logger.info(f"Set speed averaging delay to {seconds} seconds")

    def set_moving_average_points(self, points: int) -> None:
        """
        Set number of points for moving average (OPS243 only).

        Args:
            points: Number of speed reports to use in moving average (1-20)

        Raises:
            RadarValidationError: If sensor is not OPS243 or points is invalid
        """
        self._validate_ops243_only()

        if not 1 <= points <= 20:
            raise RadarValidationError("Moving average points must be between 1 and 20")

        self.send_command(f"Ym{points}")
        self._config.averaging.moving_average_points = points
        logger.info(f"Set moving average to {points} points")

    def configure_range_averaging(
        self, period: int = 5, delay: int = 300, enable: bool = True
    ) -> None:
        """
        Configure all range averaging parameters at once (OPS243 only).

        Args:
            period: Time period in seconds to average over (default: 5)
            delay: Delay in seconds between averaging cycles (default: 300)
            enable: Whether to enable range averaging (default: True)

        Raises:
            RadarValidationError: If sensor is not OPS243 or parameters are invalid
        """
        self.set_range_averaging_period(period)
        self.set_range_averaging_delay(delay)
        self.enable_range_averaging(enable)

    def configure_speed_averaging(
        self, period: int = 5, delay: int = 300, enable: bool = True
    ) -> None:
        """
        Configure all speed averaging parameters at once (OPS243 only).

        Args:
            period: Time period in seconds to average over (default: 5)
            delay: Delay in seconds between averaging cycles (default: 300)
            enable: Whether to enable speed averaging (default: True)

        Raises:
            RadarValidationError: If sensor is not OPS243 or parameters are invalid
        """
        self.set_speed_averaging_period(period)
        self.set_speed_averaging_delay(delay)
        self.enable_speed_averaging(enable)

    def configure_moving_average(self, points: int = 5, enable: bool = True) -> None:
        """
        Configure moving average mode (OPS243 only).

        This automatically sets the speed averaging period to 0 to enable moving average mode.

        Args:
            points: Number of speed reports to use in moving average (1-20, default: 5)
            enable: Whether to enable speed averaging (default: True)

        Raises:
            RadarValidationError: If sensor is not OPS243 or parameters are invalid
        """
        self.set_moving_average_points(points)
        self.set_speed_averaging_period(0)  # 0 enables moving average mode
        self.enable_speed_averaging(enable)

    def get_averaging_config(self) -> AveragingConfig:
        """
        Get current averaging configuration.

        Returns:
            Current AveragingConfig object
        """
        return self._config.averaging

    def enable_peak_speed_averaging(self, enable: bool = True) -> None:
        """
        Enable or disable peak speed averaging.

        When enabled, filters out multiple speed reports from the same object and
        provides the primary (peak) speed. The reported speed is the average of the
        three nearest detected speeds around the peak signal value.

        This is useful to reduce noise and report only the dominant speed of a
        detected object, filtering out secondary reflections or signal artifacts.

        Args:
            enable: True to enable, False to disable

        Example:
            # Enable peak speed averaging for cleaner speed reports
            radar.enable_peak_speed_averaging(True)
        """
        if not self.get_sensor_info().has_doppler:
            raise RadarValidationError(
                "Peak speed averaging only available on Doppler sensors"
            )

        command = "K+" if enable else "K-"
        self.send_command(command)
        logger.info(f"{'Enabled' if enable else 'Disabled'} peak speed averaging")

    # =============================================================================
    # Filter Commands
    # =============================================================================

    def set_speed_filter(
        self, min_speed: Optional[float] = None, max_speed: Optional[float] = None
    ) -> None:
        """
        Set speed filtering range.

        Args:
            min_speed: Minimum speed threshold (None to disable)
            max_speed: Maximum speed threshold (None to disable)
        """
        if not self.get_sensor_info().has_doppler:
            raise RadarValidationError(
                "Speed filtering only applies to Doppler sensors"
            )

        if min_speed is not None:
            if min_speed < 0:
                raise RadarValidationError("Minimum speed must be non-negative")
            self.send_command(f"R>{min_speed}")
            self._config.speed_filter_min = min_speed
            logger.info(f"Set minimum speed filter to {min_speed}")

        if max_speed is not None:
            if max_speed < 0:
                raise RadarValidationError("Maximum speed must be non-negative")
            if min_speed is not None and max_speed <= min_speed:
                raise RadarValidationError("Maximum speed must be greater than minimum")
            self.send_command(f"R<{max_speed}")
            self._config.speed_filter_max = max_speed
            logger.info(f"Set maximum speed filter to {max_speed}")

    def set_range_filter(
        self, min_range: Optional[float] = None, max_range: Optional[float] = None
    ) -> None:
        """
        Set range filtering range.

        Args:
            min_range: Minimum range threshold (None to disable)
            max_range: Maximum range threshold (None to disable)
        """
        if not self.get_sensor_info().has_fmcw:
            raise RadarValidationError("Range filtering only applies to FMCW sensors")

        if min_range is not None:
            if min_range < 0:
                raise RadarValidationError("Minimum range must be non-negative")
            self.send_command(f"r>{min_range}")
            self._config.range_filter_min = min_range
            logger.info(f"Set minimum range filter to {min_range}")

        if max_range is not None:
            if max_range < 0:
                raise RadarValidationError("Maximum range must be non-negative")
            if min_range is not None and max_range <= min_range:
                raise RadarValidationError("Maximum range must be greater than minimum")
            self.send_command(f"r<{max_range}")
            self._config.range_filter_max = max_range
            logger.info(f"Set maximum range filter to {max_range}")

    def set_direction_filter(self, direction: Optional[Direction] = None) -> None:
        """
        Set direction filtering.

        Args:
            direction: Direction to filter for (None to disable)
        """
        if not self.get_sensor_info().has_doppler:
            raise RadarValidationError(
                "Direction filtering only applies to Doppler sensors"
            )

        if direction == Direction.APPROACHING:
            self.send_command("R+")
        elif direction == Direction.RECEDING:
            self.send_command("R-")
        elif direction is None:
            self.send_command("R|")  # Clear direction filter
        else:
            raise RadarValidationError(f"Invalid direction: {direction}")

        self._config.direction_filter = direction
        logger.info(f"Set direction filter to {direction}")

    def enable_range_and_speed_filter(self, enable: bool = True) -> None:
        """
        Enable or disable range AND speed filtering (OPS243-C only).

        When enabled, only speed reports are shown when an object is detected within
        the configured range filter boundaries. This is useful for traffic monitoring
        where you only want speed reports when vehicles are in a specific detection zone.

        Requires both range filter (r>n, r<n) and speed capabilities to be available.

        Args:
            enable: True to enable combined filtering, False to disable

        Raises:
            RadarValidationError: If sensor doesn't support both speed and range

        Example:
            # Set up detection zone and enable combined filtering
            radar.set_range_filter(min_range=5.0, max_range=20.0)
            radar.set_speed_filter(min_speed=5.0)
            radar.enable_range_and_speed_filter(True)
            # Now only speeds detected within 5-20m range will be reported
        """
        sensor_info = self.get_sensor_info()
        if not (sensor_info.has_doppler and sensor_info.has_fmcw):
            raise RadarValidationError(
                "Range AND speed filter only available on OPS243-C combined sensors"
            )

        command = "OY" if enable else "Oy"
        self.send_command(command)
        self._config.range_and_speed_filter = enable
        logger.info(f"{'Enabled' if enable else 'Disabled'} range AND speed filter")

    # =============================================================================
    # Cosine Correction Methods
    # =============================================================================

    def enable_cosine_correction(
        self,
        angle_inbound_degrees: float,
        angle_outbound_degrees: Optional[float] = None,
    ) -> None:
        """
        Enable hardware cosine error correction for angled radar installations.

        Cosine error occurs when the radar is not perpendicular to the target's
        direction of motion. The radar measures radial velocity: v_radial = v_actual × cos(θ)

        The sensor applies correction in hardware. Separate angles can be configured
        for inbound (approaching) and outbound (receding) traffic to account for
        lane positioning in traffic monitoring applications.

        Args:
            angle_inbound_degrees: Installation angle for approaching objects (0-89 degrees)
            angle_outbound_degrees: Installation angle for receding objects (0-89 degrees).
                                   If None, uses same angle as inbound.

        Raises:
            RadarValidationError: If angles are invalid

        Example:
            # Single angle for both directions
            radar.enable_cosine_correction(30)

            # Different angles for inbound/outbound lanes
            radar.enable_cosine_correction(angle_inbound=25, angle_outbound=35)
        """
        import math

        # Use same angle for both if outbound not specified
        if angle_outbound_degrees is None:
            angle_outbound_degrees = angle_inbound_degrees

        # Validate angles
        if angle_inbound_degrees < 0 or angle_inbound_degrees >= 90:
            raise RadarValidationError(
                f"Inbound angle must be between 0 and 89 degrees, got {angle_inbound_degrees}"
            )
        if angle_outbound_degrees < 0 or angle_outbound_degrees >= 90:
            raise RadarValidationError(
                f"Outbound angle must be between 0 and 89 degrees, got {angle_outbound_degrees}"
            )

        # Warn for large angles
        for angle, label in [
            (angle_inbound_degrees, "inbound"),
            (angle_outbound_degrees, "outbound"),
        ]:
            if angle > 45:
                correction_factor = 1 / math.cos(math.radians(angle))
                logger.warning(
                    f"Large {label} correction angle ({angle}°) may produce unreliable results. "
                    f"Correction factor: {correction_factor:.2f}x"
                )

        # Send hardware commands
        self.send_command(f"^/+{angle_inbound_degrees}")
        self.send_command(f"^/-{angle_outbound_degrees}")

        # Update configuration
        self._config.cosine_correction.enabled = True
        self._config.cosine_correction.angle_inbound_degrees = angle_inbound_degrees
        self._config.cosine_correction.angle_outbound_degrees = angle_outbound_degrees

        logger.info(
            f"Enabled hardware cosine correction: "
            f"inbound={angle_inbound_degrees}°, outbound={angle_outbound_degrees}°"
        )

    def disable_cosine_correction(self) -> None:
        """
        Disable hardware cosine error correction.

        Sensor will return uncorrected measurements.
        """
        # Send commands to disable (0 degrees = no correction)
        self.send_command("^/+0")
        self.send_command("^/-0")

        self._config.cosine_correction.enabled = False
        self._config.cosine_correction.angle_inbound_degrees = 0.0
        self._config.cosine_correction.angle_outbound_degrees = 0.0

        logger.info("Disabled hardware cosine correction")

    def get_cosine_correction(self) -> CosineCorrection:
        """
        Get current cosine correction configuration from sensor.

        Queries the sensor's hardware cosine correction settings using the ^? command.

        Returns:
            CosineCorrection object with current settings

        Raises:
            RadarCommandError: If query fails
        """
        import json

        response = self.send_command("^?", expect_response=True)
        if response:
            try:
                # Parse JSON response: {"InboundSensorAngleDegrees": 0.00, "OutboundSensorAngleDegrees": 20.00}
                data = json.loads(response)
                angle_inbound = float(data.get("InboundSensorAngleDegrees", 0.0))
                angle_outbound = float(data.get("OutboundSensorAngleDegrees", 0.0))

                # Update local config
                self._config.cosine_correction.angle_inbound_degrees = angle_inbound
                self._config.cosine_correction.angle_outbound_degrees = angle_outbound
                self._config.cosine_correction.enabled = (
                    angle_inbound != 0.0 or angle_outbound != 0.0
                )

                return self._config.cosine_correction
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"Failed to parse cosine correction response: {e}")

        return self._config.cosine_correction

    # =============================================================================
    # Output Control Commands
    # =============================================================================

    def enable_output_mode(self, mode: OutputMode, enable: bool = True) -> None:
        """
        Enable or disable specific output mode.

        Per OPS radar API conventions:
        - First letter: O (uppercase) = Speed/Doppler, o (lowercase) = Range/FMCW
        - Second letter: Uppercase = Enable, Lowercase = Disable

        Examples:
        - OM = Enable speed magnitude
        - Om = Disable speed magnitude
        - oM = Enable range magnitude
        - om = Disable range magnitude

        Args:
            mode: OutputMode enum value
            enable: True to enable, False to disable

        Raises:
            RadarValidationError: If mode is not supported by sensor type
        """
        # Validate sensor capability for range-specific modes
        if mode == OutputMode.MAGNITUDE_RANGE:
            if not self.get_sensor_info().has_fmcw:
                raise RadarValidationError(
                    "Range magnitude output only available on FMCW sensors (OPS241-B, OPS243-C)"
                )

        # Determine first letter (data type prefix)
        if mode == OutputMode.MAGNITUDE_RANGE:
            # Range/FMCW modes use lowercase 'o'
            first_letter = "o"
        else:
            # Speed/Doppler modes use uppercase 'O'
            first_letter = "O"

        # Determine second letter (enable/disable)
        mode_letter = mode.value
        if enable:
            second_letter = mode_letter.upper()
        else:
            second_letter = mode_letter.lower()

        # Construct and send command
        command = first_letter + second_letter
        self.send_command(command)

        # Update config tracking
        if enable:
            if mode not in self._config.output_modes:
                self._config.output_modes.append(mode)
        else:
            if mode in self._config.output_modes:
                self._config.output_modes.remove(mode)

        logger.info(
            f"{'Enabled' if enable else 'Disabled'} {mode.name} (command: {command})"
        )

    def enable_json_output(self, enable: bool = True) -> None:
        """Enable/disable JSON formatted output."""
        self.enable_output_mode(OutputMode.JSON, enable)

    def enable_magnitude_output(
        self, enable: bool = True, range_magnitude: bool = False
    ) -> None:
        """
        Enable/disable signal magnitude in output.

        Args:
            enable: True to enable, False to disable
            range_magnitude: If True, enables range magnitude (oM/om).
                           If False, enables speed magnitude (OM/Om).
                           Range magnitude only available on FMCW sensors.

        Raises:
            RadarValidationError: If range_magnitude requested on non-FMCW sensor
        """
        if range_magnitude:
            self.enable_output_mode(OutputMode.MAGNITUDE_RANGE, enable)
        else:
            self.enable_output_mode(OutputMode.MAGNITUDE_SPEED, enable)

    def enable_timestamp_output(self, enable: bool = True) -> None:
        """Enable/disable timestamps in output."""
        self.enable_output_mode(OutputMode.TIMESTAMP, enable)

    # =============================================================================
    # Data Streaming
    # =============================================================================

    def start_streaming(self, callback: Callable[[RadarReading], None]) -> None:
        """
        Start streaming radar data with callback.

        Args:
            callback: Function called for each radar reading
        """
        if self._reader_thread and self._reader_thread.is_alive():
            logger.warning("Data streaming already active")
            return

        self._callback = callback
        self._stop_event.clear()
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        logger.info("Started radar data streaming")

    def stop_streaming(self) -> None:
        """Stop radar data streaming."""
        if self._reader_thread and self._reader_thread.is_alive():
            logger.info("Stopping radar data streaming...")
            self._stop_event.set()
            self._reader_thread.join(timeout=2.0)
            if self._reader_thread.is_alive():
                logger.warning("Data streaming thread did not stop cleanly")
            else:
                logger.info("Radar data streaming stopped")
        self._reader_thread = None
        self._callback = None

    def _read_loop(self) -> None:
        """Main data reading loop - runs in separate thread."""
        logger.debug("Radar data reader thread started")
        buf = b""

        while not self._stop_event.is_set():
            try:
                if not self.is_connected():
                    break

                # Read chunk with timeout
                chunk = self.ser.read(1024) if self.ser else b""
                if not chunk:
                    continue

                buf += chunk

                # Process complete lines from buffer
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try:
                        line_str = line.decode("ascii", errors="ignore").strip()
                    except Exception as e:
                        logger.debug(f"Error decoding line: {e}")
                        line_str = ""

                    if line_str and self._callback:
                        try:
                            reading = self._parse_radar_data(line_str)
                            if reading:
                                self._callback(reading)
                        except Exception as e:
                            logger.debug(f"Error in callback: {e}")

            except serial.SerialTimeoutException:
                continue  # Normal timeout, continue loop
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Radar read error: {e}")
                break

        # Process any remaining data in buffer
        if buf and self._callback:
            try:
                remaining_str = buf.decode("ascii", errors="ignore").strip()
                if remaining_str:
                    reading = self._parse_radar_data(remaining_str)
                    if reading:
                        self._callback(reading)
            except Exception as e:
                logger.debug(f"Error parsing radar data: {e}")

        logger.debug("Radar data reader thread ended")

    @abstractmethod
    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """
        Parse raw radar data string into RadarReading object.
        Must be implemented by sensor-specific subclasses.

        Args:
            data: Raw data string from radar

        Returns:
            RadarReading object or None if data cannot be parsed
        """

    @abstractmethod
    def _validate_units(self, units: Units) -> None:
        """
        Validate that units are supported by this sensor type.
        Must be implemented by sensor-specific subclasses.

        Args:
            units: Units enum value to validate

        Raises:
            RadarValidationError: If units not supported
        """

    # =============================================================================
    # Utility Methods
    # =============================================================================

    def get_config(self) -> RadarConfig:
        """Get current radar configuration."""
        return self._config

    def reset_sensor(self) -> None:
        """
        Reset sensor to factory default settings.

        This resets both the current configuration and flash memory to factory defaults.
        Uses the AX command and includes required 1-second delay.
        """
        self.send_command("AX")
        time.sleep(1.0)  # Required 1-second delay for flash operations
        self._config = RadarConfig()  # Reset local config
        logger.info("Sensor reset to factory defaults")

    def save_config_to_memory(self, save_baudrate: bool = False) -> None:
        """
        Save current configuration to flash memory.

        Configuration will be retained even after power loss or power cycling.
        Uses the A! command and includes required 1-second delay.

        Args:
            save_baudrate: If True, also save current baudrate to persistent memory.
                          This uses the AI command after saving main config.
        """
        self.send_command("A!")
        time.sleep(1.0)  # Required 1-second delay for flash operations
        logger.info("Configuration saved to flash memory")

        if save_baudrate:
            try:
                self.send_command("AI")
                time.sleep(1.0)  # Required 1-second delay for flash operations
                logger.info(f"Baudrate {self.baudrate} saved to persistent memory")
            except Exception as e:
                logger.warning(f"Failed to save baudrate to persistent memory: {e}")

    def save_baudrate_to_memory(self) -> None:
        """
        Save current baudrate setting to persistent memory.

        The saved baudrate will be used as default on power-up.
        Uses the AI command and includes required 1-second delay.

        Note: This only saves baudrate, not other configuration settings.
        Use save_config_to_memory(save_baudrate=True) to save both.
        """
        try:
            self.send_command("AI")
            time.sleep(1.0)  # Required 1-second delay for flash operations
            logger.info(f"Baudrate {self.baudrate} saved to persistent memory")
        except Exception as e:
            logger.error(f"Failed to save baudrate to persistent memory: {e}")
            raise RadarCommandError(f"Failed to save baudrate: {e}") from e

    def get_persistent_memory_settings(self) -> str:
        """
        Get current persistent memory settings.

        Returns:
            String containing current persistent memory settings

        Raises:
            RadarCommandError: If command fails or no response received
        """
        response = self.send_command("A?", expect_response=True)
        if response:
            logger.debug(f"Retrieved persistent memory settings: {response}")
            return response
        else:
            raise RadarCommandError("Failed to retrieve persistent memory settings")

    def read_flash_settings(self) -> str:
        """
        Read current flash settings.

        Returns:
            String containing current flash settings

        Raises:
            RadarCommandError: If command fails or no response received
        """
        response = self.send_command("A.", expect_response=True)
        if response:
            logger.debug(f"Retrieved flash settings: {response}")
            return response
        else:
            raise RadarCommandError("Failed to read flash settings")

    def reset_flash_settings(self) -> None:
        """
        Reset flash settings to factory defaults.

        This is equivalent to reset_sensor() but more explicit about what it does.
        Uses the AX command and includes required 1-second delay.
        """
        self.send_command("AX")
        time.sleep(1.0)  # Required 1-second delay for flash operations
        self._config = RadarConfig()  # Reset local config
        logger.info("Flash settings reset to factory defaults")

    def __str__(self) -> str:
        """String representation of radar sensor."""
        info = self.get_sensor_info()
        return f"{info.model} on {self.port_name} (FW: {info.firmware_version})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"{self.__class__.__name__}(port='{self.port_name}', "
            f"baudrate={self.baudrate}, connected={self.is_connected()})"
        )


# =============================================================================
# Specialized Sensor Classes
# =============================================================================


class OPS241A_DopplerRadar(OPSRadarSensor):
    """
    OPS241-A Doppler radar sensor.

    Features:
    - Motion detection
    - Speed measurement
    - Direction detection
    - Signal magnitude
    - Detection range: 20-25m (RCS = 10)
    """

    def _validate_units(self, units: Units) -> None:
        """Validate units for Doppler sensor."""
        doppler_units = {
            Units.METERS_PER_SECOND,
            Units.KILOMETERS_PER_HOUR,
            Units.FEET_PER_SECOND,
            Units.MILES_PER_HOUR,
            Units.CENTIMETERS_PER_SECOND,
        }
        if units not in doppler_units:
            raise RadarValidationError(
                f"OPS241-A only supports speed units: {[u.value for u in doppler_units]}"
            )

    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """Parse OPS241-A Doppler radar data."""
        try:
            # Handle JSON output
            if data.startswith("{"):
                return self._parse_json_data(data)

            # Handle standard output format: "speed direction magnitude" or "speed direction"
            parts = data.split()
            if len(parts) >= 2:
                speed = float(parts[0])
                direction = (
                    Direction.APPROACHING if parts[1] == "+" else Direction.RECEDING
                )
                magnitude = float(parts[2]) if len(parts) > 2 else None

                return RadarReading(
                    speed=abs(speed),  # Speed is always positive
                    direction=direction,
                    magnitude=magnitude,
                    raw_data=data.strip(),
                )

        except (ValueError, IndexError) as e:
            logger.debug(f"Could not parse radar data '{data}': {e}")

        return None

    def _parse_json_data(self, data: str) -> Optional[RadarReading]:
        """Parse JSON formatted radar data."""
        try:
            json_data = json.loads(data)
            return RadarReading(
                speed=abs(float(json_data.get("speed", 0))),
                direction=(
                    Direction.APPROACHING
                    if json_data.get("direction") == "+"
                    else Direction.RECEDING
                ),
                magnitude=(
                    float(json_data.get("magnitude", 0))
                    if "magnitude" in json_data
                    else None
                ),
                timestamp=float(json_data.get("time", time.time())),
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Could not parse JSON data '{data}': {e}")
            return None


class OPS242A_DopplerRadar(OPS241A_DopplerRadar):
    """
    OPS242-A Enhanced Doppler radar sensor.

    Features:
    - All OPS241-A features
    - Enhanced sensitivity and range
    - Detection range: 20-25m (RCS = 10)
    """


class OPS243A_DopplerRadar(OPS241A_DopplerRadar):
    """
    OPS243-A Advanced Doppler radar sensor.

    Features:
    - All OPS241-A features
    - Range measurement (pending in firmware)
    - FCC/IC modular approval
    - Detection range: 75-100m (RCS = 10)
    """


class OPS241B_FMCWRadar(OPSRadarSensor):
    """
    OPS241-B FMCW radar sensor.

    Features:
    - Range measurement only
    - Signal magnitude
    - Detection range: 15-20m (RCS = 10)
    """

    def _validate_units(self, units: Units) -> None:
        """Validate units for FMCW sensor."""
        fmcw_units = {Units.METERS, Units.CENTIMETERS, Units.FEET}
        if units not in fmcw_units:
            raise RadarValidationError(
                f"OPS241-B only supports range units: {[u.value for u in fmcw_units]}"
            )

    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """Parse OPS241-B FMCW radar data."""
        try:
            # Handle JSON output
            if data.startswith("{"):
                return self._parse_json_data(data)

            # Handle standard output format: "range magnitude" or "range"
            parts = data.split()
            if len(parts) >= 1:
                range_m = float(parts[0])
                magnitude = float(parts[1]) if len(parts) > 1 else None

                return RadarReading(range_m=range_m, magnitude=magnitude)

        except (ValueError, IndexError) as e:
            logger.debug(f"Could not parse radar data '{data}': {e}")

        return None

    def _parse_json_data(self, data: str) -> Optional[RadarReading]:
        """Parse JSON formatted radar data."""
        try:
            json_data = json.loads(data)
            return RadarReading(
                range_m=float(json_data.get("range", 0)),
                magnitude=(
                    float(json_data.get("magnitude", 0))
                    if "magnitude" in json_data
                    else None
                ),
                timestamp=float(json_data.get("time", time.time())),
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Could not parse JSON data '{data}': {e}")
            return None


class OPS243C_CombinedRadar(OPSRadarSensor):
    """
    OPS243-C Combined FMCW & Doppler radar sensor.

    Features:
    - Motion detection
    - Speed measurement
    - Direction detection
    - Range measurement
    - Signal magnitude
    - FCC/IC modular approval
    - Detection range: 50-60m (RCS = 10)
    """

    def _validate_units(self, units: Units) -> None:
        """Validate units for combined sensor - supports both speed and range units."""
        # Combined sensor supports all units
        all_units = set(Units)
        if units not in all_units:
            raise RadarValidationError(f"Invalid units: {units}")

    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """Parse OPS243-C combined radar data."""
        try:
            # Handle JSON output
            if data.startswith("{"):
                return self._parse_json_data(data)

            # Handle OPS243-C specific format: "units",value or "units",value,extra
            # Example: "m",2.1 or "kmph",48,-1.3
            if '"' in data and "," in data:
                # Parse format like "m",2.1 or "kmph",48,-1.3
                parts = data.split(",")
                if len(parts) >= 2:
                    units_part = parts[0].strip().strip('"')
                    value_str = parts[1].strip()

                    try:
                        value = float(value_str)
                        reading = RadarReading(raw_data=data.strip())

                        # Determine if this is speed or range based on units
                        if units_part in ["mps", "mph", "kmh", "kmph", "m/s", "km/h"]:
                            # Speed data
                            reading.speed = abs(value)
                            # OPS243-C typically sends positive for approaching, negative for receding
                            reading.direction = (
                                Direction.APPROACHING
                                if value >= 0
                                else Direction.RECEDING
                            )

                            # Check for third value (might be additional data or range)
                            if len(parts) >= 3:
                                try:
                                    third_val = float(parts[2].strip())
                                    # If it's a reasonable range value, use it
                                    if (
                                        0 < abs(third_val) < 100
                                    ):  # Reasonable range in meters
                                        reading.range_m = abs(third_val)
                                except ValueError:
                                    pass

                        elif units_part in ["m", "ft", "cm"]:
                            # Range data
                            reading.range_m = value

                        return reading
                    except ValueError:
                        pass

            # Handle standard output format: "speed direction range magnitude"
            # or various combinations depending on enabled outputs
            parts = data.split()
            if len(parts) >= 1:
                reading = RadarReading(raw_data=data.strip())

                # Parse based on number of parts and content
                if len(parts) >= 4:
                    # Full format: speed, direction, range, magnitude
                    reading.speed = abs(float(parts[0]))
                    reading.direction = (
                        Direction.APPROACHING if parts[1] == "+" else Direction.RECEDING
                    )
                    reading.range_m = float(parts[2])
                    reading.magnitude = float(parts[3])
                elif len(parts) == 3:
                    # Could be speed+direction+range or speed+direction+magnitude
                    reading.speed = abs(float(parts[0]))
                    reading.direction = (
                        Direction.APPROACHING if parts[1] == "+" else Direction.RECEDING
                    )
                    # Heuristic: if third value is large, it's probably magnitude
                    third_val = float(parts[2])
                    if third_val > 100:  # Typical magnitude values are > 100
                        reading.magnitude = third_val
                    else:
                        reading.range_m = third_val
                elif len(parts) == 2:
                    # Could be speed+direction or range+magnitude
                    first_val = float(parts[0])
                    if parts[1] in ["+", "-"]:
                        # Speed and direction
                        reading.speed = abs(first_val)
                        reading.direction = (
                            Direction.APPROACHING
                            if parts[1] == "+"
                            else Direction.RECEDING
                        )
                    else:
                        # Range and magnitude
                        reading.range_m = first_val
                        reading.magnitude = float(parts[1])
                else:
                    # Single value - could be speed or range
                    val = float(parts[0])
                    # Heuristic: speeds are typically < 50, ranges can be higher
                    if val < 50:
                        reading.speed = abs(val)
                    else:
                        reading.range_m = val

                return reading

        except (ValueError, IndexError) as e:
            logger.debug(f"Could not parse radar data '{data}': {e}")

        return None

    def _parse_json_data(self, data: str) -> Optional[RadarReading]:
        """Parse JSON formatted radar data."""
        try:
            json_data = json.loads(data)
            return RadarReading(
                speed=(
                    abs(float(json_data.get("speed", 0)))
                    if "speed" in json_data
                    else None
                ),
                direction=(
                    Direction.APPROACHING
                    if json_data.get("direction") == "+"
                    else (
                        Direction.RECEDING
                        if json_data.get("direction") == "-"
                        else None
                    )
                ),
                range_m=(
                    float(json_data.get("range", 0)) if "range" in json_data else None
                ),
                magnitude=(
                    float(json_data.get("magnitude", 0))
                    if "magnitude" in json_data
                    else None
                ),
                timestamp=float(json_data.get("time", time.time())),
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Could not parse JSON data '{data}': {e}")
            return None


# =============================================================================
# Factory Functions and Utilities
# =============================================================================


def create_radar(
    model: str,
    port: str,
    baudrate: Optional[int] = None,
    auto_detect_baudrate: bool = True,
    **kwargs: Any,
) -> OPSRadarSensor:
    """
    Factory function to create appropriate radar sensor instance.

    Args:
        model: Radar model string (e.g., 'OPS241-A', 'OPS243-C')
        port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
        baudrate: Serial communication speed. If None, uses radar default (19200)
                 or auto-detection if enabled
        auto_detect_baudrate: Enable automatic baudrate detection if initial connection fails
        **kwargs: Additional arguments passed to sensor constructor

    Returns:
        Appropriate radar sensor instance

    Raises:
        RadarValidationError: If model is not supported

    Examples:
        Basic usage with auto-detection:
        ```python
        radar = create_radar('OPS243-C', '/dev/ttyUSB0')
        ```

        Specify exact baudrate:
        ```python
        radar = create_radar('OPS243-C', '/dev/ttyUSB0', baudrate=19200)
        ```

        Disable auto-detection:
        ```python
        radar = create_radar('OPS243-C', '/dev/ttyUSB0', auto_detect_baudrate=False)
        ```
    """
    model = model.upper().replace("-", "").replace("_", "")

    sensor_classes: Dict[str, Type[OPSRadarSensor]] = {
        "OPS241A": OPS241A_DopplerRadar,
        "OPS242A": OPS242A_DopplerRadar,
        "OPS243A": OPS243A_DopplerRadar,
        "OPS241B": OPS241B_FMCWRadar,
        "OPS243C": OPS243C_CombinedRadar,
    }

    if model not in sensor_classes:
        available = ", ".join(sensor_classes.keys())
        raise RadarValidationError(
            f"Unsupported radar model '{model}'. Available: {available}"
        )

    sensor_class = sensor_classes[model]

    # Pass baudrate and auto_detect_baudrate explicitly, along with other kwargs
    return sensor_class(
        port=port,
        baudrate=baudrate,
        auto_detect_baudrate=auto_detect_baudrate,
        **kwargs,
    )


def get_supported_models() -> List[str]:
    """
    Get list of supported radar models.

    Returns:
        List of supported model strings
    """
    return ["OPS241-A", "OPS242-A", "OPS243-A", "OPS241-B", "OPS243-C"]


def get_model_info(model: str) -> Dict[str, Any]:
    """
    Get information about a specific radar model.

    Args:
        model: Radar model string

    Returns:
        Dictionary with model information

    Example:
        ```python
        info = get_model_info('OPS243-C')
        print(f"Detection range: {info['detection_range']}")
        ```
    """
    model_info = {
        "OPS241-A": {
            "type": "Doppler",
            "features": ["Motion", "Speed", "Direction", "Signal Magnitude"],
            "detection_range": "20-25m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": False,
        },
        "OPS242-A": {
            "type": "Doppler",
            "features": ["Motion", "Speed", "Direction", "Signal Magnitude"],
            "detection_range": "20-25m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": False,
        },
        "OPS243-A": {
            "type": "Doppler",
            "features": [
                "Motion",
                "Speed",
                "Direction",
                "Signal Magnitude",
                "Range (pending)",
            ],
            "detection_range": "75-100m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": True,
        },
        "OPS241-B": {
            "type": "FMCW",
            "features": ["Range", "Signal Magnitude"],
            "detection_range": "15-20m",
            "max_speed": "N/A",
            "fcc_approved": False,
        },
        "OPS243-C": {
            "type": "FMCW & Doppler",
            "features": ["Motion", "Speed", "Direction", "Range", "Signal Magnitude"],
            "detection_range": "50-60m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": True,
        },
    }

    model = model.upper()
    if model not in model_info:
        raise RadarValidationError(f"Unknown model: {model}")

    return model_info[model]
