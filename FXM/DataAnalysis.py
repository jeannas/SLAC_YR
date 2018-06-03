import psana
import sys
import numpy as np
from matplotlib import pyplot as plt
from decimal import Decimal

run = int(sys.argv[-1])

ds = psana.MPIDataSource('exp=cxix29016:run=%d' % run)
det = psana.Detector('DsaCsPad')
gas_det = psana.Detector('FEEGasDetEnergy')
phot_energy = psana.Detector('EBeam')

def accessData(run):

    photon_energies = []
    intensities = []
    pulse_energies = []
    total_events = []

    low_limit = 0.90
    high_limit = 1.10

    for nevent, evt in enumerate(ds.events()):
        intensity_per_event = sum(sum(sum(det.calib(evt))))
        intensities.append(intensity_per_event)
        total_events.append(nevent)     

        pulse_energy = gas_det.get(evt)
        if not (pulse_energy is None):
            pulse_energy_evt = pulse_energy.f_11_ENRC()
            pulse_energies.append(pulse_energy_evt)
        else:
            pulse_energy_evt = 0
            pulse_energies.append(pulse_energy_evt)

        phot = phot_energy.get(evt)
        if not (phot is None):
            phot_energy_evt = phot.ebeamPhotonEnergy()    
            photon_energies.append(phot_energy_evt)

    intensities = np.array(intensities)
    pulse_energies = np.array(pulse_energies)
    photon_energies = np.array(photon_energies)

    pulse_energy_filter = np.mean(pulse_energies)

    final = np.column_stack([intensities,pulse_energies, photon_energies])
    
    #Filter negative pulse energies
    negative_index = []
    for index, array in enumerate(final):
        if array[1] < (low_limit * pulse_energy_filter) or array[1] > (high_limit * pulse_energy_filter):
            negative_index.append(index)

    print("Total number of events is %d, the number of images that do not have proper pulse intensity is %d" % (len(total_events), len(negative_index)))        
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

    print("Post-Filtering")
    print("The average pulse energy for run %d is %.7f mJ" % (run, pulse_average))
    print("The average summed intensity for run %d is %.3E ADU" % (run, Decimal(intensity_average)))
    print("The average beam energy for run %d is %.7f eV" % (run, beam_energy_average))

    neg_index=[]
    for index, array in enumerate(final):
        if array[0] < (low_limit * intensity_average) or array[0] > (high_limit * intensity_average):
            neg_index.append(index)

    final_two = np.delete(final, neg_index, axis=0)

    hit_rate = (float(len(final_two))/float(len(total_events))) * 100
    
    print("Of the remaining %d events, the number of images that do not have the proper mean intensity is %d" % (len(final), len(neg_index)))
    print("The number of accepted hits is %d" % ((len(final) - len(neg_index))))
    print("Hit rate after pulse energy and mean intensity filtering is %.4f percent" % hit_rate)


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
        mean = np.mean(array)
        bad_indices = []
        for index,val in enumerate(array):
            if int(val) < int(0.7*mean) or int(val) > int(1.3*mean):
                bad_indices.append(index)
       
        print("Bad index length - %d" % len(bad_indices))
        array = np.delete(array, bad_indices)
        print(len(array))
      
        variance.append(np.var(array, ddof=1))

    print(variance)
    plt.plot(variance)
    plt.ylabel("Variance")
    plt.xlabel("Number of bins - %d" % number_event_intervals)
    plt.show()

if __name__ == '__main__':

    run = int(sys.argv[-1])

    accessData(run)
   # calculate_variance(10)
