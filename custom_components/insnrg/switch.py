"""Switch platform for the Insnrg Pool integration."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import asyncio

from . import InsnrgPoolEntity
from .const import DOMAIN
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
        current_status = self.coordinator.data[self._device_id].get("switchStatus")
        _LOGGER.debug(f"VF Contact - Heat Pump switchStatus: {current_status}")
        return current_status == "ON"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        success = await self.coordinator.insnrg_pool.turn_the_switch(
            "ON", self._device_id
        )
        if success:
            _LOGGER.debug(f"Attempting to turn ON {self.entity_id}. Polling for state change...")
            target_state = "ON"
            polling_timeout = 300  # seconds (5 minutes)
            polling_interval = 5  # seconds
            start_time = self.hass.loop.time()

            while self.hass.loop.time() - start_time < polling_timeout:
                await self.coordinator.async_request_refresh()
                current_status = self.coordinator.data[self._device_id].get("switchStatus")
                _LOGGER.debug(f"Polling {self.entity_id}. Current switchStatus: {current_status}, Target: {target_state}")
                if current_status == target_state:
                    _LOGGER.debug(f"{self.entity_id} successfully turned ON and state confirmed.")
                    return
                await asyncio.sleep(polling_interval)
            _LOGGER.warning(f"Timeout: {self.entity_id} did not report {target_state} within {polling_timeout} seconds.")
        else:
            _LOGGER.error(f"Failed to turn ON {self.entity_id}.")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        success = await self.coordinator.insnrg_pool.turn_the_switch(
            "OFF", self._device_id
        )
        if success:
            _LOGGER.debug(f"Attempting to turn OFF {self.entity_id}. Polling for state change...")
            target_state = "OFF"
            polling_timeout = 300  # seconds (5 minutes)
            polling_interval = 5  # seconds
            start_time = self.hass.loop.time()

            while self.hass.loop.time() - start_time < polling_timeout:
                await self.coordinator.async_request_refresh()
                current_status = self.coordinator.data[self._device_id].get("switchStatus")
                _LOGGER.debug(f"Polling {self.entity_id}. Current switchStatus: {current_status}, Target: {target_state}")
                if current_status == target_state:
                    _LOGGER.debug(f"{self.entity_id} successfully turned OFF and state confirmed.")
                    return
                await asyncio.sleep(polling_interval)
            _LOGGER.warning(f"Timeout: {self.entity_id} did not report {target_state} within {polling_timeout} seconds.")
        else:
            _LOGGER.error(f"Failed to turn OFF {self.entity_id}.")
