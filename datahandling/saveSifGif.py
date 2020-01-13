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
def saveSifGif(sif,ylo=0,yhi=10000,xlo=0,xhi=10000,**options):
    """Convert kinetic series to animated gif

    Saves files to <siffilebase>.gif
    The color range is scaled from min to max of the complete series. Other
    options will hopefully be implemented soon.

    Parameters:
        ylo/yhi: lower/higher row index
        xlo/xhi: lower/higher coloumn index
    Known keyword arguments:
        path: directory wherer to write images, default sif location
        fname: filename base to use <fname>_iii.png, default sif name
        figsize: tuple (w,h) for plt.set_size_inches(), default (4,4)
        norm: default is max in series; other options to be added
        extent: To be implemented, (xmin,xmax,ymin,ymax) axis limits, default px indices
        aspect: To be implemented, axis aspect ratio, default "auto" (->square image)
        transpose: (boolean) flip axis, default False
        reversex/reverssey: to be implemented
        reversex/reverssey: (boolean) invert data in x/y, default False
            -> Axis labelling is not inverted! (to be implemented)
        --- Further options kw-args are passed on to plt.imshow ---
    """

    try:
        fname = options.pop("fname",os.path.basename(sif.path)[:-3]+"gif")
        path = options.pop("path",os.path.dirname(sif.path))
        sifdata = sif.data
        if options.pop("transpose",False):
            sifdata = sif.data.transpose([0,2,1])
        yhi = np.min([yhi,sifdata.shape[-2]])
        xhi = np.min([xhi,sifdata.shape[-1]])
        sifdata = sifdata[:,ylo:yhi,xlo:xhi]
        extent = options.pop("extent",(xlo,xhi,ylo,yhi)) # TODO: invert for reversexy
        if options.pop("reversex", False):
            sifdata = sifdata[:,:,::-1]
        if options.pop("reversey", False):
            sifdata = sifdata[:,::-1,:]
        outpath = os.path.join(path, fname)
        if not outpath.endswith(".gif"):
            outpath += ".gif"
        fig = plt.figure()
        mx = np.max(sifdata)
        mn = np.min(sifdata)
        arts = [[plt.imshow(sifdata[i,:,:],vmin=mn,vmax=mx,extent=extent)] for i in range(sif.kineticlength)]
        anima = anim.ArtistAnimation(fig, arts)
        anima.save(outpath, writer=anim.PillowWriter())
    except:    # TODO
        raise()    # TODO