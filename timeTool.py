import psana
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

 
ds = psana.MPIDataSource('exp=cxilr3816:run=4')
 
evr       = psana.Detector('NoDetector.0:Evr.1')
tt_camera = psana.Detector('Timetool')
tt_pos    = psana.Detector('CXI:TTSPEC:FLTPOS')
tt_amp    = psana.Detector('CXI:TTSPEC:AMPL')
tt_fwhm   = psana.Detector('CXI:TTSPEC:FLTPOSFWHM')
 

fltPosArray = []
roundedFltArray = []

for evt in ds.events():
    fltPosArray.append(tt_pos(evt))

for item in fltPosArray:
    rounded = int(item)
    roundedFltArray.append(rounded)

fltCount = Counter(roundedFltArray)
topTen = sorted(fltCount.items(), key=lambda x:-x[1])[:10]

topArray = []
for item in topTen:
    topArray.append(item[0])

topArray.sort()
lowRange = (topArray[0] - 50)
highRange = (topArray[9] + 50)

fltRange = range(lowRange, highRange)
relevantData = []


for item in fltPosArray:
    if int(item) not in fltRange or int(item) == 0.0:
        pass
    else:
        relevantData.append(item)

bar_width=1.1

data = np.array(relevantData)
plt.hist(data, bins=np.arange(min(data), max(data)))
plt.show()

#for i,evt in enumerate(ds.events()):
   # tt_img = tt_camera.raw(evt)
    #print(tt_pos(evt))
    # <...>
