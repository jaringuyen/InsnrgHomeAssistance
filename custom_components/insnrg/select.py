from __future__ import annotations
import asyncio
from .call_api import InsnrgPool
from .exceptions import InsnrgPoolError
from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import aiohttp_client
from . import InsnrgPoolEntity
from .const import DOMAIN
import logging
_LOGGER = logging.getLogger(__name__)
KEYS_TO_CHECK = [
    "SPA",
    "MODE",
    "TIMERS",
    "OUTLET_1",
    "OUTLET_2",
    "OUTLET_3",
    "OUTLET_HUB_3",
    "OUTLET_HUB_4",
    "OUTLET_HUB_5",
    "OUTLET_HUB_6",
    "VALVE_1",
    "VALVE_2",
    "VALVE_3",
    "VALVE_HUB_1",
    "VALVE_HUB_2",
    "VALVE_HUB_3",
    "VALVE_HUB_4",
    "LIGHT_MODE",
    "TIMER_1_STATUS",
    "TIMER_2_STATUS",
    "TIMER_3_STATUS",
    "TIMER_4_STATUS",
    "TIMER_1_CHL",
    "TIMER_2_CHL",
    "TIMER_3_CHL",
    "TIMER_4_CHL",
    "VF_CONTACT_1",
    "VF_CONTACT_HUB_1",
    "VF_CONTACT_HUB_2",
    "VF_CONTACT_HUB_3",
    "PUMP_SPEED",
    "CHLORINATOR"
]
LIGHT_MODE_LIST = []

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Defer select setup to the shared select module."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    select_descriptions = []
    for key in KEYS_TO_CHECK:
        if key in coordinator.data:
            select_descriptions.append(
                SelectEntityDescription(
                    key=key,
                    name=coordinator.data[key]["name"],
                )
            )
    entities = [
        InsnrgPoolSelect(coordinator, hass, config_entry, description)
        for description in select_descriptions
    ]
    async_add_entities(entities, False)

class InsnrgPoolSelect(InsnrgPoolEntity, SelectEntity):
    """Select representing Insnrg Pool data."""
    def __init__(self, coordinator, hass, entry, description):
        super().__init__(coordinator, entry, description)
        self.insnrg_pool = InsnrgPool(
            aiohttp_client.async_get_clientsession(hass),
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
        )
    @property 
    def available(self) -> bool: 
        """Return True if entity has valid data, else False (Unavailable).""" 
        return self.entity_description.key in self.coordinator.data

    @property
    def current_option(self):
        """Return the current selected option."""
        device_data = self.coordinator.data.get(self.entity_description.key) 
        if not device_data: 
            return None # Entity Unavailable 
        deviceId = device_data.get("deviceId")
        if deviceId in ["LIGHT_MODE", "PUMP_SPEED", "CHLORINATOR"]: 
            return device_data.get("modeValue") 
        elif device_data.get("toggleStatus") == "ON": 
            return "TIMER" 
        elif device_data.get("switchStatus") == "ON": 
            return "ON" 
        else: return "OFF"

    @property
    def options(self):
        device_data = self.coordinator.data.get(self.entity_description.key) 
        if not device_data: 
            return [] # No data → entity Unavailable
        deviceId = device_data.get("deviceId")
        """Return the list of available options."""
        timerDevices = ["TIMER_1_STATUS","TIMER_2_STATUS", 
                        "TIMER_3_STATUS","TIMER_4_STATUS",
                        "TIMER_1_CHL", "TIMER_2_CHL", "TIMER_3_CHL", 
                        "TIMER_4_CHL"]
        if deviceId in ["LIGHT_MODE", "PUMP_SPEED", "CHLORINATOR"]: 
            return device_data.get("modeList", []) 
        elif deviceId in ["SPA", "TIMERS"] or deviceId in timerDevices: 
            return ["ON", "OFF"] 
        else: return ["ON", "OFF", "TIMER"]

    async def async_select_option(self, option: str) -> None:
        device_data = self.coordinator.data.get(self.entity_description.key, {}) 
        if not device_data: 
            _LOGGER.error("No data for key %s, entity unavailable", self.entity_description.key) 
            return
        deviceId = device_data.get("deviceId")
        _LOGGER.info({option: option, deviceId: deviceId}) 
        """Change the selected option."""
        if not deviceId: 
            _LOGGER.error("DeviceId missing for key %s", self.entity_description.key) 
            return 
        if deviceId == "LIGHT_MODE": 
            supportCmd = device_data.get("supportCmd") 
            success = await self.insnrg_pool.change_light_mode(option, supportCmd) 
        elif deviceId in ["PUMP_SPEED", "CHLORINATOR"]: 
            success = await self.insnrg_pool.set_pump_value(option, deviceId) 
        else: 
            success = await self.insnrg_pool.turn_the_switch(option, deviceId) 
        if success: 
            await asyncio.sleep(3) 
            await self.coordinator.async_request_refresh() 
        else: _LOGGER.error("Failed to select the option.")
