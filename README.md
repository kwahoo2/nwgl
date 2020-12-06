nwgl
==========
nwgl stands for: No-GUI WebGL exporter. It is a simple headless WebGL/HTML5 exported for FreeCAD. Supports multiple shapes export (as a single mesh).
Screenshot: http://imgur.com/YRC8DQk

Installation:  
* Install FreeCAD http://www.freecadweb.org/  
* Clone this repository  
* Adjust FREECADPATH in the noguiWebGLexport.py file  
* Run Python interpreter inside the "nwgl" directory and try some examples.  

Examples:  
Import a STEP file, and export all shapes in the file as HTML:

``` 
import noguiWebGLexport as nwgl
import Part
f = "piston.stp"
s = Part.read(f)
nwgl.export(s.Solids, "piston.html")
```

Official FreeCAD website:  
http://www.freecadweb.org/

Adrian Przekwas  
June 29, 2014  

Additional credits:  
https://code.google.com/p/glmatrix/  
http://learningwebgl.com/blog/?page_id=1217  

Navigation in the generated HTML file:
* LMB + move - rotate
* MMB + move - zoom
* RMB + move - pan
