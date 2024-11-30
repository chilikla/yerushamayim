"""Sensor platform for Yerushamayim integration."""
from __future__ import annotations
from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfPrecipitationDepth
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .data_coordinator import YerushamayimDataCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Yerushamayim sensors."""
    coordinator = YerushamayimDataCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        YerushamayimTemperatureSensor(coordinator),
        YerushamayimHumiditySensor(coordinator),
        YerushamayimStatusSensor(coordinator),
        YerushamayimForecastSensor(coordinator),
        YerushamayimPrecipitationSensor(coordinator)
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
        return UnitOfTemperature.CELSIUS

    @property
    def native_value(self):
        """Return the temperature value."""
        temp = self.coordinator.data.temperature.get("temperature")
        try:
            return float(temp) if temp is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:thermometer"

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
    def native_value(self):
        """Return the humidity value."""
        return self.coordinator.data.humidity.get("humidity")

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:water-percent"

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
    def native_value(self):
        """Return the forecast text."""
        return self.coordinator.data.status.get("forecast")

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:weather-sunny"

class YerushamayimForecastSensor(YerushamayimBaseSensor):
    """Forecast sensor for Yerushamayim."""

    sensor_type = "forecast"

    @property
    def native_value(self):
        """Return the day of the week."""
        days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }
        return days[datetime.now().weekday()]

    @property
    def icon(self):
        """Return the icon."""
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

class YerushamayimPrecipitationSensor(YerushamayimBaseSensor):
    """Precipitation sensor for Yerushamayim."""

    sensor_type = "precipitation"

    @property
    def device_class(self):
        """Return the device class."""
        return SensorDeviceClass.PRECIPITATION 

    @property
    def state_class(self):
        """Return the state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfPrecipitationDepth.MILLIMETERS

    @property
    def native_value(self):
        """Return the forecast text."""
        return float(self.coordinator.data.precipitation["precipitation"])

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:weather-pouring"

    @property
    def extra_state_attributes(self):
        """Return the state attributes with numeric conversions for precipitation."""
        attrs = super().extra_state_attributes
        attrs["precipitation_probability_unit"] = PERCENTAGE
        return attrs