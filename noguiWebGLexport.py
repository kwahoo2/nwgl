#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014                                                    *  
#*   Adrian Przekwas <adrian.v.przekwas@gmail.com>                         *
#*   Yorik van Havre <yorik@uncreated.net>                                 *  
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

"FreeCAD no-gui webgl exporter"

FREECADPATH = '/usr/lib/freecad-daily/lib'
import sys
sys.path.append(FREECADPATH)
import FreeCAD,Part,MeshPart,Mesh
from pivy import coin

if open.__module__ == '__builtin__':
    pythonopen = open
    
def export(exportList,filename):
    "exports the given objects to a .html file"
    
    nshp = len(exportList)
    print "Exporting: " + str(nshp) + " shapes"
    n = 0
    VerticesData = []
    VertexNormalsData = []
    ItemsData = 0
    
    for shp in exportList:
        Verts,Vnorms,Itms,BBMax,BBCenter = getObjectData(shp)
        n = n + 1
        VerticesData = VerticesData + Verts
        VertexNormalsData = VertexNormalsData + Vnorms
        ItemsData = ItemsData + Itms
        print "Shape: " + str(n) + " of " +str(nshp)
        
    html = getHTML(VerticesData,VertexNormalsData,ItemsData,BBMax,BBCenter) 
    print "Saving: " + filename
    outfile = pythonopen(filename,"wb")
    outfile.write(html)
    outfile.close()



def getHTML(VerticesData,VertexNormalsData,ItemsData,BBMax,BBCenter):
    "returns the complete HTML code of a viewer for the given shape"
    template = getTemplate()
    template = template.replace("$verticesData",str(VerticesData))
    template = template.replace("$vertexnormalsData",str(VertexNormalsData))
    template = template.replace("$itemsData",str(ItemsData))
    template = template.replace("$bbMax",str(BBMax))
    template = template.replace("$bbX",str(-BBCenter.x))
    template = template.replace("$bbY",str(-BBCenter.y))
    return template
       
def getObjectData(shape):
    
    vertices = []
    normals = []
    items = 0

    try: 
        fcmesh = shape.tessellate(0.1)
        fcmeshm = Mesh.Mesh(fcmesh)
        gen = coin.SoNormalGenerator(True)
        vertices = [] #non-indexed vertices list
        normals = [] #non-indexed normals list
        for f in fcmesh[1]: #indexes
            rnd = 3 #how many digits
            v0 = fcmesh[0][f[0]]
            v1 = fcmesh[0][f[1]]
            v2 = fcmesh[0][f[2]]
            #vertices =  vertices + [v0.x] + [v0.y] + [v0.z] + [v1.x] + [v1.y] + [v1.z] +[v2.x] + [v2.y] + [v2.z]
            vertices =  vertices + [round(v0.x, rnd)] + [round(v0.y, rnd)] + [round(v0.z, rnd)] + [round(v1.x, rnd)] + [round(v1.y, rnd)] + [round(v1.z, rnd)] +[round(v2.x, rnd)] + [round(v2.y, rnd)] + [round(v2.z, rnd)] 
            sbv0 = coin.SbVec3f(v0)
            sbv1 = coin.SbVec3f(v1)
            sbv2 = coin.SbVec3f(v2)
            gen.triangle(sbv0, sbv1, sbv2)

        gen.generate(0.5) #generate normals with crease angle 0.5 rad
        for i in range(gen.getNumNormals()):
           #normals = normals + [gen.getNormal(i).getValue()[0]] + [gen.getNormal(i).getValue()[1]] + [gen.getNormal(i).getValue()[2]]
           normals = normals + [round(gen.getNormal(i).getValue()[0], rnd)] + [round(gen.getNormal(i).getValue()[1], rnd)] + [round(gen.getNormal(i).getValue()[2], rnd)] #rounded to save space

        items = gen.getNumNormals()
        bb = fcmeshm.BoundBox
        bbmax = max (bb.XLength,bb.YLength,bb.ZLength)
        bbcenter = bb.Center

        return vertices,normals,items,bbmax,bbcenter

    except:
        print "Something went wrong"
        return "","",0,0,0

def getTemplate():
    "returns a html template"
    
    result = """<html>
            <head>
            <title>WebGL-FreeCAD model</title>
            <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">

            <script type="text/javascript" src="glMatrix-0.9.5.min.js"></script>
            <script type="text/javascript" src="webgl-utils.js"></script>

            <script id="shader-fs" type="x-shader/x-fragment">
                precision mediump float;

                varying vec3 vLightWeighting;

                void main(void) {
                    gl_FragColor = vec4(vLightWeighting, 1.0);
                }
            </script>

            <script id="shader-vs" type="x-shader/x-vertex">
                attribute vec3 aVertexPosition;

                attribute vec3 aVertexNormal;

                uniform mat4 uMVMatrix;
                uniform mat4 uPMatrix;
                uniform mat3 uNMatrix;

                uniform vec3 uAmbientColor;

                uniform vec3 uLightingDirection;
                uniform vec3 uDirectionalColor;

                uniform bool uUseLighting;

                varying vec3 vLightWeighting;

                void main(void) {
                    gl_Position = uPMatrix * uMVMatrix * vec4(aVertexPosition, 1.0);

                    if (!uUseLighting) {
                        vLightWeighting = vec3(1.0, 1.0, 1.0);
                    } else {
                        vec3 transformedNormal = uNMatrix * aVertexNormal;
                        float directionalLightWeighting = max(dot(transformedNormal, uLightingDirection), 0.0);
                        vLightWeighting = uAmbientColor + uDirectionalColor * directionalLightWeighting;
                    }
                }
            </script>

            <script type="text/javascript">

                var gl;

                function initGL(canvas) {
                    try {
                        gl = canvas.getContext("experimental-webgl");
                        gl.viewportWidth = canvas.width;
                        gl.viewportHeight = canvas.height;
                    } catch (e) {
                    }
                    if (!gl) {
                        alert("Could not initialise WebGL, sorry :-(");
                    }
                }


                function getShader(gl, id) {
                    var shaderScript = document.getElementById(id);
                    if (!shaderScript) {
                        return null;
                    }

                    var str = "";
                    var k = shaderScript.firstChild;
                    while (k) {
                        if (k.nodeType == 3) {
                            str += k.textContent;
                        }
                        k = k.nextSibling;
                    }

                    var shader;
                    if (shaderScript.type == "x-shader/x-fragment") {
                        shader = gl.createShader(gl.FRAGMENT_SHADER);
                    } else if (shaderScript.type == "x-shader/x-vertex") {
                        shader = gl.createShader(gl.VERTEX_SHADER);
                    } else {
                        return null;
                    }

                    gl.shaderSource(shader, str);
                    gl.compileShader(shader);

                    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                        alert(gl.getShaderInfoLog(shader));
                        return null;
                    }

                    return shader;
                }


                var shaderProgram;

                function initShaders() {
                    var fragmentShader = getShader(gl, "shader-fs");
                    var vertexShader = getShader(gl, "shader-vs");

                    shaderProgram = gl.createProgram();
                    gl.attachShader(shaderProgram, vertexShader);
                    gl.attachShader(shaderProgram, fragmentShader);
                    gl.linkProgram(shaderProgram);

                    if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
                        alert("Could not initialise shaders");
                    }

                    gl.useProgram(shaderProgram);

                    shaderProgram.vertexPositionAttribute = gl.getAttribLocation(shaderProgram, "aVertexPosition");
                    gl.enableVertexAttribArray(shaderProgram.vertexPositionAttribute);

                    shaderProgram.vertexNormalAttribute = gl.getAttribLocation(shaderProgram, "aVertexNormal");
                    gl.enableVertexAttribArray(shaderProgram.vertexNormalAttribute);

                    shaderProgram.pMatrixUniform = gl.getUniformLocation(shaderProgram, "uPMatrix");
                    shaderProgram.mvMatrixUniform = gl.getUniformLocation(shaderProgram, "uMVMatrix");
                    shaderProgram.nMatrixUniform = gl.getUniformLocation(shaderProgram, "uNMatrix");

                    shaderProgram.useLightingUniform = gl.getUniformLocation(shaderProgram, "uUseLighting");
                    shaderProgram.ambientColorUniform = gl.getUniformLocation(shaderProgram, "uAmbientColor");
                    shaderProgram.lightingDirectionUniform = gl.getUniformLocation(shaderProgram, "uLightingDirection");
                    shaderProgram.directionalColorUniform = gl.getUniformLocation(shaderProgram, "uDirectionalColor");
                }


                var mvMatrix = mat4.create();
                var mvMatrixStack = [];
                var pMatrix = mat4.create();

                function mvPushMatrix() {
                    var copy = mat4.create();
                    mat4.set(mvMatrix, copy);
                    mvMatrixStack.push(copy);
                }

                function mvPopMatrix() {
                    if (mvMatrixStack.length == 0) {
                        throw "Invalid popMatrix!";
                    }
                    mvMatrix = mvMatrixStack.pop();
                }


                function setMatrixUniforms() {
                    gl.uniformMatrix4fv(shaderProgram.pMatrixUniform, false, pMatrix);
                    gl.uniformMatrix4fv(shaderProgram.mvMatrixUniform, false, mvMatrix);

                    var normalMatrix = mat3.create();
                    mat4.toInverseMat3(mvMatrix, normalMatrix);
                    mat3.transpose(normalMatrix);
                    gl.uniformMatrix3fv(shaderProgram.nMatrixUniform, false, normalMatrix);
                }


                function degToRad(degrees) {
                    return degrees * Math.PI / 180;
                }

                var mouseDown = false; //mouse manipulation code
                var lastMouseX = null;
                var lastMouseY = null;
                var left, right, middle, isleft, isright, ismiddle;
                left = 0; //http://www.quirksmode.org/js/events_properties.html#button
                right = 2;
                middle = 1;
                isleft = false;
                isright = false;
                ismiddle = false;

                var modelRotationMatrix = mat4.create();
                mat4.identity(modelRotationMatrix);
                var translation = [0, 0, 0]; // for mouse driven translation

                function handleMouseDown(event) {

                    mouseDown = true;
                    switch(event.button){
                        case left:
                            isleft = true;
                            isright = false;
                            ismiddle = false;
                        break;
                        case right:
                            isright = true;
                            isleft = false;
                            ismiddle = false;
                        break; 
                        case middle:
                            isright = false;
                            isleft = false;
                            ismiddle = true;
                        break; 
                        default:
                            isleft = false;
                            isright = false;
                            ismiddle = false;
                    }
                    lastMouseX = event.clientX;
                    lastMouseY = event.clientY;

                }


                function handleMouseUp(event) {
                    mouseDown = false;
                }


                function handleMouseMove(event) {
                    if (!mouseDown) {
                        return;
                    }
                    var newX = event.clientX;
                    var newY = event.clientY;
                    var deltaX = newX - lastMouseX
                    var deltaY = newY - lastMouseY;
                    if (isleft){
                        var newRotationMatrix = mat4.create();
                        mat4.identity(newRotationMatrix);
                        mat4.rotate(newRotationMatrix, degToRad(deltaX / 10), [0, 1, 0]);
                        mat4.rotate(newRotationMatrix, degToRad(deltaY / 10), [1, 0, 0]);
                        mat4.multiply(newRotationMatrix, modelRotationMatrix, modelRotationMatrix);
                    }
                    if (isright){
                        var newtranslation = [0, 0, 0];
                        newtranslation = [(deltaX / 10), (-deltaY / 10), 0]; //paning
                        for (i = 0; i < 3; i++){
                            translation[i] = translation[i] + newtranslation[i];
                        }
                    } 
                    if (ismiddle){
                        var newtranslation = [0, 0, 0];
                        newtranslation = [0, 0, (-deltaY)]; //zoom
                        for (i = 0; i < 3; i++){
                            translation[i] = translation[i] + newtranslation[i];
                        }
                    }
                    
                    
 


                    lastMouseX = newX
                    lastMouseY = newY;
                }


                var modelVertexPositionBuffer;
                var modelVertexNormalBuffer;

                function initBuffers() {

                    modelVertexPositionBuffer = gl.createBuffer();
                    gl.bindBuffer(gl.ARRAY_BUFFER, modelVertexPositionBuffer);
                    vertices = 
                    $verticesData //vertices placeholder 
                    ;
                    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
                    modelVertexPositionBuffer.itemSize = 3;
                    modelVertexPositionBuffer.numItems = $itemsData; //number of vertex placeholder

                    modelVertexNormalBuffer = gl.createBuffer();
                    gl.bindBuffer(gl.ARRAY_BUFFER, modelVertexNormalBuffer);
                    var vertexNormals = 
                    $vertexnormalsData //vertex normals placeholder
                    ;
                    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexNormals), gl.STATIC_DRAW);
                    modelVertexNormalBuffer.itemSize = 3;
                    modelVertexNormalBuffer.numItems = $itemsData; //number of vertex placeholder

                }

                var rModel = 0;

                function drawScene() {
                    gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
                    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

                    mat4.perspective(45, gl.viewportWidth / gl.viewportHeight, 0.1, 30*$bbMax, pMatrix);

                    mat4.identity(mvMatrix);

                    mat4.translate(mvMatrix, [-5.0, -5.0, -3*$bbMax]);

                    mat4.translate(mvMatrix, translation);
                    mat4.multiply(mvMatrix, modelRotationMatrix);

                    gl.bindBuffer(gl.ARRAY_BUFFER, modelVertexPositionBuffer);
                    gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, modelVertexPositionBuffer.itemSize, gl.FLOAT, false, 0, 0);

                    gl.bindBuffer(gl.ARRAY_BUFFER, modelVertexNormalBuffer);
                    gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, modelVertexNormalBuffer.itemSize, gl.FLOAT, false, 0, 0);

                    var lighting = 1;
                    gl.uniform1i(shaderProgram.useLightingUniform, lighting);
                    if (lighting) {
                        gl.uniform3f(
                            shaderProgram.ambientColorUniform,
                            0.1, 0.1, 0.1
                        );

                        var lightingDirection = [
                            0.25, -0.25, -0.5
                        ];
                        var adjustedLD = vec3.create();
                        vec3.normalize(lightingDirection, adjustedLD);
                        vec3.scale(adjustedLD, -1);
                        gl.uniform3fv(shaderProgram.lightingDirectionUniform, adjustedLD);

                        gl.uniform3f(
                            shaderProgram.directionalColorUniform,
                            0.7, 0.7, 0.7
                        );
                    }

                    setMatrixUniforms();
                    gl.drawArrays(gl.TRIANGLES, 0, modelVertexPositionBuffer.numItems);


                }



                function tick() {
                    requestAnimFrame(tick);
                    drawScene();
                }


                function webGLStart() {
                    var canvas = document.getElementById("fc-test");
                    initGL(canvas);
                    initShaders()
                    initBuffers();

                    gl.clearColor(0.0, 0.0, 0.0, 1.0);
                    gl.enable(gl.DEPTH_TEST);

                    canvas.onmousedown = handleMouseDown; //mouse events
                    document.onmouseup = handleMouseUp;
                    document.onmousemove = handleMouseMove;

                    tick();

                }

            </script>


            </head>


            <body onload="webGLStart();" oncontextmenu="return false;">
                <canvas id="fc-test" style="border: none;" width="800" height="600"></canvas>



            </body>

            </html>"""
    
    return result
        
