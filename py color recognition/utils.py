import numpy as np
import cv2
from naoqi import ALProxy


def getCameraFeed(robotIP, port, camera, showContour=False):
    if showContour:
        coords = getCoordinatesFromFile("coordinates_ONE_FINGER.txt")

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

                cv2.line(image, coords[i+1], coords[0], (255, 0, 0), 2)

            cv2.imshow("Camera", image)

            # exit by [ESC]
            if cv2.waitKey(33) == 27:
                videoDevice.stop(camera)
                break
            elif cv2.waitKey(33) == 32:
                img_name = "test_images/finger_obj{}.png".format(img_counter)
                img_counter += 1
                cv2.imwrite(img_name, image)
                print "Saved img"


def getCoordinatesFromFile(path):
    # file = open(path, 'r')

    # coords = []
    with open(path) as f:
        lines = f.readlines()

    coords = [tuple(map(int, line.split(" "))) for line in lines]
    return coords

    # for l in file:
    #     row = l.split()
    #     coords.append(tuple(row[0], row[1]))


def getCoordinatesOfContour(img):
    file = open('coordinates_ONE_FINGER.txt', 'a')
    file.truncate(0)

    image = cv2.imread(img)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((5, 5), np.float) / 25

    gaussian_blur = cv2.filter2D(gray_image, -1, kernel)

    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # find threshold of the image
    _, thrash = cv2.threshold(gaussian_blur, 170, 250, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

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


if __name__ == "__main__":
    robotIp = "192.168.90.238"
    port = 9559

    topCamera = 0
    bottomCamera = 1

    # getCameraFeed(robotIp, port, bottomCamera)
    # getCoordinatesOfContour("InkedFINGER_imag_frame_0.jpg")
    getCameraFeed(robotIp, port, 1, False)
