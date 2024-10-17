"""Support for YBC sensors."""
from __future__ import annotations

import logging
import voluptuous as vol
from typing import Any, Optional
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import BinarySensorEntity, SensorStateClass, SensorDeviceClass, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.typing import StateType
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from homeassistant.util import dt as dt_util
from .const import (
    DOMAIN
)

from .ybc_update_coordinator import YBCUpdateCoordinator
from .entity import YBCBaseEntity

_LOGGER = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
@dataclass(frozen=True, kw_only=True)
class YBCBinarySensorEntityDescription(SensorEntityDescription):
    """Describes YBC sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType]

SENSORS = (
    YBCBinarySensorEntityDescription(
        key="collection_due_today",
        translation_key="collection_due_today",
        value_fn=lambda data: datetime.today().date() == datetime.strptime(data.lastCollected, DATETIME_FORMAT).date(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up YBC sensor platform."""
    coordinator: YBCUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        YBCSensor(
            coordinator,
            entity_description,
            index,
            service.service
        )
        for entity_description in SENSORS
        for index, service in coordinator.data.items()
    ]

    async_add_entities(sensors) 

class YBCSensor(YBCBaseEntity, BinarySensorEntity):
    """Representation of a YBC sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entity_description,
        idx,
        device_model: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, idx, device_model)

        self.entity_description = entity_description

        self._attr_unique_id = f"{self.idx}_{self.entity_description.key}"

    @property
    def is_on(self) -> StateType:
        """Return the state."""

        try:
            state = self.entity_description.value_fn(self.data)
        except (KeyError, ValueError):
            return None

        return state