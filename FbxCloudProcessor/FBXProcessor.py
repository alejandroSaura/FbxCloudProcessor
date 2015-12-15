from subprocess import Popen
from subprocess import call
import os  

from PIL import Image 

def CreateAnimationSheet() :

    imageWidth = 128   
    imageHeight = 128

    numberOfFrames = 6;
    animationLength = 100;

    # we'll render all frames for each camera angle
    cameraAngleList = [0, 45, 90, 135, 180, -135, -90, -45]

    for k in cameraAngleList :

        # array of process
        pArray = []

        # launch one process per frame to render
        count = list(range(numberOfFrames))
        for i in count :
            frame = int((animationLength/numberOfFrames)*i)
            pArray.append(Popen(["python", "FrameProcessor.py", str(frame), str(k), str(imageWidth), str(imageHeight)]))

        # wait for all processes to finish
        for i in count :         
                pArray[i].wait()

        print "FBXProcessor: All frames rendered for camera angle: " + str(k)



    # TO-DO: take the images from /Temporal and compose them into the animations sheet
    # one row per camera view, 4 camera views
    #animationSheet = Image.new('RGB', (imageWidth*numberOfFrames, imageHeight*4))

    # TO-DO: push final image to the client's repository

    # TO-DO: delete contents on temporal

