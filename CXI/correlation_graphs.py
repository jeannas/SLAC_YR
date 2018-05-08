import psana
import numpy as np
from matplotlib import pyplot as plt


ds = psana.DataSource('exp=cxilr3816:run=8:smd')

las_dly = psana.Detector('LAS:FS5:VIT:FS_TGT_TIME_DIAL', ds.env())
tt_edge = psana.Detector('CXI:TTSPEC:FLTPOS', ds.env())
tt_famp = psana.Detector('CXI:TTSPEC:AMPL', ds.env())
tt_fwhm = psana.Detector('CXI:TTSPEC:FLTPOSFWHM', ds.env())

ampArray =  []
fwhmArray = []
delayArray = []
edgeArray = []

for evt in ds.events():
    ampArray.append(tt_famp(evt))
    fwhmArray.append(tt_fwhm(evt))
    delayArray.append(las_dly(evt))
    edgeArray.append(tt_edge(evt))    

#This specific ex has cutoff at 19,800

#edgeArray = np.array(edgeArray)
#ampArray = np.array(ampArray)
#fwhmArray = np.array(fwhmArray)
#print(len(edgeArray))
#print(len(ampArray))

edgeArray = np.array(edgeArray[0:19800])
ampArray = np.array(ampArray[0:19800])
delayArray = np.array(delayArray[0:19800])
fwhmArray = np.array(fwhmArray[0:19800])

#plt.scatter(edgeArray, delayArray)
#plt.xlabel('FLTPOS')
#plt.ylabel('DELAY')
#plt.show()


corrected = []

a = -1.527864480143
b =  0.003652900467
c = -0.000001106143

for edge, las in zip(edgeArray, delayArray):
    tt_correction = a + b*edge + c*edge**2
    y = las + tt_correction
    corrected.append(y)
print(corrected)


smd = ds.small_data('run8_acq_data.h5')
evr = psana.Detector('NoDetector.0.Evr.1')
acq = psana.Detector('Acqiris')
