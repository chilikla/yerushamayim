"""Data coordinator for Yerushamayim integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict
import json

from homeassistant.components.rest.data import RestData
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    URL,
    SCAN_INTERVAL,
    JSON_API,
    COLDMETER_API,
    ALERTS_PAGE,
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class YerushamayimData:
    """Class to hold Yerushamayim data."""
    temperature: Dict[str, Any]
    humidity: Dict[str, Any]
    status: Dict[str, Any]
    forecast: Dict[str, Any]
    precipitation: Dict[str, Any]
    wind: Dict[str, Any]

class YerushamayimDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Yerushamayim data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Yerushamayim Weather",
            update_interval=SCAN_INTERVAL,
        )
        
        # Initialize REST clients
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        self.json_api = RestData(
            hass=hass,
            method="GET",
            resource=JSON_API,
            encoding="UTF-8",
            auth=None,
            headers=headers,
            params=None,
            data=None,
            verify_ssl=False,
            ssl_cipher_list="python_default",
            timeout=30
        )

        self.coldmeter_api = RestData(
            hass=hass,
            method="GET",
            resource=COLDMETER_API,
            encoding="UTF-8",
            auth=None,
            headers=headers,
            params=None,
            data=None,
            verify_ssl=False,
            ssl_cipher_list="python_default",
            timeout=30
        )
        
        self.alerts = RestData(
            hass=hass,
            method="GET",
            resource=ALERTS_PAGE,
            encoding="UTF-8",
            auth=None,
            headers=headers,
            params=None,
            data=None,
            verify_ssl=False,
            ssl_cipher_list="python_default",
            timeout=30
        )

    async def _async_update_data(self) -> YerushamayimData:
        """Fetch data from Yerushamayim."""
        try:
            await self.json_api.async_update(False)
        except Exception as err:
            _LOGGER.error("Error updating from JSON API: %s", err)
            raise PlatformNotReady("Failed to fetch JSON API data") from err

        if self.json_api.data is None:
            raise PlatformNotReady("JSON API data is None")

        try:
            await self.coldmeter_api.async_update(False)
        except Exception as err:
            _LOGGER.warning("Error updating from coldmeter API: %s", err)
            # Don't raise here as we can continue with partial data
            
        try:
            await self.alerts.async_update(False)
        except Exception as err:
            _LOGGER.warning("Error updating from alerts page: %s", err)
            # Don't raise here as we can continue with partial data

        try:
            return await self.hass.async_add_executor_job(self._extract_data)
        except Exception as err:
            _LOGGER.error("Error extracting data: %s", err)
            raise

    def _extract_data(self) -> YerushamayimData:
        """Extract data from API responses."""
        try:
            data = json.loads(self.json_api.data)
            jws = data.get("jws", {})
            current = jws.get("current", {})
            forecast_days = jws.get("forecastDays", [])
            today_forecast = forecast_days[0] if forecast_days else {}
        except Exception as err:
            _LOGGER.error("Failed to parse JSON API data: %s", err)
            raise PlatformNotReady("Failed to parse JSON API data") from err

        # Temperature data
        temp_data = {
            "temperature": current.get("temp", ""),
        }

        # Add apparent temperature (feels like)
        if current.get("thw"):
            temp_data["apparent_temperature"] = current["thw"]
        elif current.get("heatidx"):
            temp_data["apparent_temperature"] = current["heatidx"]
        elif current.get("windchill"):
            temp_data["apparent_temperature"] = current["windchill"]

        # Humidity data
        humidity_data = {
            "humidity": current.get("hum", ""),
        }

        # Status data
        status_data = {
            "condition": "unknown",
        }

        # Add coldmeter data if available
        if self.coldmeter_api is not None and self.coldmeter_api.data:
            try:
                coldmeter = json.loads(self.coldmeter_api.data)
                status_data.update({
                    "status": coldmeter["coldmeter"]["current_feeling"],
                    "cloth_icon": URL + "images/clothes/" + coldmeter["coldmeter"]["cloth_name"],
                    "cloth_info": coldmeter["coldmeter"]["clothtitle"],
                    "laundry": coldmeter.get("laundryidx", {}).get("laundry_con_title", None)
                })
            except Exception as err:
                _LOGGER.debug("Could not parse coldmeter data: %s", err)

        # Precipitation data
        precipitation_data = {
            "precipitation": current.get("rainrate", "0"),
            "precipitation_probability": current.get("rainchance", "0"),
        }

        # Wind data
        wind_data = {
            "wind_speed": current.get("windspd", "0"),
            "wind_direction": current.get("winddir", ""),
        }

        # Forecast data from today's forecast
        forecast_data = {}
        if today_forecast:
            forecast_data.update({
                "morning_temp": today_forecast.get("TempLow", ""),
                "morning_cloth_icon": URL + today_forecast.get("TempLowCloth", ""),
                "morning_cloth_info": today_forecast.get("TempLowClothTitle1", ""),
                "noon_temp": today_forecast.get("TempHigh", ""),
                "noon_cloth_icon": URL + today_forecast.get("TempHighCloth", ""),
                "noon_cloth_info": today_forecast.get("TempHighClothTitle1", ""),
                "night_temp": today_forecast.get("TempNight", ""),
                "night_cloth_icon": URL + today_forecast.get("TempNightCloth", ""),
                "night_cloth_info": today_forecast.get("TempNightClothTitle1", ""),
            })
            status_data.update({
                "forecast": today_forecast.get("lang1", ""),
            })

        return YerushamayimData(
            temperature=temp_data,
            humidity=humidity_data,
            status=status_data,
            forecast=forecast_data,
            precipitation=precipitation_data,
            wind=wind_data
        )