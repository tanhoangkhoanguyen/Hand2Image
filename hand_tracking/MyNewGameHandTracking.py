import HandTrackingModule as htm

import cv2, time
import mediapipe as mp

cap = cv2.VideoCapture(0)
pTime = cTime = 0
detector = htm.handDetector()

while True:
    success, img = cap.read()

    img = detector.findHands(
            img = img,
            draw = False
        )
    lmList = detector.findPosition(
            img = img, 
            draw = False
        )
    if lmList and len(lmList) > 4:
        print (lmList[4])

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)