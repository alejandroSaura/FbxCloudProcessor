import time
import BaseHTTPServer
import json

import sys
import fbx
import urllib2


# example of a python class
 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler): 

  def do_GET(s):
    """Count vertex of a fbx file on the server"""  

    path = s.path    
    filepath = path[1:]     

    manager = fbx.FbxManager.Create()
    importer = fbx.FbxImporter.Create(manager, 'myImporter')

    req = urllib2.Request('https://www.dropbox.com/s/48fpvxdvk4l4qv2/cubeMan.fbx?dl=1')
    req.add_header('Content-Type', 'application/octet-stream')
    r = urllib2.urlopen(req)

    
    object = r.read()    

    newFile = open ("object.fbx", 'wb')
    newFile.write(object);
    newFile.close()
            

    status = importer.Initialize("object.fbx")
    if status == False :
      print 'fbx initialization failed'
      print 'Error: %s' % importer.GetLastErrorString()
      sys.exit()

    scene = fbx.FbxScene.Create( manager, 'myScene')
    importer.Import(scene)
    importer.Destroy()

    
    root = scene.GetRootNode() 
    
    
    vertexCount = 0

    def countVertex (node) :
        result = 0
        mesh = node.GetMesh()
        if(mesh != None) :
            result += mesh.GetPolygonVertexCount()
        childNumber = node.GetChildCount()
        count = list(range(childNumber))
        for i in count:
            result += countVertex(node.GetChild(i)) 
        return result
       
    vertexCount = countVertex(root)    

    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    s.wfile.write("<html><head><title>FBX online counter</title></head>")
    s.wfile.write("<body><p>Put the fbx file path in the URL</p>")
    s.wfile.write("<p>Vertex count: %s</p>" % (vertexCount))
    
    s.wfile.write("</body></html>")

httpd = BaseHTTPServer.HTTPServer(("0.0.0.0", 8000), MyHandler)
httpd.serve_forever()