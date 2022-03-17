# -*- coding: utf-8 -*-
################################################################################
#                                 PROFILE PLOTS                                #
################################################################################

'''
Max Planck Institute for Astronomy
Planet Genesis Group

Nicolas Kurtovic
Contact: kurtovic at mpia.de

This is an example code to generate the profile plots. Execute after 
generating the images with simio.
'''

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from matplotlib.colors import LogNorm
from scipy.interpolate import interp1d
from astropy.visualization import (AsinhStretch, LogStretch, LinearStretch, ImageNormalize)


# Get the current directory path
current_dir = os.getcwd()+'/'


##############################################################################
#                                    CMAPS                                   #
##############################################################################

import matplotlib        as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable

# set upper part: 4 * 256/4 entries
upper = mpl.cm.viridis(np.arange(256))
# set lower part: 1 * 256/4 entries
# - initialize all entries to 1 to make sure that the alpha channel (4th column) is 1
lower = np.ones((int(256/8),4))
# - modify the first three columns (RGB):
#   range linearly between white (1,1,1) and the first color of the upper colormap
for i in range(3):
    lower[:,i] = np.linspace(0, upper[0,i], lower.shape[0])
# combine parts of colormap
cmap_viridis = np.vstack(( lower, upper ))
# convert to matplotlib colormap
cmap_viridis = mpl.colors.ListedColormap(cmap_viridis, name='MODVIR', N=cmap_viridis.shape[0])


##############################################################################
#                                   FUNCTIONS                                #
##############################################################################


def deproject(x, y, inc, pa):
    '''
    
    '''
    xp = (x * np.cos(pa) + y * np.sin(pa)) / np.cos(inc)
    yp = (x *-np.sin(pa) + y * np.cos(pa))
    return xp, yp


def project(x, y, inc, pa):
    '''
    
    '''
    xpi = x * np.cos(inc)
    xp = (xpi * np.cos(-pa) + y * np.sin(-pa))
    yp = (xpi *-np.sin(-pa) + y * np.cos(-pa))
    return xp, yp


def gaussiana(r, p_mod):
    '''
    One dimension gaussian.
    Calculates the gaussian value of the position r, given that the gaussian
    is centered at gr0 and has a sigma width of gsig. The gaussian amplitude
    is given by gf0.
    '''
    gf0, gr0, gsig = p_mod
    # Calculate the gaussian value
    profile = gf0 * np.exp(-0.5 * ( (r - gr0) / gsig )**2)
    # Return.
    return profile


def mk_ellipse(incl, PA, npts=200):
    '''
    General Ellipse, for desplaying the beam purpose. The inclination and PA
    must be in degrees.
    '''
    # Calculate parameters
    semimajor = 1.
    semiminor = semimajor * np.cos(np.radians(incl))
    ang = np.radians(90. - PA)
    phi = 2. * np.pi * np.arange(npts) / (npts-1.)
    # Get positions
    xp = semimajor * np.cos(phi) * np.cos(ang) - \
         semiminor * np.sin(phi) * np.sin(ang)
    yp = semimajor * np.cos(phi) * np.sin(ang) + \
         semiminor * np.sin(phi) * np.cos(ang)
    # Return
    return [xp, yp]


def make_circle(r):
    t = np.arange(0, np.pi * 2.0, 0.01)
    t = t.reshape((len(t), 1))
    x = r * np.cos(t)
    y = r * np.sin(t)
    return np.hstack((x, y))


def bineado(array, position, bins, weights=None):
    '''
    Bins the array 'array' in a new array, taking the mean of the values in each
    bin, given their positions specified by 'position'. 'bins' can specify the
    edge position of each bin, or the number of bins desired.
    Returns the binned array, and the errors array.
    
    The errors are calculated with the standard deviation, or the sum of the weights.
    '''
    if weights is not None:
        # Number of bins
        nbins = len(bins) - 1
        # Binned vectors
        bin_array = np.zeros(nbins)
        bin_err = np.zeros(nbins)
        # Bin
        for i in range(nbins):
            index = np.where(np.bitwise_and(position >= bins[i], position < bins[i+1]))
            # Acumulator
            bin_aux = array[index]
            bin_array[i], bin_err[i] = np.average(bin_aux, weights=weights[index], returned=True)
        return bin_array, 1./np.sqrt(bin_err)

    if isinstance(bins, int):
        # Number of elements per bin
        nbins = bins
        n_el = (len(position) / nbins)
        # Binned vectors
        bin_array = np.zeros(nbins)
        bin_low = np.zeros(nbins)
        bin_high = np.zeros(nbins)
        bin_quan = np.zeros(nbins)
        # Auxiliar counter
        aux = 0
        # Bin
        for i in range(nbins):
            index = np.arange(aux*n_el, (aux+1)*n_el, dtype=int)
            # Acumulator
            bin_aux = array[index]
            bin_array[i] = np.mean(bin_aux)
            bin_quan = len(array[index])
            # Error bars
            bin_low[i]  = np.percentile(bin_aux, [16], axis=0)
            bin_high[i] = np.percentile(bin_aux, [84], axis=0)
            # Increase counter
            aux += 1
        return bin_array, (bin_array - bin_low) , (bin_high - bin_array)
    
    else:
        # Number of bins
        nbins = len(bins) - 1
        # Binned vectors
        bin_array = np.zeros(nbins)
        bin_low = np.zeros(nbins)
        bin_high = np.zeros(nbins)
        bin_quan = np.zeros(nbins)
        # Bin
        for i in range(nbins):
            index = np.where(np.bitwise_and(position >= bins[i], position < bins[i+1]))
            # Acumulator
            bin_aux = array[index]
            bin_array[i] = np.mean(bin_aux)
            bin_quan = len(array[index])
            # Error bars
            bin_low[i]  = np.percentile(bin_aux, [16], axis=0)
            bin_high[i] = np.percentile(bin_aux, [84], axis=0)
        return bin_array, (bin_array - bin_low) , (bin_high - bin_array)


def makeprofile(cont_fits, mod_fits, geom_params, dist, simobj_name='', ang_size=1.2):
    '''
    
    '''
    # Geometry of the observation
    dRa, dDec, inc, pa = geom_params
    # Open fits file
    hdulist_cont = fits.open(cont_fits)
    header_cont  = hdulist_cont[0].header
    # Extract image
    image_cont = np.squeeze(hdulist_cont[0].data)
    # RA and Dec
    ra_cont  = 3600. * header_cont['CDELT1'] * (np.arange(header_cont['NAXIS1']) - (header_cont['CRPIX1']-1))
    dec_cont = 3600. * header_cont['CDELT2'] * (np.arange(header_cont['NAXIS2']) - (header_cont['CRPIX2']-1))
    ext_cont = [np.max(ra_cont), np.min(ra_cont), np.min(dec_cont), np.max(dec_cont)]
    # Beam size
    beam_inc = np.degrees(np.arccos(header_cont['BMIN'] / header_cont['BMAJ']))
    beam_pa = header_cont['BPA']
    bx, by = mk_ellipse(beam_inc, beam_pa)
    bmaj = header_cont['BMAJ']
    bmin = header_cont['BMIN']

    # Open fits file
    hdulist_mod = fits.open(mod_fits)
    header_mod = hdulist_mod[0].header
    # Extract image
    image_mod = np.squeeze(hdulist_mod[0].data)
    # RA and Dec
    ra_mod  = 3600. * header_mod['CDELT1'] * (np.arange(header_mod['NAXIS1']) - (header_mod['CRPIX1']-1))
    dec_mod = 3600. * header_mod['CDELT2'] * (np.arange(header_mod['NAXIS2']) - (header_mod['CRPIX2']-1))
    ext_mod = [np.max(ra_mod), np.min(ra_mod), np.min(dec_mod), np.max(dec_mod)]

    # Pixel size
    pix_size_cont = np.abs(np.round(3600. * header_cont['CDELT1'], 5))
    pix_size_mod = np.abs(np.round(3600. * header_mod['CDELT1'], 5))

    # Deproject image in inclination and position angle.
    x = np.arange(len(image_mod)) * pix_size_mod
    y = np.arange(len(image_mod)) * pix_size_mod
    x, y = np.meshgrid(x, y)
    x = x - (len(image_mod) / 2.) * pix_size_mod - ( 0.000)
    y = y - (len(image_mod) / 2.) * pix_size_mod - ( 0.000)
    # Deproject
    xd, yd = deproject(x, y, np.deg2rad(inc), np.deg2rad(pa))
    # Calculate distance
    rd = np.sqrt(xd**2 + yd**2)
    barra = 10. * parallax * 10**-3     # Scale bar in au

    # Vectorize the radial matrix
    rd_fl = rd.ravel()
    # Sort by distance
    arg_sort = np.argsort(rd_fl)
    rd_fl = rd_fl[arg_sort]
    image_cont_fl = image_cont.ravel()[arg_sort]
    image_mod_fl  = image_mod.ravel()[arg_sort]

    # Binning
    ebin = 2*pix_size_mod
    bins = np.arange(0., np.max(rd_fl)+ebin, ebin)
    # Get profiles
    mids_radprof, low_mids_radprof, high_mids_radprof = bineado(rd_fl, rd_fl, bins)
    bin_cont,     low_cont,         high_cont         = bineado(image_cont_fl, rd_fl, bins)
    bin_mod,      low_mod,          high_mod          = bineado(image_mod_fl,  rd_fl, bins)

    # Figure
    fig = plt.figure(figsize=(2.5 * 3, 2.5*1))
    # Images             [left, bottom,  width, height]
    ax1 =  fig.add_axes([ 0.00,   0.05,   0.30,   0.90])
    ax2 =  fig.add_axes([ 0.33,   0.05,   0.30,   0.90])
    ax3 =  fig.add_axes([ 0.66,   0.05,   0.30,   0.90])
    ax4 =  ax3.twiny()
    # SET LIMITS
    xlims = np.array([  ang_size, -ang_size])
    ylims = np.array([ -ang_size,  ang_size])
    rlims = np.array([ -0.01    ,  ang_size])
    ilims = np.array([ -0.05    ,  1.3     ])
    # [left, bottom, width, height] in fractions of the figure size
    dx, dy = np.abs(xlims[0] - xlims[1]), np.abs(ylims[0] - ylims[1])
    dr, di = np.abs(rlims[0] - rlims[1]), np.abs(ilims[0] - ilims[1])
    # Limits of the figure
    ax1.set_xlim(xlims)
    ax1.set_ylim(ylims)
    ax2.set_xlim(xlims)
    ax2.set_ylim(ylims)
    ax3.set_xlim(rlims)
    ax3.set_ylim(ilims)
    ax4.set_xlim(rlims*dist)
    ax4.set_ylim(ilims)

    # Plot ALMA data
    norm1 = ImageNormalize(vmin=0, vmax=np.max(image_cont)*1e6, stretch=AsinhStretch())
    im1   = ax1.imshow(image_cont*1e6, origin='lower', cmap='inferno', \
                       extent=ext_cont, aspect='equal', norm=norm1)
    # Print measuring size bar
    ax1.plot([0.1*dx+xlims[1],         0.1*dx+xlims[1]+(barra)], [ylims[1]-0.1*dy,         ylims[1]-0.1*dy],         'w')
    ax1.plot([0.1*dx+xlims[1],         0.1*dx+xlims[1]],         [ylims[1]-0.1*dy-0.01*dy, ylims[1]-0.1*dy+0.01*dy], 'w')
    ax1.plot([0.1*dx+xlims[1]+(barra), 0.1*dx+xlims[1]+(barra)], [ylims[1]-0.1*dy-0.01*dy, ylims[1]-0.1*dy+0.01*dy], 'w')
    # Print the beamsize
    ax1.plot( xlims[0] - 0.1*dx + (3600. * 0.5 * bmaj * bx), \
              ylims[0] + 0.1*dy + (3600. * 0.5 * bmaj * by), 'w')
    # Labels
    ax1.annotate(simobj_name, xy=(xlims[0] - 0.03*dx, ylims[1] - 0.1*dy), \
                 xycoords='data', horizontalalignment='left', color='w', size=11)
    # Labels and ticks
    ax1.set_xlabel(r'$\Delta$ RA [arcsec]')
    ax1.set_ylabel(r'$\Delta$ Dec [arcsec]')

    # Plot ALMA model
    norm2 = ImageNormalize(vmin=0, vmax=0.1*np.max(image_mod)*1e3, stretch=AsinhStretch())
    im2   = ax2.imshow(image_mod*1e3, origin='lower', cmap=cmap_viridis, \
                       extent=ext_mod, aspect='equal', norm=norm2)
    # Labels and ticks
    ax2.annotate(r'Model', xy=(xlims[0] - 0.03*dx, ylims[1] - 0.1*dy), \
                 xycoords='data', horizontalalignment='left', color='w', size=11)
    ax2.set_yticklabels([])

    # Plot
    ax4.plot(mids_radprof*dist, np.zeros(len(mids_radprof)), '.', color='white', lw=1, alpha=0.)
    # Labels
    ax4.set_xlabel('Distance [au]', labelpad=10)
    ax4.set_yticks([])
    ax4.tick_params(direction = 'out')

    # Radial profile
    ax3.fill_between(x=mids_radprof, \
                     y1=(bin_cont-low_cont)  / np.max(bin_cont), \
                     y2=(bin_cont+high_cont) / np.max(bin_cont), \
                     color='gray', alpha=0.6, label=r'$1\sigma$ data')
    ax3.plot(mids_radprof, bin_cont / np.max(bin_cont), '--', color='k', lw=1, alpha=0.9, label='data')
    ax3.plot(mids_radprof, bin_mod  / np.max(bin_mod) * 1.,   '-', color='steelblue', lw=2, alpha=0.8, label=r'model')
    # Resolution
    s_radgauss = (3600. * 0.5 * (bmaj + bmin)) / 2.35482
    x_radgauss = np.linspace(0.8*rlims[1]-3*s_radgauss, 0.8*rlims[1]+3*s_radgauss, 200)
    ax3.plot(x_radgauss, 0.35 + gaussiana(x_radgauss, (0.25, 0.8*rlims[1], s_radgauss)), '-', color='gray', lw=1, alpha=0.8)
    # Labels
    ax3.annotate('Profile', xy=(rlims[0] + 0.03*dr, ilims[1] - 0.1*di), \
                  xycoords='data', horizontalalignment='left', color='k', size=11)
    ax3.set_ylabel('Intensity [norm]')
    ax3.yaxis.set_label_position('right')
    ax3.set_xlabel('Distance [arcsec]')
    ax3.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
    ax3.set_yticklabels(['0.0', '0.2', '0.4', '0.6', '0.8', '1.0', '1.2'])
    ax3.yaxis.tick_right()
    ax3.legend(loc='upper right')

    # Save figure
    plt.savefig('plots/'+simobj_name+'_summary.pdf', \
                bbox_inches='tight')
    plt.show()


################################################################################
#                                  RUN FIGURES                                 #
################################################################################

template = 'HD163296'
simobj_name = 'SolarS'

# Obtain Template info, to recover the geometric parameters
with open('templates/' + template + '/' + template + '_info.py') as f:
    for line in f:
        exec (line)

# Path to images
dir_cont = current_dir+'projects/SolarS_'+template+'/images/SolarS_'+template+'_im.fits'
dir_mod  = current_dir+'projects/SolarS_'+template+'/images/SolarS_'+template+'_im_model.fits'

makeprofile(cont_fits=dir_cont, \
            mod_fits=dir_mod, \
            geom_params=geom_params, \
            dist=dist, \
            simobj_name=simobj_name, \
            ang_size=0.6)


