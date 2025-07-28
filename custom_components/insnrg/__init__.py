"""The InsnrgPool integration."""
import asyncio
from datetime import timedelta
import logging
import async_timeout
from .call_api import InsnrgPool
from .exceptions import InsnrgPoolError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from .const import ATTRIBUTION, DOMAIN

PLATFORMS = [Platform.SELECT, Platform.CLIMATE, Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]
_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Insnrg Pool from a config entry."""
    insnrg_pool = InsnrgPool(
        aiohttp_client.async_get_clientsession(hass),
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )
    auth_valid = await insnrg_pool.test_insnrg_pool_credentials()
    if not auth_valid:
        _LOGGER.error("Invalid authentication")
        return False
    coordinator = InsnrgPoolDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
class InsnrgPoolEntity(CoordinatorEntity):
    """Implements a common class elements representing the Insnrg Pool component."""
    _attr_attribution = ATTRIBUTION
    def __init__(self, coordinator, email, description: EntityDescription) -> None:
        """Initialize insnrg pool sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"InsnrgPool {description.name}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
class InsnrgPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to hold Insnrg Pool data."""
    def __init__(self, hass, entry):
        """Initialize."""
        self.insnrg_pool = InsnrgPool(
            aiohttp_client.async_get_clientsession(hass),
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
        )
        self.hass = hass
        self.entry = entry
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=5))
    async def _async_update_data(self):
        """Update data via library."""
        data = {}
        async with async_timeout.timeout(60):
            try:
                data = await self.insnrg_pool.get_insnrg_pool_data()
            except InsnrgPoolError as error:
                _LOGGER.error("Insnrg Pool query did not complete")
                raise UpdateFailed(error) from error
        return data
