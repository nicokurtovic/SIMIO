# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
##############################################################################

'''
Max Planck Institute for Astronomy
Planet Genesis Group

Nicolas Kurtovic
Contact: kurtovic at mpia.de
'''

import sys
import os
import numpy as np
from scipy.interpolate import interp1d, RectBivariateSpline
from scipy.integrate import trapz, quadrature


##############################################################################
#                                                                            #
##############################################################################


def deproject_uv(u, v, Re, Im, inc, pa, dRa, dDec, inverse=False):
    '''
    Projects and deprojects visibility points based on the input parameters
    
    Args:
        - u: (numpy array) Array containing the ``u`` coordinates of the
                    visibilities.
        - v: (numpy array) Array containing the ``v`` coordinates of the
                    visibilities.
        - Re: (numpy array) Array containing the ``Real`` part of the
                    visibilities.
        - Im: (numpy array) Array containing the ``Imaginary`` part of the
                    visibilities.
        - inc: (float) Value to incline the visibilities, in **degrees**.
        - pa: (float) Value to rotate the visibilities, in **degrees**.
        - dRa: (float) Value to shift the visiblities in RA, in **arcsec**.
        - dDec: (float) Value to shift the visiblities in Dec, in **arcsec**.
        - inverse: (bool) Set ``False`` to deproject, set ``True`` to project.
                    Default: False.
    '''
    # Convert to radian
    pa  = pa  * np.pi / 180.
    inc = inc * np.pi / 180.
    dDec *= np.pi / (180. * 3600)
    dRa  *= np.pi / (180. * 3600)
    # Correct the phase position by dRA and dDec
    if not inverse:
        Intensity = (Re + Im * 1j) * np.exp(2j * np.pi * (u * -dRa + v * -dDec))
        # Calculate deprojected arrays
        Rep = np.real(Intensity)
        Imp = np.imag(Intensity)
    # Calculate transformation
    cos_t = np.cos(pa)
    sin_t = np.sin(pa)
    aux = 1.
    if inverse:
        sin_t *= -1.
        aux = 1. / np.cos(inc)
    up = u * aux * cos_t - v * sin_t
    vp = u * aux * sin_t + v * cos_t
    #   Deproject
    if not inverse:
        up *= np.cos(inc)
    if inverse:
        Intensity = (Re + Im * 1j) * np.exp(2j * np.pi * (up * -dRa + vp * -dDec))
        # Calculate deprojected arrays
        Rep = np.real(Intensity)
        Imp = np.imag(Intensity)
    # Return
    return up, vp, Rep, Imp


def py_sampleImage(reference_image, dxy, udat, vdat, dRA=0., dDec=0., PA=0., origin='upper'):
    '''
    Original from ``galario``.
    Python implementation of sampleImage.
    
    Args:
        - reference_image: (numpy matrix) Name of the image from where the
                    visibilities will be calculated.
        - dxy: (float) Pixel size in **rad**. 
        - udat: (numpy array) Array with the ``u`` coordinates, in 
                    **wavelength units**.
        - vdat: (numpy array) Array with the ``u`` coordinates, in 
                    **wavelength units**.
        - dRa: (float) Value to shift the visiblities in RA, in **arcsec**.
        - dDec: (float) Value to shift the visiblities in Dec, in **arcsec**.
        - PA: (float) Value to rotate the visibilities, in **rad**.
        - origin: (str) Origin of the coordinate system in the image. It has
                    to be 'lower' or 'upper'.
    '''
    if origin == 'upper':
        v_origin = 1.
    elif origin == 'lower':
        v_origin = -1.

    nxy = reference_image.shape[0]

    dRA *= 2.*np.pi
    dDec *= 2.*np.pi

    du = 1. / (nxy*dxy)

    # Real to Complex transform
    fft_r2c_shifted = np.fft.fftshift(
                        np.fft.rfft2(
                            np.fft.fftshift(reference_image)), axes=0)
    # apply rotation
    cos_PA = np.cos(PA)
    sin_PA = np.sin(PA)

    urot = udat * cos_PA - vdat * sin_PA
    vrot = udat * sin_PA + vdat * cos_PA

    dRArot = dRA * cos_PA - dDec * sin_PA
    dDecrot = dRA * sin_PA + dDec * cos_PA

    # interpolation indices
    uroti = np.abs(urot)/du
    vroti = nxy/2. + v_origin * vrot/du
    uneg = urot < 0.
    vroti[uneg] = nxy/2 - v_origin * vrot[uneg]/du

    # coordinates of FT
    u_axis = np.linspace(0., nxy // 2, nxy // 2 + 1)
    v_axis = np.linspace(0., nxy - 1, nxy)

    # We use RectBivariateSpline to do only linear interpolation, which is faster
    # than interp2d for our case of a regular grid.
    # RectBivariateSpline does not work for complex input, so we need to run it twice.
    f_re = RectBivariateSpline(v_axis, u_axis, fft_r2c_shifted.real, kx=1, ky=1, s=0)
    ReInt = f_re.ev(vroti, uroti)
    f_im = RectBivariateSpline(v_axis, u_axis, fft_r2c_shifted.imag, kx=1, ky=1, s=0)
    ImInt = f_im.ev(vroti, uroti)
    f_amp = RectBivariateSpline(v_axis, u_axis, np.abs(fft_r2c_shifted), kx=1, ky=1, s=0)
    AmpInt = f_amp.ev(vroti, uroti)

    # correct for Real to Complex frequency mapping
    uneg = urot < 0.
    ImInt[uneg] *= -1.
    PhaseInt = np.angle(ReInt + 1j*ImInt)

    # apply the phase change
    theta = urot*dRArot + vrot*dDecrot
    vis = AmpInt * (np.cos(theta+PhaseInt) + 1j*np.sin(theta+PhaseInt))

    return vis


def uvmodel_from_image(model_image, u, v, real_part, imag_part, params, px):
    '''
    Given a model image, its image size and pixel size, it returns the
    visibilities calculated with ``galario``.
    The ``params`` contain the geometric information of the disk.

    Args:
        - model_image: (numpy matrix) 
        - u: (numpy array) Array with the ``u`` coordinates, in 
                    **wavelength units**.
        - v: (numpy array) Array with the ``v`` coordinates, in 
                    **wavelength units**.
        - real_part: (numpy_array) Not really needed it. Will be corrected in
                    a future version. Must be same size as ``u``.
        - imag_part: (numpy_array) Not really needed it. Will be corrected in
                    a future version. Must be same size as ``u``.
        - params: (list) List with the geometrical parameters of the disk, in
                    the order of [``dRa``, ``dDec``, ``inc``, ``pa``] and in
                    units of [**arcsec**, **arcsec**, **degrees**, **degrees**].
        - px: (float) Pixel size in **arcsec**.
    '''
    # Params
    dRa, dDec, inc, pa = params
    # Modify visibilities with geometry
    u_mod, v_mod, Re_mod, Im_mod = deproject_uv(u, v, \
                                                real_part, imag_part, \
                                                inc, pa, dRa, dDec, \
                                                inverse=False)
    # Compute model visibilities
    model_vis = py_sampleImage(model_image, \
                               px * (180. * 3600. / np.pi)**-1, \
                               u_mod, v_mod, dRA=0., dDec=0., \
                               origin='lower')
    # Return
    return model_vis


