"""Temperature Handler Module of nibcq package."""

import math
from dataclasses import dataclass
from typing import Optional

import nidaqmx
from nidaqmx.constants import CJCSource, TemperatureUnits, ThermocoupleType


@dataclass
class TemperatureParameter:
    """Container for temperature measurement data and validation parameters.

    Stores the current temperature reading along with the acceptable temperature
    delta for compensation validation. Used by the temperature capability system
    to track measurement conditions and validate compensation requirements.

    Attributes:
        temperature (float): Current temperature reading in the defined degrees unit.
            None if no measurement has been taken.
        temperature_delta (float): Acceptable temperature variation in the defined degrees unit.
            for compensation validation. None if not set.

    Examples:
        >>> param = TemperatureParameter(25.5, 2.0)
        >>> print(f"Temperature: {param.temperature}°C ±{param.temperature_delta}°C")
    """

    temperature: float = None
    temperature_delta: float = None


@dataclass
class ThermocoupleSettings:
    """Configuration settings for thermocouple temperature measurements.

    Contains all the parameters needed to configure a thermocouple measurement
    task including the physical connection, measurement range, and thermocouple
    type specifications. Used by TemperatureCapability to set up temperature
    monitoring for compensation validation.

    Attributes:
        resource_name (str): DAQ device resource name (e.g., "Dev1/ai0")
        cjc_source (CJCSource): Cold junction compensation source type.
            Defaults to built-in compensation.
        units (TemperatureUnits): Temperature measurement units.
            Defaults to degrees Celsius.
        thermocouple_type (ThermocoupleType): Type of thermocouple being used.
            Defaults to Type T thermocouple.
        min_value (float): Minimum expected temperature value in specified units.
            Defaults to 0.0.
        max_value (float): Maximum expected temperature value in specified units.
            Defaults to 100.0.

    Examples:
        >>> settings = ThermocoupleSettings("Dev1/ai0")
        >>> settings = ThermocoupleSettings(
        ...     resource_name="Dev1/ai0",
        ...     thermocouple_type=ThermocoupleType.K,
        ...     min_value=-50.0,
        ...     max_value=150.0
        ... )
    """

    resource_name: str
    cjc_source: CJCSource = CJCSource.BUILT_IN
    units: TemperatureUnits = TemperatureUnits.DEG_C
    thermocouple_type: ThermocoupleType = ThermocoupleType.T
    min_value: float = 0.0
    max_value: float = 100.0


class TemperatureCapability:
    """Temperature measurement capability that can be added to measurement devices.

    Provides thermocouple-based temperature monitoring functionality for devices
    that require temperature for validating compensation values. Manages DAQ tasks for
    temperature acquisition and tracks acceptable temperature variations for
    measurement validity.

    This capability can be added to Device instances to enable temperature
    monitoring during measurements, which is essential for proper compensation
    validation in precision measurement applications.

    Examples:
        >>> capability = TemperatureCapability()
        >>> settings = ThermocoupleSettings("Dev1/ai0")
        >>> capability.setup_thermocouple(settings)
        >>> temp = capability.read_temperature()
    """

    def __init__(self):
        """Initialize temperature measurement capability.

        Creates a new temperature capability instance with no active measurement
        task. The capability must be configured with thermocouple settings before
        temperature measurements can be performed.

        Examples:
            >>> temp_cap = TemperatureCapability()
            >>> print(temp_cap.thermocouple_settings)  # None until configured
        """
        self._temperature_task: Optional[nidaqmx.Task] = None
        self._thermocouple_settings: Optional[ThermocoupleSettings] = None
        self._temperature_measurement = TemperatureParameter(math.nan, math.nan)

    @property
    def thermocouple_settings(self) -> Optional[ThermocoupleSettings]:
        """Get the current thermocouple configuration settings.

        Returns the ThermocoupleSettings object that defines how temperature
        measurements are performed, including the DAQ resource, thermocouple
        type, and measurement range. Returns None if temperature capability
        has not been configured yet.

        Returns:
            Optional[ThermocoupleSettings]: The current thermocouple settings,
                or None if not configured yet

        Examples:
            >>> capability = TemperatureCapability()
            >>> print(capability.thermocouple_settings)  # None
            >>> settings = ThermocoupleSettings("Dev1/ai0")
            >>> capability.setup_thermocouple(settings)
            >>> print(capability.thermocouple_settings.resource_name)  # "Dev1/ai0"
        """
        return self._thermocouple_settings

    @property
    def acceptable_temperature_delta(self) -> float:
        """Get the acceptable temperature delta for compensation validation.

        Returns the maximum allowed temperature difference in the configured data type
        between the current measurement temperature and the reference temperature used
        for compensation. This value is used to validate whether compensation
        data is still valid for the current thermal conditions.

        Returns:
            float: The acceptable temperature delta in the defined degrees unit, or NaN if not set

        Examples:
            >>> capability = TemperatureCapability()
            >>> capability.acceptable_temperature_delta = 2.5
            >>> delta = capability.acceptable_temperature_delta
            >>> print(f"Max temperature delta: ±{delta}°C")
        """
        return self._temperature_measurement.temperature_delta

    @acceptable_temperature_delta.setter
    def acceptable_temperature_delta(self, value: float):
        """Set the acceptable temperature delta for compensation validation.

        Defines the maximum allowed temperature difference in the configured data type
        between the current measurement temperature and the reference temperature used
        for compensation. Values outside this range may indicate that compensation
        data is no longer valid and a recapture of the compensation data is needed.

        Args:
            value (float): The acceptable temperature delta in the defined degrees unit.
                Should be a positive value representing the tolerance range.

        Raises:
            ValueError: If value is negative or not a valid number

        Examples:
            >>> capability = TemperatureCapability()
            >>> capability.acceptable_temperature_delta = 2.5  # ±2.5 tolerance
            >>> capability.acceptable_temperature_delta = 1.0  # Tighter tolerance
        """
        if value < 0:
            raise ValueError("Temperature delta must be non-negative")
        self._temperature_measurement.temperature_delta = value

    @property
    def temperature_measurement(self) -> TemperatureParameter:
        """Get the latest temperature measurement data.

        Returns the most recent temperature reading along with the acceptable
        temperature delta for validation. This information is used for
        compensation validation and thermal monitoring during measurements.

        Returns:
            TemperatureParameter: Object containing the latest temperature
                reading in the defined degrees unit and the acceptable temperature delta

        Examples:
            >>> capability = TemperatureCapability()
            >>> measurement = capability.temperature_measurement
            >>> if not math.isnan(measurement.temperature):
            ...     print(f"Current temperature: {measurement.temperature}°C")
        """
        return self._temperature_measurement

    def _create_temperature_task(self):
        """Establish a connection to the temperature measurement device.

        Creates and configures a DAQ task for thermocouple temperature measurements
        using the settings provided in thermocouple_settings. The task is configured
        with the appropriate thermocouple type, cold junction compensation, and
        measurement range.

        This method requires self._thermocouple_settings to be configured before
        it can create the measurement task.

        Raises:
            RuntimeError: If thermocouple_settings is not configured
            nidaqmx.errors.DaqError: If DAQ device configuration fails

        Examples:
            >>> capability = TemperatureCapability()
            >>> settings = ThermocoupleSettings("Dev1/ai0")
            >>> capability.setup_thermocouple(settings)
            >>> capability._create_temperature_task()  # Internal method
        """
        if not self._thermocouple_settings:
            raise RuntimeError("Thermocouple settings not configured")

        self._temperature_task = nidaqmx.Task()
        self._temperature_task.ai_channels.add_ai_thrmcpl_chan(
            physical_channel=self._thermocouple_settings.resource_name,
            name_to_assign_to_channel="",
            min_val=self._thermocouple_settings.min_value,
            max_val=self._thermocouple_settings.max_value,
            units=self._thermocouple_settings.units,
            thermocouple_type=self._thermocouple_settings.thermocouple_type,
            cjc_source=self._thermocouple_settings.cjc_source,
        )

    def setup_thermocouple(
        self,
        settings: ThermocoupleSettings,
        temperature_delta: float = math.nan,
    ):
        """Configure the thermocouple settings for temperature measurements.

        Args:
            settings: The thermocouple configuration settings
            temperature_delta: The acceptable temperature delta for validation.
                The base suggested value is 1.5. Leave as NaN to use compensation
                file defined target value.
        """
        self.acceptable_temperature_delta = temperature_delta or math.nan
        self._thermocouple_settings = settings

    def _run_task(self):
        """Read the temperature from the thermocouple.

        Creates a new task for each measurement to ensure clean, isolated
        temperature readings. Task is automatically closed after reading.

        Raises:
            RuntimeError: If thermocouple settings are not initialized
        """
        if self._thermocouple_settings is None:
            raise RuntimeError(
                "Thermocouple settings not initialized. Use 'setup_thermocouple' first."
            )
        self._create_temperature_task()
        self._temperature_measurement.temperature = self._temperature_task.read()
        self._close_thermocouple()

    def measure_temperature(self) -> TemperatureParameter:
        """Get a new, current temperature reading and update the measured temperature.

        Returns:
            The current temperature reading with delta information
        """
        if not self._thermocouple_settings:
            return TemperatureParameter(math.nan, math.nan)
        self._run_task()
        return self._temperature_measurement

    def _validate_latest_temperature(self, target_temperature: TemperatureParameter) -> None:
        """Validate the current temperature against the compensation file's target.

        Checks if the measured temperature is within the acceptable delta specified
        in the compensation file. It also handles cases where the acceptable delta
        is overwritten or if the thermocouple is not connected.

        Args:
            target_temperature: The target temperature parameters for validation

        Raises:
            ValueError: If the current temperature exceeds the target range
        """
        # Get temperature targets
        target_temp = target_temperature.temperature
        target_delta = target_temperature.temperature_delta
        # Check if temperature validation is needed
        if self._thermocouple_settings is not None:
            if not math.isnan(target_temp) and not math.isnan(target_delta):
                # Check if target delta was overwritten.
                if (
                    not math.isnan(self._temperature_measurement.temperature_delta)
                    and self._temperature_measurement.temperature_delta != target_delta
                ):
                    print("WARNING! Acceptable temperature delta was overwritten.")
                    target_delta = self.acceptable_temperature_delta
                # Check if current temperature exceeds the target range
                if abs(self._temperature_measurement.temperature - target_temp) > target_delta:
                    raise ValueError(
                        f"Current temperature {self._temperature_measurement.temperature} "
                        f"exceeds target temperature {target_temp} ± {target_delta}."
                    )
        # Warn about unchecked but existing temperature
        elif not math.isnan(target_temp):
            if not self._thermocouple_settings:
                print(
                    "WARNING! Thermocouple is not connected, "
                    "but target temperature compensation is set."
                )
        return

    def _close_thermocouple(self):
        """Close the connection to the thermocouple device.

        Called automatically after each temperature measurement to ensure
        proper resource cleanup. Safe to call multiple times.
        """
        if self._temperature_task is not None:
            self._temperature_task.close()
            self._temperature_task = None


class TemperatureAware:
    """Mixin class for measurements that need temperature awareness.

    This class provides a simple interface for measurements that need access
    to temperature functionality. It delegates to the device's temperature
    capability if available.
    """

    def __init__(self):
        """Initialize temperature awareness."""
        # This will be overridden by the actual TemperatureCapability class
        pass

    @property
    def acceptable_temperature_delta(self) -> float:
        """Get the acceptable temperature delta for compensation validation.

        Returns the maximum allowed temperature difference from the device's
        temperature capability. This is a pass-through property that delegates
        to the underlying TemperatureCapability.

        Returns:
            float: The acceptable temperature delta in degrees, or NaN if no temperature capability

        Examples:
            >>> measurement = EIS(device)
            >>> measurement.acceptable_temperature_delta = 2.5
            >>> delta = measurement.acceptable_temperature_delta
        """
        if hasattr(self.device, "_temperature_capability") and self.device._temperature_capability:
            return self.device._temperature_capability.acceptable_temperature_delta
        return math.nan

    @acceptable_temperature_delta.setter
    def acceptable_temperature_delta(self, value: float):
        """Set the acceptable temperature delta for compensation validation.

        Sets the maximum allowed temperature difference through the device's
        temperature capability. This is a pass-through property that delegates
        to the underlying TemperatureCapability.

        Args:
            value (float): The acceptable temperature delta in degrees.
                Should be a positive value representing the tolerance range.

        Raises:
            ValueError: If value is negative or not a valid number
            RuntimeError: If device has no temperature capability

        Examples:
            >>> measurement = EIS(device)
            >>> measurement.acceptable_temperature_delta = 2.5
        """
        if hasattr(self.device, "_temperature_capability") and self.device._temperature_capability:
            self.device._temperature_capability.acceptable_temperature_delta = value
        else:
            raise RuntimeError("Device has no temperature capability configured")

    @property
    def temperature_measurement(self) -> TemperatureParameter:
        """Get the latest temperature reading from the device.

        Returns:
            The most recent temperature measurement, or NaN if no temperature capability
        """
        if hasattr(self.device, "_temperature_capability") and self.device._temperature_capability:
            return self.device._temperature_capability.temperature_measurement
        return TemperatureParameter(math.nan, math.nan)

    def measure_temperature(self) -> TemperatureParameter:
        """Get a new temperature reading from the device.

        Returns:
            Current temperature reading, or NaN if no temperature capability
        """
        if hasattr(self.device, "_temperature_capability") and self.device._temperature_capability:
            return self.device._temperature_capability.measure_temperature()
        return TemperatureParameter(math.nan, math.nan)
