import psana
import sys
import numpy as np
from matplotlib import pyplot as plt
from decimal import Decimal

run = int(sys.argv[-1])

ds = psana.MPIDataSource('exp=cxilr7416:run=%d' % run)
det = psana.Detector('DsaCsPad')
gas_det = psana.Detector('FEEGasDetEnergy')
phot_energy = psana.Detector('EBeam')

def accessData(run):

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
    
    #Remove negative pulse energies
    negative_index = []
    for index, array in enumerate(final):
        if array[1] < 0.5:
            negative_index.append(index)
        
    final = np.delete(final, negative_index, axis=0)

    #Calculate averages
    pulse_sum = 0
    intensity_sum = 0
    beam_energy_sum = 0

    for count, array in enumerate(final):
        pulse_sum += array[1]
        intensity_sum += array[0]
        beam_energy_sum += array[2]

    pulse_average = pulse_sum / float(len(final))
    intensity_average = intensity_sum / float(len(final))
    beam_energy_average = beam_energy_sum / float(len(final))    

    print("The average pulse energy for run %d is %.7f mJ" % (run, pulse_average))
    print("The average summed intensity for run %d is %.3E ADU" % (run, Decimal(intensity_average)))
    print("The average beam energy for tun %d is %.7f mJ" % (run, beam_energy_average))

def calculate_variance(number_event_intervals):
   
    variance = {}
    summed_intensities = []

    for nevent, evt in enumerate(ds.events()):
        summed_intensities.append(sum(sum(sum(det.calib(evt)))))         

    summed_intensities = np.array(summed_intensities)

    bad_index = []
    for index, intensity in enumerate(summed_intensities):
        if intensity < 9E6:
            bad_index.append(index)

    summed_intensities = np.delete(summed_intensities, bad_index, axis=0)

    #Bins the summed intensities based on the intervals
    summed_intensities = np.array_split(summed_intensities, number_event_intervals)

    variance = []

    for array in summed_intensities:
        print(array)
        variance.append(np.var(array, ddof=(len(summed_intensities)/len(array))))

    print(variance)
    plt.plot(variance)
    plt.ylabel("Variance")
    plt.xlabel("Number of bins - %d" % number_event_intervals)
    plt.show()

if __name__ == '__main__':

    run = int(sys.argv[-1])

   # accessData(run)
    calculate_variance(10)
