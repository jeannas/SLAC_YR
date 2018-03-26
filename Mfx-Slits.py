from bluesky import RunEngine
from ophyd import EpicsSignal, EpicsSignalRO
from pcdsdevices import epicsmotor, Slits
from bluesky.plan_stubs import *
import sys
import numpy as np


RE = RunEngine({})

#Hard-coded Dictionary for positions

states = {'lasin' : 6,
          'lasinMS' : 2,
          'lasout': 0.7}

#Configure devices

inVal = states['lasin']
inValMS = states['lasinMS']
outVal = states['lasout']
outValMS = states['lasout']

dg1Slits = Slits('MFX:DG1:JAWS', name='dg1Slits')
dg2SlitsUS = Slits('MFX:DG2:JAWS:US', name='dg2SlitsUS')
dg2SlitsMS = Slits('MFX:DG2:JAWS:MS', name='dg2SlitsMS')
dg2SlitsDS = Slits('MFX:DG2:JAWS:DS', name='dg2SlitsDS')

refLaser = EpicsSignal('MFX:REFLASER:MIRROR:GO', name = 'refLaser')

slitArray = [dg1Slits, dg2SlitsUS, dg2SlitsDS]


def changeSlits(slitArray, msSlit, mirrPos, slitVal, msVal):

    """
    The user will select the position of the mirror, and will match that position
    with the slit width values defined in the above dictionary
    
    Parameters
    ----------

    slitArray: [Slits]
        The array is defined above. The instantiated slits to be moved
        Array has already been instantiated
        input = slitArray

    msSlit: Slit
        The DG2 Midstream slit requires a different in-value and was separated
        from the slitArray

        input = dg2SlitsMS
    
    mirrPos: 0 or 1
        This value will determine the position of the mirror. 0 indicates the mirror
        will be in the 'OUT' position and 1 will place the mirror in the 'IN'
        position
 
    slitVal: inVal or outVal
        Depending on the position of the mirror, the values of the slits will also
        be in either an IN or OUT position. Both input options have already been
        instantiated
    
    msVal: inValMS, outValMS
        Corresponds directly to the values chosen for the mirror position and the 
        slitVal variable. Both input options have already been instantiated. 
    """

    yield from abs_set(refLaser.put(value=mirrPos))
    
    for slit in slitArray:

        ogSlitXCenter = slit.xcenter.readback.value
        ogSlitYCenter = slit.ycenter.readback.value

        rangeXCenter = np.linspace((ogSlitXCenter - 0.005), (ogSlitXCenter + 0.005))
        rangeYCenter = np.linspace((ogSlitYCenter - 0.005), (ogSlitYCenter + 0.005))

        if slit.xcenter.readback.value not in rangeXCenter:

            raise ValueError("The position of the %s XCenter has signficantly changed since being instantiated. The current position is %s") % (slit, str(slit.xcenter.readback.value))
            return
            
        else:
            print("Moving slits to inputted location")
            yield from mv(slit.xwidth,setpoint, slitVal)
       
           if slit.xcenter.readback.value not in rangeXCenter:
               print("Changing %s XWidth has significantly changed %s XCenter. Current %s X Center slit position is %s") % (slit, slit,  str(slit.xcenter.readback.value))
               yield from mv(slit.xcenter.setpoint, ogSlitXCenter)

 
        if slit.ycenter.readback.value not in rangeYCenter:
            
                raise ValueError("The position of the %s YCenter has signficantly changed since being instantiated. The current position is %s") % (slit, str(slit.ycenter.readback.value))))
                return

        else:
            print("Moving slits to inputted location")
            yield from mv(slit.ywidth.setpoint, slitVal)


           if slit.Ycenter.readback.value not in rangeYCenter:
               print("Changing %s YWidth has significantly changed %s YCenter. Current %s Y Center slit position is %s") % (slit, slit,  str(slit.ycenter.readback.value))
               yield from mv(slit.ycenter.setpoint, ogSlitYCenter)


    msSlitXCenter = msSlit.xcenter.readback.value
    msSlitYCenter = msSlit.ycenter.readback.value

    rangeMSXCent = np.linspace((msSlitXCenter - 0.005), (msSlitXCenter + 0.005))
    rangeMSYCent = np.linspace((msSlitYCenter - 0.005), (msSlitYCenter + 0.005))

    if msSlit.xcenter.readback.value not in rangeMSXCent:

        raise ValueError("The position of the %s xCenter has significantly changed since being instantiated. The current position is %s") % (msSlit, str(msSlit.xcenter.readback.value))
        return
  
    else:
        print("Moving %s to inputted location") % (msSlit)
        yield from mv(msSlit.xwidth.setpoint, msVal)

        if msSlit.xcenter.readback.value not in rangeMSXCent:
            print("Changing %s XWidth has significantly changed %s XCenter. Current %s X Center slit position is %s") % (msSlit, msSlit, str(msSlit.xcenter.readback.value))            
            yield from mv(msSlit.xcenter.setpoint, msSlitXCenter)
        
    if msSlit.ycenter.readback.value not in rangeMSYCent:
        raise ValueError("The position of the %s xCenter has significantly changed since being instantiated. The current position is %s") % (msSlit, str(msSlit.ycenter.readback.value)) 
        return

    else:
        yield from mv(msSlit.ywidth.msVal)

        if msSlit.ycenter.readback.value not in rangeMSYCent:
            print("Changing %s YWidth has significantly changed %s YCenter. Current %s Y Center slit position is %s") % (msSlit, msSlit, str(msSlit.ycenter.readback.value))  
            yield from mv(msSlit.ycenter.setpoint, msSlitYCenter)

#if __name__ -- '__main__':

    #RE(changeSlits())
