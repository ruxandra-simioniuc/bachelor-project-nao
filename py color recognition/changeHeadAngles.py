import os
import sys
from naoqi import ALProxy
import almath
import re
import walking
import time

# classes = ['doll', 'frog', 'dino', 'duck', 'bear', 'flamingo', 'blue football', 'white football', 'blue ball',
#            'rainbow ball', 'orange spike', 'unicorn']
classes = ['bear', 'flamingo', 'duck', 'blue ball', 'frog', 'orange spike', 'dino']
width = 320
height = 240


# sorts the dirs and files: 910 is after 99
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


def getLatestObjects():
    path = 'D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\yolo_project\\yolov5\\runs\\detect\\'
    dirs = sorted_alphanumeric(os.listdir(path))

    path_to_txts = path + dirs[-1] + '\\labels\\'

    # if there was actually any detection made, return the objects and the coordinates
    if len(os.listdir(path_to_txts)) != 0:

        txt = sorted_alphanumeric(os.listdir(path_to_txts))[-1]

        txtfile = open(path_to_txts + txt, 'r')
        # print("txt = " + path_to_txts.split('detect')[1] + txt)
        objects = txtfile.readlines()

        # a dict of dicts
        current_objects = {}

        for o in objects:
            o = o.strip().split(' ')

            # if there is more than one of the same toy detected
            # look at the one with the highest confidence level
            if (int(o[0]) in current_objects and float(o[5]) > current_objects[int(o[0])]['conf']) or int(
                    o[0]) not in current_objects:
                current_objects[int(o[0])] = {}
                current_objects[int(o[0])]['x'] = float(o[1])
                current_objects[int(o[0])]['y'] = float(o[2])
                current_objects[int(o[0])]['conf'] = float(o[5])

        txtfile.close()

        return current_objects, txt

    # if there's no detection, return None
    return None


# requested must be an int -> check the classes
def checkRequestedObject(requested, currentObjects):
    if requested in currentObjects:
        return True
    return False


# coordinates given by YOLO are scaled from 0 to 1
# this method translates the coordinates to image-space (pixels)
# width, height = the image resolution (check utils.py)
def coordsToPixels(x, y):
    pixelX = int(x * width)
    pixelY = int(y * height)
    return pixelX, pixelY


def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)


def moveHeadToCoords(x, y, robotIP, motionProxy):
    # try:
    #     motionProxy = ALProxy("ALMotion", robotIP, 9559)
    # except Exception, e:
    #     print "Could not create proxy to ALMotion"
    #     print "Error was: ", e
    #     sys.exit(1)

    # aici erau cu - unghiurile nuj de ce
    yawAngle = (-x) * almath.TO_RAD
    pitchAngle = y * almath.TO_RAD

    timeList = [[1.0], [1.0]]
    isAbsolute = True

    # print(str(yawAngle) + " " + str(pitchAngle) + " " + " " + str(x) + " " + str(y))


    # aici trb schimbate [x,y] cu anngle
    # motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [x, y], timeList, isAbsolute)
    motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [yawAngle, pitchAngle], timeList, isAbsolute)

    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)

    # pitchAngle += commandAngles[0]
    # yawAngle += commandAngles[1]

    print "Yaw: " + str(commandAngles[0] * almath.TO_DEG) + " Pitch: " + str(commandAngles[1] * almath.TO_DEG)


if __name__ == "__main__":

    robotIP = "172.20.10.3"

    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    requestedObjText = raw_input("Requested Object: ").lower()
    lastTxt = ""
    counter = 0

    exit_condition = False
    pitchAngle = 0
    yawAngle = 0

    oldX = 0
    oldY = 0

    targetPosition = [160, 120]

    lastY = 0

    # controller gains
    hc = [0.7, 0.04]
    moved = False

    while not exit_condition:

        latestObjects, currentTxt = getLatestObjects()
        # print("lastTXT = " + lastTxt + " currentTXT = " + currentTxt)

        if lastTxt == currentTxt:
            # counter += 1
            # if counter >= 4:
            # print("No new data")
            lastTxt = currentTxt
            # exit_condition = True
        else:
            lastTxt = currentTxt
            time.sleep(1)
            if latestObjects is not None:
                requestedObj = -1

                try:
                    # checks if the received class exists
                    requestedObj = classes.index(requestedObjText)
                except Exception, e:
                    print('Not a valid class')

                if moved:
                    time.sleep(2)
                    moved = False

                if checkRequestedObject(requestedObj, latestObjects):
                    x, y = coordsToPixels(latestObjects[requestedObj]['x'], latestObjects[requestedObj]['y'])

                    # if x != oldX and y != oldY:
                    oldX = x
                    oldY = y
                    # yawAngle = (targetPosition[0]-x) * hc[0]
                    # pitchAngle = (targetPosition[1] - y) * hc[1]
                    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)
                    # yawAngle = commandAngles[0]
                    # pitchAngle = commandAngles[1]
                    # a 10 pixel error left and right (160 is the center of the image on the x-axis)
                    if x not in range(150, 170):
                        # on the left half of the image
                        if x in range(0, 140):
                            yawAngle -= 2
                        else:
                            yawAngle += 2

                        # yawAngle = (x - targetPosition[0]) * hc[0]
                        # 1 grad ~= 5 pixeli
                        # yawAngle = (x - targetPosition[0]) / 5.0
                        changedX = 1
                    else:
                        changedX = 0

                    # a 10 pixel error up and down (120 is the center of the image on the y-axis)
                    if y not in range(85, 140):
                        # in the upper half of the image
                        if y in range(0, 110):
                            pitchAngle -= 2
                        else:
                            pitchAngle += 2
                        # pitchAngle = (y - targetPosition[1]) * hc[1]
                        # 1 grad ~= 5-7 pixeli
                        # pitchAngle = (y - targetPosition[1]) / 6.0
                        if commandAngles[1] == lastY:
                            changedY = 0
                        else:
                            lastY = commandAngles[1]
                            changedY = 1
                    else:
                        changedY = 0

                    # print str(changedX) + " " + str(changedY)
                    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)

                    if changedX == 0 and changedY == 0:
                        if commandAngles[1] < 7.0 * almath.TO_RAD:
                            # print str(changedX) + " " + str(changedY)
                            #      exit_condition = True
                            theta = (-yawAngle) * almath.TO_RAD

                            walking.walkDistanceAndRotate(robotIP, 0.3, 0.0)
                            time.sleep(3)
                            commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)

                            moveHeadToCoords(yawAngle, pitchAngle + 3 * almath.TO_RAD, robotIP, motionProxy)
                            yawAngle = commandAngles[0]
                            pitchAngle = commandAngles[1]
                            moved = True
                        elif 7.0 * almath.TO_RAD <= commandAngles[1] < 9.0 * almath.TO_RAD:

                            walking.walkDistanceAndRotate(robotIP, 0.1, 0.0)
                            print 'Head is low'
                            time.sleep(3)
                            moved = True
                            commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)
                            moveHeadToCoords(yawAngle, pitchAngle + 3 * almath.TO_RAD, robotIP, motionProxy)
                            yawAngle = commandAngles[0]
                            pitchAngle = commandAngles[1]

                        else:
                            print 'reached obj'
                            walking.turnToHeadAngle(robotIP)
                            exit_condition = True

                    else:
                        moved = False
                        # moveHeadToCoords(latestObjects[requestedObj]['x'], latestObjects[requestedObj]['y'], robotIP)
                        moveHeadToCoords(yawAngle, pitchAngle, robotIP, motionProxy)
                    print "target: " + str(x) + " " + str(y) + '\n'
                    print("moved to: " + str(yawAngle) + " " + str(pitchAngle))
                    print "command angles: yaw = " + str(commandAngles[0] * almath.TO_DEG) + " pitch = " + str(commandAngles[1] * almath.TO_DEG)
                else:
                    print('Can\'t find requested object')
            else:
                print("No object detected yet")

        # requestedObjText = raw_input("Requested Object: ").lower()

    # walking.walkDistance(robotIP, 1.4)

    print 'here'
