from __future__ import annotations

import logging
import traceback

from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import json

from homeassistant.components.rest.data import RestData
from homeassistant.components.sensor import (
  CONF_STATE_CLASS,
  DEVICE_CLASSES_SCHEMA,
  PLATFORM_SCHEMA,
  STATE_CLASSES_SCHEMA,
  SensorEntity,
)
from homeassistant.const import (
  CONF_AUTHENTICATION,
  CONF_DEVICE_CLASS,
  CONF_HEADERS,
  CONF_NAME,
  CONF_PASSWORD,
  CONF_RESOURCE,
  CONF_UNIT_OF_MEASUREMENT,
  CONF_USERNAME,
  CONF_VALUE_TEMPLATE,
  CONF_VERIFY_SSL,
  HTTP_BASIC_AUTHENTICATION,
  HTTP_DIGEST_AUTHENTICATION,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "yerushamayim"
SCAN_INTERVAL = timedelta(seconds=180)
URL = "https://www.02ws.co.il/"
API = URL + "coldmeter_service.php?lang=1&json=1&cloth_type=e"

async def async_setup_platform(
  hass: HomeAssistant,
  config: ConfigType,
  async_add_entities: AddEntitiesCallback,
  discovery_info: DiscoveryInfoType | None = None,
) -> None:
  site = RestData(hass, "GET", URL, "UTF-8", None, None, None, None, False, "python_default")
  await site.async_update(False)
  api = RestData(hass, "GET", API, "UTF-8", None, None, None, None, False, "python_default")
  await api.async_update(False)

  if site.data is None:
    raise PlatformNotReady

  async_add_entities([Yerushamayim(hass, site, api)], True)

class Yerushamayim(SensorEntity):
  def __init__(self, hass, site, api):
    self._hass = hass
    self.site = site
    self.api = api
    self._attr_name = "yerushamayim"
    self._state = None
    self._attrs: dict[str, str] = {}

  @property
  def native_value(self):
    """Return the state of the device."""
    return self._state

  @property
  def extra_state_attributes(self) -> dict[str, str]:
    """Return the state attributes."""
    return self._attrs

  def getDayPart(self, data, forecast_line, time):
    part = forecast_line.select(".forcast_" + time + " .line:nth-child(1)")[0]
    temp = part.select(".number")[0].get_text()
    cloth = part.select(".cloth img")[0]
    cloth_icon = URL + cloth["src"]
    cloth_info = cloth["title"]
    data[time + "_temp"] = temp
    data[time + "_cloth_icon"] = cloth_icon
    data[time + "_cloth_info"] = cloth_info
    return data

  def _extract_value(self):
    data = {}
    content = BeautifulSoup(self.site.data, "html.parser")

    # top information
    latest_now = content.select("div#latestnow")[0]
    current_temp = latest_now.find(id="tempdivvalue").get_text().strip().replace("C", "").replace("°", "")
    data["current_temp"] = current_temp

    it_feels_anchor_children = latest_now.select("#itfeels a")
    it_feels_css_selector = "#itfeels #itfeels_windchill span.value"
    if len(it_feels_anchor_children) == 1:
      it_feels_css_selector = "#itfeels span.value"
    elif len(it_feels_anchor_children) == 0:
      it_feels_css_selector = None
    if it_feels_css_selector:
      try:
        feels_like_temp = latest_now.select(it_feels_css_selector)[0].get_text().replace("°", "")
        data["feels_like_temp"] = feels_like_temp
        if (len(latest_now.select("#itfeels #itfeels_thsw")) > 0):
          feels_like_temp_sun = latest_now.select("#itfeels #itfeels_thsw span.value")[0].get_text()
          data["feels_like_temp_sun"] = feels_like_temp_sun
      except IndexError:
        # no feels like attributes
        _LOGGER.debug("Feels like attributes could not retrieved in Yerushamayim")

    if self.api is not None and self.api.data:
      coldmeter = json.loads(self.api.data)
      data["status_title"] = coldmeter["coldmeter"]["current_feeling"]
      data["status_icon"] = URL + "images/clothes/" + coldmeter["coldmeter"]["cloth_name"]
      data["status_icon_info"] = coldmeter["coldmeter"]["clothtitle"]
      data["laundry"] = coldmeter.get("laundryidx", {}).get("laundry_con_title", None)

    # bottom infromation
    forecast_line = content.select("ul#forcast_table li:nth-child(2) ul")[0]

    forecast_text = forecast_line.select(".forcast_text")[0].get_text()
    forecast_text_child = forecast_line.select(".forcast_text  .likedislike")[0].get_text()
    forecast_text = forecast_text.replace(forecast_text_child, "").strip().replace("\n", "")
    data["forecast_text"] = forecast_text
    day_icon = forecast_line.select(".icon_day img")[0]["src"]
    data["day_icon"] = URL + day_icon
    data = self.getDayPart(data, forecast_line, "morning")
    data = self.getDayPart(data, forecast_line, "noon")
    data = self.getDayPart(data, forecast_line, "night")

    return data

  async def async_update(self):
    """Get the latest data from the source and updates the state."""
    await self.site.async_update(False)
    await self.api.async_update(False)
    await self._async_update_from_rest_data()

  async def async_added_to_hass(self):
    """Ensure the data from the initial update is reflected in the state."""
    await self._async_update_from_rest_data()

  async def _async_update_from_rest_data(self):
    """Update state from the rest data."""
    if self.site.data is None:
      _LOGGER.error("Yerushamayim wasn't available")
      return

    try:
      value = await self.hass.async_add_executor_job(self._extract_value)
    except IndexError:
      _LOGGER.error("Unable to extract data from HTML for Yerushamayim: " + traceback.format_exc())
      self._state = "unavailable"
      return

    self._state = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    self._attrs = value
