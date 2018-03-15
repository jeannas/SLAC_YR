from pcdsdevices import epicsmotor
from bluesky.plan_stubs import *
from bluesky import RunEngine
from ophyd import Device, EpicsSignal, EpicsSignalRO, EpicsMotor
import sys


"""

Moving CXI-stands between the kb1, kb2, and straight configurations

This script will require the user to input the stand as an argument
The dictionary below contains the values for the positions of the
respective configurations. 
Using bluesky, the user can edit the # of steps, and the time
between each step to ensure that the motors move
simultaneously at a defined speed.

"""


#Jason's Stand Dictionary for values
"""

Dictionary containing the final position for kb1/kb2 config
Contains the pvs to create epicsmotor devices with

"""

_stands = ['standDG2', 'stand1MS', 'standDG3', 'standDG4']

_stand_detectors = {
         'stand1MS': {
                      'Ax': {'kb1': 84.3998, 'kb2': 64.18,    'pv': 'CXI:1MS:MMS:04'},
                      'Ay': {'kb1': 81.5299, 'kb2': 55.2699,  'pv': 'CXI:1MS:MMS:05'},
#                      'Az': {'kb1': 9.3998,  'kb2': 9.39978,  'pv': 'CXI:1MS:MMS:06'},
                      'By': {'kb1': 52.281,  'kb2': 31.4952,  'pv': 'CXI:1MS:MMS:01'},
                      'Cx': {'kb1': 54.9002, 'kb2': 37.3503,  'pv': 'CXI:1MS:MMS:02'},
                      'Cy': {'kb1': 52.3008, 'kb2': 31.415,   'pv': 'CXI:1MS:MMS:03'},
                     },
         'standDG2': {
                      'Ax': {'kb1': 36.0798, 'kb2': 20.33,    'pv': 'CXI:DG2:MMS:14'},
                      'Ay': {'kb1': 34.41,   'kb2': 16.58,    'pv': 'CXI:DG2:MMS:15'},
#                      'Az': {'kb1': 0.2002,  'kb2': 0.20021,  'pv': 'CXI:DG2:MMS:16'},
                      'By': {'kb1': 39.88,   'kb2': 21.018,   'pv': 'CXI:DG2:MMS:11'},
                      'Cx': {'kb1': 41.8487, 'kb2': 25.662,   'pv': 'CXI:DG2:MMS:12'},
                      'Cy': {'kb1': 39.9501, 'kb2': 20.988,   'pv': 'CXI:DG2:MMS:13'},
                     },
         'standDG3': {
                      'Ax': {'kb1': 90.7329, 'kb2': 70.0217,  'pv': 'CXI:DG3:MMS:09'},
                      'Ay': {'kb1': 88.406,  'kb2': 60.16,    'pv': 'CXI:DG3:MMS:10'},
#                      'Az': {'kb1': -0.0034, 'kb2': -0.00323, 'pv': 'CXI:DG3:MMS:11'},
                      'By': {'kb1': 91.088,  'kb2': 61.9193,  'pv': 'CXI:DG3:MMS:06'},
                      'Cx': {'kb1': 91.8417, 'kb2': 70.53,    'pv': 'CXI:DG3:MMS:07'},
                      'Cy': {'kb1': 95.2873, 'kb2': 65.8574,  'pv': 'CXI:DG3:MMS:08'},
                     },
         'standDG4': {
                      'Ax': {'kb1': 107.911, 'kb2': 85.4314,  'pv': 'CXI:DG4:MMS:09'},
                     'Ay': {'kb1': 107.333, 'kb2': 76.101,   'pv': 'CXI:DG4:MMS:10'},
#                      'Az': {'kb1': 3.033,   'kb2': 3.03418,  'pv': 'CXI:DG4:MMS:11'},
                      'By': {'kb1': 112.969, 'kb2': 80.77,    'pv': 'CXI:DG4:MMS:06'},
                      'Cx': {'kb1': 113.263, 'kb2': 90.2427,  'pv': 'CXI:DG4:MMS:07'},
                      'Cy': {'kb1': 112.63,  'kb2': 80.35,    'pv': 'CXI:DG4:MMS:08'},
                     },
          }

#Need to define motors at full-scope
"""
Defines and creates the motor objects. Also parses the dictionary
and creates arrays of the kb1/kb2 end positions to use in the
respective bluesky plans

"""

try:
    stand = sys.argv[1]
    standDictionary = _stand_detectors[stand]
    nameArray = []
    pvArray = []
    kb1Positions = []
    kb2Positions = []

    for key, value in standDictionary.items():
        nameArray.append(key)
        pv = value['pv']
        kb1 = value['kb1']
        kb2 = value['kb2']
        pvArray.append(pv)
        kb1Positions.append(kb1)
        kb2Positions.append(kb2)

    motor_Ax = epicsmotor.EpicsMotor(pvArray[0], name = 'motor_Ax')
    motor_Ay = epicsmotor.EpicsMotor(pvArray[1], name = 'motor_Ay')
    motor_By = epicsmotor.EpicsMotor(pvArray[2], name = 'motor_By')
    motor_Cx = epicsmotor.EpicsMotor(pvArray[3], name = 'motor_Cx')
    motor_Cy = epicsmotor.EpicsMotor(pvArray[4], name = 'motor_Cy')

    motorArray = [motor_Ax, motor_Ay, motor_By, motor_Cx, motor_Cy]
    print(motorArray)


except IndexError:
    print("Your choices are 'stand1MS', 'standDG2', 'standDG3', 'standDG4'")

except KeyError:
    print("Your choices are 'stand1MS', 'standDG2', 'standDG3', 'standDG4'")


RE = RunEngine({})



def straightConfig(motorArray, nSteps, tSteps, tWait):
    
    """

    Straight Configuration is all motors return to position 0
    
    Parameters
    ----------

    motorArray: [EpicsMotors]
        The instantiated motor objects that will be moved

    nSteps: Int
        The number of total steps that the motors should take to reach
        position 0. All motors will reach 0 simultaneously

    tSteps: Int
        This number will determine the velocity. The total distance/step
        is calculated in the function. This parameter will determine
        how quickly each step should be taken"

    tWait: Int:
        This number will tell the runEngine how long to wait between
        conducting each step.

    """

    #Variables
    startPosArray = []
    distTravel = []
    endPos = 0
    tweekVals = []
    velocityVals = []

    #Figure out position of motors first
    for motor in motorArray:
        startPos = motor.user_readback.value
        startPosArray.append(startPos)
    
    #Calculate distance to travel for each motor, and set velocity based on distance so motors will reach at position 0 at same time
    for val in startPosArray:
        distance = endPos - val
        distTravel.append(distance)

    for dist in distTravel:
        tweek = dist/nSteps
        tweekVals.append(tweek)
   
    for tweek in tweekVals:
        velocity = tweek/tSteps
        velocityVals.append(velocity)

    for motor in motorArray:
        for veloc in velocityVals:
            yield from abs_set(motor.velocity.put(value=veloc))


    print("Moving all motors to position Zero")

    #All motors will move in calculated steps & speeds to 0, while also reaching 0 simultaneously with tSteps being the time between each step

    for _ in nSteps:
        yield from mv(motorArray[0],tweekVals[0],motorArray[1],tweekVals[1],motorArray[2],tweekVals[2], motorArray[3],tweekVals[3], motorArray[4],tweekVals[4])

        yield from sleep(tWait)
    


def kb1Config(motorArray,kb1Pos,nSteps,tSteps,tWait):


    """

    KB1 configuration requires the motors to be moved to the positions defined
    in the _stand_detector dictionary above
    
    Parameters
    ----------

    motorArray: [EpicsMotors]
        The instantiated motor objects that will be moved

    nSteps: Int
        The number of total steps that the motors should take to reach
        position 0. All motors will reach 0 simultaneously

    kb1Pos: [Float]
        This variable is instantiated with the motors since these values
        come from the dictionary. The values within the array represent
        the end location of each motor in the KB1 configuration.

    tSteps: Int
        This number will determine the velocity. The total distance/step
        is calculated in the function. This parameter will determine
        how quickly each step should be taken"

    tWait: Int:
        This number will tell the runEngine how long to wait between
        conducting each step.

    """

    startPosArray = []
        #Variables
    startPosArray = []
    distTravel = []
    tweekVals = []
    velocityVals = []

    #Figure out position of motors first
    for motor in motorArray:
        startPos = motor.user_readback.value
        startPosArray.append(startPos)

    #Calculate distance to travel for each motor, and set velocity based on distance so motors will reach at position 0 at same time
    for start in startPosArray:
        for final in kb1Pos:
            distance = final - start
            distTravel.append(distance)

    for dist in distTravel:
        tweek = dist/nSteps
        tweekVals.append(tweek)

    for tweek in tweekVals:
        velocity = tweek/tSteps
        velocityVals.append(velocity)

    for motor in motorArray:
        for veloc in velocityVals:
            yield from abs_set(motor.velocity.put(value=veloc))


    print("Moving all motors to position Zero")

    #All motors will move in calculated steps & speeds to 0, while also reaching 0 simultaneously with tSteps being the time between each step

    for _ in nSteps:
        yield from mv(motorArray[0],tweekVals[0],motorArray[1],tweekVals[1],motorArray[2],tweekVals[2], motorArray[3],tweekVals[3], motorArray[4],tweekVals[4])

        yield from sleep(tWait)


def kb2Config(motorArray,kb2Pos,nSteps, tSteps, tWait):

    """

    KB2 configuration requires the motors to be moved to the positions defined
    in the _stand_detector dictionary above
    
    Parameters
    ----------

    motorArray: [EpicsMotors]
        The instantiated motor objects that will be moved

    nSteps: Int
        The number of total steps that the motors should take to reach
        position 0. All motors will reach 0 simultaneously

    kb1Pos: [Float]
        This variable is instantiated with the motors since these values
        come from the dictionary. The values within the array represent
        the end location of each motor in the KB2 configuration.

    tSteps: Int
        This number will determine the velocity. The total distance/step
        is calculated in the function. This parameter will determine
        how quickly each step should be taken"

    tWait: Int:
        This number will tell the runEngine how long to wait between
        conducting each step.

    """

    startPosArray = []
        #Variables
    startPosArray = []
    distTravel = []
    tweekVals = []
    velocityVals = []

    #Figure out position of motors first
    for motor in motorArray:
        startPos = motor.user_readback.value
        startPosArray.append(startPos)

    #Calculate distance to travel for each motor, and set velocity based on distance so motors will reach at position 0 at same time
    for start in startPosArray:
        for final in kb2Pos:
            distance = final - start
            distTravel.append(distance)

    for dist in distTravel:
        tweek = dist/nSteps
        tweekVals.append(tweek)

    for tweek in tweekVals:
        velocity = tweek/tSteps
        velocityVals.append(velocity)

    for motor in motorArray:
        for veloc in velocityVals:
            yield from abs_set(motor.velocity.put(value=veloc))


    print("Moving all motors to position Zero")

    #All motors will move in calculated steps & speeds to 0, while also reaching 0 simultaneously with tSteps being the time between each step

    for _ in nSteps:
        yield from mv(motorArray[0],tweekVals[0],motorArray[1],tweekVals[1],motorArray[2],tweekVals[2], motorArray[3],tweekVals[3], motorArray[4],tweekVals[4])

        yield from sleep(tWait)


#if __name__ == '__main__':

 #   connectStandMotors()    
