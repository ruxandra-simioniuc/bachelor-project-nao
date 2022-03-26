import sys
import motion
import time
from naoqi import ALProxy
import almath
import utils


def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)


def main(robotIP, port, effectorName):
    ''' Example of a whole body Left or Right Arm position control
        Warning: Needs a PoseInit before executing
                 Whole body balancer must be inactivated at the end of the script
    '''

    # Init proxies.
    try:
        motionProxy = ALProxy("ALMotion", robotIP, port)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, port)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e

    # Set NAO in Stiffness On
    StiffnessOn(motionProxy)

    # Send NAO to Pose Init
    postureProxy.goToPosture("StandInit", 0.5)

    space = motion.FRAME_ROBOT
    useSensor = False

    effectorInit = motionProxy.getPosition(effectorName, space, useSensor)

    # Active LArm tracking
    isEnabled = True
    motionProxy.wbEnableEffectorControl(effectorName, isEnabled)

    # Example showing how to set position target for LArm
    # The 3 coordinates are absolute LArm position in NAO_SPACE
    # Position in meter in x, y and z axis.

    # X Axis LArm Position feasible movement = [ +0.00, +0.12] meter
    # Y Axis LArm Position feasible movement = [ -0.05, +0.10] meter
    # Y Axis RArm Position feasible movement = [ -0.10, +0.05] meter
    # Z Axis LArm Position feasible movement = [ -0.10, +0.10] meter

    coef = 1.0
    if (effectorName == "LArm"):
        coef = +1.0
    elif (effectorName == "RArm"):
        coef = -1.0

    targetCoordinateList = [
        [+0.12, +0.00 * coef, +0.00],  # target 0
        [+0.12, +0.00 * coef, -0.10],  # target 1
        [+0.12, +0.05 * coef, -0.10],  # target 1
        [+0.12, +0.05 * coef, +0.10],  # target 2
        [+0.12, -0.10 * coef, +0.10],  # target 3
        [+0.12, -0.10 * coef, -0.10],  # target 4
        [+0.12, +0.00 * coef, -0.10],  # target 5
        [+0.12, +0.00 * coef, +0.00],  # target 6
        [+0.00, +0.00 * coef, +0.00],  # target 7
    ]

    # wbSetEffectorControl is a non blocking function
    # time.sleep allow head go to his target
    # The recommended minimum period between two successive set commands is
    # 0.2 s.
    for targetCoordinate in targetCoordinateList:
        targetCoordinate = [targetCoordinate[i] + effectorInit[i] for i in range(3)]
        motionProxy.wbSetEffectorControl(effectorName, targetCoordinate)
        time.sleep(4.0)

    # Deactivate Head tracking
    isEnabled = False
    motionProxy.wbEnableEffectorControl(effectorName, isEnabled)

    postureProxy.goToPosture("StandInit", 0.5)


def joints(robotIP):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    motionProxy.setStiffnesses("Head", 1.0)

    # Simple command for the HeadYaw joint at 10% max speed
    names = "HeadYaw"
    angles = 30.0 * almath.TO_RAD
    fractionMaxSpeed = 0.1
    motionProxy.setAngles(names, angles, fractionMaxSpeed)

    time.sleep(3.0)
    motionProxy.setStiffnesses("Head", 0.0)


def angleInterpolation(robotIP):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e
        sys.exit(1)

    motionProxy.setStiffnesses("Head", 1.0)
    motionProxy.setStiffnesses("LArm", 1.0)

    # Example showing a single target angle for one joint
    # Interpolate the head yaw to 1.0 radian in 1.0 second
    # names = "HeadYaw"
    # angleLists = 50.0 * almath.TO_RAD
    # timeLists = 1.0
    # isAbsolute = True
    # motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    time.sleep(1.0)

    # Example showing a single trajectory for one joint
    # Interpolate the head yaw to 1.0 radian and back to zero in 2.0 seconds
    names = "HeadYaw"
    #              2 angles
    angleLists = [30.0 * almath.TO_RAD, -20.0 * almath.TO_RAD, 0.0]
    #              2 times
    timeLists = [1.0, 3.0, 4.0]
    isAbsolute = True
    #motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    time.sleep(1.0)

    names = "RShoulderPitch"
    #              2 angles
    angleLists = [70.0 * almath.TO_RAD, 0.0, 20.0 * almath.TO_RAD, 70.0 * almath.TO_RAD]
    #              2 times
    timeLists = [1.0, 3.0, 5.0, 6.0]
    isAbsolute = True
    #motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    useSensors = False
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
    commandAngles = motionProxy.getAngles(names, useSensors)

    for i in range(0, len(names)):
        angle = commandAngles[i] * almath.TO_DEG
        print names[i] + " angle: " + str(angle)

    # print "RShoulderPitch angles:"
    # print str(commandAngles[0] * almath.TO_DEG)
    # print ""

    # Example showing multiple trajectories
    # names = ["HeadYaw", "HeadPitch"]
    # angleLists = [30.0 * almath.TO_RAD, 30.0 * almath.TO_RAD]
    # timeLists = [1.0, 1.2]
    # isAbsolute = True
    # motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)
    #
    # Example showing multiple trajectories
    # Interpolate the head yaw to 1.0 radian and back to zero in 2.0 seconds
    # while interpolating HeadPitch up and down over a longer period.
    names = ["RShoulderPitch", "RElbowRoll", "RElbowYaw"]
    # Each joint can have lists of different lengths, but the number of
    # angles and the number of times must be the same for each joint.
    # Here, the second joint ("HeadPitch") has three angles, and
    # three corresponding times.
    angleLists = [[30.0 * almath.TO_RAD, 0.0],
                  [30.0 * almath.TO_RAD, 0.0],
                  [30.0 * almath.TO_RAD, 0.0]]
    timeLists = [[1.0, 2.0], [1.0, 2.0], [1.0, 2.0]]
    isAbsolute = True
    #motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    motionProxy.setStiffnesses("Head", 0.0)
    motionProxy.setStiffnesses("RArm", 0.0)


if __name__ == "__main__":
    robotIp = "192.168.90.238"
    port = 9559

    topCamera = 0
    bottomCamera = 1
    # utils.getCameraFeed(robotIp, port, topCamera)

    effectorName = "LArm"
    # main(robotIp, port, effectorName)
    # joints(robotIp)
    angleInterpolation(robotIp)
