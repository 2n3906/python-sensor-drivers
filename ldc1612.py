#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Just a little python script."""

__author__ = 'Scott Johnston'
__version__ = '0.0.1'

import smbus2
import time


class LDC1612:
    """TI LDC1612 inductive sensor API."""

    # LDC1612 register addresses (do not change)
    LDC1612_DATA_MSB_CH0 = 0x00
    LDC1612_DATA_LSB_CH0 = 0x01
    LDC1612_DATA_MSB_CH1 = 0x02
    LDC1612_DATA_LSB_CH1 = 0x03
    LDC1612_RCOUNT_CH0 = 0x08
    LDC1612_RCOUNT_CH1 = 0x09
    LDC1612_SETTLECOUNT_CH0 = 0x10
    LDC1612_SETTLECOUNT_CH1 = 0x11
    LDC1612_CLOCK_DIVIDERS_CH0 = 0x14
    LDC1612_CLOCK_DIVIDERS_CH1 = 0x15
    LDC1612_STATUS = 0x18
    LDC1612_ERROR_CONFIG = 0x19
    LDC1612_CONFIG = 0x1A
    LDC1612_MUX_CONFIG = 0x1B
    LDC1612_RESET_DEV = 0x1C
    LDC1612_DRIVE_CURRENT_CH0 = 0x1E
    LDC1612_DRIVE_CURRENT_CH1 = 0x1F
    LDC1612_MANUFACTURER_ID = 0x7E
    LDC1612_DEVICE_ID = 0x7F

    def __init__(self, i2c_bus=2, i2c_address=0x2A):
        """Opens the i2c device."""
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = i2c_address
        # Check that we're talking to a LDC1612.
        device_id = self.get_register(self.LDC1612_DEVICE_ID)
        assert device_id == 0x3055

    def close(self):
        self.bus.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def get_register(self, register):
        d = self.bus.read_i2c_block_data(self.address, register, 2)
        return int.from_bytes(d, byteorder='big')

    def set_register(self, register, value):
        data = bytearray(value.to_bytes(2, byteorder='big'))
        d = self.bus.write_i2c_block_data(self.address, register, data)
        return

    def read_channels(self):
        # Conversion data must be read MSB-first!
        ch0_msb = self.bus.read_i2c_block_data(
            self.address, self.LDC1612_DATA_MSB_CH0, 2)
        ch0_lsb = self.bus.read_i2c_block_data(
            self.address, self.LDC1612_DATA_LSB_CH0, 2)
        ch1_msb = self.bus.read_i2c_block_data(
            self.address, self.LDC1612_DATA_MSB_CH1, 2)
        ch1_lsb = self.bus.read_i2c_block_data(
            self.address, self.LDC1612_DATA_LSB_CH1, 2)
        # Assemble output values
        ch0_int = ((ch0_msb << 16) + ch0_lsb) & 0x0FFFFFFF
        ch1_int = ((ch1_msb << 16) + ch1_lsb) & 0x0FFFFFFF
        ch0_err = bool(ch0_int & 0xF0000000)
        ch1_err = bool(ch1_int & 0xF0000000)
        return ch0_int, ch1_int, ch0_err, ch1_err


if __name__ == '__main__':
    try:
        with LDC1612() as ldc1612:
            print("Manufacturer ID: 0x{:02X}".format(
                ldc1612.get_register(ldc1612.LDC1612_MANUFACTURER_ID)))
            print("Device ID      : 0x{:02X}".format(
                ldc1612.get_register(ldc1612.LDC1612_DEVICE_ID)))
            print("Config         : 0x{:02X}".format(
                ldc1612.get_register(ldc1612.LDC1612_CONFIG)))
    except IOError:
        print("Error creating connection to i2c.")
