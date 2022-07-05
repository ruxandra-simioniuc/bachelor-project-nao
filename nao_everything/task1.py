import argparse
import sys
import time

from utils_movement import defaultStand, crouch, lookAtObject, extendHand
from naoqi import ALProxy
import utils_camera_voice


# if for 2 frames the color in the ROI is the same, return it then close hand
def checkForColor(robotIP, port, motionProxy):
    prevColor = ''
    counter = 0
    color = ''

    while counter < 2:
        color = utils_camera_voice.getCameraFeedAndColor(robotIP, port)

        if color == "no_obj":
            break

        if prevColor != color:
            counter = 0
        prevColor = color
        counter += 1

    motionProxy.closeHand("RHand")
    motionProxy.setStiffnesses("RArm", 0.5)

    return color


def executeTask1(robotIp, requiredColor):
    port = 9559

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIp, port)
        motionProxy = ALProxy("ALMotion", robotIp, port)
        tts = ALProxy("ALTextToSpeech", robotIp, port)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture and ALMotion"
        print "Error was: ", e
        sys.exit(1)

    defaultStand(postureProxy)
    counter = 0

    # requiredColor = raw_input("What color? ")
    utils_camera_voice.saySomethingSimple(tts, "Can you give me a " + requiredColor + " toy, please?")

    extendHand(motionProxy)
    color = checkForColor(robotIp, port, motionProxy)

    if color != "no_obj":
        lookAtObject(motionProxy)

        while color != str(requiredColor).lower():
            counter += 1
            #  if too much time has passed and no object was placed
            # or if wrong color object were offered 3 times
            if color == "no_obj" or counter == 3:
                break
            else:
                utils_camera_voice.saySomethingSimple(tts,
                                                      "This is not " + requiredColor + ", this is " + color + "! Can you try again?")

                extendHand(motionProxy)
                color = checkForColor(robotIp, port, motionProxy)

                lookAtObject(motionProxy)
                utils_camera_voice.eyeLEDs(robotIp, port)

        if color == "no_obj" or counter == 3:
            utils_camera_voice.saySomethingSimple(tts, "Thank you!")
        else:
            utils_camera_voice.saySomethingSimple(tts, "Congratulations! You know your colors!")

    defaultStand(postureProxy)
    crouch(postureProxy)


if __name__ == "__main__":
    # girl
    robotIP = "172.20.10.3"

    # boy
    # robotIP = "172.20.10.5"

    # parser = argparse.ArgumentParser("Arguments for running Task 1")
    # parser.add_argument("robotIP", help="The robot ip as a string")
    # parser.add_argument("color", help="The color of the object NAO will request")
    # args = parser.parse_args()
    #
    # executeTask1(args.robotIP, args.color)

    color = "red"
    executeTask1(robotIP, color)
