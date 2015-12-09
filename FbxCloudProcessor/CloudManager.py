import MyScene
import MyRenderer
import sys

arguments = sys.argv
frameNumber = arguments[1]

imageWidth = 256   
imageHeight = 256
 

renderer = MyRenderer.Renderer(imageWidth, imageHeight)

scene = MyScene.Scene()        
scene.InitializeScene("Assets/MAskboy.FBX", renderer)  
scene.setTime(int(frameNumber))
scene.exploreScene(scene.root)
print "Starting render of frame "+ frameNumber
scene.Render("render"+frameNumber)
print "End render of frame "+ frameNumber

