#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Just a little python script."""

__author__ = 'Scott Johnston'
__version__ = '0.0.1'

import smbus2
import time
import struct
import crcmod


class SHT31:
    """Sensiron SHT31 temp/humidity sensor API."""

    # datasheet (v0.93), page 5, table 4
    _MEASUREMENT_WAIT_TIME = 0.015  # (datasheet: typ=12.5, max=15)

    def __init__(self, i2c_bus=2, i2c_address=0x44):
        """Opens the i2c device (assuming that the kernel modules have been
        loaded)."""
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = i2c_address
        # standard addresses are 0x44 (ADDR=low) or 0x45 (ADDR=high)
        time.sleep(0.050)

    def get_temperature_and_humidity(self):
        """Reads the temperature and humidity - note that this call blocks
        the program for 15ms"""
        # Command: measure, high repeatability, clock stretching on
        self.bus.write_i2c_block_data(self.address, 0x2C, [0x06])
        time.sleep(self._MEASUREMENT_WAIT_TIME)
        data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
        temp_data, temp_checksum, humidity_data, humidity_checksum = struct.unpack(
            ">HBHB", bytearray(data))
        crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0)
        if crc8(bytearray(data[0:2])) == temp_checksum and crc8(bytearray(data[3:5])) == humidity_checksum:
            return self._calculate_temperature(temp_data), self._calculate_humidity(humidity_data)
        else:
            return None, None

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
        """This function reads the first two bytes of data and
        returns the temperature in C by using the following function:
        T = -45 + (175 * (ST/2^16))
        where ST is the value from the sensor
        """
        unadjusted *= 175.0
        unadjusted /= 1 << 16  # divide by 2^16
        unadjusted -= 45
        return unadjusted

    @staticmethod
    def _calculate_humidity(unadjusted):
        """This function reads the first two bytes of data and returns
        the relative humidity in percent by using the following function:
        RH = (100 * (SRH / 2 ^16))
        where SRH is the value read from the sensor
        """
        unadjusted *= 100.0
        unadjusted /= 1 << 16  # divide by 2^16
        unadjusted -= 0
        return unadjusted


if __name__ == "__main__":
    try:
        with SHT31() as sht31:
            temperature, humidity = sht31.get_temperature_and_humidity()
            print("Temperature (deg C): {}".format(temperature))
            print("Humidity           : {}%".format(humidity))
    except IOError:
        print("Error creating connection to i2c.")
