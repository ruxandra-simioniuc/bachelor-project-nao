import numpy as np
import cv2
import re


# sorts the dirs and files: 910 is after 99
def sort_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


# Reads the coordinates from file
def getCoordinatesFromFile(path):

    with open(path) as f:
        lines = f.readlines()

    coords = [tuple(map(int, line.split(" "))) for line in lines]
    return coords


# Gets the coordinates from file and returns a data structure as contour
def getContourFromFile(path):
    coords = getCoordinatesFromFile(path)
    cnt = []
    for c in coords:
        cnt.append([c])
    cnt = np.asarray(cnt)
    return [cnt]


# extracts the contour from img and writes its coordinates to the specified file
def getCoordinatesOfContour(img, fileName='coordinates_ONE_FINGER_FIN.txt'):
    file = open(fileName, 'a')
    file.truncate(0)

    image = cv2.imread(img)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((5, 5), np.float) / 25

    gaussian_blur = cv2.filter2D(gray_image, -1, kernel)

    # find threshold of the image
    _, thresh = cv2.threshold(gaussian_blur, 170, 250, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        shape = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        if len(shape) > 8:  # and area >= (height * width) / 150:

            shapeMask = np.zeros(image.shape, dtype=np.uint8)
            cv2.fillPoly(shapeMask, [shape], (255, 255, 255))
            shapeMask = cv2.cvtColor(shapeMask, cv2.COLOR_BGR2GRAY)
            result = cv2.bitwise_and(image, image, mask=shapeMask)

            cv2.drawContours(image, [shape], 0, (255, 0, 255), 1)
            n = shape.ravel()
            i = 0
            for j in n:
                if i % 2 == 0:
                    x = n[i] + 5
                    y = n[i + 1]
                    string = str(x) + " " + str(y)
                    file.write(string)
                    file.write("\n")

                    # if i == 0:
                    #     cv2.putText(image, "Arrow tip", (x, y),
                    #                 cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))
                    # else:
                    #     # text on remaining co-ordinates.
                    #     cv2.putText(image, string, (x, y),
                    #                 cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0))
                i = i + 1

    cv2.imshow("Frame", image)
    cv2.waitKey()
    file.close()
    return contours
