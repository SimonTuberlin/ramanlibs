# -*- coding: utf-8 -*-
"""
Created on on 2019-12-23 13:00 GMT

@author: kubi_si (simon.kubitza at dlr.de/protonmail.com)
"""

# % header, import libraries

import numpy as np
import matplotlib
matplotlib.use("qt5agg")
import matplotlib.pyplot as plt
import os

# %%

def saveSifPngs(sif,ylo=0,yhi=10000,xlo=0,xhi=10000,**options):
    """Convert kinetic series to png images

    Saves files to <siffilebase>_iii.png

    Parameters:
        ylo/yhi: lower/higher row index
        xlo/xhi: lower/higher coloumn index
    Known keyword arguments:
        path: directory wherer to write images, default sif location
        fname: filename base to use <fname>_iii.png, default sif name
        figsize: tuple (w,h) for plt.set_size_inches(), default (4,4)
        norm: default is max per frame; other options to be added
        extent: (xmin,xmax,ymin,ymax) axis limits, default px indices
        aspect: axis aspect ratio, default "auto" (->square image)
        transpose: (boolean) flip axis, default False
        reversex/reverssey: (boolean) invert data in x/y, default False
            -> Axis labelling is not inverted! (to be implemented)
        --- Further options kw-args are passed on to plt.imshow ---
    """
    fig = plt.figure()
    fig.set_size_inches(*options.pop("figsize",(4,4)))
    fname = options.pop("fname",os.path.basename(sif.path)[:-4])
    path = options.pop("path",os.path.dirname(sif.path))
    aspect = options.pop("aspect","auto")
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

    plt.show(block=False)
    ax = fig.add_subplot(111)
    outpath = os.path.join(path, fname)
    if extent:
        for i in range(sif.kineticlength):
            ax.imshow(sifdata[i,:,:], extent=extent,aspect=aspect, **options)
            fig.tight_layout()
            fig.savefig("{:s}_{:03d}.png".format(outpath, i),dpi=300,pad_inches=0)
    else:
        for i in range(sif.kineticlength):
            ax.imshow(sifdata[i,:,:], aspect=aspect, **options)
            fig.tight_layout()
            fig.savefig("{:s}_{:03d}.png".format(outpath, i),dpi=300,pad_inches=0)