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


def _shift_uv(u, v, Re, Im, dRa, dDec):
    '''
    Applies rotation and inclination to the input visibilities.
    
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
    '''
    # Calculate the value of the visibilities
    intensity = (Re + Im * 1j) * np.exp(2j * np.pi * (u * -dRa + v * -dDec))
    # Separate in real and imaginary part
    Re_shift = np.real(intensity)
    Im_shift = np.imag(intensity)
    # Return
    return u, v, Re_shift, Im_shift


def _rotate_uv(u, v, pa):
    '''
    Applies a rotation matrix to the visibilities, given a rotation angle
    of 'pa'.

    Args:
        - u: (numpy array) Array containing the ``u`` coordinates of the
                    visibilities.
        - v: (numpy array) Array containing the ``v`` coordinates of the
                    visibilities.
        - pa: (float) Value to rotate the visibilities, in **radians**.
    '''
    # Calculate rotation components
    cos_rot = np.cos(pa)
    sin_rot = np.sin(pa)
    # Rotate coordinates
    u_rot = u * cos_rot - v * sin_rot
    v_rot = u * sin_rot + v * cos_rot
    # Return
    return u_rot, v_rot


def _deproject_uv(u, v, inc):
    '''
    Applies rotation and inclination to the input visibilities.
    
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
    '''
    # Apply inclination
    u_inc = u * np.cos(inc)
    # Return
    return u_inc, v


def _project_uv(u, v, inc):
    '''
    Applies rotation and inclination to the input visibilities.
    
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
    '''
    # Apply inclination
    u_inc = u / np.cos(inc)    
    # Return
    return u_inc, v


def handle_uv(u, v, Re, Im, inc, pa, dRa, dDec, inverse=False):
    '''
    Projects, deprojects, and shifts visibility points based on the input
    parameters.
    
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
    pa   *= np.pi / 180.
    inc  *= np.pi / 180.
    dDec *= np.pi / (180. * 3600)
    dRa  *= np.pi / (180. * 3600)

    # If deprojection
    if not inverse:
        # Calculate shifted visibilities
        u, v, Re_shift, Im_shift = _shift_uv(u, v, Re, Im, dRa, dDec)
        # Cprrect rotation
        u_rot, v_rot = _rotate_uv(u, v, pa)
        # Correct inclination
        u_inc, v_inc = _deproject_uv(u_rot, v_rot, inc)
        # Return
        return u_inc, v_inc, Re_shift, Im_shift

    # If projection
    if inverse:
        # Apply inclination
        u_inc, v_inc = _project_uv(u, v, inc)
        # Apply rotation
        u_rot, v_rot = _rotate_uv(u_inc, v_inc, -pa)
        # Calculate shifted visibilities
        u_rot, v_rot, Re_shift, Im_shift = _shift_uv(u_rot, v_rot, Re, Im, dRa, dDec)
        # Return
        return u_rot, v_rot, Re_shift, Im_shift


