import secrets
import logging

from typing import Any

from aiohttp import ClientResponse
from .models.service import Service

_LOGGER = logging.getLogger(__name__)

class YBCClient:
    def __init__(self, host: str, session, uprn: str):
        self._host = host
        self._session = session
        self._uprn = uprn
    
    async def make_request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        response = await self._session.request(
            method, f"{self._host}/{url}", **kwargs, headers=headers,
        )
        return await response.json()

    async def async_get_services(self) -> list[Service]:
        data = await self.make_request("GET", f"Collections/GetBinCollectionDataForUprn/{self._uprn}")
        try:
            services = [Service(**a) for a in data['services']]
        except KeyError:
            _LOGGER.error("Failed to get services from Waste API: %s", str(data))
            _raise_auth_or_response_error(data)
        return services