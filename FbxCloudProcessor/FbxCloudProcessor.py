import time
import BaseHTTPServer
import json

import sys
import fbx
import svgwrite
import urllib2
import math

 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler): 

  def do_GET(s):
    """Count vertex of a fbx file on the server"""  

    imageWidth = 500
    imageHeight = 500

    maxRenderX = 100
    maxRenderY = 100

    path = s.path    
    filepath = path[1:]     

    manager = fbx.FbxManager.Create()
    importer = fbx.FbxImporter.Create(manager, 'myImporter')

    """req = urllib2.Request('https://www.dropbox.com/s/48fpvxdvk4l4qv2/cubeMan.fbx?dl=1')
    req.add_header('Content-Type', 'application/octet-stream')
    r = urllib2.urlopen(req)

    
    object = r.read()    

    newFile = open ("object.fbx", 'wb')
    newFile.write(object);
    newFile.close()"""
            

    """status = importer.Initialize("object.fbx")"""
    status = importer.Initialize("TestMesh.FBX")
    if status == False :
      print 'fbx initialization failed'
      print 'Error: %s' % importer.GetLastErrorString()
      sys.exit()

    scene = fbx.FbxScene.Create( manager, 'myScene')
    importer.Import(scene)
    importer.Destroy()

    
    root = scene.GetRootNode() 

    """MATHS"""

    def transposeMatrix (matrix) :

        """from 'python cookbook' """
        t = [[r[col] for r in matrix] for col in range(len(matrix[0]))] 

        return t

    def vectorDotMatrix (vector, matrix) :

        result = [0] * 4
        for i in range(4) :
            result[i] = vector[0] * matrix[0][i] + vector[1] * matrix[1][i] + vector[2] * matrix[2][i] + vector[3] * matrix[3][i]
        
        return result

    def matrixDotMatrix (m1, m2) :
        result = [[ 1, 0, 0, 0],
                  [ 0, 1, 0, 0],
                  [ 0, 0, 1, 0],
                  [ 0, 0, 0, 0]]
        for i in range(4) :
            for j in range(4) :
                result[i][j] = m1[i][0] * m2[0][j] + m1[i][1] * m2[1][j] + m1[i][2] * m2[2][j] + m1[i][3] * m2[3][j];
        return result

    def rotateMatrix (matrix, Yaw, Pitch, Roll) :

        y = Yaw * math.pi/180;
        x = Pitch * math.pi/180;
        z = Roll * math.pi/180;
        result = matrix

        yawRotationMatrix = [[ math.cos(y), 0, -math.sin(y), 0],
                            [ 0, 1, 0, 0],
                            [ math.sin(y), 0, math.cos(y), 0],
                            [ 0, 0, 0, 0]]
        result = matrixDotMatrix(result, yawRotationMatrix);

        pitchRotationMatrixLocal = [[ 1, 0, 0, 0],
                            [ 0, math.cos(x), math.sin(x), 0],
                            [ 0, -math.sin(x), math.cos(x), 0],
                            [ 0, 0, 0, 0]]
        """F(g->g) = I(g->l) * F(l->l) * I(l->g) . Transform local->local rotation to global->global"""
        pitchRotationMatrixGlobal = matrixDotMatrix(matrixDotMatrix(transposeMatrix(result), pitchRotationMatrixLocal), result)
        result = matrixDotMatrix(result, pitchRotationMatrixGlobal);

        rollRotationMatrixLocal = [[ math.cos(z), math.sin(z), 0, 0],
                            [ -math.sin(z), math.cos(z), 0, 0],
                            [ 0, 0, 1, 0],
                            [ 0, 0, 0, 0]]
        rollRotationMatrixGlobal = matrixDotMatrix(matrixDotMatrix(transposeMatrix(result), rollRotationMatrixLocal), result)
        result = matrixDotMatrix(result, rollRotationMatrixGlobal);        

        return result

    def interpolate3Vectors(v1, v2, v3) :
        result = [0, 0, 0, 0]
        for i in range(4):
            result[i] = (v1[i] + v2[i] + v3[i])/3
        return result

    def vector4ScalarProduct (v1, v2) :
        result = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2];
        return result;

    """END MATHS"""

    cameraToWorld = [[ 1, 0, 0, 0],
                     [ 0, 1, 0, 0],
                     [ 0, 0, 1, 0],
                     [ 0, 0, 0, 0]]    
    """rotate the camera to have an isometric point of view"""
    cameraToWorld = rotateMatrix(cameraToWorld, -180, 45, 0)
    worldToCamera = transposeMatrix(cameraToWorld)

    controlPoints = [];
    vertexIndicesArray = []

    def getVertices (node) :

        mesh = node.GetMesh()        
        if(mesh != None and mesh.IsTriangleMesh()) :

            cPoints = mesh.GetControlPoints();
            count = list(range(len(cPoints)))
            for i in count:
                controlPoints.append(cPoints[i])

            polygonCount = mesh.GetPolygonCount()
            count = list(range(polygonCount))
            for i in count:       
                """Get indices for the current triangle"""   
                _indices = []   
                for j in range(0, 3): 
                    _indices.append(mesh.GetPolygonVertex(i, j))

                """Check if the polygon is facing the camera, discard it if not"""                

                _normals = []
                for j in range(0, 3): 
                    normal = fbx.FbxVector4()
                    mesh.GetPolygonVertexNormal(i, j, normal)                    
                    _normals.append([normal[0], normal[1], normal[2], normal[3]])

                """Here we have the normals of the 3 vertices. Interpolate and compare with the camera z vector"""
                interpolatedNormal = interpolate3Vectors(_normals[0], _normals[1], _normals[2])
                if (vector4ScalarProduct(interpolatedNormal, cameraToWorld[2]) > 0) :
                    vertexIndicesArray.append(_indices)

                                                   
                        
                             
        childNumber = node.GetChildCount()
        count = list(range(childNumber))
        for i in count:
            getVertices(node.GetChild(i))   
                           
        return     
    
    def projectVertices () :

        count = range(len(controlPoints))
        for i in count:       
            """controlPoints world->camera space"""                         
            controlPoints[i] = vectorDotMatrix(controlPoints[i], worldToCamera)
            """orthographic projection: get rid of z component, normalize respect the image size and adapt to svg coordinates (Y axis inverted)"""
            controlPoints[i] = [controlPoints[i][0]/maxRenderX*imageWidth + imageWidth/2, -controlPoints[i][1]/maxRenderY*imageHeight + imageWidth/2]
        return  

    """Main"""
    getVertices(root)    
    projectVertices()       

    dwg = svgwrite.Drawing('testTriangle.svg' ,size=(imageWidth, imageHeight))
    """we draw a polygon for each entry in vertexIndicesArray"""
    count = range(len(vertexIndicesArray))
    for i in count:
        polygon = svgwrite.shapes.Polygon()
        for j in range(0,3) :            
            """take the corresponding control points for forming this polygon"""
            polygon.points.append(controlPoints[vertexIndicesArray[i][j]])
        dwg.add(polygon)     
       
    dwg.save()

    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    s.wfile.write("<html><head><title>FBX online counter</title></head>")
    s.wfile.write("<body><p>Put the fbx file path in the URL</p>")
    """s.wfile.write("<p>Vertex count: %s</p>" % (vertexCount))"""
    
    s.wfile.write("</body></html>")

httpd = BaseHTTPServer.HTTPServer(("localhost", 8000), MyHandler)
httpd.serve_forever()