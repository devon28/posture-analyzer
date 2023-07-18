# Devon Miller
# Date: 1/3/2023
# Posture analysis backend

import math
from math import acos, degrees

# CLIENT POSITION: profile facing to the right in the picture

def get_results(cordinatesDict):
    "cordinatesDict values: Ear, Shoulder Joint, Low Back, Hip Joint, Knee, hip, Ankle"
    neckAngle = getNeckAngle(cordinatesDict)
    backAngle = getBackAngle(cordinatesDict)
    hipAngle = getHipAngle(cordinatesDict)

    angleDict = {"neck": neckAngle, "back": backAngle, "hip": hipAngle}
    
    issues = getResults(angleDict)
    return {"issues": issues, "angleDict": angleDict}

def getNeckAngle(cordinatesDict):
    """returns angle of neck compared to head"""
    Ear = cordinatesDict["Ear"]
    Neck = cordinatesDict.get("Neck Base")
    rise = Neck[1] - Ear[1]
    run = Ear[0] - Neck[0]
    angle = getAngle(rise, run)
    return angle

def getAngle(rise, run):
    """returns float angle between two landmarks"""
    if run == 0:
        return 0
    hypotnuse = math.sqrt(rise*rise + run*run)
    A = run
    B = hypotnuse
    C = rise
    angle = degrees(acos((A * A + B * B - C * C)/(2.0 * A * B)))
   
    return angle

def getBackAngle(cordinatesDict):
    """returns angle of upperback to shoulder"""
    Neck = cordinatesDict.get("Neck Base")
    upperBack = cordinatesDict.get("Upper Back")
    lowBack = cordinatesDict.get('Low Back')
    rise = lowBack[1] - Neck[1]
    run = max(Neck[0], lowBack[0]) - upperBack[0]
    kyphosisAngle = rise/run
    return kyphosisAngle

def getHipAngle(cordinatesDict):
    """returns low back/hip abnormalities"""
    lowBack = cordinatesDict.get('Low Back')
    Hip = cordinatesDict.get('Hip Joint')
    Knee = cordinatesDict.get('Knee')
    # create triangle
    A = math.sqrt((Hip[1] - lowBack[1])**2 + (Hip[0] - lowBack[0])**2)
    B = math.sqrt((Knee[1] - Hip[1])**2 + (Hip[0] - Knee[0])**2)
    C = math.sqrt((Knee[1] - lowBack[1])**2 + (Knee[0] - lowBack[0])**2)
    angle = degrees(acos((A * A + B * B - C * C)/(2.0 * A * B)))
    return angle

def getResults(angleDict):
    neck = angleDict.get('neck')
    back = angleDict.get('back')
    hip = angleDict.get('hip')

    issueDict = {}
    if neck <= 50:
        muscles = forwardHeadMuscles()
        issueDict['Forward Head Posture'] = muscles
    if back < 3:
        muscles = kyphosisMuscles()
        issueDict['Rounded Back'] = muscles
    if hip > 140:
        muscles = hipMuscles()
        issueDict['Anterior pelvic tilt'] = muscles
    return issueDict

def forwardHeadMuscles():
    tight = "scalenes, SCM, longissimus capitis, Splenius Capitis, pectoralis major/minor"
    weak = "Rhomboids and middle, lower trapezius, Teres Minor and Infraspinatus."
    return {'tight': tight, 'weak': weak}

def kyphosisMuscles():
    tight = "pectoralis major, pectoralis minor, subscapularis, suprspinatus"
    weak = "rhomboids, latisimus dorsi, trapezious"
    return {'tight': tight, 'weak': weak}

def hipMuscles():
    tight = "iliopsoas, rectus femoris, sartorious"
    weak = "gluteals, hamstrings"
    return {'tight': tight, 'weak': weak}
