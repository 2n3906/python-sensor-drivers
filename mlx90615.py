#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Just a little python script."""

__author__ = 'Scott Johnston'
__version__ = '0.0.1'

import smbus2
import time

# TODO:
# * test RAW IR, TA, TO with negative numbers! word_data is a uint16.
# * fix register writing, because PEC code isn't being created by smbus2.


class MLX90615:
    """Melexis MLX90615 IR temperature sensor API."""

    # Register addresses (0x1x = EEPROM, 0x2x = RAM)
    MLX90615_CONFIG = 0x12
    MLX90615_EMISSIVITY = 0x13
    MLX90515_ID1 = 0x1E
    MLX90615_ID2 = 0x1F
    MLX90615_RAWIR = 0x25
    MLX90615_TA = 0x26
    MLX90615_TO = 0x27

    def __init__(self, i2c_bus=2, i2c_address=0x5B):
        """Opens the i2c device."""
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = i2c_address

    def get_register(self, register):
        return self.bus.read_word_data(self.address, register)

    def set_register(self, register, value):
        return self.bus.write_word_data(self.address, register, value)

    def get_ambient_temperature(self):
        """Reads ambient temperature in deg C."""
        data = self.get_register(self.MLX90615_TA)
        return self._calculate_temperature(data)

    def get_object_temperature(self):
        """Reads object temperature in deg C."""
        data = self.get_register(self.MLX90615_TO)
        return self._calculate_temperature(data)

    def close(self):
        self.bus.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    @staticmethod
    def _calculate_temperature(raw):
        """Converts temperature register value to degrees C."""
        return (raw * 0.02) - 273.15

    @property
    def emissivity(self):
        "Emissivity (ε)."
        data = self.get_register(self.MLX90615_EMISSIVITY)
        return data / 16384.0

    @emissivity.setter
    def emissivity(self, value):
        assert 0.1 < value < 1
        data = round(16384 * value)
        return self.set_register(self.MLX90615_EMISSIVITY, data)

if __name__ == '__main__':
    try:
        with MLX90615() as mlx90615:
            print("Object temperature (deg C) : {}".format(mlx90615.get_object_temperature()))
            print("Ambient temperature (deg C): {}".format(mlx90615.get_ambient_temperature()))
            print("Emissivity calibration (ε) : {}".format(mlx90615.emissivity))
    except IOError:
        print("Error creating connection to i2c.")
