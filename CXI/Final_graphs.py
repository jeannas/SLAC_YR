import psana
import numpy as np
from matplotlib import pyplot as plt
import h5py

f = h5py.File('run8_acq_data.h5')

#Pull vars from h5 file (refer to get_acq_data.py)
acq = np.array(f['acqiris'][:18500])
las = np.array(f['las_delay'][:18500])

edge  = np.array(f['edge'][0:18500])
delay = np.array(f['las_delay'][0:18500])
fwhm  = np.array(f['fwhm'][0:18500])
amp   = np.array(f['famp'][0:18500])

correction = np.array(f['edge_ps'][0:18500])

f.close()

#Filters to apply to data

fwhm_veto = (fwhm < 250.0) * (fwhm > 50.0)
amp_veto = (amp > 0.02)
range_veto = (edge < 200) * (edge > 800)

bad = np.isnan(Acq)
nb = np.logical_not(bad)

keepers = fwhm_veto * amp_veto * range_veto * nb

h,b = np.histogram(correction[keepers], bins=bins, weights=acq[keepers])


plt.figure()
plt.plot(b[:-1], h)
plt.xlabel('Laser Delay')
plt.ylabel('Acqiris Response')
#plt.savefig('delay_vs_diode.png')
plt.show()
