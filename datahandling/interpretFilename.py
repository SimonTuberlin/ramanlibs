
import re

re_ind = re.compile(r"(\d+)_")
re_samp_ind = re.compile(r"_(.+?)_\d")
re_samp_noind = re.compile(r"(.+?)_\d")
re_samp = re_samp_ind
re_dist = re.compile(r"(\d+)mm_")
re_expt = re.compile(r"(\d+[\.,]?\d*)(m?s)_")
re_avg = re.compile(r"(\d+)avg")

def interpretFilename(fname):
	"""Try to extract metadata from Avantes/Flame/ECLIBS file names.

	Likely only works for a certain naming convention, which I currently cannot
	recall... However, exposure time in s and ms as well as sampling distance
	should be detected in _***s_/_***ms_ or _***mm_ sections of file name.
	Parameters:
		fname: File name to study
	Returns:
		tuple of index#, samplename, samplingdistance, expTime, #avg
	"""
	match = re_ind.match(fname)
	global re_samp
	if match:
		ind = int(match.group(1))
		re_samp = re_samp_ind
	else:
		ind = -1
		re_samp = re_samp_noind
	match = re_samp.search(fname)
	if match:
		samp = match.group(1)
	else:
		samp = ""
	match = re_dist.search(fname)
	if match:
		dist = int(match.group(1))
	else:
		dist = -1
	match = re_expt.search(fname)
	if match:
		expt = float(match.group(1).replace(',','.'))
		if match.group(2) == "s":
			expt *= 1000
		expt = int(expt)
	else:
		expt = -1
	match = re_avg.search(fname)
	if match:
		avg = int(match.group(1))
	else:
		avg = -1
	return (ind, samp, dist, expt, avg)