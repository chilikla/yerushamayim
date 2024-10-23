"""Weather platform for Yerushamayim integration."""
from __future__ import annotations

from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfTemperature
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
    """Set up the Yerushamayim weather platform."""
    coordinator = YerushamayimDataCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([YerushamayimWeather(coordinator)], True)

class YerushamayimWeather(CoordinatorEntity, WeatherEntity):
    """Weather entity for Yerushamayim."""

    def __init__(self, coordinator: YerushamayimDataCoordinator):
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_weather"
        self._attr_name = "Yerushamayim Weather"
        self._attr_native_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def native_temperature(self) -> float | None:
        """Return the platform temperature."""
        try:
            return float(self.coordinator.data.temperature["temperature"])
        except (ValueError, KeyError, TypeError):
            return None

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent temperature."""
        try:
            return float(self.coordinator.data.temperature["apparent_temperature"])
        except (ValueError, KeyError, TypeError):
            return None

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        try:
            return float(self.coordinator.data.humidity["humidity"])
        except (ValueError, KeyError, TypeError):
            return None

    @property
    def condition(self) -> str | None:
        """Return the weather condition."""
        try:
            return self.coordinator.data.status["condition"]
        except (KeyError, TypeError):
            return None