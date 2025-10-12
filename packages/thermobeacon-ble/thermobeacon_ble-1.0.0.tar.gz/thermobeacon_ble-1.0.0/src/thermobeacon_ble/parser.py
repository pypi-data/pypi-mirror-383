"""Parser for ThermoBeacon BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/thermoplus.py

MIT License applies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from struct import unpack

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import BinarySensorDeviceClass, SensorLibrary

_LOGGER = logging.getLogger(__name__)


@dataclass
class ThermoBeaconDevice:

    model: str
    name: str


DEVICE_TYPES = {
    0x10: ThermoBeaconDevice("16", "Lanyard/mini hygrometer"),
    0x11: ThermoBeaconDevice("17", "Smart hygrometer"),
    0x14: ThermoBeaconDevice("20", "Smart hygrometer"),
    0x15: ThermoBeaconDevice("21", "Smart hygrometer"),
    0x18: ThermoBeaconDevice("24", "Smart hygrometer"),
    0x1B: ThermoBeaconDevice("27", "Smart hygrometer"),
    0x30: ThermoBeaconDevice("48", "Smart hygrometer"),
}
MFR_IDS = set(DEVICE_TYPES)

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"


class ThermoBeaconBluetoothDeviceData(BluetoothData):
    """Date update for ThermoBeacon Bluetooth devices."""

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing thermobeacon BLE advertisement data: %s", service_info)
        if SERVICE_UUID not in service_info.service_uuids:
            return
        if not MFR_IDS.intersection(service_info.manufacturer_data):
            return
        changed_manufacturer_data = self.changed_manufacturer_data(service_info)
        if not changed_manufacturer_data:
            return
        last_id = list(changed_manufacturer_data)[-1]
        data = (
            int(last_id).to_bytes(2, byteorder="little")
            + changed_manufacturer_data[last_id]
        )
        msg_length = len(data)
        if msg_length not in (20, 22):
            return
        device_id = data[0]
        device_type = DEVICE_TYPES[device_id]
        name = device_type.name
        self.set_device_type(device_id)
        self.set_title(f"{name} {short_address(service_info.address)}")
        self.set_device_name(f"{name} {short_address(service_info.address)}")
        self.set_device_manufacturer("ThermoBeacon")
        _LOGGER.debug("Parsing ThermoBeacon BLE advertisement data: %s", data)
        if len(data) != 20:
            # Not a data packet
            return
        button_pushed = data[3] & 0x80
        xvalue = data[10:16]

        (volt, temp16, humi16) = unpack("<HhH", xvalue)
        temp = temp16 / 16
        humi = humi16 / 16

        if temp > 100 or humi > 100:
            return

        if volt >= 3000:
            batt = 100
        elif volt >= 2600:
            batt = 60 + (volt - 2600) * 0.1
        elif volt >= 2500:
            batt = 40 + (volt - 2500) * 0.2
        elif volt >= 2450:
            batt = 20 + (volt - 2450) * 0.4
        else:
            batt = 0

        self.set_precision(0)
        self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, batt)
        self.set_precision(2)
        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp)
        self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi)
        self.update_predefined_sensor(
            SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT, volt / 1000
        )
        self.update_predefined_binary_sensor(
            BinarySensorDeviceClass.OCCUPANCY, bool(button_pushed)
        )
