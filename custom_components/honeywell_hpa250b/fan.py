"""Fan entity for the Honeywell HPA250B."""
import logging

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, PLATFORMS, COMMANDS, MODE_TO_COMMAND
from .coordinator import HPA250BCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HPA250BFan(coordinator, entry)])


class HPA250BFan(CoordinatorEntity, FanEntity):
    """Represent the purifier fan."""

    _attr_has_entity_name = True
    _attr_name = "Air purifier"
    _attr_supported_features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF | FanEntityFeature.PRESET_MODE
    _attr_preset_modes = ["General", "Germ", "Allergen", "Turbo"]

    def __init__(self, coordinator: HPA250BCoordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.data['address']}_fan"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data["address"])},
            name="Honeywell HPA250B",
            manufacturer="Honeywell",
            model="HPA250B",
        )

    @property
    def available(self):
        return self.coordinator.data is not None

    @property
    def is_on(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("is_on", False)

    @property
    def preset_mode(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("preset_mode")

    async def async_turn_on(self, **kwargs):
        if self.is_on is True:
            return
        if self.is_on is None:
            raise HomeAssistantError(
                "Purifier state is unknown; wait for a status update before toggling power."
            )
        # 0x01 is a confirmed power toggle; from Off it starts in General mode.
        await self.coordinator.async_send_command(COMMANDS["off_toggle"])

    async def async_turn_off(self, **kwargs):
        if self.is_on is False:
            return
        if self.is_on is None:
            raise HomeAssistantError("Purifier state is unknown; refresh status before toggling power.")
        await self.coordinator.async_send_command(COMMANDS["off_toggle"])

    async def async_set_preset_mode(self, preset_mode: str):
        if preset_mode not in MODE_TO_COMMAND:
            raise HomeAssistantError(f"Unsupported purifier mode: {preset_mode}")
        if self.is_on is not True:
            if self.is_on is None:
                raise HomeAssistantError("Purifier state is unknown; wait for a status update before changing modes.")
            await self.coordinator.async_send_command(COMMANDS["off_toggle"])
            # Toggle-on starts in General. Give the device a moment to report that state.
            await self.coordinator.async_send_command(COMMANDS[MODE_TO_COMMAND[preset_mode]])
            return
        await self.coordinator.async_send_command(COMMANDS[MODE_TO_COMMAND[preset_mode]])
