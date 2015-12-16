import time
import BaseHTTPServer
import json
import os.path
import sys

import urllib2

from subprocess import Popen
import os  

from FBXProcessor import CreateAnimationSheet
 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_POST(s):

        s.send_response(200)        
        
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

        print "Server: FBX file fetched"

        # here we have the (TO-DO: list-of) FBX to process
        CreateAnimationSheet()
    
            
# server start :
#httpd = BaseHTTPServer.HTTPServer(("0.0.0.0", 8000), MyHandler)
#httpd.serve_forever()
CreateAnimationSheet("Maskboy")
