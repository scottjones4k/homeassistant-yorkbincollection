"""The YBC integration."""
from __future__ import annotations

import secrets
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_TOKEN
from homeassistant.core import HomeAssistant

from .const import DOMAIN, API_ENDPOINT
from .ybc_update_coordinator import YBCUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up YBC from a config entry."""
    uprn: str = entry.data[CONF_TOKEN]

    websession = async_get_clientsession(hass)
    client = YBCClient(API_ENDPOINT, websession, uprn)
    coordinator = YBCUpdateCoordinator(hass, client)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True