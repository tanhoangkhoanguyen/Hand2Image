import cv2, math, time
import numpy as np
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import HandTrackingModule as htm  # FIX 1: removed duplicate import

# Camera setup
wCam, hCam = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

# Hand detector
detector = htm.handDetector(detectionCon=0.7)

# Audio setup
devices = AudioUtilities.GetSpeakers()
devices = AudioUtilities.GetSpeakers()
interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
# FIX 3: removed stray volume.SetMaster.VolumeLevel(0, None) line
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0  # FIX 5: was 400, should start at 0

while True:
    success, img = cap.read()

    img = detector.findHands(img=img, draw=True)
    lmList = detector.findPosition(img=img, draw=False)

    if lmList:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        vol    = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)          # FIX 4: use `vol`, not 0

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (225, 0, 0), 3)              # FIX 6: retangle → rectangle
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (225, 0, 0), cv2.FILLED)  # FIX 6+7: retangle → rectangle, vol → volBar
    cv2.putText(img, f"{int(volPer)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 3, (225, 0, 0), 3)

    cTime = time.time()
    fps   = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (40, 50), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 255), 3)

    cv2.imshow("Img", img)
    cv2.waitKey(1)