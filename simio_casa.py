# -*- coding: utf-8 -*-
################################################################################
#                                     SIMIO                                    #
################################################################################

'''
This is an example code with the step-by-step of how to use SIMIO.
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
# Solar System as HD163296
###########################

# Create a simio object.
# Object name is your project name
# im_file_name is the name of your ".out" file inside your project folder
# The template name must match upper and lower cases
# Set use_tempgeom to False if you do not want to use the template geometry
simobj = simio_object(object_name  = 'SolarS_HD163296', 
                      im_file_name = 'image_1300micron.out', 
                      template     = 'HD163296', 
                      use_tempgeom = True)

# Create the measurement file of your simio object, and get the path.
# Can take several minutes
mod_ms = get_mod_ms_ft(simobj)

# Create a mask for your system, and one to measure the residuals
# Our SolarSystem model outer radius is about 0.65 arcsec at
# the distance of HD163296
mask_obj = simobj.get_mask(mask_semimajor=0.65)
mask_res = simobj.get_residual_mask()

# Generate image for your simio object.
# Can take several minutes, maybe an hour.
easy_mod_tclean(simobj, interactive=True)

