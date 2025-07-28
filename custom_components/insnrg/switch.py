"""Switch platform for the Insnrg Pool integration."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import InsnrgPoolEntity
from .const import DOMAIN


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
                coordinator, config_entry.data[CONF_EMAIL], description, "VF_SETTING_SET_HEATER_MODE"
            )
        )

    async_add_entities(entities, True)


class InsnrgPoolSwitch(InsnrgPoolEntity, SwitchEntity):
    """Switch representing Insnrg Pool data."""

    def __init__(self, coordinator, email, description, device_id):
        """Initialize Insnrg Pool switch."""
        super().__init__(coordinator, email, description)
        self._device_id = device_id

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data[self._device_id].get("switchStatus") == "ON"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        success = await self.coordinator.insnrg_pool.turn_the_switch(
            "ON", self._device_id
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        success = await self.coordinator.insnrg_pool.turn_the_switch(
            "OFF", self._device_id
        )
        if success:
            await self.coordinator.async_request_refresh()
