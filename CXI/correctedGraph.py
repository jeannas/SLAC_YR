import psana
import numpy as np
from matplotlib import pyplot as plt


ds = psana.MPIDataSource('exp=cxilr3816:run=8:smd')
smd = ds.small_data('run8_acq_data.h5')

las_dly = psana.Detector('LAS:FS5:VIT:FS_TGT_TIME_DIAL', ds.env())
tt_edge = psana.Detector('CXI:TTSPEC:FLTPOS', ds.env())

delayArray = []
edgeArray = []

for evt in ds.events():
    delayArray.append(las_dly(evt))
    edgeArray.append(tt_edge(evt))

edgeArray = np.array(edgeArray[0:19800])
delayArray = np.array(delayArray[0:19800])

for n,evt in enumerate(ds.events()):

    try:
        diode = np.sum( acq(evt)[0][0,760:860] )
    except:
        diode = None
    delay = las_delay(evt)

    smd.event(acqiris=diode,
              las_delay=delay)

    if smd.master:
        if n % 100 == 0:
            print n

smd.save()

corrected = []

a = -1.527864480143
b =  0.003652900467
c = -0.000001106143

for edge, las in zip(edgeArray, delayArray):
    tt_correction = a + b*edge + c*edge**2
    y = las + tt_correction
    corrected.append(y)



