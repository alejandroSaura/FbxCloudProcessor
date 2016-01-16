from subprocess import Popen
from subprocess import call
import os  
import threading

from PIL import Image 
import MyScene

def GetTextures(fileName) :
    scene = MyScene.Scene()        
    scene.InitializeScene("Temporal/"+fileName+".FBX", None)
    scene.InitializeCamera(0);
    scene.setTime(0)
    textures = scene.extractAllTextures(scene.root) 
    # those could be duplicated, process this list:
    unifiedTextures = []
    for t in textures:
        found = False
        for ut in unifiedTextures:
            if ( t == ut) : 
                found = True
                break
        if not found : unifiedTextures.append(t)

    return unifiedTextures

def CreateAnimationSheet(fileName) :

    # Animation Sheet Parameters:
    imageWidth = 256   
    imageHeight = 256
    numberOfFrames = 8;
    animationLength = 100;

    # list of camera angles
    cameraAngleList = [0, 45, 90, 135, 180, -135, -90, -45]

    #def compareBoundaries(bound1, bound2) :
    #    result = []
    #    maxX = max(bound1[0][0], bound2[0][0])
    #    minX = min(bound1[7][0], bound2[7][0])
    #    maxY = max(bound1[0][1], bound2[0][1])
    #    minY = min(bound1[7][1], bound2[7][1])
    #    maxZ = max(bound1[0][2], bound2[0][2])
    #    minZ = min(bound1[7][2], bound2[7][2])
    #    result.append([maxX, maxY, maxZ, 1])
    #    result.append([maxX, minY, maxZ, 1]) 
    #    result.append([minX, maxY, maxZ, 1])
    #    result.append([minX, minY, maxZ, 1])
    #    result.append([maxX, maxY, minZ, 1])
    #    result.append([maxX, minY, minZ, 1])
    #    result.append([minX, maxY, minZ, 1])
    #    result.append([minX, minY, minZ, 1]) 
    #    return result       

    # calculate max world boundaries in projected coordinates
    print "Calculating scene boundaries..."
    
    globalBoundaries = None
    #count = list(range(numberOfFrames))     
    #for i in count :                
    #    frame = int((animationLength/numberOfFrames)*i)
    #    print "Calculating boundaries: frame " + str(frame)
    #    scene = MyScene.Scene()        
    #    scene.InitializeScene("Assets/"+fileName+".FBX", None)
    #    scene.InitializeCamera(0);
    #    scene.setTime(int(frame))
    #    scene.exploreScene(scene.root) 
    #    boundaries = scene.calculateWorldBoundaries() #Projected
    #    if globalBoundaries != None :
    #        globalBoundaries = compareBoundaries(boundaries, globalBoundaries)
    #    else :
    #        globalBoundaries = boundaries

    # We take just the first frame of the front camera Angle for time sake
    scene = MyScene.Scene()        
    scene.InitializeScene("Temporal/"+fileName+".FBX", None)
    scene.InitializeCamera(0);
    scene.setTime(0)
    scene.exploreScene(scene.root) 
    boundaries = scene.calculateProjectedBoundaries() #Projected
    globalBoundaries = boundaries

    maxX = globalBoundaries[0][0] - globalBoundaries[0][0]*0.2    
    minX = globalBoundaries[2][0] - globalBoundaries[2][0]*0.2
    maxY = globalBoundaries[0][1] - globalBoundaries[0][1]*0.2   
    minY = globalBoundaries[1][1] - globalBoundaries[1][1]*0.2
    maxZ = globalBoundaries[0][2] - globalBoundaries[0][0]*0.2    
    minZ = globalBoundaries[7][2] - globalBoundaries[7][0]*0.2

    minX = -maxX
    minY = -maxY
    minZ = -maxZ

     
    for k in cameraAngleList :       

        # array of process
        pArray = []

        # launch one process per frame
        count = list(range(numberOfFrames))
        for i in count :
            frame = int((animationLength/numberOfFrames)*i)
            pArray.append(Popen(["python", "FrameProcessor.py", str(frame), str(k), str(imageWidth), str(imageHeight), fileName, str(maxX), str(maxY), str(maxZ), str(minX), str(minY), str(minZ)]))

        # wait for all processes to finish
        for i in count :         
                pArray[i].wait()

        print "FBXProcessor: All frames rendered for camera angle: " + str(k)



    # take the images from /Temporal and compose them into the animations sheet
    # one row per camera view, 8 camera views

    animationSheet = Image.new('RGB', (imageWidth*numberOfFrames, imageHeight*8))

    rowCount = list(range(8))
    columnCount = list(range(numberOfFrames))
    for row in rowCount:
        for column in columnCount:
            frameNumber = int((animationLength/numberOfFrames)*column)
            im = Image.open("Temporal/"+str(cameraAngleList[row]) + "_" + fileName + "_" + str(frameNumber) + ".PNG")
            animationSheet.paste(im, (column*imageWidth,row*imageHeight))

    animationSheet.save("Temporal/animationSheet.PNG")

