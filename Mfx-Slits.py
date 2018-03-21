from bluesky import RunEngine
from ophyd import EpicsSignal, EpicsSignalRO
from pcdsdevices import epicsmotor, Slits
from bluesky.plan_stubs import *
import sys


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

    msSlit: Slit
        The DG2 Midstream slit requires a different in-value and was separated
        from the slitArray

    mirrPos: 0 or 1
        This value will determine the position of the mirror. 0 indicates the mirror
        will be in the 'OUT' position and 1 will place the mirror in the 'IN'
        position

    slitVal: inVal or outVal
        Depending on the position of the mirror, the values of the slits will also
        be in either an IN or OUT position

    msVal: inValMS, outValMS
        Corresponds directly to the values chosen for the mirror position and the 
        slitVal variable. 

    """

    yield from abs_set(refLaser.put(value=mirrPos))
    
    for slit in slitArray:
        if slit.xcenter.readback.value < 0.1 or slit.xcenter.readback.value > -0.1:
            
            yield from mv(slit.xwidth.setpoint.put(value=slitVal))

            if slit.xcenter.readback.value > 0.1 or slit.xcenter.readback.value < -0.1:
                raise ValueError('The xCenter of the slits %s is not equal to 0 AFTER changing the width. It is %s') % (slit, str(slit.xcenter.readback.value))
                return

        else:
            raise ValueError('The xCenter of the slits %s is not equal to 0 BEFORE changing the width. It is %s') % (slit, str(slit.xcenter.readback.value))
            return
        
        if slit.ycenter.readback.value < 0.1 or slit.ycenter.readback.value > -0.1:
            
            yield from mv(slit.ywidth.setpoint.put(value=slitVal))

            if slit.ycenter.readback.value > 0.1 or slit.ycenter.readback.value < -0.1:
                raise ValueError('The yCenter of the slits %s is not equal to 0 AFTER changing the width. It is %s') % (slit, str(slit.ycenter.readback.value))
                return

        else:
            raise ValueError('The yCenter of the slits %s is not equal to 0 BEFORE changing the width. It is %s') % (slit, str(slit.ycenter.readback.value))
            return 


    if msSlit.xcenter.readback.value < 0.1 or msSlit.xcenter.readback.value > -0.1:
    
        yield from mv(msSlit.xwidth.setpoint.put(value=msVal))

        if msSlit.xcenter.readback.value > 0.1 or msSlit.xcenter.readback.value < -0.1:
            raise ValueError('The xCenter of the slits %s is not equal to 0 AFTER changing the width. It is %s') % (msSlit, str(msSlit.xcenter.readback.value))
            return

    else:
        raise ValueError('The xCenter of the slits %s is not equal to 0 BEFORE changing the width. It is %s') % (msSlit, str(msSlit.xcenter.readback.value))
        return
        
    if slit.ycenter.readback.value < 0.1 or slit.ycenter.readback.value > -0.1:
            
        yield from mv(slit.ywidth.setpoint.put(value=slitVal))

        if slit.ycenter.readback.value > 0.1 or slit.ycenter.readback.value < -0.1:
            raise ValueError('The yCenter of the slits %s is not equal to 0 AFTER changing the width. It is %s') % (msSlit, str(msSlit.ycenter.readback.value))
            return

    else:
        raise ValueError('The yCenter of the slits %s is not equal to 0 BEFORE changing the width. It is %s') % (msSlit, str(msSlit.ycenter.readback.value))
        return 

#if __name__ -- '__main__':

    #RE(changeSlits())
