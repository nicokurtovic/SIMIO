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
import matplotlib.pyplot as plt

# Directories
current_dir = os.getcwd()+'/'
# Read the codes directory
sys.path.append(current_dir+'codes/')

################################################################################
#                                                                              #
################################################################################

# at this point, simio assumes you already did "import analysisUtils as au"
print (' ')
print (" SIMIO assumes you already did 'import analysisUtils as au'")
print (' ')

# Append ms to ascii functions
execfile(current_dir+'codes/read_out.py')


################################################################################
#                                SIMIO IMAGE CLASS                             #
################################################################################


class simio_image():
    '''
    Reads the model image and stores all the information needed for simio_object
    '''
    # Needed constants
    global au_cm

    # Init the simio_image
    def __init__(self, im_file_name, pxsize_au=None):
        # Name and format of the image
        self.im_file_name = im_file_name
        self._is_out_file = self._check_im_format()
        # 1au in cm
        au_cm = 14959787070000.0
        # Read image
        if self._is_out_file:
            # Read image from out
            simulated_im = read_out_image(self.im_file_name)
            self.model_im = np.squeeze(simulated_im.imageJyppix)
            # Pixel size in au
            self.pxsize_au = simulated_im.sizepix_x / au_cm
            # Image size
            self.imsize = np.shape(self.model_im)[0]
        elif not self._is_out_file:
            # Read image from out
            simulated_im = np.read(self.im_file_name)
            self.model_im = np.squeeze(simulated_im)
            if pxsize_au is None:
                print (' ')
                print (" If im_file_name ends in '.npy', then you have to input the pixel")
                print (" size of the image in au, through the argument pxsize_au of simobj")
                print (' ')
                print (" Please execute simio_object again, with the correct parameters")
                print (' ')
                return 0
            # Pixel size in au
            self.pxsize_au = pxsize_au
            # Image size
            self.imsize = np.shape(self.model_im)[0]


    def _check_im_format(self, ):
        '''
        Checks the format of the input model.
        '''
        # Check if image is .out or .npy
        if self.im_file_name[-4:] == '.out':
            return True
        elif self.im_file_name[-4:] == '.npy':
            return False
        else:
            print (' ')
            print (" The model in 'im_file_name must' end in '.out' or '.npy'")
            print (' ')
            print (" Please execute simio_object again, with the correct parameters")
            print (' ')
            return 0


################################################################################
#                             SIMIO OBJECT CLASS                               #
################################################################################


class simio_object():
    '''
    The simio main object

    The simio_object is the main object of the simio package. It contains the
    functions and properties needed to generate the synthetic visibilities and
    images from a simulation.

    PARAMETERS:
        - object_name (str): Name of the project.
        - out_file_name (str): Name of the RADMC3D out file, or npy file name.
        - template (str): Template to be used as observation base.
        - use_geom (bool): Set to True if you want to use the geometry of the
                     template. If you set it to False, then the parameters
                     "add_inc, add_pa, add_dRa, add_dDec" are activated.
                     Default: True
        - distance (float): Distance at which your model has to be positioned, 
                     in parsecs. If set to None, then the distance of the
                     template will be used.
                     Default: None
        - rescale_flux (float): Your model image is rescaled by a scalar, so
                     that the total flux is rescale_flux. The units are mJy. If
                     set to None, no flux rescaling is applied.
                     Default: None
        - pxsize_au (float): Pixel size in au. If your input model is a '.npy' 
                     file, then this parameter is mandatory. It is not used if 
                     your file format is '.out'.
                     Default: None
        - add_inc  (float): Incline the source by this value, in degrees.
                     Default: 0.
        - add_pa   (float): Rotate the source by this value, in degrees.
                     Default: 0.
        - add_dRa  (float): Shift the source by this value in RA, in arcsec.
                     Default: 0.
        - add_dDec (float): Shift the source by this value in Dec, in arcsec.
                     Default: 0.
    '''

    def __init__(self, object_name, im_file_name, template, use_tempgeom=True, \
                 distance=None, rescale_flux=None, pxsize_au=None, \
                 add_inc=0., add_pa=0., add_dRa=0., add_dDec=0.):
        # Warn about deprecated arguments
        if type(object_name) is not str:
            print ("The 'object_name' argument must be string")
        # Set the object properties
        self._prefix = object_name        # Mainly for imaging
        self.object_name = object_name    # Public instance
        self.im_file_name = im_file_name  # Input model to be mimicked
        # Template to use
        self.template = template
        # Set directories paths
        self._temp_dir = current_dir + 'templates/' + template + '/'
        self._source_dir = current_dir + 'projects/' + object_name + '/'
        # Load template properties
        self._spw_temp = np.load(self._temp_dir + 'uvtables/'+template+'_spws.npy')
        self._ms_temp = self._temp_dir + 'msfiles/' + template + '_avg.ms'
        self._info_temp = self._temp_dir + template + '_info.py'

        # Geometry of the observation
        with open(self._info_temp) as f:
            for line in f:
                exec (line)
        self._use_tempgeom = use_tempgeom

        # Set distance
        if distance is not None:
            dist = distance
        # Template sky coordinates and size
        self._temp_center_ra  = temp_center_ra
        self._temp_center_dec = temp_center_dec
        self._temp_semimaj    = temp_semimaj
        # Set geometry
        if use_tempgeom:
            # Read template info file
            self.dRa = dRa
            self.dDec = dDec
            self.inc = inc
            self.pa = pa
            self._geom_params = [dRa, dDec, inc, pa]
        elif not use_tempgeom:
            self.dRa = add_dRa
            self.dDec = add_dDec
            self.inc = add_inc
            self.pa = add_pa
            self._geom_params = [add_dRa, add_dDec, add_inc, add_pa]

        # Set clean information
        self._clean_robust   = temp_robust
        self._clean_cellsize = temp_cellsize
        self._clean_imsize   = temp_imsize

        # Open the model image
        self.sim_im = simio_image(self._source_dir + self.im_file_name, \
                                  pxsize_au=pxsize_au)
        # Rescale image by distance
        self.sim_im.scaled_model_im = self.sim_im.model_im / (dist**2)
        # Does image has a desired total flux?
        if rescale_flux is not None:
            aux_flux = np.sum(self.sim_im.scaled_model_im)
            self.sim_im.scaled_model_im *= rescale_flux / aux_flux        
        # Pixel size in arcsec
        self.sim_im.pxsize_arcsec = self.sim_im.pxsize_au / dist


    def get_mask(self, mask_semimajor=None, inc=None, pa=None):
        '''
        Elliptical mask for CLEAN. The emission inside this mask will be
        cleaned. If no input is specified, the parameters of the template will
        be used. The output is a CASA region.
        See https://casa.nrao.edu/casadocs/casa-5.4.1/image-analysis/region-file-format

        PARAMETERS:
         - mask_semimajor (int,float)= Semimajor axis of the ellipse in arcsec.
         - inc (int,float)= inclination of the ellipse in degrees.
         - pa  (int,float)= position angle of the ellipse, measured from the
                 north to the east, or counter-clock wise, in degrees.
        OUTPUT:
         - mask_obj (str)= elliptical mask. This is a CASA region.
        '''
        # Semimajor axis size
        if mask_semimajor is None:
            mask_semimajor = self._temp_semimaj
        # Inclination
        if inc is None:
            inc = self.inc
        # Position angle
        if pa is None:
            pa = self.pa
        # Size of mask in each axis
        mask_semiminor = str(mask_semimajor*np.cos(np.deg2rad(inc)))+'arcsec'
        mask_semimajor = str(mask_semimajor)+'arcsec'
        # Mask position angle
        pa_mask = str(pa)
        # Set mask
        mask_obj = 'ellipse[[%s, %s], [%s, %s], %sdeg]' % (self._temp_center_ra, \
                                                           self._temp_center_dec, \
                                                           mask_semimajor, \
                                                           mask_semiminor, \
                                                           pa_mask)
        # Write mask property
        self.mask_obj = mask_obj
        # Return mask
        return mask_obj


    def get_residual_mask(self, mask_rin=None, mask_rout=None):
        '''
        Elliptical mask to calculate the residuals properties. This mask is a
        circular annulus centered on the phase-center. The inner and outer
        radius should be set such that the mask does not include any real 
        emission.

        PARAMETERS:
         - mask_rin (int,float)= Inner radius of the annulus in arcsec.
         - mask_rout (int,float)= Outer radius of the annulus in arcsec.
        '''
        # Inner radius for annulus
        if mask_rin is None:
            mask_rin = 2.5 # arcsec
        # Outer radius for annulus
        if mask_rout is None:
            mask_rout = 3.5 # arcsec
        # Size of mask in each axis
        mask_rin  = str(mask_rin)  + 'arcsec'
        mask_rout = str(mask_rout) + 'arcsec'
        # Set mask
        res_mask_obj = 'annulus[[%s, %s], [%s, %s]]' % (self._temp_center_ra, \
                                                    self._temp_center_dec, \
                                                    mask_rin, mask_rout)
        # Write mask property
        self.res_mask_obj = res_mask_obj
        # Return mask
        return res_mask_obj


