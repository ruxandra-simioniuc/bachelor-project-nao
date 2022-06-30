from utils_file import *
from utils_movement import defaultStand, crouch, lookAtObject, extendHand
from naoqi import ALProxy
import utils_camera_voice


# if for 2 frames the color in the ROI is the same, return it then close hand
def checkForColor(robotIP, port, motionProxy):
    prevColor = ''
    counter = 0
    color = ''
    while counter <= 2:
        color = utils_camera_voice.getCameraFeedAndColor(robotIP, port)
        print "color: " + color
        if prevColor != color:
            counter = 0
        prevColor = color
        counter += 1

    motionProxy.closeHand("RHand")
    motionProxy.setStiffnesses("RArm", 0.5)

    return color


def executeTask1(robotIp):
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

    requiredColor = raw_input("What color? ")
    utils_camera_voice.saySomethingSimple(tts, "Can you give me a " + requiredColor + " toy, please?")

    extendHand(motionProxy)
    color = checkForColor(robotIp, port, motionProxy)

    lookAtObject(motionProxy)

    while color != str(requiredColor).lower():
        utils_camera_voice.saySomethingSimple(tts, "This is not " + requiredColor + ", this is " + color + "! Can you try again?")

        extendHand(motionProxy)
        color = checkForColor(robotIp, port, motionProxy)

        lookAtObject(motionProxy)
        utils_camera_voice.eyeLEDs(robotIp, port)

    utils_camera_voice.saySomethingSimple(tts, "Congratulations! You know your colors!")

    defaultStand(postureProxy)
    crouch(postureProxy)


if __name__ == "__main__":
    # girl
    robotIP = "172.20.10.3"

    # boy
    # robotIP = "172.20.10.5"
    executeTask1(robotIP)