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

import re
import six


class GCodeException(Exception):
    def __init__(self, *args, **kwargs):
        self.gcode = kwargs.pop('gcode', None)
        Exception.__init__(self, *args, **kwargs)


class BaseCode:
    FLOAT_RE = re.compile('\\-?\\d+\\.?\\d*')

    def __init__(self, codekey, ncode, required_params=[], valid_params=[], param_alias={},
                 required_min=0, strict=False, callback=[], **kwargs):
        """
            BaseCode is a class used for make easy and fast write codes
            The optional parameters are for validate the codes
            :param codekey: M or G
            :param ncode: Number of code ej: 1, 17.1
            :param required_params: Array with all requiered params
            :param valid_params: Array with valid params
            :param param_alias: Dict with {'kwargs_name': 'param'}
            :param required_min: Number of requiered parameters ej: 1 for G1
            :param required_args: Number of requiered arguments, usefull for SD Mcodes ej: M23 filename
            :param strict: Boolean for raise error, default=False
            :param callback: List of function with format "callback_funct(gcode=self.gcode, **kwargs)" calling when 
            get() is call with filtered params and only if all is ok, default=None
            :param kwargs: **kwargs Use for extend
        """
        self.gcode = "%s%s" % (codekey, ncode)
        self.ncode = ncode
        self.required_params = required_params
        self.valid_params = valid_params
        self.param_alias = param_alias
        self.required_min = required_min
        self.strict = strict
        self.error = None
        self.callback = callback
        self._re = None

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
            Are calling when class is call.
            This will call all callbacks installed if not error happen.
            :param args:
            :param kwargs: parameters used for generate the gcode
            :return: String with code or None if error
            :raise GCodeException: If strict and error occurred
        """
        self.error = None
        code = self.gcode
        req_min = 0
        req_param = []
        callback_kwargs = {'gcode': self.gcode}
        for key in kwargs:
            if key in self.param_alias:
                key = self.param_alias[key]
            if key in self.valid_params:
                code += " %s%s" % (key.upper(), kwargs[key])
                req_min += 1
                req_param.append(key)
                if len(self.callback) > 0:
                    callback_kwargs[key.lower()] = kwargs[key]
            else:
                self.error = "Param %s not valid for %s" % (key, self.gcode)
                if self.strict:
                    raise GCodeException(self.error, gcode=self.gcode, **kwargs)
        if self.required_min > req_min:
            self.error = "Need at last %s of %s for %s" % (self.required_min, self.valid_params, self.gcode)
            if self.strict:
                raise GCodeException(self.error, gcode=self.gcode, **kwargs)
            return None
        for key in self.required_params:
            self.error = "Required %s in %s" % (key, self.gcode)
            if not (key in req_param):
                if self.strict:
                    raise GCodeException(self.error, gcode=self.gcode, **kwargs)
                return None
        if len(self.callback) > 0:
            for f in self.callback:
                f(**callback_kwargs)
        return code

    def get_re(self):
        """
            :return re: Regular expresion for valid the code
        """
        if self._re is None:
            p_res = {}
            for p in self.valid_params:
                p_res[p] = "([%s%s]\\-?\\d+\\.?\\d*) ?" % (p.lower(), p.upper())
            valid_re = "(%s) ?" % self.gcode

            if len(self.required_params):
                p_req = {}
                for p in self.required_params:
                    p_req[p] = p_res[p]
                    del (p_res[p])
                if len(p_req) == 1:
                    valid_re += "%s" % (''.join(p_req.values()))
                else:
                    valid_re += "(?:%s){%s}" % ('|'.join(p_req.values()), len(p_req))
            if len(p_res) > 0:
                valid_re += "(?:%s){%s,}" % ('|'.join(p_res.values()), self.required_min)
            self._re = re.compile(valid_re)
        return self._re

    def get_kwargs(self, code):
        """
            :param code: The code to get kwargs
            :return dict: **kwargs Use for call get on this class
            :raise GCodeException: If strict and error occurred
        """
        kwargs = {}
        if isinstance(code, str) or isinstance(code, unicode) or isinstance(code, six.string_types):
            code = six.u(code)

        code = code.strip()
        if code.startswith(self.gcode):
            re_exp = self.get_re()
            if self.strict:
                ok = re_exp.match(code)
                if ok.end() != len(code):
                    self.error = 'Validation error for "%s" check the arguments' % code
                    raise GCodeException(self.error, gcode=self.gcode)
            fa = re_exp.findall(code)
            if len(fa) > 0 and isinstance(fa[0], tuple):
                for param in fa[0][1:]:
                    f = BaseCode.FLOAT_RE.findall(param)
                    if len(f) == 1:
                        key = param.replace(f[0], '')
                        kwargs[key.lower()] = f[0]
        elif self.strict:
            self.error = '"%s" is not %s command' % (code, self.gcode)
            raise GCodeException(self.error, gcode=self.gcode)
        return kwargs


class GCode(BaseCode):
    def __init__(self, ncode, **kwargs):
        BaseCode.__init__(self, "G", ncode, **kwargs)


class MCode(BaseCode):
    def __init__(self, ncode, **kwargs):
        BaseCode.__init__(self, "M", ncode, **kwargs)


class ArgsMCode(MCode):
    """
        Usefull for SD MCodes
    """

    def __init__(self, ncode, required_args=0, no_args=True, **kwargs):
        """
            :param ncode: Number of code ej: 28
            :param required_args: Number of arguments required
            :param no_args: Boolean arguments requiered, default=True, if required_args>0 allways no_args==False
            :param no_args: Boolean for not arguments, default=True, if required_args == True allways no_args==True
        """
        self.required_args = required_args
        if required_args > 0:
            no_args = False
        self.no_args = no_args
        MCode.__init__(self, ncode, **kwargs)

    def get(self, *args, **kwargs):
        s_args = len(args)
        if self.required_args > s_args:
            self.error = "%s argument requires for %s" % (self.required_args, self.gcode)
            if self.strict:
                raise GCodeException(self.error, gcode=self.gcode, **kwargs)
            return None
        code = MCode.get(self, *args, **kwargs)
        if self.required_args <= s_args:
            if s_args > 0 and self.no_args:
                self.error = "Command %s do not accept any argument" % self.gcode
                if self.strict:
                    raise GCodeException(self.error, gcode=self.gcode, **kwargs)
                return None
            for arg in args:
                code += " %s" % arg
        return code

    def get_re(self):  # TODO
        return MCode.get_re(self)

    def get_kwargs(self, code):  # TODO
        return MCode.get_kwargs(self, code)


class StandardInstructionSet():
    """
        Implementation of common used Standar GCodes and MCodes see http://www.machinemate.com/StandardCodes.htm
    """

    def __init__(self, strict=False):
        """
        :param strict: If True when error happen functions will raise an exception, else return None
        self.code_supportered storage {str code: class BaseCode} dict
        self.code_functions storage alias functions for BaseCodes {str function name: str code} dict
        """
        self.strict = strict
        self.code_supportered = {
            'G0': GCode(0, valid_params=['x', 'y', 'z', 'f'], param_alias={'speed': 'f'}, required_min=1,
                        strict=self.strict),
            'G1': GCode(1, valid_params=['x', 'y', 'z', 'f'], param_alias={'speed': 'f'}, required_min=1,
                        strict=self.strict),
            'G2': GCode(2, valid_params=['x', 'y', 'i', 'j', 'f'], required_params=['x', 'y', 'i', 'j'],
                        param_alias={'speed': 'f'}, strict=self.strict),
            'G3': GCode(3, valid_params=['x', 'y', 'i', 'j', 'f'], required_params=['x', 'y', 'i', 'j'],
                        param_alias={'speed': 'f'}, strict=self.strict),
            'G4': GCode(4, valid_params=['p', 's'], param_alias={'milliseconds': 'p', 'seconds': 's'}, required_min=1,
                        strict=self.strict),
            'G28': GCode(28, valid_params=['x', 'y', 'z'], strict=self.strict),
            'G20': GCode(20, strict=self.strict),
            'G21': GCode(21, strict=self.strict),
            'G90': GCode(90, strict=self.strict),
            'G91': GCode(91, strict=self.strict),
            'G92': GCode(92, valid_params=['x', 'y', 'z'], required_min=1, strict=self.strict),

            'M0': MCode(0, strict=self.strict),
            'M1': MCode(1, strict=self.strict),
            'M3': MCode(3, valid_params=['s'], param_alias={'speed': 's'}, required_min=1, strict=self.strict),
            'M4': MCode(4, valid_params=['s'], param_alias={'speed': 's'}, required_min=1, strict=self.strict),
            'M5': MCode(5, strict=self.strict)
        }
        self.code_functions = {
            'line_fast': 'G0',
            'line_normal': 'G1',
            'arc_normal': 'G2',
            'arc_clockwise': 'G3',
            'dwell': 'G4',
            'home': 'G28',
            'set_inches': 'G20',
            'set_mm': 'G21',
            'set_absolute': 'G90',
            'set_relative': 'G91',
            'set_position': 'G92',

            'motor_stop': 'M0',
            'motor_sleep': 'M1',
            'spindle_on_counter_clockwise': 'M3',
            'spindle_on_clockwise': 'M4',
            'spindle_off': 'M5'
        }

    def __getattr__(self, key):
        if key in self.code_functions:
            key = self.code_functions[key]
        key = key.upper()
        if key in self.code_supportered:
            cls = self.code_supportered[key]
            if not cls:
                raise AttributeError("%s instance has no attribute '%s'" % (self.__class__, key))
            cls.strict = self.strict
            return cls
        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__, key))

    def arc(self, clockwise=False, **kwargs):
        if clockwise:
            return self.arc_clockwise(**kwargs)
        return self.arc_normal(**kwargs)

    def line(self, fast=False, slow=True, **kwargs):
        if fast or not slow:
            return self.line_fast(**kwargs)
        return self.line_normal(**kwargs)

    def clean_code(self, code, callback=None):
        """
            Filter the code and remove not allowed parameters or raise a GCodeException
            :param code:  Object with __str__ function for clean
            :return: String Code filtering
            :raise GCodeException: If strict and error occurred
        """
        key = six.u(code).split(' ')[0]
        if key in self.code_supportered and self.code_supportered[key]:
            self.code_supportered[key].strict = self.strict
            kwargs = self.code_supportered[key].get_kwargs(code)
            if callback not in self.code_supportered[key].callback:
                self.code_supportered[key].callback.append(callback)
            clean = self.code_supportered[key].get(**kwargs)
            if callback in self.code_supportered[key].callback:
                self.code_supportered[key].callback.remove(callback)
            return clean
        return None
