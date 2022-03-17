# -*- coding: utf-8 -*-
################################################################################
#                                     SIMIO                                    #
################################################################################

'''
This is an example code with the step-by-step of how to use simio.
'''

# Import needed python packages
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Get the current directory path
current_dir = os.getcwd()+'/'

################################################################################
#                                                                              #
################################################################################

# Import the analysis utils functions
sys.path.append(current_dir+'codes/analysis_scripts/')
import analysisUtils as au

# Import the simio object
execfile(current_dir+'codes/simio_obj.py')
# Import functions for uv-handling
execfile(current_dir+'codes/simio_ms2ascii.py')
# Import functions for imaging
execfile(current_dir+'codes/simio_clean.py')


################################################################################
#                         GENERATE SIMIO OBSERVATIONS                          #
################################################################################


###########################
# Solar System as TWHya
###########################

# Create a simio object.
simobj = simio_object(object_name  = 'SolarS_TWHya', 
                      im_file_name = 'image_1300micron.out', 
                      template     = 'TWHya', 
                      use_tempgeom = True)

# Create the measurement file of your simio object, and get the path.
# Can take several minutes
mod_ms = get_mod_ms(simobj)

# Create a mask for your system, and one to measure the residuals
# Our SolarSystem model outer radius is about 0.65 arcsec at
# the distance of TWHya
mask_obj = simobj.get_mask(mask_semimajor=1.1)
mask_res = simobj.get_residual_mask()

# Generate image for your simio object.
# Can take several minutes, maybe an hour.
easy_mod_tclean(simobj, interactive=True)



###########################
# Solar System as HD163296
###########################

# Create a simio object.
simobj = simio_object(object_name  = 'SolarS_HD163296', 
                      im_file_name = 'image_1300micron.out', 
                      template     = 'HD163296', 
                      use_tempgeom = True)

# Create the measurement file of your simio object, and get the path.
# Can take several minutes
mod_ms = get_mod_ms(simobj)

# Create a mask for your system, and one to measure the residuals
# Our SolarSystem model outer radius is about 0.65 arcsec at
# the distance of HD163296
mask_obj = simobj.get_mask(mask_semimajor=0.65)
mask_res = simobj.get_residual_mask()

# Generate image for your simio object.
# Can take several minutes, maybe an hour.
easy_mod_tclean(simobj, interactive=True)



###########################
# Solar System as MYLup
###########################

# Create a simio object.
simobj = simio_object(object_name  = 'SolarS_MYLup', 
                      im_file_name = 'image_1300micron.out', 
                      template     = 'MYLup', 
                      use_tempgeom = True)

# Create the measurement file of your simio object, and get the path.
# Can take several minutes
mod_ms = get_mod_ms(simobj)

# Create a mask for your system, and one to measure the residuals
# Our SolarSystem model outer radius is about 0.41 arcsec at
# the distance of MYLup
mask_obj = simobj.get_mask(mask_semimajor=0.41)
mask_res = simobj.get_residual_mask()

# Generate image for your simio object.
# Can take several minutes, maybe an hour.
easy_mod_tclean(simobj, interactive=True)



###########################
# Solar System as LkHa330
###########################

# Create a simio object.
simobj = simio_object(object_name  = 'SolarS_LkHa330', 
                      im_file_name = 'image_1300micron.out', 
                      template     = 'LkHa330', 
                      use_tempgeom = True)

# Create the measurement file of your simio object, and get the path.
# Can take several minutes
mod_ms = get_mod_ms(simobj)

# Create a mask for your system, and one to measure the residuals
# Our SolarSystem model outer radius is about 0.41 arcsec at
# the distance of MYLup
mask_obj = simobj.get_mask(mask_semimajor=0.21)
mask_res = simobj.get_residual_mask()

# Generate image for your simio object.
# Can take several minutes, maybe an hour.
easy_mod_tclean(simobj, interactive=True)



###########################
# Solar System as PDS70
###########################

# Create a simio object.
simobj = simio_object(object_name  = 'SolarS_PDS70', 
                      im_file_name = 'image_1300micron.out', 
                      template     = 'PDS70', 
                      use_tempgeom = True)

# Create the measurement file of your simio object, and get the path.
# Can take several minutes
mod_ms = get_mod_ms(simobj)

# Create a mask for your system, and one to measure the residuals
# Our SolarSystem model outer radius is about 0.65 arcsec at
# the distance of HD163296
mask_obj = simobj.get_mask(mask_semimajor=0.60)
mask_res = simobj.get_residual_mask()

# Generate image for your simio object.
# Can take several minutes, maybe an hour.
easy_mod_tclean(simobj, interactive=True)



