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
        ylo/xhi: lower/higher row index
        xlo/hxi: lower/higher coloumn index
    Known keyword arguments:
            path: directory wherer to write images, default sif location
            fname: filename base to use <fname>_iii.png, default sif name
            extent: (xmin,xmax,ymin,ymax) axis limits, default px indices
            aspect: axis aspect ratio, default "auto" (->square image)
            transpose: To be implemented
            reversex/reverssey: to be implemented
    """
    fig = plt.figure()
    extent = options.pop("extent",None)
    aspect = options.pop("aspect","auto")
    fig.set_size_inches(4,4)
    plt.show(block=False)
    ax = fig.add_subplot(111)
    fname = options.pop("fname",os.path.basename(sif.path)[:-4])
    path = options.pop("path",os.path.dirname(sif.path))
    outpath = os.path.join(path, fname)
    if extent:
        for i in range(sif.kineticlength):
            ax.imshow(sif.data[i,ylo:np.min([yhi,sif.data.shape[-2]]),xlo:np.min([xhi,sif.data.shape[-1]]):-1].transpose(),extent=extent,aspect=aspect)
            fig.tight_layout()
            fig.savefig("{:s}_{:03d}.png".format(outpath, i),dpi=300,pad_inches=0)
    else:
        for i in range(sif.kineticlength):
            ax.imshow(sif.data[i,ylo:np.min([yhi,sif.data.shape[-2]]),xlo:np.min([xhi,sif.data.shape[-1]])].transpose(),aspect=aspect)
            fig.tight_layout()
            fig.savefig("{:s}_{:03d}.png".format(outpath, i),dpi=300,pad_inches=0)