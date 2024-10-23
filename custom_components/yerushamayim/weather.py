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
    coordinator = hass.data[DOMAIN]
    async_add_entities([YerushamayimWeather(coordinator)], True)

class YerushamayimWeather(CoordinatorEntity, WeatherEntity):
    def __init__(self, coordinator: YerushamayimDataCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_weather"
        self._attr_name = "Yerushamayim Weather"

    @property
    def native_temperature(self) -> float:
        return float(self.coordinator.data.temperature["temperature"])

    @property
    def native_apparent_temperature(self) -> float:
        return float(self.coordinator.data.temperature["apparent_temperature"])

    @property
    def native_temperature_unit(self) -> str:
        return UnitOfTemperature.CELSIUS

    @property
    def humidity(self) -> float:
        return float(self.coordinator.data.humidity["humidity"])

    @property
    def condition(self) -> str:
        return self.coordinator.data.status["forecast"]