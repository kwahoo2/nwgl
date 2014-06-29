nwgl
==========
nwgl stands for: No-GUI WebGL exporter. It is a simple headless WebGL/HTML5 exported for FreeCAD. It exports only one shape, not shape list. 
Screenshot: http://imgur.com/YRC8DQk

Installation:
1. Install FreeCAD http://www.freecadweb.org/
2. Clone this repository
3. Adjust FREECADPATH in the noguiWebGLexport.py file
4. Run Python interpreter inside the "nwgl" directory and try some examples.

Examples:
Import a STEP file, and export the first shape in the file as HTML:

import noguiWebGLexport as nwgl
import Part
f = "piston.stp"
s = Part.read(f)
nwgl.export(s.Solids[0], "piston.html")

Create a bottle:

import noguiWebGLexport as nwgl
import Part
import MakeBottle
bottle = MakeBottle.makeBottle()
nwgl.export(bottle, "bottle.html")

Official FreeCAD website:
http://www.freecadweb.org/

Adrian Przekwas
June 29, 2014

Additional credits:
https://code.google.com/p/glmatrix/
http://learningwebgl.com/blog/?page_id=1217

 
