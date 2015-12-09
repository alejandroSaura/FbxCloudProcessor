import time
import BaseHTTPServer
import json

import sys

import urllib2

import MyScene
import MyRenderer

imageWidth = 256   
imageHeight = 256
 
arguments = sys.argv
frameNumber = arguments[1]

renderer = MyRenderer.Renderer(imageWidth, imageHeight)

scene = MyScene.Scene()        
scene.InitializeScene("./Assets/Maskboy.FBX", renderer)  

#scene.clear()
scene.setTime(int(frameNumber))
scene.exploreScene(scene.root)
print "Starting render of frame: " + frameNumber
scene.Render("render"+frameNumber)
print "Finished render of frame: " + frameNumber
        

