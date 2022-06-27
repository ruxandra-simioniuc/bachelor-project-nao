import math
import os
import sys
from naoqi import ALProxy
import almath
import re
import walking
import time
import numpy as np
import utils

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
    # print path_to_txts

    # if there was actually any detection made, return the objects and the coordinates
    if len(os.listdir(path_to_txts)) != 0:

        txt = sorted_alphanumeric(os.listdir(path_to_txts))[-1]

        txtfile = open(path_to_txts + txt, 'r')

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
                current_objects[int(o[0])]['w'] = float(o[3])
                current_objects[int(o[0])]['h'] = float(o[4])
                current_objects[int(o[0])]['conf'] = float(o[5])

        txtfile.close()

        return current_objects, txt

    # if there's no detection, return None
    return None, None


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


def getHeadAnglesDeg(motionProxy):
    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)
    return [commandAngles[0] * almath.TO_DEG, commandAngles[1] * almath.TO_DEG]


def getHeadAnglesRad(motionProxy):
    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)
    return commandAngles


def moveHeadToCoords(x, y, motionProxy):
    # aici erau cu - unghiurile nuj de ce
    yawAngle = x * almath.TO_RAD
    pitchAngle = y * almath.TO_RAD

    timeList = [[1.0], [1.0]]
    isAbsolute = True

    # print(str(yawAngle) + " " + str(pitchAngle) + " " + " " + str(x) + " " + str(y))

    # aici trb schimbate [x,y] cu anngle
    # motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [x, y], timeList, isAbsolute)
    motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [yawAngle, pitchAngle], timeList, isAbsolute)

    # wait for the move to finish
    # motionProxy.waitUntilMoveIsFinished()
    time.sleep(1.5)

    angles = getHeadAnglesDeg(motionProxy)
    print "After movement Yaw: " + str(angles[0]) + " Pitch: " + str(angles[1])


def pointAtObject(motionProxy):
    nameList = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
    angleList = [58.0, 5.0, 67.5, 29.0, -60.0, 0.7]
    angleList = [x * almath.TO_RAD for x in angleList]
    timeList = [[1.0], [1.0], [1.0], [1.0], [1.0], [1.0]]
    isAbsolute = True

    motionProxy.angleInterpolation(nameList, angleList, timeList, isAbsolute)


def getAreaInPixels(w, h):
    return round(w * h * width * height)


def getDistance(pitch):
    # bottom camera height from the ground in meters
    height = 0.34405

    # in radians
    correction = 39.7 * almath.TO_RAD

    distance = height / np.tan(pitch + correction)

    return distance


def searchForObject(motionProxy, moved):
    # no movement made
    if moved == 0:
        pass


if __name__ == "__main__":

    # girl
    # robotIP = "172.20.10.3"

    # boy
    robotIP = "172.20.10.5"

    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)

    postureProxy.goToPosture('Crouch', 1.0)

    # Wake up robot
    motionProxy.wakeUp()

    walking.initialPosture(motionProxy, postureProxy)

    # Send robot to Stand
    # postureProxy.goToPosture("StandInit", 0.5)

    requestedObjText = raw_input("Requested Object: ").lower()
    lastTxt = ""
    counter = 0

    exit_condition = False
    pitchAngle = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)[1] * almath.TO_DEG
    yawAngle = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)[0] * almath.TO_DEG

    oldX = 0
    oldY = 0

    targetPosition = [160, 120]

    lastY = -100.0

    lowhead = 0

    # controller gains
    hc = [0.7, 0.04]
    moved = False
    looked_left = 0
    loopCounter = 0

    timer = time.time()
    elapsed = 0
    time_since_found_obj = 0
    last_seen_obj = 0

    while not exit_condition:

        latestObjects, currentTxt = getLatestObjects()
        # print("lastTXT = " + lastTxt + " currentTXT = " + currentTxt)

        if lastTxt == currentTxt:
            # print("No new data")
            lastTxt = currentTxt
            elapsed += time.time() - timer
        else:
            print 'Elapsed seconds: ' + str(elapsed)
            timer = time.time()
            elapsed = 0
            lastTxt = currentTxt
            # time.sleep(1)
            if latestObjects is not None:
                requestedObj = -1

                try:
                    # checks if the received class exists
                    requestedObj = classes.index(requestedObjText)
                except Exception, e:
                    print('Not a valid class')
                    exit_condition = True

                if checkRequestedObject(requestedObj, latestObjects):
                    x, y = coordsToPixels(latestObjects[requestedObj]['x'], latestObjects[requestedObj]['y'])
                    w = latestObjects[requestedObj]['w']
                    h = latestObjects[requestedObj]['h']
                    area = getAreaInPixels(w, h)
                    print 'Area: ' + str(area) + ' pixels'

                    # if x != oldX and y != oldY:
                    oldX = x
                    oldY = y

                    anglesDeg = getHeadAnglesDeg(motionProxy)
                    # yawAngle = commandAngles[0]
                    # pitchAngle = commandAngles[1]

                    # a 10 pixel error left and right (160 is the center of the image on the x-axis)
                    if x not in range(150, 170):
                        # 1 grad ~= 5 pixeli
                        yawAngle -= (x - targetPosition[0]) / 5.0
                        changedX = True
                    else:
                        print 'yaw not changed'
                        changedX = False
                        # exit_condition = True

                    # a 15 pixel error up and down (120 is the center of the image on the y-axis)
                    if y not in range(105, 135):
                        # 1 grad ~= 5-7 pixeli
                        pitchAngle += (y - targetPosition[1]) / 7.0
                        # changedY = True
                        if anglesDeg[1] == lastY:
                            print 'Can\'t move that way'
                            changedY = False
                        else:
                            lastY = anglesDeg[1]
                            changedY = True
                    else:
                        changedY = False

                    if not changedY and not changedX:
                        if loopCounter == 1:
                            loopCounter = 0
                            anglesRad = getHeadAnglesRad(motionProxy)
                            anglesDeg = getHeadAnglesDeg(motionProxy)
                            print 'no angle changed, current angles are:'
                            print 'currentYaw = ' + str(anglesDeg[0]) + " currentPitch = " + str(
                                anglesDeg[1])

                            currentDistance = getDistance(anglesRad[1])
                            print 'computed distance is ' + str(round(currentDistance, 2)) + ' m'
                            print '\n'

                            if round(currentDistance, 2) <= 0.23:
                                print 'Arrived at object'
                                walking.turnToHeadAngle(motionProxy)
                                pointAtObject(motionProxy)
                                exit_condition = True
                                utils.saySomething(robotIP, 9559, "This is " + requestedObjText)
                                lowhead = 3
                            elif currentDistance >= 1.5:
                                print 'Walking only 1.5'
                                walking.walkDistanceAndRotate(motionProxy, 1.5, 0.0)
                                [yawAngle, pitchAngle] = getHeadAnglesDeg(motionProxy)
                                time.sleep(1)
                                moved = True
                            else:
                                print 'Far, walking ' + str(round(currentDistance - 0.2))
                                walking.walkDistanceAndRotate(motionProxy, currentDistance - 0.2, 0.0)
                                [yawAngle, pitchAngle] = getHeadAnglesDeg(motionProxy)
                                time.sleep(1)
                                moved = True
                                lowHead = 1
                            print ' '
                        else:
                            loopCounter += 1

                        # the pitch
                        # if commandAnglesDeg[1] < -7.0:
                        #     # if not moved:
                        #     #     print 'Normal walk'
                        #     #     walking.walkDistance(robotIP, 0.5, 0.0)
                        #     #     time.sleep(5)
                        #     # else:
                        #     #     print('Normal walk but less')
                        #     #     walking.walkDistance(robotIP, 0.3, 0.0)
                        #     #     time.sleep(3)
                        #
                        #     print 'Normal walk'
                        #     walking.walkDistance(robotIP, 0.5, 0.0)
                        #     # time.sleep(5)
                        #     moved = True
                        #     lowhead = 0
                        #
                        # elif -7.0 <= commandAnglesDeg[1] < 5.0:
                        #     print 'Closer'
                        #     walking.walkDistance(robotIP, 0.3, 0.0)
                        #     # time.sleep(3)
                        #     lowhead = 1
                        #
                        # elif 5.0 <= commandAnglesDeg[1] <= 8.0:
                        #     print 'Really close'
                        #     walking.walkDistance(robotIP, 0.2, 0.0)
                        #     # time.sleep(2)
                        #
                        #     # moved = True
                        #     lowHead = 2
                        # elif 8.0 < commandAngles[1] <= 10.0:
                        #     walking.walkDistance(robotIP, 0.1, 0.0)
                        #     print 'Almost there'
                        #     # moved = True
                        #     lowHead = 2
                        # else:
                        #     print 'Arrived at object'
                        #     moved = True
                        #     walking.turnToAngle(motionProxy)
                        #     pointAtObject(motionProxy)
                        #     exit_condition = True
                        #     utils.saySomething(robotIP, 9559, "This is " + requestedObjText)
                        #     lowhead = 3

                        # exit_condition = True
                    else:

                        moveHeadToCoords(yawAngle, pitchAngle, motionProxy)

                        time.sleep(1.0)

                        commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)
                        comDeg = [yawAngle * almath.TO_RAD, pitchAngle * almath.TO_RAD]
                else:
                    print('Can\'t find requested object')
                    print 'Searching'

                    if lowhead == 3:
                        moveHeadToCoords(0.0, 14.0, motionProxy)
                    elif lowhead == 2:
                        moveHeadToCoords(0.0, 8.0, motionProxy)
                    elif lowhead == 1:
                        moveHeadToCoords(0.0, 5.0, motionProxy)
                    else:
                        if looked_left == 0:
                            moveHeadToCoords(12.0, -10.0, motionProxy)
                            looked_left = 1
                        else:
                            moveHeadToCoords(-12.0, -10.0, motionProxy)
                            looked_left = 0
                    # time.sleep(2)


            else:
                print("No object detected yet")
                print("Searching...")
                if looked_left == 0:
                    moveHeadToCoords(12.0, -10.0, motionProxy)
                    looked_left = 1
                else:
                    moveHeadToCoords(-12.0, -10.0, motionProxy)
                    looked_left = 0
            # time.sleep(2)

        # more than 3 seconds have passed and yolo did not detect anything
        if elapsed > 3:
            print 'More than 3 secs: ' + str(elapsed)
            searchForObject(motionProxy, 0)
            # exit_condition = True

        # requestedObjText = raw_input("Requested Object: ").lower()

    # walking.walkDistance(robotIP, 1.4)
    walking.initialPosture(motionProxy, postureProxy)
    postureProxy.goToPosture('Crouch', 1.0)

    print 'here'
