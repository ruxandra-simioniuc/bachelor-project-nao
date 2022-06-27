import cv2
import numpy as np
import sys


def dominantColor(path="", image=None, c=None):
    if path != "":
        img = cv2.imread(path)
    elif image is not None:
        img = image.copy()
    else:
        print "No path or image recieved"
        sys.exit()

    if c is None:
        print "No contour given"
        sys.exit()

    # coords = getCoordinatesFromFile(contour_file)

    # https://pyimagesearch.com/2016/02/15/determining-object-color-with-opencv/
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv2.drawContours(mask, [c[0]], -1, 255, -1)
    # mask = cv2.copyTo()

    # erosion
    mask = cv2.erode(mask, None, iterations=2)

    # cv2.imshow("Mask2", mask)
    # mean = cv2.mean(img, mask=mask)[:3]
    img = cv2.GaussianBlur(img, (3, 3), 0)
    masked = cv2.bitwise_and(img, img, mask=mask)

    # getting the number of pixels for each unique color
    unique, counts = np.unique(masked.reshape(-1, 3), axis=0, return_counts=True)
    # removing the black pixels
    unique = np.delete(unique, [0, 0, 0], axis=0)
    counts = np.delete(counts, np.argmax(counts))

    # find dominant color in image
    dominantColorBGR = unique[counts == counts.max()][0]

    # print "R = " + str(mean[2]) + " G = " + str(mean[1]) + " B = " + str(mean[0])
    # print "R = " + str(dominantColorBGR[2]) + " G = " + str(dominantColorBGR[1]) + " B  = " + str(dominantColorBGR[0])
    # cv2.imshow("mask", masked)
    # cv2.waitKey()
    ### returns R, G, B
    return dominantColorBGR[2], dominantColorBGR[1], dominantColorBGR[0]


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
    if s > 65 and v > 70:
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
