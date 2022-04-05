import sys
import motion
import time
from naoqi import ALProxy
import almath
import cv2
import time
import utils
from positions import *


def joints(robotIP):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    # motionProxy.setStiffnesses("Head", 1.0)

    # Simple command for the HeadYaw joint at 10% max speed
    names = "HeadYaw"
    angles = 30.0 * almath.TO_RAD
    fractionMaxSpeed = 0.1
    # motionProxy.setAngles(names, angles, fractionMaxSpeed)

    # time.sleep(3.0)
    # motionProxy.setStiffnesses("Head", 0.0)

    handName = 'RHand'
    motionProxy.openHand(handName)
    time.sleep(3)
    x = True

    # while x:
    motionProxy.closeHand(handName)

    stiffness = 0.1
    motionProxy.setStiffnesses("RHand", stiffness)
    # time.sleep(5)
    # print motionProxy.getBodyNames()


# for testing
def arm_movement(robotIP, arm="RArm"):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    if arm == "RArm":
        currentArm = "R"
    elif arm == "LArm":
        currentArm = "L"
    else:
        print "Not a valid hand. Choose RArm or LArm"
        sys.exit(1)

    shoulderPitch = currentArm + "ShoulderPitch"
    shoulderRoll = currentArm + "ShoulderRoll"
    elbowYaw = currentArm + "ElbowYaw"
    elbowRoll = currentArm + "ElbowRoll"
    wristYaw = currentArm + "WristYaw"

    names = []
    names.append("HeadPitch")
    names.append(shoulderPitch)
    names.append(shoulderRoll)
    names.append(elbowYaw)
    names.append(elbowRoll)
    names.append(wristYaw)

    motionProxy.setStiffnesses(arm, 1.0)
    degrees = ""

    while degrees != "exit":
        for joint in names:
            degrees = ""
            while degrees != "next":
                degrees = raw_input("Degrees for " + joint + ": ")
                if degrees == 'exit' or degrees == 'next':
                    break
                else:
                    # try:
                    degrees = float(degrees)
                    #

                # names = elbowYaw
                angleList = degrees * almath.TO_RAD
                timeList = 1.0
                isAbsolute = True
                motionProxy.angleInterpolation(joint, angleList, timeList, isAbsolute)

    # motionProxy.setStiffnesses(arm, 0.0)


def lookAtObject(robotIP, port, arm, color):
    try:
        motionProxy = ALProxy("ALMotion", robotIP, port)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    if arm == "RArm":
        currentArm = "R"
    elif arm == "LArm":
        currentArm = "L"
    else:
        print "Not a valid hand. Choose RArm or LArm"
        sys.exit(1)

    names = []
    names.append("HeadPitch")
    names.append(currentArm + "ShoulderPitch")
    names.append(currentArm + "ShoulderRoll")
    names.append(currentArm + "ElbowYaw")
    names.append(currentArm + "ElbowRoll")
    names.append(currentArm + "WristYaw")

    motionProxy.setStiffnesses(arm, 1.0)

    angleList = [[18 * almath.TO_RAD],  # headPitch
                 [75 * almath.TO_RAD],  # shoulderPitch
                 [10 * almath.TO_RAD],  # ShoulderRoll
                 [45 * almath.TO_RAD],  # elbowYaw
                 [75 * almath.TO_RAD],  # elbowRoll
                 [85 * almath.TO_RAD]]  # wristYaw
    timeList = [[1.0], [1.0], [1.0], [1.0], [1.0], [1.0], [1.0]]

    isAbsolute = True
    motionProxy.angleInterpolation(names, angleList, timeList, isAbsolute)

    useSensors = False
    commandAngles = motionProxy.getAngles(names, useSensors)
    utils.eyeLEDs(robotIP, port)

    # for i in range(0, len(names)):
    #     angle = commandAngles[i] * almath.TO_DEG
    #     print names[i] + " angle: " + str(angle)

    # time.sleep(2)
    #
    # tts = ALProxy("ALTextToSpeech", robotIP, port)
    # tts.say(color)
    #
    # stop = raw_input("Press y to default pos: ")
    # if stop == 'y':
    #     defaultStand(robotIP, port)


def extendHand(robotIP, port, arm):
    try:
        motionProxy = ALProxy("ALMotion", robotIP, port)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    if arm == "RArm":
        currentArm = "R"
    elif arm == "LArm":
        currentArm = "L"
    else:
        print "Not a valid hand. Choose RArm or LArm"
        sys.exit(1)

    names = []
    names.append("HeadPitch")
    names.append(currentArm + "ShoulderPitch")
    names.append(currentArm + "ShoulderRoll")
    names.append(currentArm + "ElbowYaw")
    names.append(currentArm + "ElbowRoll")
    names.append(currentArm + "WristYaw")

    motionProxy.setStiffnesses(arm, 1.0)

    angleList = [[10 * almath.TO_RAD],  # headPitch
                 [40 * almath.TO_RAD],  # shoulderPitch
                 [20 * almath.TO_RAD],  # shoulderRoll
                 [50 * almath.TO_RAD],  # elbowYaw
                 [40 * almath.TO_RAD],  # elbowRoll
                 [100 * almath.TO_RAD]]  # wristYaw
    timeList = [[1.0], [1.0], [1.0], [1.0], [1.0], [1.0], [1.0]]

    isAbsolute = True
    motionProxy.angleInterpolation(names, angleList, timeList, isAbsolute)

    # useSensors = False
    # commandAngles = motionProxy.getAngles(names, useSensors)

    # for i in range(0, len(names)):
    #     angle = commandAngles[i] * almath.TO_DEG
    #     print names[i] + " angle: " + str(angle)
    #
    # print "\n"

    motionProxy.openHand(currentArm + "Hand")

    color = utils.getCameraFeedAndColor(robotIP, port)
    #print "color: " + color

    motionProxy.closeHand(currentArm + "Hand")
    motionProxy.setStiffnesses(arm, 0.5)

    return color


if __name__ == "__main__":
    robotIp = "192.168.90.238"
    port = 9559

    topCamera = 0
    bottomCamera = 1
    # utils.getCameraFeed(robotIp, port, bottomCamera)

    effectorName = "LArm"

    # main(robotIp, port, effectorName)
    # joints(robotIp)
    # defaultStand(robotIp, port)

    defaultStand(robotIp, port)

    requiredColor = raw_input("What color? ")
    utils.saySomething(robotIp, port, "Can you give me a "+requiredColor+" toy, please?")

    color = extendHand(robotIp, port, "RArm")
    lookAtObject(robotIp, port, "RArm", color)

    while color != str(requiredColor).lower():
        utils.saySomething(robotIp, port, "This is not " + requiredColor+"! Can you try again?")
        color = extendHand(robotIp, port, "RArm")
        lookAtObject(robotIp, port, "RArm", color)

    utils.saySomething(robotIp, port, "Congratulations! You know your colors!")
    defaultStand(robotIp, port)

    #arm_movement(robotIp, "RArm")
