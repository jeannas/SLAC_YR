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

delay_array = []
edge_array = []
fwhm_array = []
amp_array = []

for evt in ds.events():
    delay_array.append(las_dly(evt))
    edge_array.append(tt_edge(evt))
    fwhm_array.append(tt_fwhm(evt))
    amp_array.append(tt_famp(evt))
   
#18500 is the cutoff I determined when it starts missing target

edge_array = np.array(edge_array[0:18500])
delay_array = np.array(delay_array[0:18500])
fwhm_array = np.array(fwhm_array[0:18500])
amp_array = np.array(amp_array[0:18500])
acq_array = np.array(acq[0:18500])

corrected = []
match_acq = []

a = -1.527864480143
b =  0.003652900467
c = -0.000001106143

#Double check the events 
for edge, lase, fwhm, amp, acqi in zip(edge_array, delay_array, fwhm_array, amp_array, acq_array):
    if (fwhm > 250.0) or (fwhm < 50.0):
        continue
    if (amp < 0.02):
        continue
    if (edge > 200) and (edge < 800):
        tt_correction = (a + b*edge + c*edge**2)/1000
        y = lase + tt_correction
        corrected.append(y)
        match_acq.append(acqi)

corrected = np.array(corrected)
match_acq = np.array(match_acq)
#print(len(corrected))
#print(len(match_acq))
#The acq has the NAN values, so this needs to be done
bad = np.isnan(acq)
#bad = np.isnan(match_acq)
nb = np.logical_not(bad)
#bins = np.unique(las).shape[0]
bins = 15
#THIS GETS ORIGINAL PLOT
h,b = np.histogram(las[nb], bins=bins, weights=acq[nb])
#h,b = np.histogram(corrected[nb], bins=bins, weights=match_acq[nb])


plt.figure()
plt.plot(b[:-1], h)
plt.xlabel('Laser Delay')
plt.ylabel('Acqiris Response')
plt.savefig('delay_vs_diode.png')
plt.show()
