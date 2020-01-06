# -*- coding: utf-8 -*-
__version__ = "0.0.1"

import re, os
import numpy as np
from ramanlibs.datahandling import getFileList, interpretFilename
from ramanlibs.datahandling import importavaspec


cals = {}
try:
#    print(dir())
#    print([__file__, __name__, __package__,__spec__])
    basedir = os.path.split(__file__)[0]
    cals["Utes"] = np.loadtxt(basedir+r"/data/Utes.cal")
    cals["UV"] = np.loadtxt(basedir+r"/data/UV.cal")
    cals["VIS1"] = np.loadtxt(basedir+r"/data/VIS1.cal")
    cals["VIS2"] = np.loadtxt(basedir+r"/data/VIS2.cal")
    cals["NIR"] = np.loadtxt(basedir+r"/data/NIR.cal")
    cals["1709193M1"] = cals["Utes"]
    cals["1712026M1"] = cals["UV"]
    cals["1804056M1"] = cals["VIS1"]
    cals["1804058M1"] = cals["NIR"]
    cals["1712027M1"] = cals["VIS2"]
except IOError as ioe:
    print("Not able to read Avantes calibration files... Calibration attempts will fail.")
    print(ioe)

def load(path,fname="*.TXT", dropRawAndDark=True, **options):
	try:
		files, i = getFileList(path,fname)
	except TypeError:
		files = [path.replace('\\','/')]
		i = files[0].rfind(r"/")+1

