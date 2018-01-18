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

import numpy
from datetime import timedelta

from py2gcode.py2gcode import StandardInstructionSet, GCodeException


class FileProcessor():
    def __init__(self, instruction_set, file_obj):
        assert isinstance(instruction_set, StandardInstructionSet)
        self.instruction_set = instruction_set
        self.file = file_obj
        self.process_end = False
        self.process_start = False
        self.comments = []
        self.errors = []

    def on_start(self):
        self.comments = []
        self.errors = []
        self.process_start = True
        self.process_end = False

    def on_complete(self):
        self.process_end = True
        self.file.seek(0)

    def raw_read(self, line):
        return line.strip()

    def read(self, raise_exception=False):
        self.on_start()
        for line in self.file.readlines():
            line = self.raw_read(line)
            init_comment = line.find(';')
            if init_comment != -1:
                self.comments.append(line)
                line = line[:init_comment].strip()
            if len(line) <= 1:
                continue
            try:
                gcode = self.instruction_set.clean_code(line, self.callback_manager)
                if gcode is None:
                    if raise_exception:
                        raise GCodeException('Command not supported "%s"' % line)
                    self.errors.append(line)
                    continue
                yield "%s\r\n" % gcode
            except GCodeException as ex:
                if raise_exception:
                    raise ex
                self.errors.append(line)
                continue
        self.on_complete()

    def callback_manager(self, gcode=None, **kwargs):
        pass


class DistanceProcessor(FileProcessor):
    INCH_2_MM = 0.0393700787

    def __init__(self, instruction_set, file_path, mm=True, absolute=True):
        FileProcessor.__init__(self, instruction_set, file_path)
        self.mm = mm
        self.abs = absolute
        self.distance = {'x': 0, 'y': 0, 'z': 0, 'total': 0}
        self.last_abs_pos = {'x': 0, 'y': 0, 'z': 0}

    def callback_manager(self, gcode=None, **kwargs):
        FileProcessor.callback_manager(self, gcode=gcode, **kwargs)
        if gcode in ['G20', 'G21']:
            self.mm = gcode == 'G21'
        elif gcode in ['G90', 'G91']:
            self.abs = gcode == 'G90'
        elif gcode in ['G3', 'G4']:
            pass  # TODO calcular las distancias de los arcos
        elif gcode in ['G0', 'G1', 'G92', 'G28']:
            x = kwargs.get('x', None)
            y = kwargs.get('y', None)
            z = kwargs.get('z', None)
            if gcode in ['G28']:
                if not (x or y or z):
                    x = 0
                    y = 0
                    z = 0
                    if not self.abs:
                        x = -self.last_abs_pos['x']
                        y = -self.last_abs_pos['y']
                        z = -self.last_abs_pos['z']
                else:
                    if x:
                        x = 0
                        if not self.abs:
                            x = -self.last_abs_pos['x']
                    if y:
                        y = 0
                        if not self.abs:
                            y = -self.last_abs_pos['y']
                    if z:
                        z = 0
                        if not self.abs:
                            z = -self.last_abs_pos['z']

            if x:
                x = float(x)
                if not self.mm:
                    x /= DistanceProcessor.INCH_2_MM
                if not self.abs:
                    x += self.last_abs_pos['x']
            else:
                x = self.last_abs_pos['x']
            if y:
                y = float(y)
                if not self.mm:
                    y /= DistanceProcessor.INCH_2_MM
                if not self.abs:
                    y += self.last_abs_pos['y']
            else:
                y = self.last_abs_pos['y']
            if z:
                z = float(z)
                if not self.mm:
                    z /= DistanceProcessor.INCH_2_MM
                if not self.abs:
                    z += self.last_abs_pos['z']
            else:
                z = self.last_abs_pos['z']
            if gcode != 'G92':  # Si es G92 No hay movimiento real
                self.distance['x'] += abs(self.last_abs_pos['x'] - x)
                self.distance['y'] += abs(self.last_abs_pos['y'] - y)
                self.distance['z'] += abs(self.last_abs_pos['z'] - z)
                init = numpy.array((self.last_abs_pos['x'], self.last_abs_pos['y'], self.last_abs_pos['z']))
                end = numpy.array((x, y, z))
                self.distance['total'] += numpy.sqrt(numpy.sum((init - end) ** 2))
            self.last_abs_pos['x'] = x
            self.last_abs_pos['y'] = y
            self.last_abs_pos['z'] = z


class SizeProcessor(DistanceProcessor):
    def __init__(self, instruction_set, file_path, mm=True, absolute=True):
        DistanceProcessor.__init__(self, instruction_set, file_path, mm=mm, absolute=absolute)
        self.size = {'x': -1, 'y': -1, 'z': -1}
        self.orig = {'x': -1, 'y': -1}

    def on_start(self):
        self.size = {'x': -1, 'y': -1, 'z': -1}
        self.orig = {'x': -1, 'y': -1}

    def callback_manager(self, gcode=None, **kwargs):
        DistanceProcessor.callback_manager(self, gcode=gcode, **kwargs)
        if gcode in ['G0', 'G1', 'G3', 'G4']:
            if self.orig['x'] < 0 or self.orig['x'] > self.last_abs_pos['x']:
                self.orig['x'] = self.last_abs_pos['x']
            if self.orig['y'] < 0 or self.orig['y'] > self.last_abs_pos['y']:
                self.orig['y'] = self.last_abs_pos['y']

            if self.size['x'] < 0 or self.size['x'] < self.last_abs_pos['x']:
                self.size['x'] = self.last_abs_pos['x']
            if self.size['y'] < 0 or self.size['y'] < self.last_abs_pos['y']:
                self.size['y'] = self.last_abs_pos['y']
            if self.size['z'] < 0 or self.size['z'] < self.last_abs_pos['z']:
                self.size['z'] = self.last_abs_pos['z']


class SpeedProcessor(SizeProcessor):
    def __init__(self, instruction_set, file_path, mm=True, absolute=True):
        SizeProcessor.__init__(self, instruction_set, file_path, mm=mm, absolute=absolute)
        self.speeds = {
            'unknown': {'x': 0, 'y': 0, 'z': 0, 'total': 0}
        }
        self.last_speed_distance = {'x': 0, 'y': 0, 'z': 0, 'total': 0}
        self.speed = 'unknown'
        self.time = -1

    def on_start(self):
        self.speeds = {
            'unknown': {'x': 0, 'y': 0, 'z': 0, 'total': 0}
        }
        self.last_speed_distance = {'x': 0, 'y': 0, 'z': 0, 'total': 0}
        self.speed = 'unknown'
        self.time = -1

    def on_complete(self):
        if self.speed not in self.speeds:
            self.speeds[self.speed] = {'x': 0, 'y': 0, 'z': 0, 'total': 0}
        self.speeds[self.speed]['x'] += self.distance['x'] - self.last_speed_distance['x']
        self.speeds[self.speed]['y'] += self.distance['y'] - self.last_speed_distance['y']
        self.speeds[self.speed]['z'] += self.distance['z'] - self.last_speed_distance['z']
        self.speeds[self.speed]['total'] += self.distance['total'] - self.last_speed_distance['total']
        td = 0
        for v in self.speeds:
            try:
                td += 60 / (float(v) / self.speeds[v]['total'])
            except ValueError:
                pass
        self.time = timedelta(minutes=td)
        SizeProcessor.on_complete(self)

    def callback_manager(self, gcode=None, **kwargs):
        f = kwargs.get('f', None)
        pre_distance = self.distance.copy()
        SizeProcessor.callback_manager(self, gcode=gcode, **kwargs)
        if gcode in ['G0', 'G1', 'G3', 'G4', 'G28'] and f:
            if self.speed != f:
                if not self.mm:
                    f = str(float(f) / DistanceProcessor.INCH_2_MM)
                dx = pre_distance['x'] - self.last_speed_distance['x']
                dy = pre_distance['y'] - self.last_speed_distance['y']
                dz = pre_distance['z'] - self.last_speed_distance['z']
                dt = pre_distance['total'] - self.last_speed_distance['total']
                if self.speed not in self.speeds:
                    self.speeds[self.speed] = {'x': dx, 'y': dy, 'z': dz, 'total': dt}
                else:
                    self.speeds[self.speed]['x'] += dx
                    self.speeds[self.speed]['y'] += dy
                    self.speeds[self.speed]['z'] += dz
                    self.speeds[self.speed]['total'] += dt
                self.last_speed_distance = pre_distance
                self.speed = f
