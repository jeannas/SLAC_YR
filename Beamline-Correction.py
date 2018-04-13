#import epics_motor
from pcdsdevices import epics_motor
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
                      'Ax': {'kb1': 84.3998, 'kb2': 64.18, 'straight':0,    'pv': 'CXI:1MS:MMS:04'},
                      'Ay': {'kb1': 81.5299, 'kb2': 55.2699, 'straight':0,  'pv': 'CXI:1MS:MMS:05'},
#                      'Az': {'kb1': 9.3998,  'kb2': 9.39978, 'straight':0,  'pv': 'CXI:1MS:MMS:06'},
                      'By': {'kb1': 52.281,  'kb2': 31.4952, 'straight':0,  'pv': 'CXI:1MS:MMS:01'},
                      'Cx': {'kb1': 54.9002, 'kb2': 37.3503, 'straight':0,  'pv': 'CXI:1MS:MMS:02'},
                      'Cy': {'kb1': 52.3008, 'kb2': 31.415, 'straight':0,   'pv': 'CXI:1MS:MMS:03'},
                     },
         'standDG2': {
                      'Ax': {'kb1': 36.0798, 'kb2': 20.33, 'straight':0,    'pv': 'CXI:DG2:MMS:14'},
                      'Ay': {'kb1': 34.41,   'kb2': 16.58, 'straight':0,   'pv': 'CXI:DG2:MMS:15'},
#                      'Az': {'kb1': 0.2002,  'kb2': 0.20021, 'straight':0,  'pv': 'CXI:DG2:MMS:16'},
                      'By': {'kb1': 39.88,   'kb2': 21.018, 'straight':0,   'pv': 'CXI:DG2:MMS:11'},
                      'Cx': {'kb1': 41.8487, 'kb2': 25.662, 'straight':0,   'pv': 'CXI:DG2:MMS:12'},
                      'Cy': {'kb1': 39.9501, 'kb2': 20.988, 'straight':0,   'pv': 'CXI:DG2:MMS:13'},
                     },
         'standDG3': {
                      'Ax': {'kb1': 90.7329, 'kb2': 70.0217, 'straight':0,  'pv': 'CXI:DG3:MMS:09'},
                      'Ay': {'kb1': 88.406,  'kb2': 60.16, 'straight':0,    'pv': 'CXI:DG3:MMS:10'},
#                      'Az': {'kb1': -0.0034, 'kb2': -0.00323, 'straight':0, 'pv': 'CXI:DG3:MMS:11'},
                      'By': {'kb1': 91.088,  'kb2': 61.9193, 'straight':0,  'pv': 'CXI:DG3:MMS:06'},
                      'Cx': {'kb1': 91.8417, 'kb2': 70.53, 'straight':0,    'pv': 'CXI:DG3:MMS:07'},
                      'Cy': {'kb1': 95.2873, 'kb2': 65.8574, 'straight':0,  'pv': 'CXI:DG3:MMS:08'},
                     },
         'standDG4': {
                      'Ax': {'kb1': 107.911, 'kb2': 85.4314, 'straight':0,  'pv': 'CXI:DG4:MMS:09'},
                     'Ay': {'kb1': 107.333, 'kb2': 76.101, 'straight':0,   'pv': 'CXI:DG4:MMS:10'},
#                      'Az': {'kb1': 3.033,   'kb2': 3.03418, 'straight':0,  'pv': 'CXI:DG4:MMS:11'},
                      'By': {'kb1': 112.969, 'kb2': 80.77, 'straight':0,    'pv': 'CXI:DG4:MMS:06'},
                      'Cx': {'kb1': 113.263, 'kb2': 90.2427, 'straight':0,  'pv': 'CXI:DG4:MMS:07'},
                      'Cy': {'kb1': 112.63,  'kb2': 80.35, 'straight':0,    'pv': 'CXI:DG4:MMS:08'},
                     },
          }

#Need to define motors at full-scope
"""
Defines and creates the motor objects. Also parses the dictionary
and creates arrays of the kb1/kb2 end positions to use in the
respective bluesky plans

"""

try:

    nameArray = []
    pvArray = []
    kb1Positions = []
    kb2Positions = []
    zeroPositions = []

    for stand in _stands:
        standDictionary = _stand_detectors[stand]
        for key, value in standDictionary.items():
            nameArray.append(key)
            
            pv = value['pv']
            kb1 = value['kb1']
            kb2 = value['kb2']
            zero = value['straight']
            pvArray.append(pv)
            kb1Positions.append(kb1)
            kb2Positions.append(kb2)
            zeroPositions.append(zero)

except IndexError:
    print("Your choices are 'stand1MS', 'standDG2', 'standDG3', 'standDG4'")

except KeyError:
    print("Your choices are 'stand1MS', 'standDG2', 'standDG3', 'standDG4'")


#SPLIT LISTS TO RESPECTIVE STAND (5 total motors/stand)


def splitLists(array, size):
    x = [array[i:i+size] for i in range(0, len(array), size)]
    return x

pvSplit = splitLists(array=pvArray, size=5)
kb1Split = splitLists(array=kb1Positions, size=5)
kb2Split = splitLists(array=kb2Positions, size=5)
zeroSplit = splitLists(array=zeroPositions, size=5)


#Instantiate Motors by stand
print("Instantiating motors DG2")
DG2_Ax = epics_motor.IMS(pvSplit[0][0], name = 'DG2_Ax')
DG2_Ay = epics_motor.IMS(pvSplit[0][1], name = 'DG2_Ay')
DG2_By = epics_motor.IMS(pvSplit[0][2], name = 'DG2_By')
DG2_Cx = epics_motor.IMS(pvSplit[0][3], name = 'DG2_Cx')
DG2_Cy = epics_motor.IMS(pvSplit[0][4], name = 'DG2_Cy')

DG2Array = [DG2_Ax, DG2_Ay, DG2_By, DG2_Cx, DG2_Cy]
DG2_kb1 = kb1Split[0]
DG2_kb2 = kb2Split[0]
DG2_zero = zeroSplit[0]

print("inistant. MS1")
MS1_Ax = epics_motor.IMS(pvSplit[1][0], name = 'MS1_Ax')
MS1_Ay = epics_motor.IMS(pvSplit[1][1], name = 'MS1_Ay')
MS1_By = epics_motor.IMS(pvSplit[1][2], name = 'MS1_By')
MS1_Cx = epics_motor.IMS(pvSplit[1][3], name = 'MS1_Cx')
MS1_Cy = epics_motor.IMS(pvSplit[1][4], name = 'MS1_Cy')

MS1Array = [MS1_Ax, MS1_Ay, MS1_By, MS1_Cx, MS1_Cy]
MS1_kb1 = kb1Split[1]
MS1_kb2 = kb2Split[1]
MS1_zero = zeroSplit[1]

print("DG3 stands")
DG3_Ax = epics_motor.IMS(pvSplit[2][0], name = 'DG3_Ax')
DG3_Ay = epics_motor.IMS(pvSplit[2][1], name = 'DG3_Ay')
DG3_By = epics_motor.IMS(pvSplit[2][2], name = 'DG3_By')
DG3_Cx = epics_motor.IMS(pvSplit[2][3], name = 'DG3_Cx')
DG3_Cy = epics_motor.IMS(pvSplit[2][4], name = 'DG3_Cy')

DG3Array = [DG3_Ax, DG3_Ay, DG3_By, DG3_Cx, DG3_Cy]
DG3_kb1 = kb1Split[2]
DG3_kb2 = kb2Split[2]
DG3_zero = zeroSplit[2]

print("DG4 stands")
DG4_Ax = epics_motor.IMS(pvSplit[3][0], name = 'DG4_Ax')
DG4_Ay = epics_motor.IMS(pvSplit[3][1], name = 'DG4_Ay')
DG4_By = epics_motor.IMS(pvSplit[3][2], name = 'DG4_By')
DG4_Cx = epics_motor.IMS(pvSplit[3][3], name = 'DG4_Cx')
DG4_Cy = epics_motor.IMS(pvSplit[3][4], name = 'DG4_Cy')

DG4Array = [DG4_Ax, DG4_Ay, DG4_By, DG4_Cx, DG4_Cy]
DG4_kb1 = kb1Split[3]
DG4_kb2 = kb2Split[3]
DG4_zero = zeroSplit[3]

#VARIABLES FOR DG2, MS1, DG3
realStand = DG2Array + MS1Array + DG3Array

kb1All = DG2_kb1 + MS1_kb1 + DG3_kb1
kb2All = DG2_kb2 + MS1_kb2 + DG3_kb2
zeroAll = DG2_zero + MS1_zero + DG3_zero

#VARIABLES FOR DG4 (Practice)
practiceStand = DG4Array
kb1DG4 = DG4_kb1
kb2DG4 = DG4_kb2
zeroDG4 = DG4_zero


RE = RunEngine({})

def setConfig(motorArray, config, nSteps, tSteps, tWait):

    """

    The user will select desired configuration which will move the motors
    to the positions defined in the _stand_detector dictionary above
    
    Parameters
    ----------

    motorArray: [EpicsMotor]
        The instantiated motor objects that will be moved
        For multiple stands, you can add motor Arrays together
        i.e MS1Array + DG2Array + DG3Array

        realStand = [DG2motors, MS1motors, DG3motors]
        practiceStand = [DG4motors]

    nSteps: Int
        The number of total steps that the motors should take to reach
        position 0. All motors will reach 0 simultaneously

    config: [Float]
        The user will select which configuration. The arrays with positions
        are already initialized. Main use is to simultaneously move 1MS,
        DG2, DG3 at once. Practice will be used for DG4, and config choices
        will be listed out.

        kb1All - KB1 configuration with DG2, MS1, DG3 (in that order)
        kb2All - KB2 configuration with DG2, MS1, DG3
        zeroAll - Zero configuratio with DG2, MS1, DG3
        kb1DG4 - KB1 configuration for DG4
        kb2DG4 - KB2 configuration for DG4
        zeroDG4 - Zero configuration for DG4 
          

    tSteps: Int
        This number will determine the velocity. The total distance/step
        is calculated in the function. This parameter will determine
        how quickly each step should be taken

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
    steps = range(1, nSteps + 1)

    nMotors = len(motorArray)
 
    print("Starting now")

    #Figure out position of motors first
    for motor in motorArray:
        print(motor)
        #Enables all motors in array with new component
        motor.enable()
        print("motor enabled")

        startPos = motor.user_readback.value
        startPosArray.append(startPos)

    #Calculate distance to travel for each motor, and set velocity based on distance so motors will reach at position 0 at same time
    #for start in startPosArray:
    #    for final in config:
    #        distance = final - start
    #        distTravel.append(distance)
    #        print("Distances")
    #        print(distance)

    for start, final in zip(startPosArray, config):
        distance = final - start
        distTravel.append(distance)

    for dist in distTravel:
        tweek = dist/nSteps
        tweekVals.append(tweek)

   # for tweek in tweekVals:
   #     velocity = tweek/tSteps
   #     velocityVals.append(velocity)

    #    print("velocity")
    #    print(velocity)

   # for motor in motorArray:
   #     for veloc in velocityVals:
           # yield from abs_set(motor.velocity.put(value=veloc))
   #         yield from mv(motor.velocity, veloc)
   #         print("success with initial params")

    print("Moving all motors to selected Configuration")

    #All motors will move in calculated steps & speeds to 0, while also reaching 0 simultaneously with tSteps being the time between each step

    theorToTravel = []
    for step in steps:

        for tweek, start in zip(tweekVals, startPosArray):
            trav = start + (step * tweek)
            print(tweek)
            print(theorToTravel)
            theorToTravel.append(trav) 

            print(len(theorToTravel))

        yield from mv(motorArray[0], theorToTravel[0], motorArray[1], theorToTravel[1], motorArray[2], theorToTravel[2], motorArray[3], theorToTravel[3], motorArray[4], theorToTravel[4])

        theorToTravel = [] 
        #FOR DG4 PRACTICE (5 MOTORS)
       # yield from mv(motorArray[0],tweekVals[0],motorArray[1],tweekVals[1],motorArray[2],tweekVals[2], motorArray[3],tweekVals[3], motorArray[4],tweekVals[4])

        #FOR DG2 + MS1 + DG3 (15 MOTORS)
       # yield from mv(motorArray[0],tweekVals[0],motorArray[1],tweekVals[1],motorArray[2],tweekVals[2], motorArray[3],tweekVals[3], motorArray[4],tweekVals[4], motorArray[5], tweekVals[5],motorArray[6],tweekVals[6],motorArray[7],tweekVals[7],motorArray[8],tweekVals[8], motorArray[9],tweekVals[9], motorArray[10],tweekVals[10],motorArray[11],tweekVals[11],motorArray[12],tweekVals[12], motorArray[13],tweekVals[13], motorArray[14], tweekVals[14])


        #yield from sleep(tWait)

 #   for motor in motorArray:
  #          for tweek in tweekVals:
  #              for start in startPosArray:
  #                  theorTravl = step * tweek
  #                  mvUp = start + theorTravl
  #                  mvDown = start - theorTravel
  #                  if motor.direction_of_travel.value == 0:
  #                      if motor.user_readback.value not in range((mvDown * .095),(mvDown * 1.05)):
  #                          motor.motor_stop.put(value=1)
  #                          motor.enable(enable=0)
   #                         print("The %s motor has been disabled. The expected position was %s and the current position is %s") % (motor, str(mvDown),str(motor.user_readback.value))

     #               elif motor.direction_of_travel.value == 1:
    #                    if motor.user_readback.value not in range((mvUp * .095),(mvUp * 1.05)):
       #                     motor.motor_stop.put(value=1)
      #                      motor.disable()
        #                    print("The %s motor has been disabled. The expected position was %s and the current position is %s") % (motor, str(mvDown),str(motor.user_readback.value))

if __name__ == '__main__':

    RE(setConfig(motorArray=practiceStand, nSteps=100, config=zeroDG4, tSteps=10, tWait=10))
