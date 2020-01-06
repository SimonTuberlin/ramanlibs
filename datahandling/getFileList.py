# -*- coding: utf-8 -*-

import glob

def getFileList(path, fname="*", **options):
    """
    Return list of files in 'path' matching pattern 'fname'.

	This function is used by import routines to scan folders for multiple data
	files of a measurement series that are to be imported. A subset of files
	can be chosen with appropriate wildcards in the fname argument. Path
	separators / and \ may be mixed.

	Parameters:
	    path: file path to search, '.' for current directory
		fname: pattern to look for, supports wildcards like '*.dat' or '*_??.esf'
	Known keyword arguments:
		silent (bool): if False (default), print list of files to stdout
	Returns:
		tuple of file list and index specifying the start of file name ([files],i)
    """
    verbose = not options.pop("silent", False)
    if not (path.endswith('/') or path.endswith('\\')):
        path = path + '/'
    if not fname:
        fname = '*'
    files = glob.glob(path+fname)
    if len(files) == 0:
        if verbose:
            print("No files found")
        return
    files = [f.replace('\\','/') for f in files]
    files.sort()
    if verbose:
        for f in files:
            print(f)
    return (files, files[0].rfind(r"/")+1)