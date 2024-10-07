"""Support for Yerushamayim weather service."""
from __future__ import annotations

from homeassistant.components.weather import (
    WeatherEntity,
    Forecast,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yerushamayim weather based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([YerushamayimWeather(coordinator)], False)

class YerushamayimWeather(CoordinatorEntity, WeatherEntity):
    """Representation of Yerushamayim weather data."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize the Yerushamayim weather entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_weather"

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return self.coordinator.data.get("current_temp")

    @property
    def native_temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return "°C"

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        # TODO: Implement if available
        return None

    @property
    def wind_speed(self) -> float | None:
        """Return the wind speed."""
        # TODO: Implement if available
        return None

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        # TODO: Implement if available
        return None

    @property
    def attribution(self) -> str:
        """Return the attribution."""
        return "Data provided by Yerushamayim Weather Service"

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        # TODO: Map the condition to HA states
        return None

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast."""
        # TODO: Implement forecast data
        return None

    # TODO: Implement other relevant properties and methods