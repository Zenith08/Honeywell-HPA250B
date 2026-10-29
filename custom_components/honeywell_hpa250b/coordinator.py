"""Bluetooth coordinator for the Honeywell HPA250B."""

import asyncio
import logging
from datetime import timedelta

from bleak import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, STATUS_UUID, WRITE_UUID

_LOGGER = logging.getLogger(__name__)


def parse_status(raw: bytes) -> dict:
    """Decode the fields currently supported by the reverse-engineered protocol."""
    data = {
        "raw": bytes(raw),
        "is_on": False,
        "preset_mode": None,
        "light_code": None,
        "timer": None,
        "voc_mode": False,
        "iaq": None,
        "prefilter": None,
        "epa_filter": None,
    }
    if not raw or raw[0] != 0xA5 or len(raw) < 3:
        return data

    status_code = raw[1]
    data["is_on"] = status_code != 0x00
    from .const import STATUS_TO_MODE

    data["preset_mode"] = STATUS_TO_MODE.get(status_code)

    if len(raw) > 2:
        data["light_code"] = raw[2] & 0x03
    if status_code == 0x03 and len(raw) > 2:
        data["voc_mode"] = True
        data["iaq"] = (raw[2] >> 2) << 2
        data["preset_mode"] = None
        data["is_on"] = True
    if len(raw) > 4:
        data["timer"] = raw[4]
    if len(raw) > 5 and raw[5]:
        data["prefilter"] = raw[5]
    if len(raw) > 6 and raw[6]:
        data["epa_filter"] = raw[6]
    return data


class HPA250BCoordinator(DataUpdateCoordinator):
    """Own the BLE connection and push notification state to entities."""

    def __init__(self, hass: HomeAssistant, address: str):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )
        self.address = address
        self.client = None
        self._retry_unsub = None
        self._status_event = asyncio.Event()
        self._connect_lock = asyncio.Lock()

    async def async_start(self):
        await self._async_connect()
        self._retry_unsub = async_track_time_interval(
            self.hass, self._async_retry, timedelta(seconds=30)
        )

    async def async_stop(self):
        if self._retry_unsub:
            self._retry_unsub()
            self._retry_unsub = None
        client, self.client = self.client, None
        if client and client.is_connected:
            try:
                await client.stop_notify(STATUS_UUID)
            except BleakError, OSError:
                pass
            await client.disconnect()

    async def _async_retry(self, _now):
        if not self.client or not self.client.is_connected:
            await self._async_connect()

    async def _async_connect(self):
        async with self._connect_lock:
            if self.client and self.client.is_connected:
                return
            ble_device = bluetooth.async_ble_device_from_address(
                self.hass, self.address, connectable=True
            )
            if ble_device is None:
                _LOGGER.debug(
                    "No Bluetooth advertisement currently available for %s",
                    self.address,
                )
                return
            try:
                client = await establish_connection(
                    BleakClientWithServiceCache,
                    ble_device,
                    f"Honeywell HPA250B {self.address}",
                    disconnected_callback=self._handle_disconnect,
                )
                self.client = client
                mac_bytes = bytes.fromhex(self.address.replace(":", ""))
                await client.write_gatt_char(
                    WRITE_UUID, b"MAC+" + mac_bytes, response=False
                )
                await asyncio.sleep(0.2)
                try:
                    raw = await client.read_gatt_char(STATUS_UUID)
                    self.async_set_updated_data(parse_status(raw))
                except (BleakError, OSError) as err:
                    _LOGGER.debug("Initial HPA250B status read failed: %s", err)
                await client.start_notify(STATUS_UUID, self._handle_notification)
                _LOGGER.info("Connected to Honeywell HPA250B at %s", self.address)
            except (TimeoutError, BleakError, OSError) as err:
                self.client = None
                _LOGGER.warning(
                    "Could not connect to HPA250B %s: %s", self.address, err
                )

    def _handle_disconnect(self, _client):
        _LOGGER.warning("Honeywell HPA250B disconnected")
        self.client = None

    def _handle_notification(self, _sender, raw: bytearray):
        self.async_set_updated_data(parse_status(bytes(raw)))
        self._status_event.set()

    async def async_send_command(self, command: bytes, *, wait_for_status=True):
        if not self.client or not self.client.is_connected:
            await self._async_connect()
        if not self.client or not self.client.is_connected:
            raise HomeAssistantError(
                "Cannot connect to the purifier. Check that it is powered and in Bluetooth range."
            )
        self._status_event.clear()
        try:
            await self.client.write_gatt_char(WRITE_UUID, command, response=True)
        except (BleakError, OSError) as err:
            self.client = None
            raise HomeAssistantError(f"Bluetooth command failed: {err}") from err
        if wait_for_status:
            try:
                await asyncio.wait_for(self._status_event.wait(), timeout=2.5)
            except TimeoutError:
                _LOGGER.debug("No status notification received after command")
