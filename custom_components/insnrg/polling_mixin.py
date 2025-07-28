import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

HOURGLASS_ICONS = [
    "mdi:timer-sand",
    "mdi:timer-sand-paused",
    "mdi:timer-sand-complete",
    "mdi:timer-sand-paused",
]

class PollingMixin:
    async def _async_animate_icon(self, entity, original_icon):
        try:
            index = 0
            while True:
                entity._attr_icon = HOURGLASS_ICONS[index]
                entity.async_write_ha_state()
                index = (index + 1) % len(HOURGLASS_ICONS)
                await asyncio.sleep(0.3) # Animation speed
        except asyncio.CancelledError:
            # Animation cancelled, revert to original icon
            entity._attr_icon = original_icon
            entity.async_write_ha_state()

    async def _async_poll_for_state_change(self, entity, target_value, current_value_getter, entity_type: str):
        original_icon = getattr(entity, '_attr_icon', None)
        animation_task = None

        try:
            # Start icon animation in the background
            animation_task = asyncio.create_task(self._async_animate_icon(entity, original_icon))

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

            return success
        finally:
            if animation_task:
                animation_task.cancel()
                # Wait for the animation task to finish its cleanup (reverting icon)
                try:
                    await animation_task
                except asyncio.CancelledError:
                    pass # Expected when cancelling
