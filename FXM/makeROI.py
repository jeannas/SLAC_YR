import psana
import numpy as np
from matplotlib import pyplot as plt
import sys


def makeCenter():

    ds = psana.MPIDataSource('exp=cxi02116:run=257:smd')
    det = psana.Detector('DsaCsPad')

    for nevent, evt in enumerate(ds.events()):
        
        #Figure out coordinates first
        img = det.image(evt)
        test = det.calib(evt)
        #Y-coords, then X-coords when slciing
        approximate = img[750:950, 775:975]
        real = approximate[65:176, 42:154]

    plt.imshow(approximate, interpolation=None)
    plt.show()

    plt.imshow(test, interpolation=None)
    plt.show()

makeCenter()

def intensityROI():

    ds = psana.MPIDataSource('exp=cxi02116:run=257:smd')
    det = psana.Detector('DsaCsPad')

    
    for nevent,evt in enumerate(ds.events()):
        raw_calib = np.array(det.calib(evt))
        test = np.array(det.image(evt))
        print(raw_calib.shape)
        print(test.shape)
        roi_approx = raw_calib[750:950, 775:975]
        print(roi_approx)
        roi_final = sum(sum(sum(roi_approx[65:176,42:154])))
        print(roi_final)

#intensityROI()
