"""Data coordinator for Yerushamayim integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict

from bs4 import BeautifulSoup
import json

from homeassistant.components.rest.data import RestData
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    URL,
    COLDMETER_API,
    REST_API
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class YerushamayimData:
    """Class to hold Yerushamayim data."""
    temperature: Dict[str, Any]
    humidity: Dict[str, Any]
    status: Dict[str, Any]
    forecast: Dict[str, Any]
    rain: Dict[str, Any]
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
        rest_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        
        _LOGGER.debug("Initializing site API with URL: %s", URL)
        self.site = RestData(
            hass=hass,
            method="GET",
            resource=URL,
            encoding="UTF-8",
            auth=None,
            headers=headers,
            params=None,
            data=None,
            verify_ssl=False,
            ssl_cipher_list="python_default",
            timeout=30
        )

        _LOGGER.debug("Initializing coldmeter API with URL: %s", COLDMETER_API)
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

        _LOGGER.debug("Initializing REST API with URL: %s", REST_API)
        self.rest_api = RestData(
            hass=hass,
            method="GET",
            resource=REST_API,
            encoding="UTF-8",
            auth=None,
            headers=rest_headers,
            params=None,
            data=None,
            verify_ssl=False,
            ssl_cipher_list="python_default",
            timeout=30
        )
        
        # self.site = RestData(
        #     hass,
        #     "GET",
        #     URL,
        #     "UTF-8",
        #     None,
        #     None,
        #     generic_headers,
        #     None,
        #     False,
        #     "python_default"
        # )
        
        # self.coldmeter_api = RestData(
        #     hass,
        #     "GET",
        #     COLDMETER_API,
        #     "UTF-8",
        #     None,
        #     None,
        #     generic_headers,
        #     None,
        #     False,
        #     "python_default"
        # )

        # self.rest_api = RestData(
        #     hass=hass,
        #     method="GET",
        #     resource=REST_API,
        #     encoding="UTF-8",
        #     username=None,
        #     password=None,
        #     headers=rest_headers,
        #     auth=None,
        #     verify_ssl=False,
        #     timeout=30
        # )

        _LOGGER.debug("Initialized REST API with URL: %s and headers: %s", REST_API, rest_headers)

    async def _async_update_data(self) -> YerushamayimData:
        """Fetch data from Yerushamayim."""
        try:
            await self.site.async_update(False)
        except Exception as err:
            _LOGGER.error("Error updating from site: %s", err)
            raise PlatformNotReady("Failed to fetch site data") from err

        if self.site.data is None:
            raise PlatformNotReady("Site data is None")

        try:
            await self.coldmeter_api.async_update(False)
        except Exception as err:
            _LOGGER.warning("Error updating from coldmeter API: %s", err)
            # Don't raise here as we can continue with partial data

        try:
            _LOGGER.debug("Attempting to fetch REST API data from: %s", URL)
            await self.rest_api.async_update(False)
            _LOGGER.debug("REST API response received. Data exists: %s", self.rest_api.data is not None)
            if self.rest_api.data is not None:
                _LOGGER.debug("REST API data length: %d", len(self.rest_api.data))
        except Exception as err:
            _LOGGER.error("Error updating from REST API: %s", err)
            # raise PlatformNotReady("Failed to fetch site data") from err

        if self.rest_api.data is None:
            _LOGGER.error("Site data is None. URL: %s, Headers: %s", URL, self.rest_api.headers)
            # raise PlatformNotReady("Site data is None")

        # try:
        #     await self.rest_api.async_update(False)
        # except Exception as err:
        #     _LOGGER.warning("Error updating from REST API: %s", err)
        #     # Don't raise here as we can continue with partial data

        try:
            return await self.hass.async_add_executor_job(self._extract_data)
        except Exception as err:
            _LOGGER.error("Error extracting data: %s", err)
            raise

    def _extract_data(self) -> YerushamayimData:
        """Extract data from API responses."""
        content = BeautifulSoup(self.site.data, "html.parser")

        # Temperature data
        latest_now = content.select("div#latestnow")[0]
        current_temp = latest_now.find(id="tempdivvalue").get_text().strip().replace("C", "").replace("°", "")
        temp_data = {"temperature": current_temp}  # Fixed variable name

        it_feels = latest_now.select("#itfeels")
        it_feels_css_selector = "#itfeels span.value"
        if len(it_feels[0].find_all("a")) > 2:
            it_feels_css_selector = "#itfeels #itfeels_thw span.value"
        elif not it_feels:
            it_feels_css_selector = None

        if it_feels_css_selector:
            try:
                feels_like_temp = latest_now.select(it_feels_css_selector)[0].get_text().strip().replace("°", "")
                temp_data["apparent_temperature"] = feels_like_temp
                if (len(latest_now.select("#itfeels .sun_toggle")) > 0):
                    feels_like_temp_sun = latest_now.select("#itfeels .sun_toggle span.value")[0].get_text().strip().replace("°", "")
                    temp_data["apparent_temperature_sun"] = feels_like_temp_sun
            except IndexError:
                _LOGGER.debug("Feels like attributes could not be retrieved")

        # Humidity data
        latest_humidity = content.select("div#latesthumidity")[0]
        humidity = latest_humidity.select("div.paramvalue :first-child")[0].get_text().strip().replace("%", "")
        humidity_data = {"humidity": humidity}

        # Status data
        forecast_line = content.select("ul#forcast_table li:nth-child(2) ul")[0]

        forecast_text = forecast_line.select(".forcast_text")[0].get_text()
        forecast_text_child = forecast_line.select(".forcast_text  .likedislike")[0].get_text()
        forecast_text = forecast_text.replace(forecast_text_child, "").strip().replace("\n", "")
        day_icon = forecast_line.select(".icon_day img")[0]["src"]
        condition = day_icon.replace("images/icons/day/n4_", "").replace(".svg", "")
        status_data = {"forecast": forecast_text, "day_icon": URL + day_icon, "condition": condition}

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

        rain_data = {}
        wind_data = {}
        _LOGGER.debug("REST API check - rest_api exists: %s", self.rest_api is not None)
        if self.rest_api is not None:
            _LOGGER.debug("REST API data exists: %s", bool(self.rest_api.data))
            _LOGGER.debug("REST API data type: %s", type(self.rest_api.data))
            _LOGGER.debug("REST API data content: %r", self.rest_api.data)  # Using %r for raw representation

            if self.rest_api.data:
                try:
                    _LOGGER.debug("Raw REST API data: %s", self.rest_api.data)
                    
                    rest_data = {}
                    for row in BeautifulSoup.find_all('tr'):
                        _LOGGER.debug("Processing row: %s", row)
                        columns = row.find_all('td')
                        if len(columns) >= 2:
                            # Skip the index column (columns[0]) and split the second column
                            key_value = columns[1].text.split(':')
                            if len(key_value) == 2:
                                key = key_value[0].strip()
                                value = key_value[1].strip()
                                rest_data[key] = value
                                _LOGGER.debug("Added key-value: %s = %s", key, value)

                    _LOGGER.debug("Processed REST data: %s", rest_data)

                    # Rain data
                    rain_data = {
                        "precipitation": rest_data["rainrate"], 
                        "precipitation_probability": rest_data["rainchance"]
                    }
                    _LOGGER.debug("Rain data: %s", rain_data)

                    # Wind data
                    wind_data = {"wind_speed": rest_data["windspd"]}
                    _LOGGER.debug("Wind data: %s", wind_data)

                except Exception as err:
                    _LOGGER.exception("Could not parse rest api data: %s", err)
            else:
                _LOGGER.debug("REST API data is empty or evaluates to False")
        else:
            _LOGGER.debug("REST API is None")

        # Forecast data
        forecast_data = {}
        day_parts = ["morning", "noon", "night"]
        for day_part in day_parts:  
            try:
                part = forecast_line.select(".forcast_" + day_part + " .line:nth-child(1)")[0]
                temp = part.select(".number")[0].get_text().strip()
                cloth = part.select(".cloth img")[0]
                cloth_icon = URL + cloth["src"]
                cloth_info = cloth["title"]
                forecast_data.update({
                    day_part + "_temp": temp,
                    day_part + "_cloth_icon": cloth_icon,
                    day_part + "_cloth_info": cloth_info,
                })
            except Exception as err:
                _LOGGER.debug("Could not extract forecast data for %s: %s", day_part, err)

        return YerushamayimData(
            temperature=temp_data,
            humidity=humidity_data,
            status=status_data,
            forecast=forecast_data,
            rain=rain_data,
            wind=wind_data
        )