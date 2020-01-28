# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 10:50:24 2020

@author: seel_fb
"""

import numpy as np
from scipy.signal import argrelmin
from abel.hansenlaw import hansenlaw_transform

##########################################################################

def hillclimbing_1d(line, hw_val):
    line_out = np.zeros(np.shape(line))
    px_prev = 0
    for j, px in enumerate(line):
        #print(px)
        if px_prev <= hw_val and px >= hw_val:
            line_out[j] = px
            #print('appended')
        if px_prev >= hw_val and px <= hw_val:
            line_out[j] = px
            #print('appended')
        px_prev = px
    return line_out

##########################################################################

def find_halfwidth(arr, method, **kwargs):
    if method == 'stupid':
        half_val = np.zeros(np.shape(arr))
        for i in range(len(half_val)):
            try:
                arr_temp = abs(arr[i]-np.amax(arr[i])/2)
                idx_max = np.argmax(arr)
                idx_1 = np.argmin(arr_temp[:idx_max])
                idx_2 = np.argmin(arr_temp[idx_max:]) + idx_max
                half_val[i][idx_1-2:idx_1+2] = 1
                half_val[i][idx_2-2:idx_2+2] = 1
            except:
                print('failed finding halfwidth at line ' + str(i))
        return half_val
    
    if method == 'local_min':
        hw_val = np.amax(arr)/2
        
        half_val = np.copy(arr)
        for i in range(len(arr)):
            arr_temp = abs(arr[i]-hw_val)
            mins = argrelmin(arr_temp)[0]
            print(mins)
            conf_interval = kwargs.get('threshold', 0.1)
            arr_truth = arr_temp[mins] < conf_interval
            print(arr_truth)
            mins = mins[arr_truth] #sth is wrong here
            mask = np.ones(np.shape(arr[i]), dtype = bool)
            mask[mins] = False
            half_val[i][mask] = 0
        return half_val
    
    if method == 'hillclimbing':
        input_array = np.copy(arr)
        input_array_tr = np.transpose(input_array)
        half_val = np.zeros(np.shape(input_array))
        half_val_tr = np.zeros(np.shape(input_array_tr))
        
        hw_val = np.amax(arr)/(kwargs.get('threshold', 2))
        #print(hw_val)
        for i, line in enumerate(input_array):
            half_val[i] = hillclimbing_1d(line, hw_val)
        for i, line in enumerate(input_array_tr):
            half_val_tr[i] = hillclimbing_1d(line, hw_val)
        half_val_tr = np.transpose(half_val_tr)
        mask = half_val > 0
        half_val_tr[mask] = 0
        output_array = half_val + half_val_tr
        
        return output_array
    
    if method == 'proper':
        half_val = np.zeros(np.shape(arr))
        for i in range(len(half_val)):
            hw_val = np.amax(arr)/2
            conf_interval = kwargs.get('conf_interval', 0.1)
            hw_interval = (hw_val-conf_interval, hw_val+conf_interval)
            half_val[i] = np.where(np.logical_and(arr[i]>hw_interval[0], arr[i]<hw_interval[1]), 1, 0)            
        return half_val

##########################################################################
        
def find_center_1d(arr):
    # projection along axis=0 of image (rows)
    QL_raw0 = arr

    # autocorrelate projections
    conv_0 = np.convolve(QL_raw0, QL_raw0, mode='full')
    len_conv = len(conv_0)/2

    center = np.argmax(conv_0)/2
    return center

##########################################################################

'''
Dosn't work for arrays, where center is off to the right, off to the left works
'''

def symmetrize_1d(arr):
    # find center
    QL_raw0 = arr
    # autocorrelate projections
    conv_0 = np.convolve(QL_raw0, QL_raw0, mode='full')
    center = int(np.argmax(conv_0)/2)
    
    #half_len_arr = int(len(arr)/2)
    l_arr = np.flip(arr[:center])
    r_arr = arr[center:]

    len_diff = int(len(l_arr) - len(r_arr))
    print('len_diff = {}'.format(len_diff))

    if len_diff > 0: #links ist länger
        l_arr = l_arr[:len_diff]
        print('left longer')
    if len_diff < 0: #rechts ist länger
        r_arr = r_arr[:len_diff]
        print('right longer')
    
    avg_arr = np.mean([l_arr, r_arr], axis = 0)
    
    output_len_diff = int(len(arr)/2-len(avg_arr))
    if output_len_diff > 0:
        avg_arr = np.concatenate((avg_arr, np.zeros(output_len_diff)))
    
    avg_arr = np.concatenate((np.flip(avg_arr), avg_arr))
    
    return avg_arr

##########################################################################
    
def saturated(dat, background, **kwargs):
    acc = kwargs.get('acc', 1)
    sat = np.amax(dat + acc*background)
    thr = acc*(2**16)
    #print(thr)
    #print(sat)
    if sat >= thr-1:
        print('SATURATED at {}'.format(sat))
        return sat/thr, True
    else:
        return sat/thr, False
    
##########################################################################
        
def transform_left_half_im(dat, center):
    shape = np.shape(dat)
    right_side = np.flip(dat[:, :int(center)], axis = 1)
    right_side = hansenlaw_transform(right_side, direction = 'inverse')
    len_diff = shape[1]/2 - np.shape(right_side)[1]
    if len_diff < 0:
        print('cutting')
        right_side = right_side[:, :int(shape[1]/2)]
    if len_diff > 0:
        print('appending')
        print(shape[1]/2 + len_diff)
        right_side = np.concatenate((right_side, np.zeros(shape[0], shape[1]/2 + len_diff)), axis = 1)
        print(np.shape(right_side))
    return np.concatenate((np.flip(right_side, axis = 1), right_side), axis = 1)

##########################################################################
    
def calc_velocity(dat, stepsize, **kwargs):
    center_idx = kwargs.get('center', int(np.shape(dat)[2]/2))
    const = kwargs.get('const', 972/15)
    
    vertical_axis = np.arange(np.shape(dat)[1])/const
    vel_points = []
    
    for i, content in enumerate(dat):
        center_line = np.mean(content[:, center_idx-5:center_idx+5], axis = 1)
        center_line = np.flip(center_line)
        for j, px in enumerate(center_line):
            if px > 0:
                vel_points.append(len(center_line)-1-j) #because we are counting from the top, but position is from bottom
                break
    time = np.arange(0, len(vel_points)*stepsize, stepsize)
    hw_pos = vertical_axis[vel_points]
    velocity = np.gradient(hw_pos*1e-3, time)
    return time, hw_pos, velocity