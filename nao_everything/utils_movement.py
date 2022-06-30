import sys

import almath

def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)


# rotates the body to match the yaw angle of the head
# sets the yaw angle back to 0.0 so the robots faces forward after movement
def turnBodyToHeadAngle(motionProxy):
    # Set NAO in stiffness On
    StiffnessOn(motionProxy)

    motionProxy.setWalkArmsEnabled(True, True)

    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    # pitch = memoryProxy.getData("HeadPitch")
    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)

    # theta is the angle of the headYaw
    Theta = commandAngles[0]

    # rotating with theta to face the object
    motionProxy.post.moveTo(0.0, 0.0, Theta)

    # resetting the yawAngle back to 0.0
    motionProxy.angleInterpolation('HeadYaw', 0.0, 1, True)
    motionProxy.waitUntilMoveIsFinished()


# rotates by the angle of the head yaw then walks the provided distance
def walkDistanceAndRotate(motionProxy, distance):
    # Set NAO in stiffness On
    StiffnessOn(motionProxy)

    motionProxy.setWalkArmsEnabled(True, True)

    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    initRobotPosition = almath.Pose2D(motionProxy.getRobotPosition(False))

    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)

    # frontal
    X = distance

    # theta is the angle of the headYaw
    Theta = commandAngles[0]

    jointName = ["HeadYaw", "HeadPitch"]
    angle = [0.0 * almath.TO_RAD, (commandAngles[1] * almath.TO_DEG + 5) * almath.TO_RAD]
    timeList = [[1.0], [1.0]]

    # rotating with theta to face the object
    motionProxy.post.moveTo(0.0, 0.0, Theta)
    motionProxy.angleInterpolation(jointName, angle, timeList, True)
    motionProxy.waitUntilMoveIsFinished()

    # actual moving
    motionProxy.post.moveTo(X, 0.0, 0.0)
    motionProxy.waitUntilMoveIsFinished()


# moved the provided distance, straight ahead
def walkDistance(motionProxy, distance):
    StiffnessOn(motionProxy)

    motionProxy.setWalkArmsEnabled(True, True)

    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    initRobotPosition = almath.Pose2D(motionProxy.getRobotPosition(False))

    # actual moving
    motionProxy.post.moveTo(distance, 0.0, 0.0)
    motionProxy.waitUntilMoveIsFinished()


# the initial posture configuration
def initialPosture(motionProxy, postureProxy):
    postureProxy.goToPosture("StandInit", 0.5)
    motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [0.0 * almath.TO_RAD, -14.0 * almath.TO_RAD],
                                   [[0.5], [0.5]], True)


# waking up and going to initial posture
def getReady(motionProxy, postureProxy):
    postureProxy.goToPosture('Crouch', 1.0)

    # Wake up robot
    motionProxy.wakeUp()

    initialPosture(motionProxy, postureProxy)


# going to sleep
def getUnready(motionProxy, postureProxy):
    initialPosture(motionProxy, postureProxy)
    postureProxy.goToPosture('Crouch', 1.0)


# turns whole body with degrees
def turnToAngle(motionProxy, degrees):
    StiffnessOn(motionProxy)

    motionProxy.setWalkArmsEnabled(True, True)

    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    Theta = degrees * almath.TO_RAD
    # rotating with theta
    motionProxy.post.moveTo(0.0, 0.0, Theta)
    motionProxy.waitUntilMoveIsFinished()


def defaultStand(postureProxy):
    postureProxy.goToPosture("Stand", 2.5)


def crouch(postureProxy):
    postureProxy.goToPosture("Crouch", 1.5)


# for testing and getting the wanted angles
def arm_movement(motionProxy, arm="RArm"):

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

    names = ["HeadPitch", shoulderPitch, shoulderRoll, elbowYaw, elbowRoll, wristYaw]

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


# moves the hand closer to its head
def lookAtObject(motionProxy):

    arm = "RArm"
    currentArm = "R"

    names = ["HeadPitch", currentArm + "ShoulderPitch", currentArm + "ShoulderRoll", currentArm + "ElbowYaw",
             currentArm + "ElbowRoll", currentArm + "WristYaw"]

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


# extends the arm and opens hand
def extendHand(motionProxy):

    arm = "RArm"
    currentArm = "R"

    names = ["HeadPitch", currentArm + "ShoulderPitch", currentArm + "ShoulderRoll", currentArm + "ElbowYaw",
             currentArm + "ElbowRoll", currentArm + "WristYaw"]

    motionProxy.setStiffnesses(arm, 1.0)

    # angles from Choreographe
    angleList = [[10 * almath.TO_RAD],  # headPitch
                 [45 * almath.TO_RAD],  # shoulderPitch
                 [11 * almath.TO_RAD],  # shoulderRoll
                 [52 * almath.TO_RAD],  # elbowYaw
                 [36 * almath.TO_RAD],  # elbowRoll
                 [99 * almath.TO_RAD]]  # wristYaw

    timeList = [[1.0], [1.0], [1.0], [1.0], [1.0], [1.0], [1.0]]

    isAbsolute = True
    motionProxy.angleInterpolation(names, angleList, timeList, isAbsolute)

    motionProxy.openHand(currentArm + "Hand")
