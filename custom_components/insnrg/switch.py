"""Switch platform for the Insnrg Pool integration."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import InsnrgPoolEntity
from .const import DOMAIN
from .polling_mixin import PollingMixin
import logging
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Defer switch setup to the shared switch module."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    # We are looking for the 'VF Contact - Heat Pump' which has deviceId 'VF_SETTING_SET_HEATER_MODE'
    if "VF_SETTING_SET_HEATER_MODE" in coordinator.data:
        heater_device = coordinator.data["VF_SETTING_SET_HEATER_MODE"]
        description = SwitchEntityDescription(
            key="VF_SETTING_SET_HEATER_MODE",
            name=heater_device["name"],
        )
        entities.append(
            InsnrgPoolSwitch(
                coordinator, config_entry.data[CONF_EMAIL], description, "VF_SETTING_SET_HEATER_MODE", hass
            )
        )

    async_add_entities(entities, True)


class InsnrgPoolSwitch(InsnrgPoolEntity, SwitchEntity, PollingMixin):
    """Switch representing Insnrg Pool data."""

    def __init__(self, coordinator, email, description, device_id, hass):
        """Initialize Insnrg Pool switch."""
        super().__init__(coordinator, email, description)
        self._device_id = device_id
        self.hass = hass # Required for polling mixin
        # Initialize _attr_is_on based on current coordinator data
        self._attr_is_on = self.coordinator.data[self._device_id].get("switchStatus") == "ON"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        # Always return _attr_is_on for optimistic updates
        return self._attr_is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        # Optimistic update
        self._attr_is_on = True
        self.async_write_ha_state()

        success = await self.coordinator.insnrg_pool.turn_the_switch(
            "ON", self._device_id
        )
        if success:
            # Pass a lambda that checks the actual coordinator data
            poll_success = await self._async_poll_for_state_change(self, "ON", 
                lambda: self.coordinator.data[self._device_id].get("switchStatus"), "switchStatus")
            if not poll_success:
                # Revert if polling failed, get actual state from coordinator
                self._attr_is_on = self.coordinator.data[self._device_id].get("switchStatus") == "ON"
                self.async_write_ha_state()
        else:
            _LOGGER.error(f"Failed to turn ON {self.entity_id}.")
            # Revert if command failed, get actual state from coordinator
            self._attr_is_on = self.coordinator.data[self._device_id].get("switchStatus") == "ON"
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        # Optimistic update
        self._attr_is_on = False
        self.async_write_ha_state()

        success = await self.coordinator.insnrg_pool.turn_the_switch(
            "OFF", self._device_id
        )
        if success:
            # Pass a lambda that checks the actual coordinator data
            poll_success = await self._async_poll_for_state_change(self, "OFF", 
                lambda: self.coordinator.data[self._device_id].get("switchStatus"), "switchStatus")
            if not poll_success:
                # Revert if polling failed, get actual state from coordinator
                self._attr_is_on = self.coordinator.data[self._device_id].get("switchStatus") == "ON"
                self.async_write_ha_state()
        else:
            _LOGGER.error(f"Failed to turn OFF {self.entity_id}.")
            # Revert if command failed, get actual state from coordinator
            self._attr_is_on = self.coordinator.data[self._device_id].get("switchStatus") == "ON"
            self.async_write_ha_state()