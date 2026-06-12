from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import AUTH_URL, CONF_DEVICE_ID, CONF_EMAIL, CONF_PASSWORD, DOMAIN, REST_HOST

STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DEVICE_ID): str,
    }
)


class RobomowConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            error = await self._validate(user_input)
            if error is None:
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Robomow {user_input[CONF_DEVICE_ID]}",
                    data=user_input,
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_SCHEMA,
            errors=errors,
        )

    async def _validate(self, data: dict[str, Any]) -> str | None:
        """Return an error key string, or None on success."""
        try:
            async with aiohttp.ClientSession() as session:
                # 1. Authenticate
                async with session.post(
                    AUTH_URL,
                    json={"email": data[CONF_EMAIL], "password": data[CONF_PASSWORD]},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    auth = await resp.json(content_type=None)

                if auth.get("ErrorCode") != 0 or not auth.get("AccessToken"):
                    return "invalid_auth"

                token = auth["AccessToken"]

                # 2. Verify device ID
                url = (
                    f"https://{REST_HOST}/Prod/api/V6/1/device"
                    f"/{data[CONF_DEVICE_ID]}/get-on-connection-data"
                )
                async with session.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    device = await resp.json(content_type=None)

                if device.get("errorCode") is not None:
                    return "invalid_device_id"

        except aiohttp.ClientError:
            return "cannot_connect"

        return None
