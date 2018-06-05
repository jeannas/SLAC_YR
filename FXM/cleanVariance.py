import numpy as np
import psana
import sys

exp_name = "cxix29016"
run_num = int(sys.argv[-1])
det_name = "DsaCsPad"
photon_energy = 6000. # In eV
user_name="yashas"

raw_data = np.load("/reg/d/psdm/cxi/{}/scratch/{}/psocake/r{:04d}/{}_{:04d}_{}_test_var.npy".format(exp_name,
                                                                                         user_name,
                                                                                         run_num,
                                                                                         exp_name,
                                                                                         run_num,
                                                                                         det_name))

location_of_nan = np.isnan(raw_data)
raw_data[location_of_nan] = 0

np.save(("/reg/d/psdm/cxi/{}/scratch/{}/psocake/r{:04d}/{}_{:04d}_{}_clean_var.npy".format(exp_name,
                                                                                         user_name,
                                                                                         run_num,
                                                                                         exp_name,
                                                                                         run_num,
                                                                                         det_name)), raw_data)
