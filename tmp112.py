#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Just a little python script."""

__author__ = 'Scott Johnston'
__version__ = '0.0.1'

import smbus2
import time


class TMP112:
    """TI TMP112 temperature sensor API."""

    def __init__(self, i2c_bus=2, i2c_address=0x48):
        """Opens the i2c device."""
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = i2c_address
        # Write configuration register: continous Conversion mode, 12-bit resolution
        # fault queue is 1 fault, polarity low, thermostat in comparator mode,
        # disables shutdown mode, normal mode, 12-bit data
        self.bus.write_i2c_block_data(self.address, 0x01, [0x60A0])
        time.sleep(0.050)

    def get_temperature(self):
        """Reads the temperature - note that this call blocks"""
        # Read data from temperature register (0x00), 2 bytes, MSB first
        data = self.bus.read_i2c_block_data(self.address, 0x00, 2)
        return self._calculate_temperature(data)

    def close(self):
        """Closes the i2c connection"""
        self.bus.close()

    def __enter__(self):
        """used to enable python's with statement support"""
        return self

    def __exit__(self, *exc_info):
        """with support"""
        self.close()

    @staticmethod
    def _calculate_temperature(unadjusted):
        """Converts data to degrees C."""
        temp =(unadjusted[0] * 256 + unadjusted[1]) / 16
        if temp > 2047 :
            temp -= 4096
        cTemp = temp * 0.0625
        return cTemp


if __name__ == '__main__':
    try:
        with TMP112() as tmp112:
            temperature = tmp112.get_temperature()
            print("Temperature (deg C): {}".format(temperature))
    except IOError:
        print("Error creating connection to i2c.")
