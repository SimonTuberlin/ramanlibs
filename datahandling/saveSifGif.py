# -*- coding: utf-8 -*-
"""
Created on 2019-12-23 11:01 GMT

@author: kubi_si (simon.kubitza at dlr.de/protonmail.com)

"""

# %% header, import libraries

import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np

# %% export Sif kinetic series to animated gif
def saveSifGif(sif,path=None,**options):
	try:
		if not path:
			path = sif.path[:-3] + "gif"
		fig = plt.figure()
		mx = np.max(sif.data)
		mn = np.min(sif.data)
		arts = [[plt.imshow(sif.data[i,:,:].transpose(),vmin=mn,vmax=mx)] for i in range(sif.kineticlength)]
		anima = anim.ArtistAnimation(fig, arts)
		anima.save(path, writer=anim.PillowWriter())
	except:	# TODO
		raise()	# TODO