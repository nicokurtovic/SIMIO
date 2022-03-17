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
    """
    Python implementation of sampleImage.
    """
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
    visibilities calculated with galario.
    The params contain the geometric information of the disk
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


