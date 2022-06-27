import os
import re
import time
import numpy as np
import almath
from naoqi import ALProxy
import sys
import head_movement_utils as head
import utils
import walking

classes = ['bear', 'flamingo', 'duck', 'blue ball', 'frog', 'orange spike', 'dino']

# image dimensions
width = 320
height = 240


# sorts the dirs and files: 910 is after 99
def sort_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


# opens the latest dir and the latest .txt to get the detected objects
# returns a dict that has each detected object (highest conf) and its props
def getLatestObjects(
        new_path='D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\yolo_project\\yolov5\\runs\\detect\\'):
    path = new_path

    # get the latest dir from the path
    # it is sorted
    req_dir = sort_alphanumeric(os.listdir(path))[-1]

    # get the path to where the txts are
    path_to_txts = path + req_dir + '\\labels\\'

    # if there was actually any detection made, return the objects and the coordinates
    # no detection -> no new txts
    if len(os.listdir(path_to_txts)) != 0:
        # get the name of the latest txt
        req_txt = sort_alphanumeric(os.listdir(path_to_txts))[-1]

        txt_file = open(path_to_txts + req_txt, 'r')

        objects_props = txt_file.readlines()

        # each line looks like this
        # class x_center y_center width height confidence
        # everything (except the class) is scaled from 0 to 1

        # a dict of dicts
        current_objects = {}

        for obj in objects_props:
            # splitting the lines -> separate each property
            obj = obj.strip().split(' ')

            # first condition: if the object is already in the current_objs and the current conf is higher
            # second condition: the object is not yet in the dictionary
            if (int(obj[0]) in current_objects and float(obj[5]) > current_objects[int(obj[0])]['conf']) or \
                    int(obj[0]) not in current_objects:
                current_objects[int(obj[0])] = {}
                current_objects[int(obj[0])]['x'] = float(obj[1])
                current_objects[int(obj[0])]['y'] = float(obj[2])
                current_objects[int(obj[0])]['w'] = float(obj[3])
                current_objects[int(obj[0])]['h'] = float(obj[4])
                current_objects[int(obj[0])]['conf'] = float(obj[5])

        txt_file.close()

        return current_objects, req_txt
    # no detection
    else:
        return None, None


# checks if the requested object is in the latest detected object
# req object must be and int
def checkRequestedObject(requestedObject, currentObjects):
    if currentObjects is not None:
        if requestedObject in currentObjects:
            return True
    return False


# coordinates given by YOLO are scaled from 0 to 1
# this method translates the coordinates to image-space (pixels)
# width, height = the image resolution (check utils.py)
def coordsToPixels(x, y):
    pixelX = int(x * width)
    pixelY = int(y * height)
    return pixelX, pixelY


# moves hand to point at object in front of the robot
def pointAtObject(motionProxy):
    nameList = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
    angleList = [58.0, 5.0, 67.5, 29.0, -60.0, 0.7]
    angleList = [x * almath.TO_RAD for x in angleList]
    timeList = [[1.0], [1.0], [1.0], [1.0], [1.0], [1.0]]
    isAbsolute = True

    motionProxy.angleInterpolation(nameList, angleList, timeList, isAbsolute)


# returns the area in pixels
def getAreaInPixels(w, h):
    return round(w * h * width * height)


# computes the distance from robot to object
# basic formula is distance = camera_height/tan(alpha)
# alpha is the angle between the ray of the camera hitting the object and the ground
# so basically alpha is just the pitch angle
# pitch must be in rads
def getDistance(pitch):
    # bottom camera height from the ground in meters
    # camera_height = 0.34405

    # experimental measurement
    camera_height = 0.47

    # in radians
    # the bottom camera needs a higher correction, since 0.0 pitch angle is different from the actual pitch
    correction = 39.7 * almath.TO_RAD

    distance = camera_height / np.tan(pitch + correction)

    return round(distance, 2)


# gets the required object as text from user
# checks if the object is known
def getRequestedObject():
    requestedObjText = raw_input("Requested Object: ").lower()

    requestedObj = -1
    try:
        requestedObj = classes.index(requestedObjText)
    except Exception, e:
        print('Not a valid class. Try again')

    return requestedObj


def getRequestedObjectVoice(ip, port):
    asrProxy = ALProxy("ALSpeechRecognition", ip, port)

    asrProxy.pause(True)

    asrProxy.setLanguage("English")
    asrProxy.setVocabulary(classes, False)
    asrProxy.subscribe(ip)

    memProxy = ALProxy("ALMemory", ip, port)
    memProxy.subscribeToEvent('WordRecognized', ip, 'wordRecognized')

    asrProxy.pause(False)

    time.sleep(10)

    asrProxy.unsubscribe(ip)
    data = memProxy.getData("WordRecognized")
    print 'word recognized: ' + data
    return data


# if the object is lost, the robot will look around, then start to rotate anti-clockwise
# all movement is based on the where variable - an int that is incremented in the calling code
def searchForObject(motionProxy, where):
    if where == 0:
        walking.turnToHeadAngle(motionProxy)
        head.moveHeadToCoords(0.0, 15, motionProxy)

    elif where == 1:
        head.lookLeft(motionProxy)

    elif where == 2:
        head.lookLeftDown(motionProxy)

    elif where == 3:
        head.lookFrontDown(motionProxy)

    elif where == 4:
        head.lookRightDown(motionProxy)

    elif where == 5:
        head.lookRight(motionProxy)

    # turn with 15 degrees until something is found
    else:
        degrees = 15
        # turn right
        walking.turnToAngle(motionProxy, -degrees)

        if where == 6:
            # look ahead
            head.moveHeadToCoords(0.0, 8.0, motionProxy)
        elif where == 7:
            head.lookFrontDown(motionProxy)


# requestedObject is a positive integer (index of the class)
def goToObject(robotIP, requestedObject):
    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
        postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
        tts = ALProxy("ALTextToSpeech", robotIP, 9559)

    except Exception, e:
        print "Could not create proxy to ALMotion, ALRobotPosture or ALTextToSpeech"
        print "Error was: ", e
        sys.exit(1)

    # get in position
    walking.getReady(motionProxy, postureProxy)
    time.sleep(1.5)

    # the center pixel
    targetPosition = [160, 120]

    # how much time has passed since no new txt
    elapsed_time = 0
    timer = time.time()

    exit_condition = False
    lastTxt = ''
    xHasChanged = True
    yHasChanged = True

    rememberWhereSearched = 0

    turned = False
    loopCounter = 0
    while not exit_condition:
        currentObjects, currentTxt = getLatestObjects()

        # if there is no new txt file, don't adjust head angles
        # no new txt file can mean 2 things:
        # no detection of any new object was made
        # the detector is delayed and generates files too slow
        if currentTxt == lastTxt:
            elapsed_time += time.time() - timer
        else:
            lastTxt = currentTxt
            elapsed_time = 0

            # the requested object is detected
            if checkRequestedObject(requestedObject, currentObjects):
                rememberWhereSearched = 0
                actualObject = currentObjects[requestedObject]
                x, y = coordsToPixels(actualObject['x'], actualObject['y'])
                w, h = actualObject['w'], actualObject['h']

                area = getAreaInPixels(w, h)

                [yawAngle, pitchAngle] = head.getHeadAnglesDeg(motionProxy)

                print 'Current x = ' + str(x) + ' current y = ' + str(y)

                # a 10 pixel error
                if x not in range(150, 170) and not turned:
                    yawAngle -= (x - targetPosition[0]) / 5.0
                    head.moveHeadToCoords(yawAngle, pitchAngle, motionProxy)
                    time.sleep(1.0)

                    xHasChanged = True
                    print 'Here in x = ' + str(x)
                    loopCounter = 0
                else:
                    xHasChanged = False
                    # turn only one time
                    # first, let the robot turn around to face the object
                    # only after it has turned continue with head Pitch
                    if not turned:

                        print "Turned with " + str(yawAngle) + " degrees"

                        walking.turnToHeadAngle(motionProxy)
                        head.moveHeadToCoords(0.0, pitchAngle, motionProxy)
                        time.sleep(1.0)
                        turned = True
                        loopCounter += 1
                    else:
                        print ' Here in else'

                # a 15 pixel error
                # TODO does it go all the way up if needed?
                # TODO dont forget about turned, so
                if y not in range(105, 135) and turned and loopCounter >= 2:
                    print 'Here in y = ' + str(y)
                    pitchAngle += (y - targetPosition[1]) / 6.0
                    head.moveHeadToCoords(0.0, pitchAngle, motionProxy)
                    time.sleep(1.0)
                    yHasChanged = True
                else:
                    yHasChanged = False
                loopCounter += 1

                if not yHasChanged and not xHasChanged:

                    print 'Here nothing has changed'
                    turned = False
                    loopCounter = 0
                    # yHasChanged = False
                    # xHasChanged = False

                    [_, currentPitch] = head.getHeadAnglesRad(motionProxy)

                    distance = getDistance(currentPitch)
                    print 'Computed distance is ' + str(distance) + ' m'

                    if pitchAngle < 8.0:
                        head.moveHeadToCoords(0.0, 5.0, motionProxy)

                    if distance > 1.50:
                        print 'A bit too far'
                        walking.walkDistance(motionProxy, 1.3)
                        time.sleep(1)
                    elif distance <= 0.35:
                        print 'Reaaally close'
                        head.moveHeadToCoords(0.0, 14.0, motionProxy)
                        walking.walkDistance(motionProxy, 0.10)
                        pointAtObject(motionProxy)
                        words = 'This is ' + classes[requestedObject]
                        utils.saySomethingSimple(tts, words)
                        walking.getUnready(motionProxy, postureProxy)
                        exit_condition = True
                    elif distance <= 0.25:
                        print 'Arrived at  object'
                        pointAtObject(motionProxy)
                        words = 'This is ' + classes[requestedObject]
                        utils.saySomethingSimple(tts, words)
                        walking.getUnready(motionProxy, postureProxy)
                        exit_condition = True
                    else:
                        print 'Normal walk'
                        walking.walkDistance(motionProxy, distance - 0.3)
                        time.sleep(1)
                print ' '

            # the requested object is not among the detected objects
            else:
                print 'I dont see the object'
                # utils.saySomethingSimple(tts, 'I don\'t see the ' + classes[requestedObject] + '. Let me search')
                searchForObject(motionProxy, rememberWhereSearched)
                # extra time for yolo to get the new images
                # TODO is 1.5 enough?
                time.sleep(1.5)
                if rememberWhereSearched < 7:
                    rememberWhereSearched += 1
                else:
                    rememberWhereSearched -= 1
                print ''

        timer = time.time()
        # more than 2.5 seconds have passed since last txt was made
        # that means the robot cannot find the object
        # TODO: is 2.5 enough?
        if elapsed_time > 2.0:
            print 'Too much time has passed: '+str(round(elapsed_time, 2))
            # utils.saySomethingSimple(tts, 'I lost the ' + classes[requestedObject] + '. I\'m searching')
            searchForObject(motionProxy, rememberWhereSearched)
            # extra time for yolo to get the new images
            # TODO is 1.5 enough?
            time.sleep(1.5)
            if rememberWhereSearched < 7:
                rememberWhereSearched += 1
            else:
                rememberWhereSearched -= 1
            print ' '
        print 'remember where searched ' + str(rememberWhereSearched)


if __name__ == "__main__":

    # girl
    robotIP = "172.20.10.3"

    # boy
    #robotIP = "172.20.10.5"
    port = 9559

    # utils.saySomething(robotIP, port, 'What object do you want?')

    # req = getRequestedObjectVoice(robotIP, port)

    requestedObject = getRequestedObject()
    while requestedObject == -1:
        requestedObject = getRequestedObject()

    goToObject(robotIP, requestedObject)
