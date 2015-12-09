import time
import BaseHTTPServer
import json

import sys


import urllib2


import MyScene
import MyRenderer
  
 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_POST(s):
        s.send_response(200)
        imageWidth = 256   
        imageHeight = 256
 

        renderer = MyRenderer.Renderer(imageWidth, imageHeight)

        scene = MyScene.Scene()        
        scene.InitializeScene("./Assets/Maskboy.FBX", renderer)  
        print "Starting render..."
        scene.Render()
        print "Render finished..."
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>My first webhook!</title></head>")
        s.wfile.write("<p>It should finish rendering</p>")
        s.wfile.write("</body></html>")
    

httpd = BaseHTTPServer.HTTPServer(("0.0.0.0", 8000), MyHandler)
httpd.serve_forever()


    #imageWidth = 256   
    #imageHeight = 256
 

    #renderer = MyRenderer.Renderer(imageWidth, imageHeight)

    #scene = MyScene.Scene()        
    #scene.InitializeScene("Assets/MAskboy.FBX", renderer)  
    #print "Starting render..."
    #scene.Render()
    #print "Render finished..."
