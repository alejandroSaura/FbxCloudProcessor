from subprocess import Popen
from subprocess import call
import os  

def CreateAnimationSheet() :

    imageWidth = 256   
    imageHeight = 256

    numberOfFrames = 16;
    animationLength = 100;

    # array of process
    pArray = []

    # launch one process per frame to render
    count = list(range(numberOfFrames))
    for i in count :
        frame = int((animationLength/numberOfFrames)*i)
        pArray.append(Popen(["python", "FrameProcessor.py", str(frame)]))

    # wait for all processes to finish
    for i in count :         
            pArray[i].wait()

    print "FBXProcessor: All frames rendered"

    # TO-DO: take the images from /Temporal and compose them into the animations sheet

    # TO-DO: push final image to the client's repository

    # TO-DO: delete contents on temporal

