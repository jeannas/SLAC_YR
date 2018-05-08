import psana
import sys
import numpy as np

run = int(sys.argv[-1])

def accessData(run):

    ds = psana.MPIDataSource('exp=cxi02116:run=%d' % run)
    det = psana.Detector('DsaCsPad')
    gas_det = psana.Detector('FEEGasDetEnergy')
    phot_energy = psana.Detector('EBeam')    

    photon_energies = []
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

        phot = phot_energy.get(evt)
        if not (phot is None):
            phot_energy_evt = phot.ebeamPhotonEnergy()    
            photon_energies.append(phot_energy_evt)

    intensities = np.array(intensities)
    pulse_energies = np.array(pulse_energies)
    photon_energies = np.array(photon_energies)

    final = np.column_stack([intensities,pulse_energies, photon_energies])
    print(final)
    print(final.shape)
    

accessData(run)
