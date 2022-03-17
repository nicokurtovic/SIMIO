# -*- coding: utf-8 -*-
################################################################################
#                               COMPARISON PLOTS                               #
################################################################################

'''
Max Planck Institute for Astronomy
Planet Genesis Group

Nicolas Kurtovic
Contact: kurtovic at mpia.de

This is an example code to generate the comparison plots. Execute after 
generating the images with simio.
'''

# Import needed python packages
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import (AsinhStretch, LogStretch, LinearStretch, ImageNormalize)

# Get the current directory path
current_dir = os.getcwd()+'/'


################################################################################
#                                   FUNCTIONS                                  #
################################################################################


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


def makefigure(temp_fits, simobj_fits, template, simobj_name='', ang_size=1.2):
    '''
    
    '''
    # Open template fits file
    hdulist_tem = fits.open(dir_tem)
    header_tem  = hdulist_tem[0].header
    # Extract image
    image_tem = np.squeeze(hdulist_tem[0].data)
    # RA and Dec
    ra_tem  = 3600. * header_tem['CDELT1'] * (np.arange(header_tem['NAXIS1']) - (header_tem['CRPIX1']-1))
    dec_tem = 3600. * header_tem['CDELT2'] * (np.arange(header_tem['NAXIS2']) - (header_tem['CRPIX2']-1))
    ext_tem = [np.max(ra_tem), np.min(ra_tem), np.min(dec_tem), np.max(dec_tem)]

    # Open object fits file
    hdulist_mod = fits.open(dir_mod)
    header_mod = hdulist_mod[0].header
    # Extract image
    image_mod = np.squeeze(hdulist_mod[0].data)
    # RA and Dec
    ra_mod  = 3600. * header_mod['CDELT1'] * (np.arange(header_mod['NAXIS1']) - (header_mod['CRPIX1']-1))
    dec_mod = 3600. * header_mod['CDELT2'] * (np.arange(header_mod['NAXIS2']) - (header_mod['CRPIX2']-1))
    ext_mod = [np.max(ra_mod), np.min(ra_mod), np.min(dec_mod), np.max(dec_mod)]

    # Pixel sizes
    pix_size_tem = np.abs(np.round(3600. * header_tem['CDELT1'], 5))
    pix_size_mod = np.abs(np.round(3600. * header_mod['CDELT1'], 5))

    # Figure
    figure_size = 5.0
    font_size = 22
    plt.rc('font', size=22)
    fig = plt.figure(figsize=(figure_size * 2, figure_size))
    # Images            [left, bottom, width, height]
    ax1 =  fig.add_axes([0.04,   0.05,  0.45,   0.90])
    ax2 =  fig.add_axes([0.50,   0.05,  0.45,   0.90])
    # Colorbars
    cax1 = fig.add_axes([0.96,   0.05,  0.01,   0.90])

    # SET LIMITS
    x1lims = [  ang_size, -ang_size]
    y1lims = [ -ang_size,  ang_size]
    x2lims = [  ang_size, -ang_size]
    y2lims = [ -ang_size,  ang_size]
    # [left, bottom, width, height] in fractions of the figure size
    dx1, dy1 = np.abs(x1lims[0] - x1lims[1]), np.abs(y1lims[0] - y1lims[1])
    dx2, dy2 = np.abs(x2lims[0] - x2lims[1]), np.abs(y2lims[0] - y2lims[1])
    # Limits of the figure
    ax1.set_xlim(x1lims)
    ax1.set_ylim(y1lims)
    ax2.set_xlim(x2lims)
    ax2.set_ylim(y2lims)

    # Plot template image
    norm1 = ImageNormalize(vmin=-np.max(image_tem)/200. * 10**3, \
                           vmax=np.max([np.max(image_tem), \
                                        np.max(image_mod)]) * 10**3, \
                           stretch=AsinhStretch())
    im1 = ax1.imshow(image_tem * 10**3, \
                     interpolation='nearest', origin='lower', \
                     cmap='inferno', extent=ext_tem, aspect='equal', \
                     norm=norm1)
    # Print the beamsize
    beam_inc = np.degrees(np.arccos(header_tem['BMIN'] / header_tem['BMAJ']))
    beam_pa = header_tem['BPA']
    bx, by = mk_ellipse(beam_inc, beam_pa)
    ax1.plot( x1lims[0] - 0.1*dx1 + (3600. * 0.5 * header_tem['BMAJ'] * bx), \
              y1lims[0] + 0.1*dy1 + (3600. * 0.5 * header_tem['BMAJ'] * by), 'w')
    # Labels and ticks
    ax1.set_xlabel(r'$\Delta$ RA [arcsec]')
    ax1.set_ylabel(r'$\Delta$ Dec [arcsec]')
    ax1.set_yticks([1.0, 0.5, 0., -0.5, -1.0])
    ax1.set_yticklabels([1.0, 0.5, 0., -0.5, -1.0])
    ax1.set_xticks([1.0, 0.5, 0., -0.5, -1.0])
    ax1.set_xticklabels([1.0, 0.5, 0., -0.5, -1.0])
    ax1.annotate(template, xy=(x1lims[0] - 0.03*dx1, y1lims[1] - 0.1*dy1), \
                 xycoords='data', horizontalalignment='left', color='w', \
                 size=font_size)

    # Plot template image
    im2 = ax2.imshow(image_mod * 10**3, \
                     interpolation='nearest', origin='lower', \
                     cmap='inferno', extent=ext_mod, aspect='equal', \
                     norm=norm1)
    # Print the beamsize
    beam_inc = np.degrees(np.arccos(header_tem['BMIN'] / header_tem['BMAJ']))
    beam_pa = header_tem['BPA']
    bx, by = mk_ellipse(beam_inc, beam_pa)
    ax2.plot( x2lims[0] - 0.1*dx2 + (3600. * 0.5 * header_tem['BMAJ'] * bx), \
              y2lims[0] + 0.1*dy2 + (3600. * 0.5 * header_tem['BMAJ'] * by), 'w')
    # Labels and ticks
    ax2.set_xlabel(r'$\Delta$ RA [arcsec]')
    ax2.set_yticks([])
    ax2.set_yticklabels([])
    ax2.set_xticks([1.0, 0.5, 0., -0.5, -1.0])
    ax2.set_xticklabels([1.0, 0.5, 0., -0.5, -1.0])
    ax2.annotate(simobj_name, xy=(x2lims[0] - 0.03*dx2, y2lims[1] - 0.1*dy2), xycoords='data', \
                 horizontalalignment='left', color='w', size=font_size)

    # Colorbar
    cbar1 = fig.colorbar(im1, cax=cax1, orientation='vertical')#, ticks=ticks)
    cbar1.set_label(r'[mJy/beam]', fontsize=font_size)#, labelpad=-36)
    cbar1.ax.tick_params(labelsize=font_size)
    cbar1.solids.set_edgecolor('face')
    cax1.xaxis.set_ticks_position('top')

    # Save figure
    plt.savefig('plots/'+simobj_name+'_'+template+'_comparison.pdf', \
                bbox_inches='tight')
    plt.show()


################################################################################
#                                  RUN FIGURES                                 #
################################################################################

template = 'HD163296'
simobj_name = 'SolarS'

# Path to images
dir_tem = current_dir+'templates/'+template+'/images/'+template+'_im.fits'
dir_mod = current_dir+'projects/SolarS_'+template+'/images/SolarS_'+template+'_im.fits'

makefigure(temp_fits=dir_tem, \
           simobj_fits=dir_mod, \
           template=template, \
           simobj_name=simobj_name, \
           ang_size=1.2)


