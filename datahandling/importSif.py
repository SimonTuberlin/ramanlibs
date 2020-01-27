# -*- coding: utf-8 -*-

"""
Created on 2019-12-23 15:56 GMT

@author: kubi_si (simon.kubitza at dlr.de/protonmail.com)

Partially based on not properly working matlab code by
Michael V. DePalatis <surname at gmail dot com>
This imports proprietary Andor(r) .sif files.
"""

# %%
import numpy as np
import re

def readSif(sif, path, **options):
	"""Open the SIF file at path and store the data in the sif object.

	This provides direct access to the raw data in .sif containers and parts of
	the metadata saved by Solis software. Metadata is experimental and some
	fields, e.g. spectrometer details, might be misinterpreted and stored under
	an inappropriate name. Relations between .sif entries and experimantal
	settings have been derived from diffs in ASCII exports correlated with
	parameter changes, or guessed from matching of string literals.

	Parameters:
		sif: the object where to store the extracted data
		path: path to the .sif file
	Known keyword arguments:
		verbose(bool): Print extra information to stdout, default False
		silent(bool): Suppress normal reporting to stdout, default False
		... # TODO: Check for more options employed here
	Raises:
		ValueError: file name not ending in .sif or .sif.bz2
		... # TODO: Check for other expected exceptions
	"""

	verbose = options.pop("verbose",False)
	silent = options.pop("silent", False)
	if not silent or verbose:	# check this :/
		print("Importing " + path + "...")
	if path.lower().endswith('.sif'):
		opener = open
	elif path.lower().endswith('.sif.bz2'): # bz2 compressed sif files
		import bz2
		opener = bz2.BZ2File
	else:
		raise ValueError('Wrong extension.')

	sif.fname = path[path.rfind('/')+1:]

	# try to interpret vuv filenames for additional attributes
	# should potentially be move to vuv package at some point...
	if options.pop("vuv",False):
		match = re.compile(r"(\d+)_").match(sif.fname)
		if match:
			sif.index = int(match.group(1))
		match = re.compile(r"\d+_(.+?)_([0-9xmh]+)Pa|\d+_(.+?)_-?\d+C").match(sif.fname)
		if match:
			if match.groups()[1]:
				sif.sample = match.group(1)
				sif.pressure = match.group(2)
			else:
				sif.sample = match.group(3)
		match = re.compile(r"_(\d*,?.?\d*)deg_").findall(sif.fname)
		try:
			sif.angle = float(match[0].replace(",","."))
		except Exception:
			if not silent or verbose:
				print("Could not retrieve angle from filename" + sif.fname)
			sif.angle = None
		match = re.search(r"_(\d+)%(\d+)Hz(\d+)p",sif.fname)
		try:
			sif.laser = int(match.group(1))
			sif.laserRep = int(match.group(2))
			sif.pulses = int(match.group(3))
		except Exception:
			pass
	# end of vuv specific part

	sif.path = path
	f = opener(path, 'rb')

	# Verify we have a SIF file
	if f.readline().strip() != b"Andor Technology Multi-Channel File":
		f.close()
		raise Exception("File %s is not an Andor SIF file." % path)

	# Extract some camera parameters. There is more to get, probably also gating...
	f.readline()  # skip this: 65538 1\n
	camSettings = f.readline().strip().split()
	sif.acqDate = int(camSettings[4])
	sif.camTemp = int(camSettings[5])
	sif.acqMode = camSettings[9] # b'\x01' -> Single, 02 accumulate, 03 kinetic, 00 real time
	sif.expTime = float(camSettings[12])
	sif.realExpTime = float(camSettings[13])
	sif.readMode = camSettings[27] # bx02 MultiTrack, 04 Image, 00 FVB?
	sif.camTempUnst = float(camSettings[47])
	if sif.camTemp == -999:
		sif.camTemp = sif.camTempUnst
		sif.camTempUnst = True
	else:
		sif.camTempUnst = False

	# Get camera model
	sif.camModel = f.readline().strip().decode()

	# Get CCD dimension in pixels -> weiter unten
#        shape = f.readline().split()
	f.readline()
#        sif.ccd_size = (int(shape[0]), int(shape[1])) # shape[2] seems to be length of orginal path

	# Original save path and file name
	f.readline()

	# Skip some not (yet) relevant stuff
	blockLen = int(f.readline().strip().split()[1]) # length of weird data block... I hope...
	f.seek(blockLen+1,1) # apparently there is a \n left after blockLen bytes
	for i in range(9):
		f.readline()
	sif.spectrometerName = f.readline().strip().decode()
	f.readline()
	acq_params = f.readline().strip().decode().split()
	sif.gate_delay = float(acq_params[6])/1e12
	sif.gate_time = float(acq_params[7])/1e12
	sif.step_size = float(acq_params[12])/1e12
	#print(acq_params)
	for line in iter(f.readline, b""):
		if line.startswith(b'Pixel'):
			break
	f.readline() # "Counts12"
	# TODO: Adpapt to handle kinetic series, item [-4] in pxCount row is series length
	line = f.readline().strip().split()
	sif.ccd_size = (int(line[4]), int(line[3]))
	sif.kineticlength = int(line[6])
	sif.nTracks = int(line[7])
	sif.pxCount = int(line[-1])

	if (sif.nTracks == 1):
		line = f.readline().strip().split()
		sif.roiCoords = np.zeros(4, np.int16)
		for l,i in zip(line[1:5],range(4)):
			sif.roiCoords[i] = np.int16(l)
		sif.binning = np.array((np.int16(line[6]), np.int16(line[5]))) # TODO: check axes
	else:
		sif.multiTracks = []
		for i in range(sif.nTracks):
			line = f.readline().strip().split()
			sif.multiTracks.append((int(line[1]),
									 int(line[2]),
									 int(line[3]),
									 int(line[4]),
									 int(line[5]),
									 int(line[6])))
		sif.binning = (sif.multiTracks[0][5], sif.multiTracks[0][4])

	if verbose:
		print(sif.roiCoords)
		print(sif.binning)
		print(sif.kineticlength)
	## Read image data (currently only first image)
	# Seek data start position
	bstartseq = '0\n0\n'.encode("ascii")
	findDataSection(f, bstartseq)
	# Actually read data (float32)
	raw_data = f.read(sif.pxCount*4*sif.kineticlength)
	if verbose:
		print(len(raw_data))
	# Convert byte to float, set NaN's zero, although there shouldn't be any
	data = np.fromstring(raw_data, dtype=np.float32)
	if verbose:
		print(data.shape)
#        mask = sif.data == np.nan
#        sif.data[mask] = 0
	if sif.nTracks == 1:
		sif.shape = (sif.kineticlength,
					  int((sif.roiCoords[1]-sif.roiCoords[3]+1)/sif.binning[1]),
					  int((sif.roiCoords[2]-sif.roiCoords[0]+1)/sif.binning[0]))
		print(sif.shape)
		sif.data = np.reshape(data, sif.shape)
	else:
		print("Multi-Track not yet implemented. Data is one long series of shape (nRows*nCols*nTracks, 1)")
	# Move to background data
	findDataSection(f, bstartseq)
	raw_data = f.read(sif.pxCount*4)
	f.close()
	if len(raw_data) < sif.pxCount*4:
		print("Background import failed. EOF reached before 4*pxCount was read")
		return
	sif.bg = np.reshape(np.fromstring(raw_data, dtype=np.float32), sif.data.shape[1:])


def findDataSection(sif, bstartseq): # here sif is the file reference!
    """Find next occurrence of bstartseq in open file sif (mode rb/wb)

    Reads bytes from open file handle <sif> and seeks for next occurrence of
    bstartseq. Leaves file open with caret at position directly after bstartseq.
    This function is used to locate the beginning of the data block."""
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
