import sys
import numpy as np
import cv2
from naoqi import ALProxy

# if len(sys.argv) <= 2:
#     print "parameter error"
#     print "python " + sys.argv[0] + " <ipaddr> <port>"
#     sys.exit()

ip_addr = "192.168.90.241"
port_num = 9559

# get NAOqi module proxy
videoDevice = ALProxy('ALVideoDevice', ip_addr, port_num)

# subscribe top camera
AL_kTopCamera = 0
AL_kQVGA = 1  # 320x240
AL_kBGRColorSpace = 13
captureDevice = videoDevice.subscribeCamera(
    "test", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

# create image
width = 320
height = 240
image = np.zeros((height, width, 3), np.uint8)

cx = int(width/2)
cy = int(height/2)

while True:

    # get image
    result = videoDevice.getImageRemote(captureDevice);

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

        hsv_frame = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        pixel_center = hsv_frame[cy, cx]
        hue_value = pixel_center[0]

        color = "Undefined"
        if hue_value < 5:
            color = "RED"
        elif hue_value < 22:
            color = "ORANGE"
        elif hue_value < 33:
            color = "YELLOW"
        elif hue_value < 78:
            color = "GREEN"
        elif hue_value < 131:
            color = "BLUE"
        elif hue_value < 170:
            color = "VIOLET"
        else:
            color = "RED"
        pixel_center_bgr = image[cy, cx]
        b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])

       # cv2.rectangle(image, (cx - 220, 10), (cx + 200, 120), (255, 255, 255), -1)
        cv2.putText(image, color, (cx-150, 25), 0, 1, (b, g, r), 5)
        cv2.circle(image, (cx, cy), 5, (25, 25, 25), 3)

        cv2.imshow("Frame", image)

        # # Red color
        # low_red = np.array([161, 155, 84])
        # high_red = np.array([179, 255, 255])
        # red_mask = cv2.inRange(hsv_frame, low_red, high_red)
        # red = cv2.bitwise_and(image, image, mask=red_mask)
        # # if cv2.countNonZero(red) == 0:
        # #     print("No red here")
        #
        # # Blue color
        # low_blue = np.array([94, 80, 2])
        # high_blue = np.array([126, 255, 255])
        # blue_mask = cv2.inRange(hsv_frame, low_blue, high_blue)
        # blue = cv2.bitwise_and(image, image, mask=blue_mask)
        #
        # # Green color
        # low_green = np.array([25, 52, 72])
        # high_green = np.array([102, 255, 255])
        # green_mask = cv2.inRange(hsv_frame, low_green, high_green)
        # green = cv2.bitwise_and(image, image, mask=green_mask)
        #
        # # Every color except white
        # low = np.array([0, 42, 0])
        # high = np.array([179, 255, 255])
        # mask = cv2.inRange(hsv_frame, low, high)
        # res = cv2.bitwise_and(image, image, mask=mask)
        # # show image
        # cv2.imshow("nao-top-camera-320x240", hsv_frame)
        # cv2.imshow("Frame", image)
        # cv2.imshow("Red", red)
        # cv2.imshow("Blue", blue)
        # cv2.imshow("Green", green)
        # cv2.imshow("Result", res)

    # exit by [ESC]
    if cv2.waitKey(33) == 27:
        break
