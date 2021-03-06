# -*- coding: utf-8 -*-
"""
Collection of sif related functions

Created on 2019-12-23 13:23 GMT
@author: kubi_si (simon.kubitza at dlr.de/protonmail.com)

List of functions:
    load(path, fname="*.sif", **options) - import sifs in folder path
    plot(sif, frame=0, **options) - plot sif object data as image
    rotate(sif, ang) - rotate data matrix; requires scipy
    sif2pngs(sif,*limits,**options) - save sif's frames to separate .png's
    sif2gif(sif,path=None,**options) - save sif's frames as animated gif
"""

__version__ = "0.0.1"

# %% header, import libraries
from .datahandling.general import *
from .datahandling.andor import *
# from .datahandling import savegif as sif2gif
# from .datahandling import getFileList
#from .datahandling import readSif
from .classes.Sif import SifFile
import numpy as np
import matplotlib.pyplot as plt
#import os

try:
	import scipy.ndimage as scimg
except ImportError as ie:
	print("Failed to import scipy.ndimage. sif.rotate(...) will not be available")
	print(ie)

try:
    import h5py
except ImportError as ie:
    print("Failed to import hdf5 module h5py. sif2hdf() will not be available")
    print(ie)

def load(path,fname="*.sif", **options):
    try:
        files, i = getFileList(path,fname,**options)
    except TypeError:
        files = [path.replace('\\','/')]
    retlist = []
    for f in files:
        s = SifFile(f, **options)
#        readSif(s, f, **options)
        retlist.append(s)
    if len(retlist) == 1:
        return retlist[0]
    return retlist

if scimg:
    def rotate(sif, ang):
        if not hasattr(sif, "orig"):
            sif.orig = sif.data.copy()
            scimg.rotate(sif.orig, ang, reshape=False, output=sif.data)
        sif.rotated = ang

if h5py:
    def sif2hdf(path, **options):
        """Convert sif objects or files(s) to .h5 file(s)
        
        ... if file or path: import
        ... export to source directory/<filenamebase>.hdf5
        ... probably add some options
        """
        if isinstance(path, SifFile):
            sifs = path
        else:
            sifs = load(path)
        if not isinstance(sifs, list):
            sifs = [sifs]
        for s in sifs:
#            h5f = h5py.File(os.path.splitext(s.path)[0]+".hdf5", "w") #robust against other names than .sif
            h5f = h5py.File(s.path[:-3]+"hdf5", "w")
            h5f.close()
                

def plot(sif,frame=0, **options):
    if options.pop("fillROI", False):
        newsif = sif.copy()
        roicords = sif.roiCoords
        olddata = sif.data
        newsif.data = np.zeros(sif.ccd_size[::-1])
        newsif.data[roicords[3]-1:roicords[1], roicords[0]-1:roicords[2]] = olddata
        sif = newsif
    fig = options.pop("fig", None)
    ax = options.pop("ax",plt)
    if ax != plt:
        pass
    elif not fig:
        plt.figure()
    elif fig == "replace":
        plt.clf()
    else:
        plt.figure(fig)
        plt.clf() # might not always be desired (?)
    colorbar = options.pop("colorbar", False)
    grid = options.pop("grid", False)
    labels = options.pop("labels",[])

    # TODO: Check indices for sif.data.shape;
    # might be deprecated due to kinetic series support
    xrange = (options.pop("xlo", 0), options.pop("xli", sif.data.shape[-1]))
    yrange = (options.pop("ylo", 0), options.pop("yli", sif.data.shape[-2]))
    extent = options.pop("extent", False)
    if not extent:
        extent = [xrange[0]-0.5, xrange[1]+0.5, yrange[1]+.5, yrange[0]-.5]
    xoffs = yoffs = 0
    if xrange[1] > sif.data.shape[-1]:
        print("Warning, xHi might violate array bounds")
        if xrange[1]-xrange[0] > sif.data.shape[-1]:
            print("Warning, index out of bounds error inevitavble. Try again")
            return
        else:
            xoffs = -xrange[0]
    if yrange[1] > sif.data.shape[-2]:
        print("Warning, yHi might violate array bounds")
        if yrange[1]-yrange[0] > sif.data.shape[-2]:
            print("Warning, index out of bounds error inevitavble. Try again")
            return
        else:
            yoffs = -yrange[0]
    if len(sif.data.shape) == 3:
        ax.imshow(sif.data[frame,yrange[0]+yoffs:yrange[1]+yoffs,xrange[0]+xoffs:xrange[1]+xoffs], extent=extent, **options)
    else:
        ax.imshow(sif.data[yrange[0]+yoffs:yrange[1]+yoffs,xrange[0]+xoffs:xrange[1]+xoffs], extent=extent, **options)
    try:
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])
    except IndexError:
        pass # normal case if no labels are given...
    if grid:
        if grid in ("x","y"):
            plt.grid(True, axis=grid)
        else:
            plt.grid(grid)
    if colorbar:
        plt.colorbar()
    plt.tight_layout()
    plt.show()

def plotAll(sif,**options):
    """Plot all frames in sif object in separate figure

    This will create a figure for each frame in a kinetic series using
    ramanlibs.sif.plot() function. Consult plot documentation for options.
    A range or list of frames can be provided to reduce number of figures.
    Parameters:
        sif: the sif object to plot
    Opt. parameters:
        range: iterable specifying the frame indices to plot, default range(nFrames)
        label: boolean, use corresponding frame index as plot title, defaut False
    Return:
        ---nothing---"""
    framerange = options.pop("range",range(sif.kineticlength))
    label = options.pop("label",False)
    if len(framerange) > 15:
        print("This will produce {:d} figures. Are you sure? <y/n>".format(sif.kineticlength))
        response = input()
        if not response in ["y","Y","yes","YES"]:
            return
    for i in framerange:
        plot(sif, i, **options)
        if label:
            plt.title(str(i))
            plt.tight_layout()
