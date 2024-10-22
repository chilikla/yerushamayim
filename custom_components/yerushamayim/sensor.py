"""Sensor platform for Yerushamayim integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .data_coordinator import YerushamayimDataCoordinator

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Yerushamayim sensors."""
    coordinator = hass.data[DOMAIN]

    sensors = [
        YerushamayimTemperatureSensor(coordinator),
        YerushamayimHumiditySensor(coordinator),
        YerushamayimStatusSensor(coordinator),
        YerushamayimForecastSensor(coordinator),
    ]

    async_add_entities(sensors, True)

class YerushamayimBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Yerushamayim sensors."""

    def __init__(self, coordinator: YerushamayimDataCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{self.sensor_type}"
        self._attr_name = f"Yerushamayim {self.sensor_type.title()}"

    @property
    def sensor_type(self) -> str:
        """Return the sensor type."""
        raise NotImplementedError

    @property
    def native_value(self) -> None:
        """No native value for these sensors."""
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return getattr(self.coordinator.data, self.sensor_type)

class YerushamayimTemperatureSensor(YerushamayimBaseSensor):
    """Temperature sensor for Yerushamayim."""

    sensor_type = "temperature"

    @property
    def device_class(self):
        """Return the device class."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        """Return the state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def extra_state_attributes(self):
        """Return the state attributes with numeric conversions."""
        attrs = super().extra_state_attributes
        # Convert temperature values to float where possible
        for key in attrs:
            if attrs[key] is not None:
                try:
                    attrs[key] = float(attrs[key])
                except (ValueError, TypeError):
                    pass
        return attrs

class YerushamayimHumiditySensor(YerushamayimBaseSensor):
    """Humidity sensor for Yerushamayim."""

    sensor_type = "humidity"

    @property
    def device_class(self):
        """Return the device class."""
        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self):
        """Return the state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def extra_state_attributes(self):
        """Return the state attributes with numeric conversion."""
        attrs = super().extra_state_attributes
        for key in attrs:
            if attrs[key] is not None:
                try:
                    attrs[key] = float(attrs[key])
                except (ValueError, TypeError):
                    pass
        return attrs

class YerushamayimStatusSensor(YerushamayimBaseSensor):
    """Status sensor for Yerushamayim."""

    sensor_type = "status"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:weather-sunny"

class YerushamayimForecastSensor(YerushamayimBaseSensor):
    """Forecast sensor for Yerushamayim."""

    sensor_type = "forecast"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:clock-outline"

    @property
    def extra_state_attributes(self):
        """Return the state attributes with numeric conversions for temperatures."""
        attrs = super().extra_state_attributes
        # Convert temperature values to float where possible
        for key in attrs:
            if key.endswith('_temp') and attrs[key] is not None:
                try:
                    attrs[key] = float(attrs[key])
                except (ValueError, TypeError):
                    pass
        return attrs