import time
import BaseHTTPServer
import json

import sys


import urllib2


import MyScene
import MyRenderer
  
 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
 

  def do_GET(s):
     
    print "request received"

    imageWidth = 500
    imageHeight = 500   

    path = s.path    
    filepath = path[1:]   
    
    """req = urllib2.Request('https://www.dropbox.com/s/48fpvxdvk4l4qv2/cubeMan.fbx?dl=1')
    req.add_header('Content-Type', 'application/octet-stream')
    r = urllib2.urlopen(req)
      
    object = r.read()    

    newFile = open ("object.fbx", 'wb')
    newFile.write(object);
    newFile.close()"""  

    renderer = MyRenderer.Renderer(imageWidth, imageHeight)

    scene = MyScene.Scene()        
    scene.InitializeScene("TestMesh02.fbx", renderer)  
    scene.Render()

    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    s.wfile.write("<html><head><title>FBX online counter</title></head>")
    s.wfile.write("<body><p>Put the fbx file path in the URL</p>")
    """s.wfile.write("<p>Vertex count: %s</p>" % (vertexCount))"""    
    s.wfile.write("</body></html>")

httpd = BaseHTTPServer.HTTPServer(("localhost", 8000), MyHandler)
httpd.serve_forever()