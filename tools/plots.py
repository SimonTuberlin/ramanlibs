# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 13:02:26 2020

@author: seel_fb
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib import animation

def anim_plot(all_dat, **kwargs):
    
    const = kwargs.get('const', 972/15)
    label = kwargs.get('label', r'label')
    xlim = kwargs.get('xlim', (-4, 4))
    normalize = kwargs.get('normalize', True)
    if normalize:
        all_dat = all_dat/np.amax(all_dat)
    
    horizontal_axis = kwargs.get('horizontal_axis', np.arange(len(all_dat[0][0]))/const - (np.arange(len(all_dat[0][0]))/const)[-1]/2)
    #horizontal_axis = horizontal_axis - horizontal_axis[-1]/2

    vertical_axis = kwargs.get('vertical_axis', np.arange(len(all_dat[0]))/const)
    
    fig, axs = plt.subplots(nrows = 1, ncols = 1, figsize = (8.07, 5))
    
    ims = []

    for i in range(len(all_dat)):
        axis_dat = np.meshgrid(horizontal_axis, vertical_axis)
        axis_dat_abel = np.meshgrid(horizontal_axis, vertical_axis)

        im = axs.pcolormesh(*axis_dat, all_dat[i], animated = True, 
                               norm = mpl.colors.LogNorm(vmin = 1e-3, vmax = 1), label = r'Original data')
        ims.append([im])
    
    axs.set_ylabel(r'Vertical position')
    axs.set_xlabel(r'Horizontal position')
    axs.tick_params(top = True, right = True, direction = 'in')
    axs.set_xlim(xlim[0], xlim[1])
    
    clb = fig.colorbar(im, ax = axs)
    clb.set_label(label)
    
    ani = animation.ArtistAnimation(fig, ims, interval=350, blit=True, repeat_delay=1000)
    
    #writer = animation.PillowWriter(bitrate = -1)
    #ani.save('test.gif', writer = writer)
    #ani_abel.save('test_abel.gif', writer = writer)
    
    plt.show()
    
    return ani

def grid_plot(all_dat, **kwargs):
    
    const = kwargs.get('const', 972/15)
    normalize = kwargs.get('normalize', True)
    if normalize:
        all_dat = all_dat/np.amax(all_dat)
    
    horizontal_axis = np.arange(len(all_dat[0][0]))/const
    horizontal_axis = horizontal_axis - horizontal_axis[-1]/2

    vertical_axis = np.arange(len(all_dat[0]))/const
    
    ims = []
    figshape = (int(len(all_dat)/2), 2)
    
    fig, axs = plt.subplots(nrows = figshape[0], ncols = figshape[1], figsize = (8.07*figshape[1]/4,5*figshape[0]/2))
    axs = axs.ravel()
    
    for i in range(len(all_dat)):
        
        axis_dat = np.meshgrid(horizontal_axis, vertical_axis)

        im = axs[i].pcolormesh(*axis_dat, all_dat[i], 
                               norm = mpl.colors.LogNorm(vmin = 1e-3, vmax = 1), label = r'Original data')
        ims.append([im])

        axs[i].tick_params(top = True, right = True, labelbottom = False, direction = 'in')
        #axs[i].set_xlim(-1, 4)


    # clb = fig.colorbar(im, ax = axs[-1])
    # clb.set_label(r'Originial data')
    axs[-2].tick_params(top = True, right = True, labelbottom = True, direction = 'in')
    axs[-2].set_ylabel(r'Vertical position')
    axs[-2].set_xlabel(r'Horizontal position')
    fig.tight_layout()
    plt.subplots_adjust(wspace=0, hspace = 0)
    #plt.savefig('C:\\Users\\seel_fb\\Desktop\\thumb.png')
    plt.show()