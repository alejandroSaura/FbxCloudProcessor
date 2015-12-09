from subprocess import Popen
import os

numberOfFrames = 10;
animationLength = 100;

pArray = []

#launch one process per frame to render
count = list(range(numberOfFrames))
for i in count :
    frame = int((animationLength/numberOfFrames)*i)
    pArray.append(Popen(["python", "FbxCloudProcessor.py", str(frame)]))

#wait for all processes to finish
for i in count :         
        pArray[i].wait()

print "all frames rendered"

