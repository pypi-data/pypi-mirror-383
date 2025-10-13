# dev_mega_0series.py
#
# Copyright 2023-2025 Clement Savergne <csavergne@yahoo.com>
#
# This file is part of yasim-avr.
#
# yasim-avr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# yasim-avr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with yasim-avr.  If not, see <http://www.gnu.org/licenses/>.

'''
This module initialises a device model for the ATmegaxx0x family:
ATmega808
ATmega809
ATmega1608
ATmega1609
ATmega3208
ATmega3209
ATmega4808
ATmega4809
'''

from ._builders_arch_xt import XT_DeviceBuilder, XT_BaseDevice
from ..descriptors import DeviceDescriptor

#========================================================================================
#Device class definition

class dev_mega_0series(XT_BaseDevice):

    def __init__(self, dev_descriptor, builder):
        super().__init__(dev_descriptor, builder)

        peripherals = [
            'CPUINT',
            'SLPCTRL',
            'CLKCTRL',
            'RSTCTRL',
            'NVMCTRL',
            'MISC',
            'PORTA',
            'PORTC',
            'PORTD',
            'PORTF',
            'PORTMUX',
            'RTC',
            'TCA0',
            'TCB0',
            'TCB1',
            'TCB2',
            'VREF',
            'ADC0',
            'ACP0',
            'USART0',
            'USART1',
            'USART2',
            'SPI0',
            'TWI0',
            'FUSES',
            'USERROW'
        ]

        if dev_descriptor.name in ('atmega809', 'atmega1609', 'atmega3209', 'atmega4809'):
            peripherals.extend(['PORTB', 'PORTE', 'TCB3', 'USART3'])

        builder.build_peripherals(self, peripherals)


    def arch_init(self):
        self._builder_.add_pin_driver_mux_configs(self, 'TCA0')
        self._builder_.add_pin_driver_mux_configs(self, 'TCB0')
        self._builder_.add_pin_driver_mux_configs(self, 'TCB1')
        self._builder_.add_pin_driver_mux_configs(self, 'TCB2')
        self._builder_.add_pin_driver_mux_configs(self, 'USART0')
        self._builder_.add_pin_driver_mux_configs(self, 'USART1')
        self._builder_.add_pin_driver_mux_configs(self, 'USART2')
        self._builder_.add_pin_driver_mux_configs(self, 'SPI0')
        self._builder_.add_pin_driver_mux_configs(self, 'TWI0')

        if self._descriptor_.name in ('atmega809', 'atmega1609', 'atmega3209', 'atmega4809'):
            self._builder_.add_pin_driver_mux_configs(self, 'TCB3')
            self._builder_.add_pin_driver_mux_configs(self, 'USART3')

        return True


def device_factory(model):
    dev_desc = DeviceDescriptor.create_from_model(model)
    return XT_DeviceBuilder.build_device(dev_desc, dev_mega_0series)
