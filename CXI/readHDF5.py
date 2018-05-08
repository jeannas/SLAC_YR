#!/usr/local/bin/python

import h5py
import sys

filename = sys.argv[1]

f = h5py.File(filename, 'r')

print(list(f.keys()))

layer1 = f['Configure:0000']

print(list(layer1.keys()))

timeTool = f['Configure:0000']['TimeTool::ConfigV2']

print(list(timeTool.keys()))

timeTool2 = timeTool['CxiDsu.0:Opal1000.0']

print(list(timeTool2.keys()))



