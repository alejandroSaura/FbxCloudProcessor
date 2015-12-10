import MyScene
import MyRenderer
import sys

arguments = sys.argv
frameNumber = arguments[1]

imageWidth = 256   
imageHeight = 256
 

renderer = MyRenderer.Renderer(imageWidth, imageHeight)

scene = MyScene.Scene()        
scene.InitializeScene("Assets/Maskboy.FBX", renderer)  
scene.setTime(int(frameNumber))
scene.exploreScene(scene.root)
print "FrameProcessor: Starting render of frame "+ frameNumber +'\n'
scene.Render("render"+frameNumber)
print "FrameProcessor: frame " + frameNumber + " rendered"+'\n'

