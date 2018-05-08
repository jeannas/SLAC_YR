import psana
import sys
import numpy as np

run = int(sys.argv[-1])

def accessData(run):

    ds = psana.MPIDataSource('exp=cxi02116:run=%d' % run)
    det = psana.Detector('DsaCsPad')
    gas_det = psana.Detector('FEEGasDetEnergy')
    

    intensities = []
    pulse_energies = []

    for nevent, evt in enumerate(ds.events()):
        intensity_per_event = sum(sum(sum(det.calib(evt))))
        intensities.append(intensity_per_event)
    
        pulse_energy = gas_det.get(evt)
        if not (pulse_energy is None):
            pulse_energy_evt = pulse_energy.f_11_ENRC()
            pulse_energies.append(pulse_energy_evt)
        else:
            pulse_energy_evt = 0

    intensities = np.array(intensities)
    pulse_energies = np.array(pulse_energies)

    test = np.column_stack([intensities,pulse_energies])
    print(test)
    print(test.shape)
    

accessData(run)
