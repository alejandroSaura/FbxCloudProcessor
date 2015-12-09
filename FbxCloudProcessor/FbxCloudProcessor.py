import time
import BaseHTTPServer
import json
import os.path
import sys

import urllib2

from subprocess import Popen
import os

  
 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_POST(s):
        s.send_response(200)
        imageWidth = 256   
        imageHeight = 256
        
        length = int(s.headers.getheader('content-length'))
        payload = json.loads(s.rfile.read(length))

        
        fileToProcess = {}
        fileToOpen = {}
        commits = payload['commits']
        for x in range (0,len(commits)):
            modified = commits[x]['modified']
            for y in range (0,len(modified)):
                print(modified[y])
            added = commits[x]['added']
            for y in range (0,len(added)):
                print(added[y])
                fileToProcess = added[y]
                fileToOpen = os.path.basename(added[y])

       # url = "https://raw.githubusercontent.com/kt-chin/CloudComputingClient/master/Input/Maskboy.FBX"
        url = "https://raw.githubusercontent.com/" + payload['repository']['full_name']+"/master"+"/"+fileToProcess

        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/octet-stream')
        r = urllib2.urlopen(req)
        object = r.read()
        newFile = open (fileToOpen, 'wb')
        newFile.write(object);
        newFile.close()

       # ouputUrl = ""

        #renderer = MyRenderer.Renderer(imageWidth, imageHeight)

        #scene = MyScene.Scene()        
        #scene.InitializeScene("./Assets/Maskboy.FBX", renderer)  
        #print "Starting render..."
        #scene.Render()
        #print "Render finished..."
        #s.send_header("Content-type", "text/html")
        #s.end_headers()
        #s.wfile.write("<html><head><title>My first webhook!</title></head>")
        #s.wfile.write("<p>It should finish rendering</p>")
        #s.wfile.write("</body></html>")

        
    
    #def do_GET(s):
    #    s.send_response(200)        

#httpd = BaseHTTPServer.HTTPServer(("0.0.0.0", 8000), MyHandler)
#httpd.serve_forever()


numberOfFrames = 10;
animationLength = 100;

pArray = []

#launch one process per frame to render
count = list(range(numberOfFrames))
for i in count :
    frame = int((animationLength/numberOfFrames)*i)
    pArray.append(Popen(["python", "CloudManager.py", str(frame)]))

#wait for all processes to finish
for i in count :         
        pArray[i].wait()

print "all frames rendered"


    #imageWidth = 256   
    #imageHeight = 256
 

    #renderer = MyRenderer.Renderer(imageWidth, imageHeight)

    #scene = MyScene.Scene()        
    #scene.InitializeScene("Assets/MAskboy.FBX", renderer)  
    #print "Starting render..."
    #scene.Render()
    #print "Render finished..."
