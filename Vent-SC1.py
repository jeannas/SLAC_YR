from bluesky import RunEngine
import bluesky.plans as bp
from pcdsdevices import Device, GateValve
from ophyd import Device, EpicsSignal, EpicsSignalRO, EpicsMotor
from turbo import *
from bluesky.callbacks.best_effort import BestEffortCallback
import sys, time


#Set up various devices to be used

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
#No Device exists yet, need to figure out how to read a PV

coldCathode = EpicsSignal('CXI:SC1:GCC:01:ENBL_SW', name='coldCathode') 


#Step 1 - Check if detector is moved back, pin is removed, and gate Valves are closed

RE = RunEngine({})
bec = BestEffortCallback()
RE.subscribe(bec)


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
        SC1_gate.close()
        print("SC1 gate valve is closed")

    if DS1_pin.value == 1:
        print("You forgot to remove the DSC pin you dumb scientist. Go fix this")
        sys.exit()    

    if DS1_gate.command.value == 0:
        print("The DSC gate valve is already closed")
 
    else:
        print("Will close DSC gate valve")
        DS1_gate.close()
        print("DSC gate valve is closed")

    if mainTurboValve.command.value == 0:
        print("Main turbo gate valve is already closed")

    else:
        print("Will close main turbo gate valve")
        mainTurboValve.closed()
        print("Main turbo valve closed")

    if foreline1.command.value == 0:
        print("Foreline valve 1 is already closed")
    
    else:
        print("Will close foreline valve 1")
        foreline1.closed()
        print("Foreline valve 1 is closed")


    if foreline2.command.value == 0:
        print("Foreline valve 2 is already closed")

    else:
        print("Will close foreline valve 2")
        foreline1.closed()
        print("Foreline valve 2 is closed")


def turnOffAllTurbos():

    turbo1.turnOff()
    print("Turbo1 turned off")

    turbo2.turnOff()
    print("Turbo2 turned off")
 
    turbo3.turnOff()
    print("Turbo3 turned off")

    coldCathode.put(value=0)
    print("Cold Cathode turned off")



def ventSC1():

    #Round 1
    print("Vent cycle is beginning - 30sec delays")

    for _ in range(2):

        ventValve1.open()
        time.sleep(0.5)
        ventValve1.close()
        ventValve2.open()
        time.sleep(0.5)
        ventValve2.close()
        time.sleep(30)

    #Round 2
    print("2nd round starting - 30sec delays")

    for _ in range(5):

        ventValve1.open()
        time.sleep(1)
        ventValve1.close()
        ventValve2.open()
        time.sleep(1)
        ventValve2.close()
        time.sleep(30)       
 
    #Round 3
    print("Venting is moving faster - 5sec delays")

    for _ in range(20):

        ventValve1.open()
        ventValve2.open()
        time.sleep(1)
        ventValve1.close()
        ventValve2.close()
        time.sleep(5)

     #Round 4
     print("Increasing vent speed - 2sec delays")

     for _ in range(20):

         ventValve1.open()
         ventValve2.open()
         time.sleep(2)
         ventValve1.close()
         ventValve2.close()
         time.sleep(2)

    #Round 5
    print("Last vent cycle - 1sec delays")

    for _ in range(20):

        ventValve1.open()
        ventValve2.open()
        time.sleep(1)
        ventValve1.close()
        ventValve2.close()
        time.sleep(1)

    print("Venting is complete")

    ventValve1.open()
    ventValve2.open()



RE(moveDetBack())
RE(checkValvesAndPin())
RE(turnOffAllTurbos())
RE(ventSC1())
