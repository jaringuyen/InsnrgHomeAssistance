"""Sensor platform for the Insnrg Pool sensor."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,  # ADDED
    SensorStateClass,  # ADDED
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_EMAIL,
    UnitOfElectricPotential,  # ADDED for ORP unit
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import InsnrgPoolEntity
from .const import DOMAIN
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
                'state_class': **SensorStateClass.MEASUREMENT**,  # ADDED for both
            }
            
            # Conditionally set specific attributes based on the key
            if key == "PH":
                description_data['device_class'] = **SensorDeviceClass.PH** # ADDED
                description_data['unit_of_measurement'] = **"pH"** # ADDED
                
            elif key == "ORP":
                description_data['device_class'] = **SensorDeviceClass.VOLTAGE** # ADDED
                description_data['unit_of_measurement'] = **UnitOfElectricPotential.MILLIVOLT** # ADDED
                description_data['icon'] = **"mdi:flash"** # MODIFIED icon for ORP sensor
            
            sersor_descriptions.append(**SensorEntityDescription(**description_data)) # MODIFIED to unpack dict
            
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
        return self.coordinator.data[self.entity_description.key]["temperatureSensorStatus"]["value"]
