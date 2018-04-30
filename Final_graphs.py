import psana
import numpy as np
from matplotlib import pyplot as plt
import h5py

ds = psana.MPIDataSource('exp=cxilr3816:run=8:smd')
#smd = ds.small_data('run8_acq_data.h5')
f = h5py.File('run8_acq_data.h5')
acq = np.array(f['acqiris'])
las = np.array(f['las_delay'])

las_dly = psana.Detector('LAS:FS5:VIT:FS_TGT_TIME_DIAL', ds.env())
tt_edge = psana.Detector('CXI:TTSPEC:FLTPOS', ds.env())
tt_fwhm = psana.Detector('CXI:TTSPEC:FLTPOSFWHM', ds.env())
tt_famp = psana.Detector('CXI:TTSPEC:AMPL', ds.env())

delayArray = []
edgeArray = []
fwhmArray = []
ampArray = []

for evt in ds.events():
    delayArray.append(las_dly(evt))
    edgeArray.append(tt_edge(evt))
    fwhmArray.append(tt_fwhm(evt))
    ampArray.append(tt_famp(evt))
   
#18500 is the cutoff I determined when it starts missing target

edgeArray = np.array(edgeArray[0:18500])
delayArray = np.array(delayArray[0:18500])
fwhmArray = np.array(fwhmArray[0:18500])
ampArray = np.array(ampArray[0:18500])

corrected = []

a = -1.527864480143
b =  0.003652900467
c = -0.000001106143

#Double check the events 
for edge, lase, fwhm, amp in zip(edgeArray, delayArray, fwhmArray, ampArray):
    if (fwhm > 250.0) or (fwhm < 50.0):
        continue
    if (amp < 0.02):
        continue
    if (edge > 200) and (edge < 800):
        tt_correction = (a + b*edge + c*edge**2)/1000
        y = lase + tt_correction
        corrected.append(y)

#The acq has the NAN values, so this needs to be done
bad = np.isnan(acq)
nb = np.logical_not(bad)
bins = np.unique(las).shape[0]
h,b = np.histogram(las, bins=bins, weights=acq)

plt.figure()
plt.plot(b[:-1], h)
plt.xlabel('Laser Delay')
plt.ylabel('Acqiris Response')
plt.savefig('delay_vs_diode.png')
plt.show()
