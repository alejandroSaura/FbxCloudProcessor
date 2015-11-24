import time
import BaseHTTPServer
import json

import sys
import fbx
import urllib2

 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler): 

  def do_GET(s):
    """Count vertex of a fbx file on the server"""  

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

    """END MATHS"""

    cameraToWorld = [[ 1, 0, 0, 0],
                     [ 0, 1, 0, 0],
                     [ 0, 0, 1, 0],
                     [ 0, 0, 0, 0]]
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
                """Check if the polygon is facing the camera, discard it if not"""                         
                vertexIndicesArray.append(mesh.GetPolygonVertices())    
                             
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
            """orthographic projection - get rid of z component"""
            controlPoints[i] = [controlPoints[i][0], controlPoints[i][1]]
        return  

    """Main"""
    getVertices(root)    
    projectVertices()

    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    s.wfile.write("<html><head><title>FBX online counter</title></head>")
    s.wfile.write("<body><p>Put the fbx file path in the URL</p>")
    """s.wfile.write("<p>Vertex count: %s</p>" % (vertexCount))"""
    
    s.wfile.write("</body></html>")

httpd = BaseHTTPServer.HTTPServer(("localhost", 8000), MyHandler)
httpd.serve_forever()