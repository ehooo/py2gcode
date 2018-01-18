# Py2GCode
Py2GCode is a library for use "gcode" in python easily

One of the most tipical problem for G and M code is that it's a facto standard,
 so many differents machines use the same code for differents thinks.

With this project you can write G and M code forgetting the real code, you only need to call a helpful function.

# Classes
All classes implements constructor with "strict" parameter for raise error or
 returning None for not supported or wrong calling functions

* py2gcode.py2gcode.StandardInstructionSet:

  Supported GCode and MCode for [Standard GCode](http://www.machinemate.com/StandardCodes.htm)
* py2gcode.py2gcode.FileProcessor:

  File processor for "instruction set"
* py2gcode.py2gcode.DistanceProcessor:

  File processor for "instruction set" for calculate the distances
* py2gcode.py2gcode.SizeProcessor:

  File processor for "instruction set" for calculate the minimum bed size for print the model
* py2gcode.py2gcode.SpeedProcessor:

  File processor for "instruction set" for calculate time needed for print the model
* py2gcode.printer3d.Printer3D:

  Supported [Common GCode and MCode](http://reprap.org/wiki/G-code) for 3D Printers
* py2gcode.printer3d.SDGCode:

  Supported common MCodes for SD used by 3D Printers
* py2gcode.printer3d.MarlinGCode:

  Support for [Marlin GCodes and MCode](https://github.com/MarlinFirmware/Marlin/blob/Development/Documentation/GCodes.md)
* py2gcode.printer3d.RepRapGCode:

  Support for [RepRap GCodes and MCode](https://github.com/reprappro/RepRapFirmware/blob/master/GCodes.cpp)

* py2gcode.cnc.CNCGCode:

  Supported Common CNC GCode
* py2gcode.cnc.LinuxCNCGCode:

  Support for [LinuxCNC GCodes](http://linuxcnc.org/docs/html/gcode/gcode.html) and [MCode](http://linuxcnc.org/docs/html/gcode/m-code.html)
* py2gcode.cnc.grblGCode:

  Support for [GRBL driver for CNC GCodes and MCode](https://github.com/grbl/grbl/wiki)
* py2gcode.cnc.TurningGCode:

  Support for [Turning CNC GCodes and MCode](http://www.cnccookbook.com/CCCNCGCodeRefTurn.html)
* py2gcode.cnc.MillingGCode:

  Support for [Turning CNC GCodes and MCode](http://www.cnccookbook.com/CCCNCGCodeRef.html)

# Others References:
 - http://www.cncezpro.com/gcodes.cfm
 - http://www.cncezpro.com/mcodes.cfm
 
# Example:

```
 from py2gcode import printer3d

 gcode = printer3d.MarlinGCode(strict=True)
 print gcode.set_mm()
 print gcode.home()
 print gcode.G28()
 print gcode.line(x=10, y=10)
 print gcode.G1(x=10, y=10)
 print gcode.line(z=1)
 print gcode.g1(z=1)
 print gcode.line(x=5, e=1, fast=True)
 print gcode.line(y=0, e=1, slow=False)
```
