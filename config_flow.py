from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .api import HsiProxyApi
from .const import DOMAIN, CONF_BASE_URL, CONF_TOKEN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL


class HsiProxyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            token = user_input[CONF_TOKEN].strip()
            scan_interval = int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

            api = HsiProxyApi(self.hass, base_url, token)
            try:
                systems = await api.list_systems()
                if not systems:
                    errors["base"] = "no_systems"
                else:
                    # Unique per base_url+token (simple)
                    await self.async_set_unique_id(f"{base_url}|{token[:8]}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"HSI Proxy ({len(systems)} systems)",
                        data={
                            CONF_BASE_URL: base_url,
                            CONF_TOKEN: token,
                            CONF_SCAN_INTERVAL: scan_interval,
                        },
                    )
            except Exception:
                errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default="http://127.0.0.1:8000"): str,
                vol.Required(CONF_TOKEN): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HsiProxyOptionsFlowHandler(config_entry)


class HsiProxyOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): int
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
