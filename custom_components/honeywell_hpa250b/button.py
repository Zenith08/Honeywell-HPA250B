"""Auxiliary command buttons for the Honeywell HPA250B."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, COMMANDS
from .coordinator import HPA250BCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HPA250BCommandButton(coordinator, entry, "light_cycle", "Cycle indicator light", "lightbulb"),
        HPA250BCommandButton(coordinator, entry, "timer_up", "Increase timer", "plus"),
        HPA250BCommandButton(coordinator, entry, "timer_down", "Decrease timer", "minus"),
        HPA250BCommandButton(coordinator, entry, "voc_toggle", "Toggle VOC mode", "air-filter"),
    ])


class HPA250BCommandButton(CoordinatorEntity, ButtonEntity):
    """A one-shot purifier command."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HPA250BCoordinator, entry, command_key, name, icon):
        super().__init__(coordinator)
        self.command_key = command_key
        self._attr_name = name
        self._attr_icon = f"mdi:{icon}"
        self._attr_unique_id = f"{entry.data['address']}_{command_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data["address"])},
            name="Honeywell HPA250B",
            manufacturer="Honeywell",
            model="HPA250B",
        )

    async def async_press(self):
        await self.coordinator.async_send_command(COMMANDS[self.command_key])
