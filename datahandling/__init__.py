# -*- coding: utf-8 -*-
"""Datahandling sub-package for import and export modules.

This package contains modules to handle import and export of data files used
in other functions of the ramanlibs library.
"""
from ramanlibs.datahandling.interpretFilename import interpretFilename
from ramanlibs.datahandling.getFileList import getFileList
from ramanlibs.datahandling.importSif import readSif
from ramanlibs.datahandling.saveSifGif import saveSifGif as savegif
from ramanlibs.datahandling.saveSifPngs import saveSifPngs
importavaspec = ""
print("imported datahandling...")
__version__ = "0.0.1"
#__all__ = [savegif,getFileList,readSif]