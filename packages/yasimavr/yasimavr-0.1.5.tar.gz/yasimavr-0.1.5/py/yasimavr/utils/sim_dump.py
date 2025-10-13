# sim_dump.py
#
# Copyright 2022-2024 Clement Savergne <csavergne@yahoo.com>
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

import io
import collections

from ..lib import core as corelib
from ..device_library.accessors import DeviceAccessor

__all__ = ['sim_dump']


class _Dumper:

    def __init__(self, stream):
        self.stream = stream
        self.indent = 0
        self._empty_line = False


    def inc_level(self, tag):
        self.stream.write((' ' * (self.indent * 4)) + tag + ':\n')
        self._empty_line = False
        self.indent += 1


    def dec_level(self):
        if not self._empty_line:
            self.stream.write('\n')
        self._empty_line = True
        self.indent = max(0, self.indent - 1)


    def dump(self, tag, value):
        self.stream.write((' ' * (self.indent * 4)) + tag + ': ' + str(value) + '\n')
        self._empty_line = False

    __setitem__ = dump


    def dump_bytes(self, tag, value):
        indent = ' ' * (self.indent * 4)
        if tag:
            self.stream.write(indent + tag + ':\n')
        indent += ' ' * 4
        for i in range(0, len(value), 16):
            sv = ' '.join('%02x' % v for v in value[i:(i+16)])
            self.stream.write(indent + sv + '\n')

        self._empty_line = False


    def dump_memory(self, tag, data, addrstart):
        indent = ' ' * (self.indent * 4)
        self.stream.write(indent + tag + ':\n')
        indent += ' ' * 4
        for i in range(0, len(data), 16):
            sv = ' '.join('%02x' % v for v in data[i:(i+16)])
            self.stream.write('%s%04x : %s\n' % (indent, addrstart + i, sv))

        self.stream.write('\n')
        self._empty_line = True


    def dump_nvm(self, nvm, name):
        indent = ' ' * (self.indent * 4)
        self.stream.write(indent + name + ':\n')
        indent += ' ' * 4

        def print_line(addr, values, progs):
            s = ' '.join((('%02x' % v) if p else '--') for v, p in zip(values, progs))
            self.stream.write('%s%04x : %s\n' % (indent, addr, s))

        skipping = 0
        nvm_size = nvm.size()
        for line_pos in range(0, nvm_size, 16):
            line_size = min(16, nvm_size - line_pos)
            is_last_line = (line_pos + line_size >= nvm_size)
            line_values = nvm.block(line_pos, line_size)
            line_programmed = nvm.programmed(line_pos, line_size)
            is_line_to_print = any(line_programmed) or is_last_line

            if is_line_to_print and skipping:
                if skipping > 4:
                    self.stream.write(indent + '....\n')
                else:
                    empty_line_values = [0] * 16
                    empty_line_programmed= [False] * 16
                    for j in range(line_pos - skipping, line_pos):
                        print_line(j, empty_line_values, empty_line_programmed)

                skipping = 0

            if is_line_to_print or not skipping:
                print_line(line_pos, line_values, line_programmed)

            if not is_line_to_print:
                skipping += 1

        self.stream.write('\n')
        self._empty_line = True


def _serialize_registers(probe, dumper):

    RegData = collections.namedtuple('RegData', ('per', 'name', 'addr', 'size', 'value'))

    hex_addr = lambda x : '0x%04x' % x

    def _reg_value_to_str(reg_data):
        if isinstance(reg_data.value, int):
            return ('0x%%0%dx' % (reg_data.size * 2)) % reg_data.value
        elif isinstance(reg_data.value, str):
            return reg_data.value
        else:
            return repr(reg_data.value)

    dumper.inc_level('I/O Registers')

    accessor = DeviceAccessor(probe)

    #Prepare the list of RegData objects
    reg_data_list = []
    for per_name, per_descriptor in accessor.descriptor.peripherals.items():
        per_class_descriptor = per_descriptor.class_descriptor
        per_accessor = getattr(accessor, per_name, None)
        if per_accessor is None: continue

        #Extract the list of register name for this peripheral
        #If a register is 16 bits, the list may also have the same name with 'L' or 'H' prefix.
        #Remove those to avoid redundancy.
        reg_names = list(per_class_descriptor.registers)
        for reg_name in list(reg_names):
            if (reg_name + 'L') in reg_names:
                reg_names.remove(reg_name + 'L')
                reg_names.remove(reg_name + 'H')

        #Create the RegData objects.
        for reg_name in reg_names:
            #Read the register values, but not as CPU to avoid triggering behaviour
            r = getattr(getattr(accessor, per_name), reg_name)
            if r.allocated:
                r.set_read_as_cpu(False)
                v = r.read()
            else:
                v = '--' * r.size

            reg_data = RegData(per_name, reg_name, r.address, r.size, v)
            reg_data_list.append(reg_data)

    #Dump the register list sorted by address
    dumper.inc_level('Address map')
    for r in sorted(reg_data_list, key=lambda r : r.addr):
        sa = hex_addr(r.addr) if r.size == 1 else (hex_addr(r.addr) + '-' + hex_addr(r.addr + r.size - 1))
        t = r.per + '.' + r.name
        if isinstance(r.value, bytes):
            dumper[sa] = t
            dumper.dump_bytes('', r.value)
        else:
            dumper[sa] = t + ' [' + _reg_value_to_str(r) + ']'

    dumper.dec_level()

    #Dump the register list sorted by peripheral
    dumper.inc_level('Peripheral map')
    for per_name in accessor.descriptor.peripherals:
        per_reg_data = [ r for r in reg_data_list if r.per == per_name]
        if not per_reg_data: continue

        dumper.inc_level(per_name)

        for reg_data in sorted(per_reg_data, key=lambda r : r.addr):
            if isinstance(reg_data.value, bytes):
                dumper.dump_bytes(reg_data.name, reg_data.value)
            else:
                dumper[reg_data.name] = _reg_value_to_str(reg_data)

        dumper.dec_level()

    dumper.dec_level()
    dumper.dec_level()


def _serialize_RAM(device, probe, dumper):
    ramstart = device.config().core.ramstart
    ramend = device.config().core.ramend
    ram_data = probe.read_data(ramstart, ramend - ramstart + 1)
    dumper.dump_memory('RAM', ram_data, ramstart)


def _serialize_NVM(device, dumper):
    for name, index in device._NVMs_.items():
        reqdata = corelib.ctlreq_data_t()
        reqdata.index = index
        device.ctlreq(corelib.IOCTL_CORE, corelib.CTLREQ_CORE_NVM, reqdata)
        nvm = reqdata.data.as_ptr(corelib.NonVolatileMemory)
        if nvm:
            dumper.dump_nvm(nvm, name)


def _serialize_CPU(probe, dumper):
    dumper.inc_level('Core')
    dumper['Program Counter'] = hex(probe.read_pc())
    dumper['Stack Pointer'] = hex(probe.read_sp())
    dumper['SREG'] = hex(probe.read_sreg())

    reg_values = [probe.read_gpreg(i) for i in range(32)]

    for i in range(32):
        dumper['R%d' % i] = hex(reg_values[i])

    dumper['X'] = hex(reg_values[27] * 256 + reg_values[26])
    dumper['Y'] = hex(reg_values[29] * 256 + reg_values[28])
    dumper['Z'] = hex(reg_values[31] * 256 + reg_values[30])

    dumper.dec_level()


def _serialize_pins(device, dumper):
    dumper.inc_level('Pins')

    for pin_name in device.config().pins:
        pin = device.find_pin(pin_name)
        dumper[pin_name] = repr(pin.state())

    dumper.dec_level()


def _serialize_device(device, dumper):
    dumper.inc_level('Device')

    dumper['Variant'] = device.config().name
    dumper['State'] = device.state()._name_
    dumper['Sleep mode'] = device.sleep_mode()._name_
    dumper['Frequency (Hz)'] = device.frequency()

    dumper.inc_level('Options')
    for dev_option in corelib.Device.Option:
        dumper[dev_option._name_] = device.test_option(dev_option)
    dumper.dec_level()

    dumper.dec_level()

    _serialize_pins(device, dumper)

    probe = corelib.DeviceDebugProbe(device)

    _serialize_CPU(probe, dumper)
    _serialize_registers(probe, dumper)
    _serialize_RAM(device, probe, dumper)
    _serialize_NVM(device, dumper)


def _serialize_simloop(simloop, dumper):
    dumper.inc_level('Simloop')
    dumper['State'] = simloop.state()._name_
    dumper['Simulated cycles'] = simloop.cycle()

    if simloop.device().state()._name_ not in ('Limbo', 'Ready'):
        t = simloop.cycle() / simloop.device().frequency()
    else:
        t = 0
    dumper['Simulated time (secs)'] = t

    dumper.dec_level()

    _serialize_device(simloop.device(), dumper)


def sim_dump(simloop : corelib.AbstractSimLoop, stream : io.TextIOBase = None) -> 'str|None':
    """Dump the current state of a simulation into a I/O stream.

    :param AbstractSimLoop simloop: instance of AbstractSimLoop to dump
    :param io.TextIOBase stream: writable stream instance or None

    If stream is None, the state is dumped into a string buffer and the string is returned.
    If stream is not None, the state is written into it and None is returned.
    """

    dumper = _Dumper(io.StringIO() if stream is None else stream)

    _serialize_simloop(simloop, dumper)

    if stream is None:
        return dumper.stream.getvalue()
    else:
        return None
