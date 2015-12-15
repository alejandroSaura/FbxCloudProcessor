import MyScene
import MyRenderer
import sys

arguments = sys.argv
frameNumber = arguments[1]
cameraAngle = int(arguments[2])

imageWidth = int(arguments[3])   
imageHeight = int(arguments[4]) 

renderer = MyRenderer.Renderer(imageWidth, imageHeight)

scene = MyScene.Scene()        
scene.InitializeScene("Assets/Maskboy.FBX", renderer)  
scene.InitializeCamera(cameraAngle);
scene.setTime(int(frameNumber))
scene.exploreScene(scene.root)
print "FrameProcessor: Starting render of frame "+ frameNumber +'\n'
scene.Render(str(cameraAngle) + "_" + "render_"+frameNumber)
print "FrameProcessor: frame " + frameNumber + " rendered"+'\n'

