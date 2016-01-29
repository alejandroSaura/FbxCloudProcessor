import MyScene
import MyRenderer
import sys

arguments = sys.argv
frameNumber = arguments[1]
cameraAngle = int(arguments[2])

imageWidth = int(arguments[3])   
imageHeight = int(arguments[4]) 

fileName = arguments[5]

maxX = float(arguments[6])
maxY = float(arguments[7])
maxZ = float(arguments[8])
minX = float(arguments[9])
minY = float(arguments[10])
minZ = float(arguments[11])

boundaries = []
boundaries.append([maxX, maxY, maxZ, 1])
boundaries.append([maxX, minY, maxZ, 1]) 
boundaries.append([minX, maxY, maxZ, 1])
boundaries.append([minX, minY, maxZ, 1])

boundaries.append([maxX, maxY, minZ, 1])
boundaries.append([maxX, minY, minZ, 1])
boundaries.append([minX, maxY, minZ, 1])
boundaries.append([minX, minY, minZ, 1])

renderer = MyRenderer.Renderer(imageWidth, imageHeight)

scene = MyScene.Scene()        
scene.InitializeScene("Temporal/"+fileName+".FBX", renderer)  
scene.InitializeCamera(cameraAngle);
scene.setTime(int(frameNumber))
scene.exploreScene(scene.root)
print "FrameProcessor: Starting render of frame "+ frameNumber +'\n'
scene.setBoundaries(boundaries)
scene.Render(str(cameraAngle) + "_" + fileName + "_" + frameNumber)
print "FrameProcessor: frame " + frameNumber + " rendered"+'\n'

#def testFrame(frameNumber, cameraAngle, imageWidth, imageHeight, fileName, maxX, maxY, maxZ, minX, minY, minZ) :
#    boundaries = []
#    boundaries.append([maxX, maxY, maxZ, 1])
#    boundaries.append([maxX, minY, maxZ, 1]) 
#    boundaries.append([minX, maxY, maxZ, 1])
#    boundaries.append([minX, minY, maxZ, 1])

#    boundaries.append([maxX, maxY, minZ, 1])
#    boundaries.append([maxX, minY, minZ, 1])
#    boundaries.append([minX, maxY, minZ, 1])
#    boundaries.append([minX, minY, minZ, 1])

#    renderer = MyRenderer.Renderer(imageWidth, imageHeight)

#    scene = MyScene.Scene()        
#    scene.InitializeScene("Temporal/"+fileName+".FBX", renderer)  
#    scene.InitializeCamera(cameraAngle);
#    scene.setTime(int(frameNumber))
#    scene.exploreScene(scene.root)
#    print "FrameProcessor: Starting render of frame "+ str(frameNumber) +'\n'
#    scene.setBoundaries(boundaries)
#    scene.Render(str(cameraAngle) + "_" + fileName + "_" + str(frameNumber))
#    print "FrameProcessor: frame " +  str(frameNumber) + " rendered"+'\n'