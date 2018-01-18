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

from py2gcode.py2gcode import StandardInstructionSet, GCode, MCode


class CNCGCode(StandardInstructionSet):
    """
        Implementation of common GCodes and MCodes used by CNC, see http://www.cncezpro.com/gcodes.cfm
    """

    def __init__(self, strict=False):
        StandardInstructionSet.__init__(self, strict)
        self.code_supportered.update({
            'G17': GCode(17, strict=self.strict),
            'G18': GCode(18, strict=self.strict),
            'G19': GCode(19, strict=self.strict)
        })
        self.code_functions.update({
            'set_plane_xy': 'G17',
            'set_plane_xz': 'G18',
            'set_plane_yz': 'G19'
        })


class LinuxCNCGCode(CNCGCode):
    """
        Implementation of common GCodes and MCodes used by LinuxCNC
        see http://www.linuxcnc.org/docs/2.5/html/gcode/gcode.html
    """

    def __init__(self, strict=False):
        CNCGCode.__init__(self, strict)
        self.code_supportered.update({
            'G5': GCode(5, valid_params=['p', 'q', 'x', 'y', 'i', 'j'], required_params=['p', 'q'], strict=self.strict),
            'G17.1': GCode(17.1, strict=self.strict),
            'G18.1': GCode(18.1, strict=self.strict),
            'G19.1': GCode(19.1, strict=self.strict)
        })
        self.code_functions.update({
            'cubic_spline': 'G5',
            'set_plane_uv': 'G17.1',
            'set_plane_wu': 'G18.1',
            'set_plane_vw': 'G19.1'
        })


class TurningGCode(CNCGCode):
    pass


class MillingGCode(CNCGCode):
    pass


class GrblGcode(LinuxCNCGCode):
    """
        Implementation of common GCodes and MCodes suported by Grbl, see https://github.com/grbl/grbl/wiki
    """

    def __init__(self, strict=False):
        LinuxCNCGCode.__init__(self, strict)
        self.code_supportered.update({  # TODO Check parameters
            'G5': None,
            'G17.1': None,
            'G18.1': None,
            'G19.1': None,
            'G28.1': GCode(28.1, strict=self.strict),
            'G30': GCode(30, strict=self.strict),
            'G30.1': GCode(30.1, strict=self.strict),
            'G38.2': GCode(38.2, strict=self.strict),
            'G43.1': GCode(43.1, strict=self.strict),
            'G49': GCode(49, strict=self.strict),
            'G53': GCode(53, strict=self.strict),
            'G54': GCode(54, strict=self.strict),
            'G55': GCode(55, strict=self.strict),
            'G56': GCode(56, strict=self.strict),
            'G57': GCode(57, strict=self.strict),
            'G58': GCode(58, strict=self.strict),
            'G59': GCode(59, strict=self.strict),
            'G92.1': GCode(92.1, strict=self.strict),
            'G93': GCode(93, strict=self.strict),
            'G94': GCode(94, strict=self.strict),
            'G80': GCode(80, strict=self.strict),
            'M2': MCode(2, strict=self.strict),
            'M30': MCode(30, strict=self.strict),
            'M8': MCode(8, strict=self.strict),
            'M9': MCode(9, strict=self.strict)
        })
        self.code_functions.update({
            'cubic_spline': None,
            'set_plane_uv': None,
            'set_plane_wu': None,
            'set_plane_vw': None,
            'set_home': 'G28.1',
            'goto_def_position': 'G30',
            'set_def_position': 'G30.1',
            'probing': 'G38.2',
            'dynamic_tool_length_offsets1': 'G43.1',
            'dynamic_tool_length_offsets2': 'G49',
            'move_abs_cord': 'G53',
            'work_coordinate_systems1': 'G54',
            'work_coordinate_systems2': 'G55',
            'work_coordinate_systems3': 'G56',
            'work_coordinate_systems4': 'G57',
            'work_coordinate_systems5': 'G58',
            'work_coordinate_systems6': 'G59',
            'clear_coordinate_system_offsets': 'G92.1',
            'feedrate_modes1': 'G93',
            'feedrate_modes2': 'G94',
            'cancel_motion': 'G80',
            'program_pause': 'M2',
            'program_stop': 'M30',
            'coolant_control1': 'M8',
            'coolant_control2': 'M9',
        })
