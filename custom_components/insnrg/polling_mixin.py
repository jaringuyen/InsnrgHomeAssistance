import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

CLOCK_ICONS = [
    "mdi:clock-time-twelve-outline",
    "mdi:clock-time-one-outline",
    "mdi:clock-time-two-outline",
    "mdi:clock-time-three-outline",
    "mdi:clock-time-four-outline",
    "mdi:clock-time-five-outline",
    "mdi:clock-time-six-outline",
    "mdi:clock-time-seven-outline",
    "mdi:clock-time-eight-outline",
    "mdi:clock-time-nine-outline",
    "mdi:clock-time-ten-outline",
    "mdi:clock-time-eleven-outline",
]
SUCCESS_ICON = "mdi:check-circle-outline"
STARTER_ICON = "mdi:circle-outline"

class PollingMixin:
    async def _async_animate_icon(self, entity, original_icon_for_animation):
        try:
            index = 0 # Start from the first icon in the animation sequence
            while True:
                entity._attr_icon = CLOCK_ICONS[index]
                entity.async_write_ha_state()
                index = (index + 1) % len(CLOCK_ICONS)
                await asyncio.sleep(1.0) # Animation speed: 1 second per icon
        except asyncio.CancelledError:
            # Animation cancelled, revert to original icon (handled in finally block of caller)
            pass

    async def _async_poll_for_state_change(self, entity, original_icon_from_entity, target_value, current_value_getter, entity_type: str, animation_task=None):
        try:
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
            
            # Set final icon based on success or revert to original
            if success:
                entity._attr_icon = SUCCESS_ICON
                entity.async_write_ha_state()
                await asyncio.sleep(0.5) # Display success icon for 0.5 second
                entity._attr_icon = original_icon_from_entity
                entity.async_write_ha_state()
            else:
                entity._attr_icon = original_icon_from_entity
                entity.async_write_ha_state()