import cv2  #opencv import
import time  #import time package (preinstalled)
import numpy as np #import numpy for lists (mostly preinstalled)
import HandTrackingModule as htm  #import another file
import math #for hypotenuse/distance function
from ctypes import cast, POINTER # import pycaw for sys vol adjust
from comtypes import CLSCTX_ALL #same
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume #same


cap = cv2.VideoCapture(0)#start webcam 0
cap.set(3, 640) #set heights limits
cap.set(4, 480)#set width limits

detector = htm.handDetector(detectionCon=0.5, maxHands=1) #confidence = 0.5 , detect only one hand

devices = AudioUtilities.GetSpeakers() #pycaw fetch speaker data
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None) #pycaw gt interface activated
volume = cast(interface, POINTER(IAudioEndpointVolume)) #pycaw cast interface vol values
volRange = volume.GetVolumeRange() #pycaw get range of volume (-65 -- 0)
minVol = volRange[0] #minimum of given vol range
maxVol = volRange[1] #maximum of given vol range

#for initial rectangle bar showing percentage
vol = 0 #can set to anything until hand comes in sight (0 for reference)
volBar = 400 #max range in screen of bar
volPer = 0 #can set to anything until hand comes in sight (0 for reference)
area = 0 #can set to anything until hand comes in sight (0 for reference)
colorVol = (255, 0, 0) #can set to anything until hand comes in sight (blue color for reference)

while True: #loop for video
    success, img = cap.read() #if image read successfully

    # Find Hand
    img = detector.findHands(img) #recognicce hand structure
    lmList, bbox = detector.findPosition(img, draw=True) #landmark list initialised
    if len(lmList) != 0: # for (no hand in sight)

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        # print(area)
        if 250 < area < 1000: #basis of area between 2 fingers right angled triangle

            # Find Distance between index and Thumb
            length, img, lineInfo = detector.findDistance(4, 8, img) #index=4 , thumb=8 , in hand

            # Convert Volume for rectangle
            volBar = np.interp(length, [50, 200], [400, 150])#graph has 150 to 400 in screen range()
            volPer = np.interp(length, [50, 200], [0, 100])#percentage in 0 to 100

            # Reduce Resolution to make it smoother
            smoothness = 10
            volPer = smoothness * round(volPer / smoothness)

            # Check fingers up
            fingers = detector.fingersUp()
            # print(fingers)

            # If pinky is down set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar((volPer / 100), None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255, 0, 0)

    # text for bar
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)



    cv2.imshow("Img", img)
    cv2.waitKey(1)