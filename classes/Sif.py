# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 11:22:20 2019

@edit: kubi_si

"""

__version__ = "0.0.1"

# %% header, import libraries

from ..datahandling import readSif
import numpy as np

# %%

class SifFile:
    """SifFile is the Python representation of an Andor SIF image
    file. Image data is stored in a numpy array indexed as [row,
    column] instead of [x, y]."""

    def __init__(self, path="",**options):
        self.data = 0
        if path != "":
            readSif(self,path,**options)

    def copy(self):
        newsif = self.__class__()
        newsif.__dict__ = self.__dict__.copy()
        print("Warning, sif.data is shallow copy, don't manipulate data by indexing!")
        return newsif

    def __str__(self):
        return self.path

    def __add__(self, other):
        new_sif = self.copy()
        if isinstance(other, (SifFile, np.ndarray)):
            new_sif.data = new_sif.data + other.data
        elif isinstance(other, (int, float)):
            new_sif.data = new_sif.data + other
        else:
            raise TypeError("Addition of SIF data requires another SifFile instance, a numpy array, or a scalar.")
        return new_sif

    def __sub__(self, other):
        new_sif = self.__class__()
        new_sif.__dict__ = self.__dict__
        if isinstance(other, (SifFile, np.ndarray)):
            new_sif.data = new_sif.data - other.data
        elif isinstance(other, (int, float)):
            new_sif.data = new_sif.data - other
        else:
            raise TypeError("Subtraction of SIF data requires another SifFile instance, a numpy array, or a scalar.")
        return new_sif

    def __mul__(self, other):
        new_sif = self.__class__()
        new_sif.__dict__ = self.__dict__
        if isinstance(other, (SifFile, np.ndarray)):
            new_sif.data = new_sif.data * other.data
        elif isinstance(other, (int, float)):
            new_sif.data = new_sif.data * other
        else:
            raise TypeError("Multiplcation of SIF data requires another SifFile instance, a numpy array, or a scalar.")
        return new_sif

    def __rmul__(self, other):
        return self.__mul__(other)


# Used to understand the proprietary sif format and to locate the data section.
# Might be useful for other purposes in the future...
def findDataSection(sif, bstartseq):
    """Find next occurrence of bstartseq in open file sif (mode rb/wb)

    Reads bytes from open file handle <sif> and seeks for next occurrence of
    bstartseq. Leaves file open with caret at position directly after bstartseq"""
    b0 = bstartseq[:1]
    curPos = sif.tell()
    end = sif.seek(0,2)
    sif.seek(curPos)
    while True:
        if sif.tell() == end:
            print("Reached end of file...")
            break
        raw_data = sif.read(128)
        i = raw_data.find(b0)
        if i>-1:
            if i>len(raw_data)-len(bstartseq):
                sif.seek(i-len(raw_data)-1,1)
                raw_data = sif.read(len(bstartseq))
                i = raw_data.find(b0)
            if raw_data.startswith(bstartseq, i):
                sif.seek(i+len(bstartseq)-len(raw_data),1) # go to byte after pattern match
                break # and leave search loop
            else:
                sif.seek(i+1-len(raw_data),1) # go byte after b0 and continue search
