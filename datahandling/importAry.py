#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 10:31:33 2020

@author: bob
"""

# %%

import zipfile
import struct
import numpy as np

class Messung:
    def __init__(self, xdata, ydata, path="", orders=[], header=""):
        self.xdata = xdata
        self.ydata = ydata
        self.path = path
        self.orders = orders
        self.header = header

    def __getitem__(self, key):
        if key==0:
            return self.xdata
        if key==1:
            return self.ydata
        raise IndexError("Key '{}' is not valid.".format(key))

def readAry(path):
    try:
        header = readEsfPart(path)
        orders = readDataPart(path)
        spek = readTmpPart(path)
    except OSError as ose:
        print(ose)
        return
    return Messung(spek[0,:], spek[1,:], path, orders, header)


def readEsfPart(fname):
    data = []
    with zipfile.ZipFile(fname) as zf:
        innerFileName = ''
        for section in zf.infolist():
            if section.filename.endswith(".~rep"):
                innerFileName = section.filename
                break
        repFile = zf.open(innerFileName)
        lines = repFile.readlines()
        for l in lines:
            l = l.decode().strip()
            if l.startswith("[end of file]"):
                break # Datei zu Ende, Schleife verlassen
            if l != "":
                data.append(l.split('='))
    return data

def readDataPart(fname):
    with zipfile.ZipFile(fname) as zf:
        innerFileName = ''
        for section in zf.infolist():
            if section.filename.endswith(".~aif"):
                innerFileName = section.filename
                break
        aifFile = zf.open(innerFileName)
        data = aifFile.read()
        orders = [struct.unpack("iiHHHHff",data[i:i+24]) for i in range(0,len(data),24)]
    return orders

def readTmpPart(fname):
    with zipfile.ZipFile(fname) as zf:
        innerFileName = ''
        for section in zf.infolist():
            if section.filename.endswith(".~tmp"):
                innerFileName = section.filename
                break
        aifFile = zf.open(innerFileName)
        data = aifFile.read()
        spek = np.array([struct.unpack("ff",data[i:i+8]) for i in range(0,len(data),8)])[:,::-1].T
    return spek
