#!/usr/bin/env python

import psana
import sys
import numpy as np
import matplotlib.pyplot as plt

run = int(sys.argv[-1]) # make me better yash

def tt_correction(edge):
    a = -1.527864480143
    b =  0.003652900467
    c = -0.000001106143
    return (a + b*edge + c*edge**2)/1000.


ds = psana.MPIDataSource('exp=cxilr3816:run=%d' % run)
smd = ds.small_data('run%d_data.h5' % run)

evr = psana.Detector('NoDetector.0:Evr.1')
acq = psana.Detector('Acqiris')

las_dly = psana.Detector('LAS:FS5:VIT:FS_TGT_TIME_DIAL')
tt_edge = psana.Detector('CXI:TTSPEC:FLTPOS')
tt_fwhm = psana.Detector('CXI:TTSPEC:FLTPOSFWHM')
tt_famp = psana.Detector('CXI:TTSPEC:AMPL') 

tt_stage_pos = psana.Detector('CXI:LAS:MMN:04') # convert me from mm to ns


for n,evt in enumerate(ds.events()):

    try:
        diode = np.sum( acq(evt)[0][0,760:860] )
    except:
        diode = None
    delay = las_dly(evt)

    smd.event(acqiris   = diode,
              las_delay = delay,
              edge      = tt_edge(evt),
              fwhm      = tt_fwhm(evt),
              famp      = tt_famp(evt),
              edge_ps   = tt_correction(tt_edge(evt)))

    if smd.master:
        if n % 100 == 0:
            print n

smd.save()

