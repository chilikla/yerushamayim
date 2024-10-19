"""Config flow for Yerushamayim integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # TODO: Add any validation logic here if needed in the future
    return {"title": "Yerushamayim Weather"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yerushamayim."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Yerushamayim Weather", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            # description_placeholders={
            #     "description": "Do you want to add Yerushamayim to Home Assistant?"
            # },
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        """Handle import step."""
        return await self.async_step_user(user_input)

    async def async_step_onboarding(
        self, data: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by onboarding."""
        return await self.async_step_user(user_input={})