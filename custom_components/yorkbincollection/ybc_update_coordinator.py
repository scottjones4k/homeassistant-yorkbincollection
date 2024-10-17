"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

import async_timeout

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .api.client import YBCClient

_LOGGER = logging.getLogger(__name__)

class YBCUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client: YBCClient):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="YBC",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=30),
        )
        self._client = client

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # try:
        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with async_timeout.timeout(10):
            result = await self._client.async_get_services()
        # except ApiAuthError as err:
        #     # Raising ConfigEntryAuthFailed will cancel future updates
        #     # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #     raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #     raise UpdateFailed(f"Error communicating with API: {err}")
        lookup_table = {}
        for service in result:
            lookup_table[service.service] = service
        
        return lookup_table