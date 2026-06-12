import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    AUTH_URL,
    CONF_DEVICE_ID,
    CONF_EMAIL,
    CONF_PASSWORD,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    REST_HOST,
)

_LOGGER = logging.getLogger(__name__)

TOKEN_INVALID_CODE = 17  # Robomow errorCode: token expired/invalid


class RobomowCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._email     = entry.data[CONF_EMAIL]
        self._password  = entry.data[CONF_PASSWORD]
        self._device_id = entry.data[CONF_DEVICE_ID]
        self._token: str | None = None
        self._session: aiohttp.ClientSession | None = None

    @property
    def device_id(self) -> str:
        return self._device_id

    # ── session ────────────────────────────────────────────────────────────────

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # ── auth ───────────────────────────────────────────────────────────────────

    async def _login(self) -> None:
        session = self._ensure_session()
        async with session.post(
            AUTH_URL,
            json={"email": self._email, "password": self._password},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            data = await resp.json(content_type=None)
        if data.get("ErrorCode") != 0 or not data.get("AccessToken"):
            raise UpdateFailed(f"Robomow authentication failed: {data.get('Message')}")
        self._token = data["AccessToken"]
        _LOGGER.debug("Token refreshed")

    # ── polling ────────────────────────────────────────────────────────────────

    async def _get_dashboard(self) -> dict:
        session = self._ensure_session()
        url = (
            f"https://{REST_HOST}/Prod/api/V6/1/device/{self._device_id}/get-dashboard"
        )
        async with session.get(
            url,
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            data = await resp.json(content_type=None)

        if data.get("errorCode") == TOKEN_INVALID_CODE:
            _LOGGER.debug("Token expired, refreshing")
            await self._login()
            return await self._get_dashboard()

        # errorCode 30 = DeviceActiveSession (another MQTT session holds the lock).
        # get-dashboard is read-only and shouldn't hit this, but if it does, keep
        # the last known data rather than marking entities unavailable.
        if data.get("errorCode") == 30:
            _LOGGER.warning("Robomow API returned errorCode 30 (active session) on dashboard poll — retaining last data")
            return self.data or {}

        if data.get("errorCode") is not None:
            raise UpdateFailed(
                f"Robomow API error {data['errorCode']}: {data.get('errorMessage')}"
            )

        return data

    async def _async_update_data(self) -> dict:
        try:
            if self._token is None:
                await self._login()
            return await self._get_dashboard()
        except UpdateFailed:
            raise
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Cannot reach Robomow cloud: {err}") from err
