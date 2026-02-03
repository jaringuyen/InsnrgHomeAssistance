"""Sensor platform for the Insnrg Pool sensor."""
from __future__ import annotations
from homeassistant.const import __version__ as HA_VERSION 
from awesomeversion import AwesomeVersion
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_EMAIL,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import InsnrgPoolEntity
from .const import DOMAIN
import logging
_LOGGER = logging.getLogger(__name__)
KEYS_TO_CHECK = ["PH", "ORP"]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Defer sensor setup to the shared sensor module."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sersor_descriptions = []
    for key in KEYS_TO_CHECK:
        if key in coordinator.data:
            description_data = {
                'key': key,
                'name': coordinator.data[key]['name'],
                'icon': "mdi:coolant-temperature",
                'state_class': SensorStateClass.MEASUREMENT,
            }
            
            # Conditionally set specific attributes based on the key
            if key == "PH":
                description_data['device_class'] = SensorDeviceClass.PH
            elif key == "ORP":
                description_data['device_class'] = SensorDeviceClass.VOLTAGE
                if AwesomeVersion(HA_VERSION) >= AwesomeVersion("2024.0.0"):
                    description_data['native_unit_of_measurement'] = UnitOfElectricPotential.MILLIVOLT
                else:
                    description_data['native_unit_of_measurement'] = "mV"
                description_data['icon'] = "mdi:flash"
            
            sersor_descriptions.append(SensorEntityDescription(**description_data))
            
    entities = [
        InsnrgPoolSensor(coordinator, config_entry.data[CONF_EMAIL], description)
        for description in sersor_descriptions
    ]
    async_add_entities(entities, False)

class InsnrgPoolSensor(InsnrgPoolEntity, SensorEntity):
    """Sensor representing Insnrg Pool data."""
    @property
    def native_value(self):
        """State of the sensor."""
        device_data = self.coordinator.data.get(self.entity_description.key, {}) 
        sensor_status = device_data.get("temperatureSensorStatus", {}) 
        value = sensor_status.get("value")
        if self.entity_description.key in ["PH", "ORP"]: 
            if value in (None, "", " "): 
                return None # Show Unavailable 
            try: 
                return float(value) 
            except (ValueError, TypeError): 
                _LOGGER.warning("Invalid %s value: %s", self.entity_description.key, value) 
                return None
        return value
