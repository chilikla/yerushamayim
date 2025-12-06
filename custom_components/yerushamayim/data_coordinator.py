"""Data coordinator for Yerushamayim integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict
import json
from datetime import datetime as dt
from bs4 import BeautifulSoup
import re

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
    forecast: list[Dict[str, Any]]
    precipitation: Dict[str, Any]
    wind: Dict[str, Any]
    alerts: list[dict]


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
            timeout=30,
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
            timeout=30,
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
            timeout=30,
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

        # Status data with enhanced recommendations parsing
        status_data = {}

        # Add coldmeter data if available
        if self.coldmeter_api is not None and self.coldmeter_api.data:
            try:
                coldmeter = json.loads(self.coldmeter_api.data)
                status_data.update(
                    {
                        "status": coldmeter["coldmeter"]["current_feeling"],
                        "cloth_icon": URL
                        + "images/clothes/"
                        + coldmeter["coldmeter"]["cloth_name"],
                        "cloth_info": coldmeter["coldmeter"]["clothtitle"],
                        "laundry": coldmeter["laundryidx"]["laundry_con_title"]
                    }
                )
            except Exception as err:
                _LOGGER.debug("Could not parse coldmeter data: %s", err)

        # Parse recommendations
        recommendations = current.get("recommendations", [])
        event_outside = next(
            (r for r in recommendations if r.get("activity") == "EVENTOUTSIDE"), {}
        )
        status_data.update(
            {
                "recommendation": (
                    event_outside.get("sig1", "").strip()
                    if event_outside.get("sig1")
                    else "Unavailable"
                ),
            }
        )

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

        # Forecast data from all forecast days
        forecast_data = []
        for day_forecast in forecast_days:
            status = re.sub(r'<[^>]+>', '', day_forecast.get("lang1", ""))
            status = ' '.join(status.split())
            forecast_item = {
                "date": day_forecast.get("date", ""),
                "day_name_eng": day_forecast.get("day_name0", ""),
                "day_name_heb": day_forecast.get("day_name1", "").strip(),
                "icon": URL + day_forecast.get("icon", ""),
                "morning_temp": day_forecast.get("TempLow", ""),
                "morning_cloth_icon": URL + day_forecast.get("TempLowCloth", ""),
                "morning_cloth_info": day_forecast.get("TempLowClothTitle1", ""),
                "noon_temp": day_forecast.get("TempHigh", ""),
                "noon_cloth_icon": URL + day_forecast.get("TempHighCloth", ""),
                "noon_cloth_info": day_forecast.get("TempHighClothTitle1", ""),
                "night_temp": day_forecast.get("TempNight", ""),
                "night_cloth_icon": URL + day_forecast.get("TempNightCloth", ""),
                "night_cloth_info": day_forecast.get("TempNightClothTitle1", ""),
                "status": status,
            }
            forecast_data.append(forecast_item)

        alerts = []
        try:
            if self.alerts.data is None:
                _LOGGER.warning("Alerts data is None")
            else:
                alerts_content = BeautifulSoup(self.alerts.data, "html.parser")
                _LOGGER.debug("Alerts HTML parsed successfully")
                article = alerts_content.find("article")

                if not article:
                    _LOGGER.warning("No article element found in alerts page")
                else:
                    # Find all alert divs
                    alert_divs = article.find_all("div", class_="inv_plain_3")
                    _LOGGER.debug("Found %d alert divs", len(alert_divs))

                    for alert_div in alert_divs:
                        # Extract title from h1
                        h1 = alert_div.find("h1")
                        title = h1.get_text(strip=True) if h1 else ""

                        # Extract date from label
                        label = alert_div.find("label")
                        date = label.get_text(strip=True) if label else None

                        # Extract description from the inner div
                        inner_div = alert_div.find("div", style=lambda value: value and "padding:0em" in value)
                        description = inner_div.get_text(strip=True) if inner_div else ""

                        if title:  # Only add if we have at least a title
                            alert = {
                                "title": title,
                                "date": date,
                                "description": description if description else title,
                            }
                            alerts.append(alert)

                    _LOGGER.debug("Extracted %d alerts", len(alerts))
        except Exception as err:
            _LOGGER.warning("Error parsing alerts HTML: %s", err)

        return YerushamayimData(
            temperature=temp_data,
            humidity=humidity_data,
            status=status_data,
            forecast=forecast_data,
            precipitation=precipitation_data,
            wind=wind_data,
            alerts=alerts,
        )
