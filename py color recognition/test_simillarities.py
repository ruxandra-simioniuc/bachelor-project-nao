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

    if c is None:
        print "No contour given"
        sys.exit()

    # coords = getCoordinatesFromFile(contour_file)

    # https://pyimagesearch.com/2016/02/15/determining-object-color-with-opencv/
    mask = np.zeros(img.shape[:2], dtype="uint8")
    cv2.drawContours(mask, [c[0]], -1, 255, -1)
    mask = cv2.erode(mask, None, iterations=2)
    # cv2.imshow("Mask2", mask)
    mean = cv2.mean(img, mask=mask)[:3]

    masked = cv2.bitwise_and(img, img, mask=mask)
    # masked = cv2.GaussianBlur(masked, 3)

    unique, counts = np.unique(masked.reshape(-1, 3), axis=0, return_counts=True)
    unique = np.delete(unique, [0, 0, 0], axis=0)
    counts = np.delete(counts, np.argmax(counts))

    dominantColorBGR = unique[counts == counts.max()][0]

    # print "R = " + str(mean[2]) + " G = " + str(mean[1]) + " B = " + str(mean[0])
    print "R = " + str(dominantColorBGR[2]) + " G = " + str(dominantColorBGR[1]) + " B  = " + str(dominantColorBGR[0])
    # cv2.imshow("mask", masked)
    # cv2.waitKey()
    return dominantColorBGR[2], dominantColorBGR[1], dominantColorBGR[0]


# if __name__ == "__main__":
#     path = "test_images/InkedFINGER_imag_frame_0_draw.jpg"
#     path2 = "test_images/finger_obj23.png"
#     filePath = "coordinates_ONE_FINGER2.txt"
#
#     # contour = getCoordinatesOfContour(path, filePath)
#
#     cnt = getContourFromFile(filePath)
#
#     img = cv2.imread(path2)
#     dominantColor(image=img, c=cnt)
