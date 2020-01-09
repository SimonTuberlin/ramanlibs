# -*- coding: utf-8 -*-
"""
Created on 2019-12-23 11:01 GMT

@author: kubi_si (simon.kubitza at dlr.de/protonmail.com)

"""

# %% header, import libraries

import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np
import os

# %% export Sif kinetic series to animated gif
def saveSifGif(sif,path=None,**options):
    try:
        fname = options.pop("fname",os.path.basename(sif.path)[:-3]+"gif")
        path = options.pop("path",os.path.dirname(sif.path))
        outpath = os.path.join(path, fname)
        if not outpath.endswith(".gif"):
            outpath += ".gif"
        fig = plt.figure()
        mx = np.max(sif.data)
        mn = np.min(sif.data)
        arts = [[plt.imshow(sif.data[i,:,:].transpose(),vmin=mn,vmax=mx)] for i in range(sif.kineticlength)]
        anima = anim.ArtistAnimation(fig, arts)
        anima.save(outpath, writer=anim.PillowWriter())
    except:    # TODO
        raise()    # TODO