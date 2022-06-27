import almath
import almath as m  # python's wrapping of almath
from naoqi import ALProxy


def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)


def turnToHeadAngle(motionProxy):
    # Set NAO in stiffness On
    StiffnessOn(motionProxy)

    motionProxy.setWalkArmsEnabled(True, True)

    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    # pitch = memoryProxy.getData("HeadPitch")
    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)

    # theta is the angle of the headYaw
    Theta = commandAngles[0]

    motionProxy.angleInterpolation('HeadYaw', 0.0, 1, True)

    # rotating with theta to face the object
    motionProxy.post.moveTo(0.0, 0.0, Theta)
    motionProxy.waitUntilMoveIsFinished()


def walkDistanceAndRotate(motionProxy, distance, theta=0.0):
    # Set NAO in stiffness On
    StiffnessOn(motionProxy)

    #####################
    ## Enable arms control by move algorithm
    #####################
    motionProxy.setWalkArmsEnabled(True, True)
    # ~ motionProxy.setWalkArmsEnabled(False, False)

    #####################
    ## FOOT CONTACT PROTECTION
    #####################
    # ~ motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION",False]])
    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    #####################
    ## get robot position before move
    #####################
    initRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))

    # pitch = memoryProxy.getData("HeadPitch")
    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)

    # frontal
    X = distance
    # lateral
    Y = 0.0
    # Theta = -math.pi/2.0
    # Theta = 0.0

    # theta is the angle of the headYaw
    Theta = commandAngles[0]

    # Theta = -105 * almath.TO_RAD

    jointName = ["HeadYaw", "HeadPitch"]
    angle = [0.0 * almath.TO_RAD, (commandAngles[1] * almath.TO_DEG + 5) * almath.TO_RAD]
    timeList = [[1.0], [1.0]]

    # rotating with theta to face the object
    motionProxy.post.moveTo(0.0, 0.0, Theta)
    motionProxy.waitUntilMoveIsFinished()
    # wait is useful because with post moveTo is not blocking function
    motionProxy.angleInterpolation(jointName, angle, timeList, True)
    motionProxy.waitUntilMoveIsFinished()

    # actual moving
    motionProxy.post.moveTo(X, 0.0, 0.0)
    motionProxy.waitUntilMoveIsFinished()

    #####################
    ## get robot position after move
    #####################
    endRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))

    #####################
    ## compute and print the robot motion
    #####################
    robotMove = m.pose2DInverse(initRobotPosition) * endRobotPosition
    print "Robot Moved :", robotMove


def walkDistance(motionProxy, distance):
    StiffnessOn(motionProxy)

    motionProxy.setWalkArmsEnabled(True, True)

    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    initRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))

    # actual moving
    motionProxy.post.moveTo(distance, 0.0, 0.0)
    motionProxy.waitUntilMoveIsFinished()

    endRobotPosition = m.Pose2D(motionProxy.getRobotPosition(False))

    robotMove = m.pose2DInverse(initRobotPosition) * endRobotPosition
    print "Robot Moved :", robotMove


def initialPosture(motionProxy, postureProxy):
    # motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [1.0 * almath.TO_RAD, -9.0 * almath.TO_RAD],
    #                                [[1.0], [1.0]], True)
    # postureProxy.goToPosture("Stand", 0.5)
    postureProxy.goToPosture("StandInit", 0.5)
    motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [0.0 * almath.TO_RAD, -14.0 * almath.TO_RAD],
                                   [[0.5], [0.5]], True)


def getReady(motionProxy, postureProxy):
    postureProxy.goToPosture('Crouch', 1.0)

    # Wake up robot
    motionProxy.wakeUp()

    initialPosture(motionProxy, postureProxy)


def getUnready(motionProxy, postureProxy):
    initialPosture(motionProxy, postureProxy)
    postureProxy.goToPosture('Crouch', 1.0)


def turnToAngle(motionProxy, degrees):
    StiffnessOn(motionProxy)

    motionProxy.setWalkArmsEnabled(True, True)

    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    Theta = degrees * almath.TO_RAD
    # rotating with theta
    motionProxy.post.moveTo(0.0, 0.0, Theta)
    motionProxy.waitUntilMoveIsFinished()


if __name__ == "__main__":
    # robotIp = "192.168.90.238"

    # girl
    robotIp = "172.20.10.3"

    # boy
    # robotIp = "172.20.10.5"

    motionProxy = ALProxy("ALMotion", robotIp, 9559)

    walkDistanceAndRotate(motionProxy, 1.73, 0.0)
