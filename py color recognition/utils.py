import numpy as np
import cv2
from naoqi import ALProxy
import test_simillarities


def getCameraFeed(robotIP, port, camera, showContour=False):
    if showContour:
        coords = getCoordinatesFromFile("coordinates_ONE_FINGER_pos4.txt")

    # get NAOqi module proxy
    videoDevice = ALProxy('ALVideoDevice', robotIP, port)

    # subscribe top camera
    # for subscribing to bottom camera = 1
    # AL_kTopCamera = 0
    AL_kQVGA = 1  # 320x240
    AL_kBGRColorSpace = 13
    FPS = 30
    captureDevice = videoDevice.subscribeCamera(
        "test", camera, AL_kQVGA, AL_kBGRColorSpace, FPS)

    # create image
    width = 320
    height = 240
    image = np.zeros((height, width, 3), np.uint8)

    img_counter = 0

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

            if showContour:
                for i in range(0, len(coords) - 1):
                    cv2.line(image, coords[i], coords[i + 1], (255, 0, 0), 2)

                cv2.line(image, coords[i + 1], coords[0], (255, 0, 0), 2)

            cv2.imshow("Camera", image)

            # exit by [ESC]
            if cv2.waitKey(33) == 27:
                videoDevice.stop(camera)
                break
            elif cv2.waitKey(33) == 32:
                img_name = "test_images/TEST2_finger_obj{}.png".format(img_counter)
                img_counter += 1
                cv2.imwrite(img_name, image)
                print "Saved img"


### Gets the coordinates from file and returns a data strucre as contour
def getContourFromFile(path):
    coords = getCoordinatesFromFile(path)
    cnt = []
    for c in coords:
        cnt.append([c])
    cnt = np.asarray(cnt)
    return [cnt]


def getCoordinatesFromFile(path):
    # file = open(path, 'r')

    # coords = []
    with open(path) as f:
        lines = f.readlines()

    coords = [tuple(map(int, line.split(" "))) for line in lines]
    return coords


def getCoordinatesOfContour(img, fileName='coordinates_ONE_FINGER_pos4.txt'):
    file = open(fileName, 'a')
    file.truncate(0)

    image = cv2.imread(img)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((5, 5), np.float) / 25

    gaussian_blur = cv2.filter2D(gray_image, -1, kernel)

    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # find threshold of the image
    _, thresh = cv2.threshold(gaussian_blur, 170, 250, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        shape = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        x_cor = shape.ravel()[0]
        y_cor = shape.ravel()[1] - 15
        area = cv2.contourArea(contour)

        if len(shape) > 8:  # and area >= (height * width) / 150:

            shapeMask = np.zeros(image.shape, dtype=np.uint8)
            cv2.fillPoly(shapeMask, [shape], (255, 255, 255))
            shapeMask = cv2.cvtColor(shapeMask, cv2.COLOR_BGR2GRAY)
            result = cv2.bitwise_and(image, image, mask=shapeMask)

            cv2.drawContours(image, [shape], 0, (255, 0, 255), 2)
            # cv2.putText(image, tag, (x_cor, y_cor), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
            n = shape.ravel()
            i = 0
            for j in n:
                if i % 2 == 0:
                    x = n[i]
                    y = n[i + 1]
                    string = str(x) + " " + str(y)
                    file.write(string)
                    file.write("\n")

                    if i == 0:
                        cv2.putText(image, "Arrow tip", (x, y),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))
                    else:
                        # text on remaining co-ordinates.
                        cv2.putText(image, string, (x, y),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0))
                i = i + 1

    cv2.imshow("Frame", image)
    cv2.waitKey()
    file.close()
    return contours


def getCameraFeedAndColor(robotIP, port):
    videoDevice = ALProxy('ALVideoDevice', robotIP, port)

    # subscribe top camera
    # for subscribing to bottom camera = 1
    AL_kTopCamera = 0
    AL_kBotCamera = 1
    AL_kQVGA = 1  # 320x240
    AL_kBGRColorSpace = 13
    FPS = 30
    captureDevice = videoDevice.subscribeCamera(
        "test", AL_kBotCamera, AL_kQVGA, AL_kBGRColorSpace, FPS)

    # create image
    width = 320
    height = 240
    image = np.zeros((height, width, 3), np.uint8)
    filePath = "coordinates_ONE_FINGER_pos4.txt"
    cnt = getContourFromFile(filePath)

    frame = 0
    print "Im here"

    while True:
        frame += 1
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

            # if frame % 2 == 0:
            domR, domG, domB = test_simillarities.dominantColor(image=image, c=cnt)
            # colorImg = np.zeros_like(image)
            # colorImg[:] = (domB, domG, domR)

            colorPixel = np.uint8([[[domB, domG, domR]]])

            hsvPixel = cv2.cvtColor(colorPixel, cv2.COLOR_BGR2HSV)[0][0]
            print "H = " + str(hsvPixel[0] * 2) + " S = " + str(hsvPixel[1]) + " v  = " + str(hsvPixel[0])

            #cv2.drawContours(image, [cnt[0]], -1, 255, -1)

            #cv2.imshow("Dom color", colorImg)

            #cv2.imshow("Camera", image)

            # if getColor(domR, domG, domB) != "white":
            #     return getColor(domR, domG, domB)

            currentColor = getColorHSV(hsvPixel[0], hsvPixel[1], hsvPixel[2])
            print "Current color: " + currentColor
            print "\n"

            if currentColor != "white" and currentColor != "black":
                return currentColor

            # exit by [ESC]
            # if cv2.waitKey(33) == 27:
            #     break


def getColor(r, g, b):
    if r > 185 and g > 185 and b > 185:
        return "white"
    elif r > 100 and g < 100 and b < 100:
        return "red"
    elif r < 100 and g < 100 and b > 100:
        return "blue"
    elif r < 100 and g > 100 and b < 100:
        return "green"
    else:
        return "white"


def getColorHSV(h, s, v):
    h = h * 2
    # s = s * 2
    # v = v * 2
    if s > 65 and v > 82:
        if h in range(0, 11) or h in range(340, 361):
            return "red"
        elif h in range(11, 41):
            return "orange"
        elif h in range(41, 71):
            return "yellow"
        elif h in range(71, 151):
            return "green"
        elif h in range(151, 261):
            return "blue"
        elif h in range(261, 286):
            return "purple"
        else:
            return "pink"
    elif v < 50 and s <= 100:
        return "black"
    else:
        return "white"




def saySomething(robotIP, port, words):
    tts = ALProxy("ALTextToSpeech", robotIP, port)
    tts.say(words)


def eyeLEDs(robotIP, port):
    leds = ALProxy("ALLeds", robotIP, port)
    # params for rotate eyes: rgb, timeForRotation, totalDuration
    # color code is in hexa: 0x00RRGGBB
    leds.rotateEyes(0x0032DC4C, 1, 2)
    leds.on("FaceLeds")


if __name__ == "__main__":
    robotIp = "192.168.90.238"
    port = 9559

    topCamera = 0
    bottomCamera = 1

    #getCameraFeed(robotIp, port, bottomCamera, False)
    #getCoordinatesOfContour("test_images/FINGER_draw_pos4.jpg")
    #getCameraFeed(robotIp, port, 1, True)

    getCameraFeedAndColor(robotIp, port)
