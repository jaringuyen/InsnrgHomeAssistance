from __future__ import annotations
import asyncio
from .call_api import InsnrgPool
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import aiohttp_client
from . import InsnrgPoolEntity
from .const import DOMAIN
from .polling_mixin import PollingMixin, STARTER_ICON
import logging
_LOGGER = logging.getLogger(__name__)
KEYS_TO_CHECK = ["PH", "ORP"]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Defer number setup to the shared number module."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    number_descriptions = []
    for key in KEYS_TO_CHECK:
        if key in coordinator.data:
            name = coordinator.data[key]['name']
            if coordinator.data[key]["thermostatStatus"]["valueMax"] > 0:
                name =  f"Set {key} Point"
            number_descriptions.append(NumberEntityDescription(
                key=key,
                name=name,
            ))
    entities = [
        InsnrgPoolNumber(coordinator, hass, config_entry, description)
        for description in number_descriptions
    ]
    async_add_entities(entities, False)

class InsnrgPoolNumber(InsnrgPoolEntity, NumberEntity, PollingMixin):
    """Number entity representing Insnrg Pool data."""
    def __init__(self, coordinator, hass, entry, description):
        """Initialize Insnrg Pool number."""
        super().__init__(coordinator, entry, description)
        self.insnrg_pool = InsnrgPool(
            aiohttp_client.async_get_clientsession(hass),
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
        )
        self.hass = hass # Required for polling mixin
        # Initialize _attr_native_value based on current coordinator data
        self._attr_native_value = self.coordinator.data[self.entity_description.key]["thermostatStatus"]["setPoint"]
    
    @property
    def mode(self) -> str | None:
        """Return the mode."""
        return "slider"

    @property
    def native_max_value(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data[self.entity_description.key]["thermostatStatus"]["valueMax"]
    
    @property
    def native_min_value(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data[self.entity_description.key]["thermostatStatus"]["valueMin"]

    @property
    def native_step(self) -> float:
        """Return the unit of measurement."""
        if self.entity_description.key == "ORP":
            return 10
        else:
            return 0.1

    @property
    def native_value(self) -> float:
        """Return the current temperature."""
        # Always return _attr_native_value for optimistic updates
        return self._attr_native_value
    
    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Optimistic update
        self._attr_native_value = value
        self.async_write_ha_state()
        original_icon = getattr(self, '_attr_icon', None) # Capture original icon
        self._attr_icon = STARTER_ICON # Set starter icon
        self.async_write_ha_state()

        deviceId = self.coordinator.data[self.entity_description.key]["deviceId"]
        api_call_task = asyncio.create_task(self.insnrg_pool.set_chemistry(value, deviceId))
        
        await asyncio.sleep(1.0) # Delay for 1 second before starting clock animation

        animation_task = asyncio.create_task(self._async_animate_icon(self, original_icon))
        success = await api_call_task # Wait for the API call to complete

        if success:
            # Pass a lambda that checks the actual coordinator data
            poll_success = await self._async_poll_for_state_change(self, original_icon, value, 
                lambda: self.coordinator.data[self.entity_description.key]["thermostatStatus"]["setPoint"], entity_type="value", animation_task=animation_task)
            if not poll_success:
                # Revert if polling failed, get actual state from coordinator
                self._attr_native_value = self.coordinator.data[self.entity_description.key]["thermostatStatus"]["setPoint"]
                self.async_write_ha_state()
        else:
            _LOGGER.error(f"Failed to set the value for {self.entity_id}.")
            # Revert if command failed, get actual state from coordinator
            self._attr_native_value = self.coordinator.data[self.entity_description.key]["thermostatStatus"]["setPoint"]
            self.async_write_ha_state()