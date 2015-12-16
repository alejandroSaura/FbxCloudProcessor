from subprocess import Popen
from subprocess import call
import os  

from PIL import Image 

def CreateAnimationSheet(fileName) :

    imageWidth = 256   
    imageHeight = 256

    numberOfFrames = 8;
    animationLength = 20;

    # we'll render all frames for each camera angle
    cameraAngleList = [0, 45, 90, 135, 180, -135, -90, -45]

    for k in cameraAngleList :

        # array of process
        pArray = []

        # launch one process per frame to render
        count = list(range(numberOfFrames))
        for i in count :
            frame = int((animationLength/numberOfFrames)*i)
            pArray.append(Popen(["python", "FrameProcessor.py", str(frame), str(k), str(imageWidth), str(imageHeight), fileName]))

        # wait for all processes to finish
        for i in count :         
                pArray[i].wait()

        print "FBXProcessor: All frames rendered for camera angle: " + str(k)



    # TO-DO: take the images from /Temporal and compose them into the animations sheet
    # one row per camera view, 8 camera views

    animationSheet = Image.new('RGB', (imageWidth*numberOfFrames, imageHeight*8))

    rowCount = list(range(8))
    columnCount = list(range(numberOfFrames))
    for row in rowCount:
        for column in columnCount:
            frameNumber = int((animationLength/numberOfFrames)*column)
            im = Image.open("Temporal/"+str(cameraAngleList[row]) + "_" + fileName + "_" + str(frameNumber) + ".PNG")
            animationSheet.paste(im, (column*imageWidth,row*imageHeight))

    animationSheet.save("animationSheet.PNG")
     

    # TO-DO: push final image to the client's repository

    # TO-DO: delete contents on temporal

