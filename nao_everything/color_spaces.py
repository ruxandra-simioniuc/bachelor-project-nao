import numpy as np
import cv2
from naoqi import ALProxy

ip_addr = "192.168.90.238"
port_num = 9559

# get NAOqi module proxy
videoDevice = ALProxy('ALVideoDevice', ip_addr, port_num)

# subscribe top camera
# for subscribing to bottom camera = 1; top camera = 0
AL_kTopCamera = 1
AL_kQVGA = 1  # 320x240
AL_kBGRColorSpace = 13
FPS = 20
captureDevice = videoDevice.subscribeCamera(
    "test", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, FPS)


depthCamera = ALProxy('ALMovementDetection', ip_addr, port_num)
depth = depthCamera.getDepthSensitivity()
print(str(depth))

# if depthCamera.movementDetected():
#     print('detected')

# create image
width = 320
height = 240
image = np.zeros((height, width, 3), np.uint8)

bgr = [50, 60, 160]
thresh = 30

minBGR = np.array([bgr[0] - thresh, bgr[1] - thresh, bgr[2] - thresh])
maxBGR = np.array([bgr[0] + thresh, bgr[1] + thresh, bgr[2] + thresh])

while True:

    # get image
    result = videoDevice.getImageRemote(captureDevice)

    if result is None:
        print 'cannot capture.'
    elif result[6] is None:
        print 'no image data string.'
    else:

        # translate value to mat

        values = map(ord, list(result[6]))
        i = 0
        for y in range(0, height):
            for x in range(0, width):
                image.itemset((y, x, 0), values[i + 0])
                image.itemset((y, x, 1), values[i + 1])
                image.itemset((y, x, 2), values[i + 2])
                i += 3

        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        ycb_img = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        lab_img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        maskBGR = cv2.inRange(image, minBGR, maxBGR)
        resultBGR = cv2.bitwise_and(image, image, mask=maskBGR)

        # convert 1D array to 3D, then convert it to HSV and take the first element
        # this will be same as shown in the above figure [65, 229, 158]
        hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]

        minHSV = np.array([hsv[0] - thresh, hsv[1] - thresh, hsv[2] - thresh])
        maxHSV = np.array([hsv[0] + thresh, hsv[1] + thresh, hsv[2] + thresh])

        maskHSV = cv2.inRange(hsv_img, minHSV, maxHSV)
        resultHSV = cv2.bitwise_and(hsv_img, hsv_img, mask=maskHSV)

        # convert 1D array to 3D, then convert it to YCrCb and take the first element
        ycb = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2YCrCb)[0][0]

        minYCB = np.array([ycb[0] - thresh, ycb[1] - thresh, ycb[2] - thresh])
        maxYCB = np.array([ycb[0] + thresh, ycb[1] + thresh, ycb[2] + thresh])

        maskYCB = cv2.inRange(ycb_img, minYCB, maxYCB)
        resultYCB = cv2.bitwise_and(ycb_img, ycb_img, mask=maskYCB)

        # convert 1D array to 3D, then convert it to LAB and take the first element
        lab = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2LAB)[0][0]

        minLAB = np.array([lab[0] - thresh, lab[1] - thresh, lab[2] - thresh])
        maxLAB = np.array([lab[0] + thresh, lab[1] + thresh, lab[2] + thresh])

        maskLAB = cv2.inRange(lab_img, minLAB, maxLAB)
        resultLAB = cv2.bitwise_and(image, image, mask=maskLAB)

        gray_image = cv2.cvtColor(resultLAB, cv2.COLOR_BGR2GRAY)

        _, thrash = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        for contour in contours:
            shape = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            x_cor = shape.ravel()[0]
            y_cor = shape.ravel()[1] - 15
            area = cv2.contourArea(contour)

            if len(shape) > 12 and area >= (width*height)/120:
                cv2.drawContours(image, [shape], 0, (255, 0, 255), 2)
                cv2.putText(image, str(area), (x_cor, y_cor), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))

        #cv2.imshow("Camera", image)
        cv2.imshow("Result BGR", resultBGR)
        cv2.imshow("Result HSV", resultHSV)
        cv2.imshow("Result YCB", resultYCB)
        cv2.imshow("Output LAB", resultLAB)
        cv2.imshow("Gray LAB", gray_image)
        cv2.imshow("Contours", image)



    # exit by [ESC]
    if cv2.waitKey(33) == 27:
        videoDevice.stop(AL_kTopCamera)
        break
