from naoqi import ALProxy
from utils_file import *
from utils_color import *


def getCameraFeed(robotIP, port, camera, showContour=False):
    if showContour:
        coords = getCoordinatesFromFile("coords/coordinates_ONE_FINGER_FIN.txt")

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

    img_counter = 1

    while True:

        # get image
        result = videoDevice.getImageRemote(captureDevice)

        if result is None:
            print 'cannot capture.'
        elif result[6] is None:
            print 'no image data string.'
        else:
            i = 0
            image = getMatValues(result, height, width)

            if showContour:
                for i in range(0, len(coords) - 1):
                    cv2.line(image, coords[i], coords[i + 1], (255, 0, 0), 1)

                cv2.line(image, coords[i + 1], coords[0], (255, 0, 0), 1)
                # c = [np.asarray([[
                #     [[126, 112]],
                #     [[127, 118]],
                #     [[152, 139]],
                #     [[159, 136]],
                #     [[171, 126]],
                #     [[170, 123]],
                #     [[162, 119]],
                #     [[146, 106]],
                #     [[139, 103]],
                #     [[130, 106]]
                # ]])]
                #
                # image = cv2.drawContours(image, c, -1, (0,255,0), 3)

            cv2.imshow("Camera", image)

            # exit by [ESC]
            if cv2.waitKey(33) == 27:
                videoDevice.stop(camera)
                videoDevice.unsubscribe(captureDevice)
                break
            elif cv2.waitKey(33) == 32:
                img_name = "training/im_{}.png".format(img_counter)
                img_counter += 1
                cv2.imwrite(img_name, image)
                print "Saved img"


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

    filePath = "coords/coordinates_ONE_FINGER_FIN.txt"
    cnt = getContourFromFile(filePath)
    # print cnt

    while True:
        # get image
        result = videoDevice.getImageRemote(captureDevice)

        if result is None:
            print 'cannot capture.'
        elif result[6] is None:
            print 'no image data string.'
        else:

            # translate value to mat
            image = getMatValues(result, height, width)

            # if frame % 2 == 0:
            domR, domG, domB = dominantColor(image=image, c=cnt)
            # colorImg = np.zeros_like(image)
            # colorImg[:] = (domB, domG, domR)

            colorPixel = np.uint8([[[domB, domG, domR]]])

            hsvPixel = cv2.cvtColor(colorPixel, cv2.COLOR_BGR2HSV)[0][0]

            cv2.imshow("Camera", image)

            currentColor = getColorHSV(hsvPixel[0], hsvPixel[1], hsvPixel[2])
            print "Current color: " + currentColor
            print "\n"

            if currentColor != "white" and currentColor != "black":
                videoDevice.unsubscribe(captureDevice)
                return currentColor


def saySomething(robotIP, port, words):
    tts = ALProxy("ALTextToSpeech", robotIP, port)
    tts.say(words)


def saySomethingSimple(tts, words):
    tts.say(words)


def eyeLEDs(robotIP, port):
    leds = ALProxy("ALLeds", robotIP, port)
    # params for rotate eyes: rgb, timeForRotation, totalDuration
    # color code is in hexa: 0x00RRGGBB
    leds.rotateEyes(0x0032DC4C, 1, 2)
    leds.on("FaceLeds")


def getMatValues(result, height=320, width=240):
    image = np.zeros((height, width, 3), np.uint8)
    values = map(ord, list(result[6]))
    i = 0
    for y in range(0, height):
        for x in range(0, width):
            image.itemset((y, x, 0), values[i + 0])
            image.itemset((y, x, 1), values[i + 1])
            image.itemset((y, x, 2), values[i + 2])
            i += 3

    return image

