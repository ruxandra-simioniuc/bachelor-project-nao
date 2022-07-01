import almath
import time


# returns the head angles in degrees
def getHeadAnglesDeg(motionProxy):
    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)
    return [commandAngles[0] * almath.TO_DEG, commandAngles[1] * almath.TO_DEG]


# returns the head angles in radians
def getHeadAnglesRad(motionProxy):
    commandAngles = motionProxy.getAngles(["HeadYaw", "HeadPitch"], False)
    return commandAngles


# moved head to given angles
# x and y must be in degrees
def moveHeadToCoords(x, y, motionProxy):
    yawAngle = x * almath.TO_RAD
    pitchAngle = y * almath.TO_RAD

    timeList = [[1.0], [1.0]]
    isAbsolute = True

    motionProxy.angleInterpolation(["HeadYaw", "HeadPitch"], [yawAngle, pitchAngle], timeList, isAbsolute)

    # wait for the move to finish
    time.sleep(1.5)

    angles = getHeadAnglesDeg(motionProxy)
    print "After movement Yaw: " + str(angles[0]) + " Pitch: " + str(angles[1])


def lookLeft(motionProxy):
    [_, pitch] = getHeadAnglesRad(motionProxy)
    if pitch * almath.TO_DEG > 12:
        pitch = 5 * almath.TO_RAD
    moveHeadToCoords(12, pitch, motionProxy)


def lookLeftDown(motionProxy):
    [_, pitch] = getHeadAnglesRad(motionProxy)

    if pitch * almath.TO_DEG > 12:
        pitch = 16 * almath.TO_RAD
    else:
        pitch = 12 * almath.TO_RAD

    moveHeadToCoords(12, pitch, motionProxy)


def lookRight(motionProxy):
    [_, pitch] = getHeadAnglesRad(motionProxy)
    if pitch * almath.TO_DEG > 12:
        pitch = 5 * almath.TO_RAD
    moveHeadToCoords(-12, pitch, motionProxy)


def lookRightDown(motionProxy):
    [_, pitch] = getHeadAnglesRad(motionProxy)

    if pitch * almath.TO_DEG > 12:
        pitch = 16 * almath.TO_RAD
    else:
        pitch = 12 * almath.TO_RAD

    moveHeadToCoords(-12, pitch, motionProxy)


def lookFrontDown(motionProxy):
    [_, pitch] = getHeadAnglesRad(motionProxy)

    if pitch * almath.TO_DEG > 12:
        pitch = 16 * almath.TO_RAD
    else:
        pitch = 14 * almath.TO_RAD

    moveHeadToCoords(0.0, pitch, motionProxy)


