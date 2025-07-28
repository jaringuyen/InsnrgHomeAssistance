import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class PollingMixin:
    async def _async_poll_for_state_change(self, entity, target_value, current_value_getter, entity_type: str):
        # Set pending icon and update state
        entity._attr_icon = "mdi:sync"
        entity.async_write_ha_state()
        await asyncio.sleep(0.1) # Give HA a moment to update the UI

        polling_timeout = 300  # seconds (5 minutes)
        polling_interval = 5  # seconds
        start_time = entity.hass.loop.time()

        success = False
        while entity.hass.loop.time() - start_time < polling_timeout:
            await entity.coordinator.async_request_refresh()
            current_value = current_value_getter()
            _LOGGER.debug(f"Polling {entity.entity_id}. Current {entity_type}: {current_value}, Target: {target_value}")
            if current_value == target_value:
                _LOGGER.debug(f"{entity.entity_id} successfully set to {target_value} and state confirmed.")
                success = True
                break
            await asyncio.sleep(polling_interval)

        if not success:
            _LOGGER.warning(f"Timeout: {entity.entity_id} did not report {target_value} within {polling_timeout} seconds.")

        # Revert icon to None to allow Home Assistant to use its default icon
        entity._attr_icon = None
        entity.async_write_ha_state()
        return success
