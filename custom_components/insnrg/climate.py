from __future__ import annotations
import asyncio
from .call_api import InsnrgPool
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import aiohttp_client
from . import InsnrgPoolEntity
from .const import DOMAIN
from .polling_mixin import PollingMixin, STARTER_ICON
import logging
_LOGGER = logging.getLogger(__name__)
KEYS_TO_CHECK = ["SPA_CONTROL", "POOL_CONTROL"]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Defer climate setup to the shared climate module."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    climate_descriptions = []
    for key in KEYS_TO_CHECK:
        if key in coordinator.data:
            climate_descriptions.append(ClimateEntityDescription(
                key=key,
                name=coordinator.data[key]['name'],
            ))
    entities = [
        InsnrgPoolClimate(coordinator, hass, config_entry, description)
        for description in climate_descriptions
    ]
    async_add_entities(entities, False)

class InsnrgPoolClimate(InsnrgPoolEntity, ClimateEntity, PollingMixin):
    """Climate entity representing Insnrg Pool data."""
    _attr_hvac_modes = [None]
    _attr_hvac_mode = None
    def __init__(self, coordinator, hass, entry, description):
        """Initialize Insnrg Pool climate."""
        super().__init__(coordinator, entry, description)
        self.insnrg_pool = InsnrgPool(
            aiohttp_client.async_get_clientsession(hass),
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
        )
        self.hass = hass # Required for polling mixin
        # Initialize _attr_target_temperature based on current coordinator data
        self._attr_target_temperature = self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("ggPoolSetTemperature") or self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("value")
    
    @property
    def supported_features(self) -> str | None:
        """Return the current temperature."""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def max_temp(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data[self.entity_description.key]["thermostatStatus"]["valueMax"]
    
    @property
    def min_temp(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data[self.entity_description.key]["thermostatStatus"]["valueMin"]

    @property
    def target_temperature_step(self) -> str:
        """Return the unit of measurement."""
        if self.entity_description.key == "PH":
            return 0.1
        elif self.entity_description.key == "ORP":
            return 10
        else:
            return 0.5

    @property
    def temperature_unit(self) -> float:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data[self.entity_description.key]["temperatureSensorStatus"]["value"]

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        # Always return _attr_target_temperature for optimistic updates
        return self._attr_target_temperature
    
    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp_value = kwargs.get("temperature")
        # Optimistic update
        self._attr_target_temperature = temp_value
        self.async_write_ha_state()
        original_icon = getattr(self, '_attr_icon', None) # Capture original icon
        self._attr_icon = STARTER_ICON # Set starter icon
        self.async_write_ha_state()

        deviceId = self.coordinator.data[self.entity_description.key]["deviceId"]
        api_call_task = asyncio.create_task(self.insnrg_pool.set_thermostat_temp(temp_value, deviceId))
        
        await asyncio.sleep(1.0) # Delay for 1 second before starting clock animation

        animation_task = asyncio.create_task(self._async_animate_icon(self, original_icon))
        success = await api_call_task # Wait for the API call to complete

        if success:
            # Pass a lambda that checks the actual coordinator data
            poll_success = await self._async_poll_for_state_change(self, original_icon, temp_value, 
                lambda: self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("ggPoolSetTemperature") or self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("value"), entity_type="target temperature", animation_task=animation_task)
            if not poll_success:
                # Revert if polling failed, get actual state from coordinator
                self._attr_target_temperature = self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("ggPoolSetTemperature") or self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("value")
                self.async_write_ha_state()
        else:
            _LOGGER.error(f"Failed to set the temperature for {self.entity_id}.")
            # Revert if command failed, get actual state from coordinator
            self._attr_target_temperature = self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("ggPoolSetTemperature") or self.coordinator.data[self.entity_description.key].get("thermostatStatus", {}).get("value")
            self.async_write_ha_state()
