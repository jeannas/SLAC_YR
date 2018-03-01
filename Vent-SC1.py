from bluesky import RunEngine
import bluesky.plans as bp
from pcdsdevices import Device, GateValve
from ophyd import Device, EpicsSignal, EpicsSignalRO, EpicsMotor
from turbo import *
from bluesky.callbacks.best_effort import BestEffortCallback
import sys, time


#Set up various devices to be usedi and refresh their values during venting

def configureDevices():

    #Detector Motor
    SC1_detMotor = EpicsMotor('CXI:DS1:MMS:06', name='SC1_detMotor')

    #Gate Valves
    SC1_gate = GateValve('CXI:SC1:VGC:01', name='SC1_gateValve')
    DS1_gate = GateValve('CXI:SC1:VGC:02', name='DS1_gateValve')

    #DS1 Pin
    DS1_pin = EpicsSignal('CXI:SC1:VGC:02:PININ_DI', name = 'DS1_pin')

    #Turbos
    turbo1 = Turbo('CXI:SC1:PTM:01', name='turbo1')
    turbo2 = Turbo('CXI:SC1:PTM:02', name='turbo2')
    turbo3 = Turbo('CXI:SC1:PTM:03', name='turbo3')

    #Main Turbo Valve
    mainTurboValve = GateValve('CXI:SC1:VGC:03', name='mainTurboValve')

    #Foreline Valves
    foreline1 = GateValve('CXI:SC1:VIC:04', name='foreline1')
    foreline2 = GateValve('CXI:SC1:VIC:05', name='foreline2')

    #Vent Valve
    ventValve1 = GateValve('CXI:SC1:VCC:01', name='ventValve1')
    ventValve2 = GateValve('CXI:SC1:VCC:02', name='ventValve2')

    #Cold Cathodes
    coldCathode = EpicsSignal('CXI:SC1:GCC:01:ENBL_SW', name='coldCathode') 

    #Sample Chamber Pressure

    chamberPressure = EpicsSignal('CXI:SC1:GPI:01:PMON', name='chamberPressure')
    cPressTorr = chamberPressure.value
    cPressmTorr = (chamberPressure.value * 1000)

#Set up RunEngine

RE = RunEngine({})
bec = BestEffortCallback()
RE.subscribe(bec)

#Step 1 - Check if detector is moved back, pin is removed, and gate Valves are closed

def moveDetBack():
    #Check current motor position

    if SC1_detMotor.user_readback.value > -.001:
        print("Detector is already moved back")

    else:
        print("Current detector position is : %s") % (SC1_detMotor.user_readback.value)
        print("Detector is moving back")
        yield from mv(SC1_detMotor, 0)
        print("Detector is home at position: %s") % (SC1_detMotor.user_readback.value)

def checkValvesAndPin():

    if SC1_gate.command.value == 0:
        print("The SC1 gate valve is already closed")

    else:
        print("Will close SC1 gate valve")
        yield from SC1_gate.close()
        print("SC1 gate valve is closed")

    if DS1_pin.value == 1:
        print("You forgot to remove the DSC pin you dumb scientist. Go fix this")
        sys.exit()    

    if DS1_gate.command.value == 0:
        print("The DSC gate valve is already closed")
 
    else:
        print("Will close DSC gate valve")
        yield from DS1_gate.close()
        print("DSC gate valve is closed")

    if mainTurboValve.command.value == 0:
        print("Main turbo gate valve is already closed")

    else:
        print("Will close main turbo gate valve")
        yield from mainTurboValve.closed()
        print("Main turbo valve closed")

    if foreline1.command.value == 0:
        print("Foreline valve 1 is already closed")
    
    else:
        print("Will close foreline valve 1")
        yield from foreline1.closed()
        print("Foreline valve 1 is closed")


    if foreline2.command.value == 0:
        print("Foreline valve 2 is already closed")

    else:
        print("Will close foreline valve 2")
        yield from foreline1.closed()
        print("Foreline valve 2 is closed")


def turnOffAllTurbos():

    yield from turbo1.turnOff()
    print("Turbo1 turned off")

    yield from turbo2.turnOff()
    print("Turbo2 turned off")
 
    yield from turbo3.turnOff()
    print("Turbo3 turned off")

    yield from coldCathode.put(value=0)
    print("Cold Cathode turned off")



def ventSC1():

    #Round 1
    print("Vent cycle is beginning - 30sec delays")

    for _ in range(2):

        yield from ventValve1.open()
        time.sleep(0.5)
        yield from ventValve1.close()
        yield from ventValve2.open()
        time.sleep(0.5)
        yield from ventValve2.close()
        time.sleep(30)

    #Round 2
    print("2nd round starting - 30sec delays")

    for _ in range(5):

        yield from ventValve1.open()
        time.sleep(1)
        yield from ventValve1.close()
        yield from ventValve2.open()
        time.sleep(1)
        yield from ventValve2.close()
        time.sleep(30)       
 
    #Round 3
    print("Venting is moving faster - 5sec delays")

    for _ in range(20):

        yield from ventValve1.open()
        yield from ventValve2.open()
        time.sleep(1)
        yield from ventValve1.close()
        yield from ventValve2.close()
        time.sleep(5)

     #Round 4
     print("Increasing vent speed - 2sec delays")

     for _ in range(20):

         yield from ventValve1.open()
         yield from ventValve2.open()
         time.sleep(2)
         yield from ventValve1.close()
         yield from ventValve2.close()
         time.sleep(2)

    #Round 5
    print("Last vent cycle - 1sec delays")

    for _ in range(20):

        yield from ventValve1.open()
        yield from ventValve2.open()
        time.sleep(1)
        yield from ventValve1.close()
        yield from ventValve2.close()
        time.sleep(1)

    print("Venting is complete")

def scrubCycle():

    print("Scrubbing cycle will now commence")
    print("The current chamber pressure is %s mTorr") % (cPressmTorr)

    for _ in range(5):
        while cPressmTorr < 500000:
            yield from ventValve1.open()
            yield from ventValve2.open()
            time.sleep(20)
            print("The current chamber pressure is %s mTorr") % (cPressmTorr)

        yield from ventValve1.close()
        yield from ventValve2.close()

        print("Opening the foreline valves")

        yield from foreline1.open()
        yield from foreline2.open()

        while cPressmTorr > 500:
            print("The chamber pressure has not reached 500 mTorr")
            print("The current chamber pressure is %s mTorr") % (cPressmTorr)
            time.sleep(30)

        print("Closing the fore line valves")
        yield from foreline1.close()
        yield from foreline2.close()

    print("Scrubbing complete - leaving chamber under rough vac for the night")
    yield from foreline1.open()
    yield from foreline2.open()

RE(configureDevices())
RE(moveDetBack())
RE(configureDevices())
RE(checkValvesAndPin())
RE(configureDevices())
RE(turnOffAllTurbos())
RE(configureDevices())
time.sleep(300)
RE(configureDevices())
RE(ventSC1())
RE(configureDevices())
RE(scrubCycle())
