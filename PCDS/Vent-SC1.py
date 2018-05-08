from bluesky import RunEngine
from pcdsdevices import Device, GateValve
from ophyd import Device, EpicsSignal, EpicsSignalRO, EpicsMotor
from turbo import *
from bluesky.callbacks.best_effort import BestEffortCallback
import sys, time
from bluesky.plan_stubs import mv,abs_set,sleep

#Set up various devices to be usedi and refresh their values during venting


#Detector Motor
SC1_detMotor = EpicsMotor('CXI:DS1:MMS:06', name='SC1_detMotor')

#Main Gate Valves
SC1_gate = GateValve('CXI:SC1:VGC:01', name='SC1_gateValve')
DS1_gate = GateValve('CXI:SC1:VGC:02', name='DS1_gateValve')
mainTurboValve = GateValve('CXI:SC1:VGC:03', name='mainTurboValve')

#DS1 Pin
DS1_pin = EpicsSignal('CXI:SC1:VGC:02:PININ_DI', name = 'DS1_pin')

#Turbos
turbo1 = Turbo('CXI:SC1:PTM:01', name='turbo1')
turbo2 = Turbo('CXI:SC1:PTM:02', name='turbo2')
turbo3 = Turbo('CXI:SC1:PTM:03', name='turbo3')

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

#Set up RunEngine

RE = RunEngine({})
bec = BestEffortCallback()
RE.subscribe(bec)

#Step 1 - Check if detector is moved back

def moveDetBack():
    #Check current motor position

    if SC1_detMotor.user_readback.value > -.001:
        print("Detector is already moved back")

    else:
        print("Current detector position is : " + str(SC1_detMotor.user_readback.value)) 
        print("Detector is moving back")
        yield from mv(SC1_detMotor, 0)
        print("Detector is home at position: ") + str(SC1_detMotor.user_readback.value)

#Step 2 - Check that pin is removed and close the turbo gate valves

def checkMainValvesAndPin(mainValves):

    if DS1_pin.value == 1:
        print("You forgot to remove the DSC pin you dumb scientist. Go fix this")
        return 

    for gateValve in mainValves:
        if gateValve.command.value == 0:
            print("%s valve is already is closed") % (gateValve)

        else:
            yield from mv(gateValve.close())
            print("%s valve has been closed") % (gateValve)

#Step 3 - close the foreline gate valves/turn off cold cathode

def closeForelines(forelineValves):

    for valve in forelineValves:
        if valve.command.value == 0:
            print("%s valve is already closed") % (valve)
        else:
            yield from mv(valve.close())
            print("%s valve is now closed") % (valve)

    yield from abs_set(coldCathode.put(value=0)) 
    print("Cold cathode is turned off")

#Step 4 - Turn off all the turbos

def turnOffTurbos(turbos):
 
    for turbo in turbos:
        yield from mv(turbo.turnOff())
        print("%s is now turned off") % (turbo)

#Convenience functions for venting (for the vent valves)

def alternateVentOnOff (ventValves, numberCycles, timeBtwnAlt, delayTime):

    for _ in range(numberCycles):

        for valve in ventValves:
            yield from mv(valve.open())
            yield from sleep(timeBtwnAlt)
            yield from mv(valve.close())
            
        yield from sleep(delayTime)

def ventOnVentOff (numberCycles, openTime, closeTime):

    for _ in range(numberCycles):

        yield from mv(ventValve1.open(), ventValve2.open())
        yield from sleep(openTime)
        yield from mv(ventValve1.close(), ventValve.close())
        yield from sleep(closeTime)

#Scrub Cycle

def scrubCycle(numberOfCycles, ventValves, forelineValves):

    print("Scrubbing cycle will now commence")
    print("The current chamber pressure is " +  str((chamberPressure.value * 1000)) + " mTorr")

    for _ in range(numberOfCycles):

        while (chamberPressure.value * 1000) < 50000:
            for valve in ventValves:
                yield from mv(valve.open())
            print("The current chamber pressure is " +  str((chamberPressure.value * 1000)) + " mTorr")
            yield from sleep(20)

        for valve in ventValves:
            yield from mv(valve.close())

        for valve in forelineValves:
            yield from mv(valve.open())

        while (chamberPressure.value * 1000) > 500:
            yield from sleep(30)
            print("The current chamber pressure is " +  str((chamberPressure.value * 1000)) + " mTorr")
        
        for valve in forelineValves:
            yield from mv(valve.close())

    print("Scrubbing complete - leaving chamber under rough vac for the night")
    for valve in forelineValves:
        yield from mv(valve.close())
     
if __name__ == "__main__":

    ventValves = [ventValve1, ventValve2]
    mainValves = [SC1_gate, DS1_gate, mainTurboValve]
    turbos = [turbo1, turbo2, turbo3]
    forelineValves = [foreline1, foreline2]

    #Set-up for vent cycle
    RE(moveDetBack())
    RE(checkMainValvesAndPin(mainValves))
    RE(turnOffTurbos(turbos))
    RE(closeForelines(forelineValves))

    #Start vent cycle
    print("1st round starting - 2 cycles, 30 second delays, 0.5 secs ventValve on-time")
    RE(alternateVentOnOff(ventValves, 2, 0.5, 30))

    print("2nd round starting - 5 cycles, 30 second delays, 1 secs ventValve on-time")
    RE(alternateVentOnOff(ventValves, 5, 1, 30))

    print("3rd round starting - 20 cycles, both vent on-time 1 sec, 5 sec off-time")
    RE(ventOnVentOff(20, 1, 5))

    print("4th round starting - 20 cycles, both vent on-time 2 sec, 2 sec off-time")
    RE(ventOnVentOff(20, 2, 2))

    print("5th round starting - 20 cycles, both vent on-time 1 sec, 1 sec off-time")
    RE(ventOnVentOff(20,1,1))

    #Scrub cycle
    print("Scrubbing cycle started")
    RE(scrubCycle(5, ventValves, forelineValves))
