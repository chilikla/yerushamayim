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
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .data_coordinator import YerushamayimDataCoordinator

from datetime import datetime

_LOGGER = logging.getLogger(__name__)

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

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yerushamayim weather based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([YerushamayimWeather(coordinator)], True)

class YerushamayimWeather(CoordinatorEntity, WeatherEntity):
    """Weather entity for Yerushamayim."""

    def __init__(self, coordinator: YerushamayimDataCoordinator):
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_weather"
        self._attr_name = "Yerushamayim Weather"
        self._attr_native_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

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
            return self.coordinator.data.status["forecast"]
        except (KeyError, TypeError):
            return None
    
    @property
    def native_precipitation(self) -> float | None:
        """Return the precipitation"""
        try:
            return float(self.coordinator.data.rain["precipitation"])
        except (ValueError, KeyError, TypeError):
            return None

    @property
    def precipitation_probability(self) -> int | None:
        """Return the precipitation probability"""
        try:
            return int(self.coordinator.data.rain["precipitation_probability"])
        except (ValueError, KeyError, TypeError):
            return None

    @property
    def native_wind_speed(self) -> int | None:
        """Return the wind speed"""
        try:
            return int(self.coordinator.data.wind["wind_speed"])
        except (ValueError, KeyError, TypeError):
            return None

    @property
    def wind_bearing(self) -> int | None:
        """Return the wind bearing"""
        try:
            return self.coordinator.data.wind["wind_direction"]
        except (ValueError, KeyError, TypeError):
            return None

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        try:
            forecasts: list[Forecast] = []
            
            forecast = {
                "datetime": datetime.now().date().isoformat(),
                "condition": self.coordinator.data.status.get("condition"),
                "native_temperature": float(self.coordinator.data.temperature["temperature"]), 
                "native_precipitation": float(self.coordinator.data.rain["precipitation"]),
                "precipitation_probability": int(self.coordinator.data.rain["precipitation_probability"])
            }

            forecasts.append(forecast)
            _LOGGER.debug("Yerushamayim forecasts: %s", forecasts)
            return forecasts

        except Exception:
            return None