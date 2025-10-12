"""
Parser for Leaone BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/leaone.py

MIT License applies.
"""

from __future__ import annotations

from sensor_state_data import (
    DeviceClass,
    DeviceKey,
    SensorDescription,
    SensorDeviceInfo,
    SensorUpdate,
    SensorValue,
    Units,
)

from .parser import LeaoneBluetoothDeviceData

__version__ = "1.0.0"

__all__ = [
    "DeviceClass",
    "DeviceKey",
    "LeaoneBluetoothDeviceData",
    "SensorDescription",
    "SensorDeviceInfo",
    "SensorDeviceInfo",
    "SensorUpdate",
    "SensorValue",
    "Units",
]
