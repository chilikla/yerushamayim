from __future__ import annotations

import logging
import traceback
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
import json

from homeassistant.components.rest.data import RestData
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
    PRESSURE_HPA,
    SPEED_METERS_PER_SECOND,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    URL,
    COLDMETER_API,
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class YerushamayimData:
    temperature: Dict[str, Any]
    humidity: Dict[str, Any]
    # pressure: str
    # wind_speed: str
    # wind_direction: str
    status: Dict[str, Any]

class YerushamayimDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, site: RestData, coldmeter_api: RestData):
        super().__init__(
            hass,
            _LOGGER,
            name="Yerushamayim Weather",
            update_interval=SCAN_INTERVAL,
        )
        self.site = site
        self.coldmeter_api = coldmeter_api

    async def _async_update_data(self):
        await self.site.async_update(False)
        await self.coldmeter_api.async_update(False)

        if self.site.data is None:
            raise PlatformNotReady("Yerushamayim site data not available")

        try:
            return await self.hass.async_add_executor_job(self._extract_data)
        except Exception as err:
            raise Exception(f"Error extracting Yerushamayim data: {err}")

    def _extract_data(self) -> YerushamayimData:
        content = BeautifulSoup(self.site.data, "html.parser")

        latest_now = content.select("div#latestnow")[0]
        temperature = latest_now.find(id="tempdivvalue").get_text().strip().replace("C", "").replace("°", "")

        latest_humidity = content.select("div#latesthumidity")[0]
        humidity = latest_humidity.select("div.paramvalue :first-child")[0].get_text().strip().replace("%", "")

        forecast_line = content.select("ul#forcast_table li:nth-child(2) ul")[0]
        day_icon = forecast_line.select(".icon_day img")[0]["src"]
        condition = day_icon.replace("images/icons/day/n4_", "").replace(".svg", "")

        # Extract pressure, wind_speed, and wind_direction similarly
        # For this example, I'm using placeholder values
        pressure = "1013"
        wind_speed = "5"
        wind_direction = "N"

        return YerushamayimData(
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            condition=condition
        )

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    site = RestData(hass, "GET", URL, "UTF-8", None, None, None, None, False, "python_default")
    coldmeter_api = RestData(hass, "GET", COLDMETER_API, "UTF-8", None, None, None, None, False, "python_default")

    coordinator = YerushamayimDataCoordinator(hass, site, coldmeter_api)
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        YerushamayimTemperatureSensor(coordinator),
        YerushamayimHumiditySensor(coordinator),
        # YerushamayimPressureSensor(coordinator),
        # YerushamayimWindSpeedSensor(coordinator),
        # YerushamayimWindDirectionSensor(coordinator),
        YerushamayimConditionSensor(coordinator),
    ]

    async_add_entities(sensors, True)

class YerushamayimBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: YerushamayimDataCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{self.sensor_type}"
        self._attr_name = f"{DOMAIN}_{self.sensor_type}"

    @property
    def sensor_type(self) -> str:
        raise NotImplementedError

    @property
    def native_value(self):
        return getattr(self.coordinator.data, self.sensor_type)

class YerushamayimTemperatureSensor(YerushamayimBaseSensor):
    sensor_type = "temperature"

    @property
    def name(self):
        return "Yerushamayim Temperature"

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        return TEMP_CELSIUS

class YerushamayimHumiditySensor(YerushamayimBaseSensor):
    sensor_type = "humidity"

    @property
    def name(self):
        return "Yerushamayim Humidity"

    @property
    def device_class(self):
        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        return PERCENTAGE

# Implement other sensor classes (Pressure, Wind Speed, Wind Direction, Condition) similarly

class YerushamayimStatusSensor(YerushamayimBaseSensor):
    sensor_type = "condition"
    
    @property
    def _attr_name(self):
        return f"{DOMAIN}_condition"

# Implement other sensor classes as needed