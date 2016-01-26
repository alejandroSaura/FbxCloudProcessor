import time
import BaseHTTPServer
import json
import os.path
import sys

import urllib2

from subprocess import Popen
import os, shutil  

from FBXProcessor import CreateAnimationSheet
from FBXProcessor import GetTextures
 
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_POST(s):

        # First, clean the temporal folder
        folder = 'Temporal'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception, e:
                print e

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

        print "Server: Fetching FBX file..."
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/octet-stream')
        r = urllib2.urlopen(req)
        object = r.read()
        newFile = open ('Temporal/'+fileToOpen, 'wb')
        newFile.write(object);
        newFile.close() 
        
        # Read the list of textures from fbx
        fileName = fileToProcess[:-4]
        fileName = fileName[6:]
        print 'Analysing needed textures'
        textures = GetTextures(fileName)

        print 'Server: Fetching needed textures...'
        for t in textures :
            t = t.replace('\\','/')
            url = "https://raw.githubusercontent.com/" + payload['repository']['full_name']+"/master/Input/"+t
            print 'Fetching '+t
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/octet-stream')
            r = urllib2.urlopen(req)
            object = r.read()
            newFile = open ('Temporal/'+t, 'wb')
            newFile.write(object);
            newFile.close()

        # Start creating animation sheet
        CreateAnimationSheet(fileName)
        print 'Server: FBX '+fileName+' processed'

        # TO-DO: push final image to the client's repository


    
            
# server start :
#httpd = BaseHTTPServer.HTTPServer(("0.0.0.0", 8000), MyHandler)
#httpd.serve_forever()

"""For stand-alone debug only"""
textures = GetTextures("Warrior")
CreateAnimationSheet("Warrior")
