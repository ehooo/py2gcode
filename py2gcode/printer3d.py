#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    author: Victor Torre

    Copyright (C) 2018 [Victor Torre](https://github.com/ehooo)
    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License. You may obtain a copy of
    the License at
    http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations under
    the License.
"""
from __future__ import absolute_import

from py2gcode.py2gcode import StandardInstructionSet, MCode, ArgsMCode


class Printer3D(StandardInstructionSet):
    """
        Implementation of common GCodes and MCodes used by 3D Printers, see http://reprap.org/wiki/G-code
    """
    ENDSTOP_IGNORE_CHECK = 0
    ENDSTOP_CHECK = 1

    def __init__(self, strict=False):
        StandardInstructionSet.__init__(self, strict=strict)
        self.code_supportered['G0'].valid_params.append('e')
        self.code_supportered['G0'].valid_params.append('s')
        self.code_supportered['G0'].param_alias['endstop_check'] = 's'
        self.code_supportered['G1'].valid_params.append('e')
        self.code_supportered['G1'].valid_params.append('s')
        self.code_supportered['G1'].param_alias['endstop_check'] = 's'
        self.code_supportered['G2'].valid_params.append('e')
        self.code_supportered['G3'].valid_params.append('e')
        self.code_supportered['G92'].valid_params.append('e')

        self.code_supportered.update({
            'M18': MCode(18, strict=self.strict),
            'M80': MCode(80, strict=self.strict),
            'M81': MCode(81, strict=self.strict),
            'M82': MCode(82, strict=self.strict),
            'M83': MCode(83, strict=self.strict),
            'M84': MCode(84, valid_params=['x', 'y', 'z', 'e', 's'], param_alias={'seconds': 's'}, strict=self.strict),
            'M92': MCode(92, valid_params=['x', 'y', 'z', 'e'], required_min=1, strict=self.strict),
            'M104': MCode(104, valid_params=['s'], param_alias={'grade': 's'}, required_params=['s'],
                          strict=self.strict),
            'M105': MCode(105, strict=self.strict),
            'M106': MCode(106, valid_params=['s'], param_alias={'power': 's'}, required_params=['s'],
                          strict=self.strict),
            'M107': MCode(107, strict=self.strict),
            'M109': MCode(109, valid_params=['s'], param_alias={'grade': 's'}, required_params=['s'],
                          strict=self.strict),
            'M112': MCode(112, strict=self.strict),
            'M114': MCode(114, strict=self.strict),
            'M115': MCode(115, strict=self.strict),
            'M119': MCode(119, strict=self.strict),
            'M140': MCode(140, valid_params=['s'], param_alias={'grade': 's'}, required_params=['s'],
                          strict=self.strict),
            'M190': MCode(190, valid_params=['s'], param_alias={'grade': 's'}, required_params=['s'],
                          strict=self.strict),
            'M203': MCode(190, valid_params=['x', 'y', 'z', 'e'], required_min=1, strict=self.strict),
            'M301': MCode(301, valid_params=['p', 'i', 'd'], required_params=['p', 'i', 'd'], strict=self.strict),
            'M400': MCode(400, strict=self.strict)
        })
        self.code_functions.update({
            'motor_off': 'M18',
            'power_on': 'M80',
            'power_off': 'M81',
            'extruder_absolute': 'M82',
            'extruder_relative': 'M83',
            'motor_idle': 'M84',
            'set_axis_steps_per_unit': 'M92',
            'extruder_set_temperature': 'M104',
            'get_temperature': 'M105',
            'fan_on': 'M106',
            'fan_off': 'M107',
            'extruder_wait_temperature': 'M109',
            'emergency_stop': 'M112',
            'get_position': 'M114',
            'get_firmware': 'M115',
            'get_endstop': 'M119',
            'bed_set_temperature': 'M140',
            'bed_wait_temperature': 'M190',
            'set_max_feedrate': 'M203',
            'set_PID': 'M301',
            'set_pid': 'M301',
            'wait_move': 'M400'
        })

    # M-Codes
    def power(self, on=False, off=True, **kwargs):
        if on or not off:
            return self.power_on(**kwargs)
        return self.power_off(**kwargs)

    def extruder_mode(self, absolute=False, relative=True, **kwargs):
        if absolute or not relative:
            return self.extruder_absolute(**kwargs)
        return self.extruder_relative(**kwargs)

    def fan(self, on=True, **kwargs):
        power = kwargs.get('power', 0)
        if int(power) > 0 and on:
            return self.fan_on(**kwargs)
        return self.fan_off(**kwargs)

    def extruder_temperature(self, wait=False, **kwargs):
        if wait:
            return self.extruder_wait_temperature(**kwargs)
        return self.extruder_set_temperature(**kwargs)

    def bed_temperature(self, wait=False, **kwargs):
        if wait:
            return self.bed_wait_temperature(**kwargs)
        return self.bed_set_temperature(**kwargs)


class SDGCode(Printer3D):
    """
        Implementation of MCode used by 3D Printers for use SD Cards, see http://reprap.org/wiki/G-code
    """
    def __init__(self, strict=False):
        Printer3D.__init__(self, strict=strict)
        self.code_supportered.update({
            'M20': MCode(20, strict=self.strict),
            'M21': MCode(21, strict=self.strict),
            'M23': ArgsMCode(23, required_args=1, strict=self.strict),
            'M24': MCode(24, strict=self.strict),
            'M25': MCode(25, strict=self.strict),
            'M26': MCode(26, valid_params=['s'], param_alias={'position': 's'}, required_min=1, strict=self.strict),
            'M27': MCode(27, strict=self.strict),
            'M28': ArgsMCode(28, required_args=1, strict=self.strict),
            'M29': ArgsMCode(29, required_args=1, strict=self.strict),
            'M30': MCode(30, required_args=1, strict=self.strict),
            'M31': MCode(31, strict=self.strict),
            'M32': ArgsMCode(32, required_args=1, strict=self.strict),
            'M36': ArgsMCode(36, required_args=1, strict=self.strict)
        })
        self.code_functions.update({
            'SD_list': 'M20',
            'SD_init': 'M21',
            'SD_select': 'M23',
            'SD_print_start': 'M24',
            'SD_print_pause': 'M25',
            'SD_set_position': 'M26',
            'SD_print_status': 'M27',
            'SD_write': 'M28',
            'SD_write_stop': 'M29',
            'SD_delete': 'M30',
            'SD_output_time': 'M31',
            'SD_print': 'M32',
            'SD_info': 'M36',

            'sd_list': 'M20',
            'sd_init': 'M21',
            'sd_select': 'M23',
            'sd_print_start': 'M24',
            'sd_print_pause': 'M25',
            'sd_set_position': 'M26',
            'sd_print_status': 'M27',
            'sd_write': 'M28',
            'sd_write_stop': 'M29',
            'sd_delete': 'M30',
            'sd_output_time': 'M31',
            'sd_print': 'M32',
            'sd_info': 'M36'
        })

    def SD_print_resume(self):
        return self.SD_print_start()


class MarlinGCode(SDGCode):
    """
        Implementation of common MCodes used by Marlin Driver
        https://github.com/MarlinFirmware/Marlin/blob/Development/Marlin/Marlin_main.cpp
    """
    def __init__(self, strict=False):
        SDGCode.__init__(self, strict=strict)
        self.code_supportered['M109'].valid_params.append('r')
        self.code_supportered['M109'].param_alias['wait_cooling'] = 'r'
        self.code_supportered['M109'].valid_params.append('s')
        self.code_supportered['M109'].param_alias['min_t'] = 'b'
        self.code_supportered['M109'].valid_params.append('b')
        self.code_supportered['M109'].param_alias['max_t'] = 'b'
        self.code_supportered['M109'].valid_params.append('f')
        self.code_supportered['M109'].param_alias['factor'] = 'f'
        self.code_supportered['M190'].valid_params.append('r')
        self.code_supportered['M190'].param_alias['wait_cooling'] = 'r'
        self.code_supportered.update({
            'M22': MCode(22, strict=self.strict),
            'M117': MCode(117, required_args=1, strict=self.strict),
            'M304': MCode(304, valid_params=['p', 'i', 'd'], required_params=['p', 'i', 'd'], strict=self.strict),
            'M928': MCode(928, required_args=1, strict=self.strict),
            'M999': MCode(999, strict=self.strict),
            'M36': None,
            'M3': None,
            'M4': None,
            'M5': None,
        })

        self.code_functions.update({
            'SD_release': 'M22',
            'sd_release': 'M22',
            'autotemp': 'M109',
            'display_message': 'M117',
            'bed_wait_temperature': 'M190',
            'bed_set_PID': 'M304',
            'SD_start_log': 'M928',
            'sd_start_log': 'M928',
            'restart': 'M999',
            'SD_info': None,
            'sd_info': None,
            'spindle_on_counter_clockwise': None,
            'spindle_on_clockwise': None,
            'spindle_off': None
        })


class RepRapGCode(SDGCode):
    """
        Implementation of common MCodes used by RepRap Driver
        https://github.com/reprappro/RepRapFirmware/blob/dc42/GCodes.cpp
    """
    def __init__(self, strict=False):
        SDGCode.__init__(self, strict=strict)
        self.code_supportered.update({
            'M116': MCode(116, strict=self.strict),
            'M120': MCode(120, strict=self.strict),
            'M121': MCode(121, strict=self.strict),
            'M122': MCode(122, strict=self.strict),
            'G2': None,
            'G3': None,
            'M32': None,
            'M36': None,
            'M3': None,
            'M4': None,
            'M5': None,
        })

        self.code_functions.update({
            'wait': 'M116',
            'push': 'M120',
            'pop': 'M121',
            'diagnose': 'M122',
            'arc_normal': None,
            'arc_clockwise': None,
            'SD_info': None,
            'sd_info': None,
            'SD_print': None,
            'sd_print': None,
            'spindle_on_counter_clockwise': None,
            'spindle_on_clockwise': None,
            'spindle_off': None
        })
