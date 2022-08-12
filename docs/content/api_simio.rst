
********
CASA API
********

Here is the description of all the functions used to generate a synthetic
observation with *SIMIO-continuum*. These functions must be executed in
a CASA 5.6.2 terminal interface.

Please, check the tutorials to see how to utilize these functions. For
simplicity, most of the *SIMIO-continuum* functions are made to run inside
the "simio_object", and therefore you will not interact directly with them.

.. note::
    blablabla


Main functions
==============

.. class:: simio_object(object_name, out_file_name, template, use_geom=True, distance=None, rescale_flux=None, pxsize_au=None, add_inc=0, add_pa=0, add_dRa=0, add_dDec=0)
   Location: ``codes/simio_obj.py``
   
   The simio_object is the main object of the simio package. It contains
   the functions and properties needed to generate the synthetic
   visibilities and images from a simulation.
   
   :param object_name: (str) Name of the project.
   :param out_file_name: (str) Name of the RADMC3D ``.out`` file, or ``.npy``
                    file name.
   :param template: (str) Template to be used as observation base.
   :param use_geom: (bool) Set to True if you want to use the geometry of the
                    template. If you set it to False, then the parameters
                    ``add_inc``, ``add_pa``, ``add_dRa``, ``add_dDec`` are
                    activated.
                    Default: True
   :param distance: (float) Distance at which your model has to be positioned, 
                    in **parsecs**. If set to None, then the distance of the
                    template will be used.
                    Default: None
   :param rescale_flux: (float) Your model image is rescaled by a scalar, so
                    that the total flux is rescale_flux. The units are **Jy**.
                    If set to None, no flux rescaling is applied.
                    Default: None
   :param pxsize_au: (float) Pixel size in **au**. If your input model is a ``.npy``
                    file, then this parameter is mandatory. It is not used if 
                    your file format is ``.out``.
                    Default: None
   :param add_inc: (float) Incline the source by this value, in **degrees**.
                    Default: 0.
   :param add_pa: (float) Rotate the source by this value, in **degrees**.
                    Default: 0.
   :param add_dRa: (float) Shift the source by this value in RA, in **arcsec**.
                    Default: 0.
   :param add_dDec: (float) Shift the source by this value in Dec, in **arcsec**.
                    Default: 0.


.. function:: get_mod_ms_ft(simobj, generate_ms=True)
   Location: ``codes/simio_ms2ascii.py``
   
   Generates the model ms file for the simobj. If ``generate_ms`` is set
   to ``False``, then the function will only return the string of the ms file
   path, but not generate the ms file itself.
   
   ..warning:: Use it if you want to calculate the visibilities with ``CASA ft``.
   
   Args:
   :param simobj: (simio_object) **SIMIO** object containing the information of
                   the synthetic observation that will be generated.
   :param generate_ms: (bool) Set to ``True`` if the measurement set is to be 
                   generated. Set to ``False`` if only the string with the name
                   of the measurement set is needed.
                   Default: ``True``.

   Returns:
       - mod_ms: Name of the measurement set with the synthetic observation.


.. function:: add_noise(mod_ms, level='10.2mJy'):

   Location: ``codes/simio_clean.py``
    
   Wrapper for sm.setnoise from ``CASA``. This function receives the name of
   the model measurement set (``mod_ms`` from **SIMIO** tutorials), and returns
   a measurement set with the same name, but with added simple thermal noise.
    
   ..warning: The noise level in the measurement set will not be the same as
                   you input in ``level``. After succesful execution, generate
                   an image to measure the noise level in the residuals image,
                   and then run SIMIO again to iteratively find the correct
                   ``level`` for the noise desired.
    
   Args:
   :param mod_ms: (str) Name of the measurement set to be modified.
   :param level: (str) Level of noise to be given to ``sm.setnoise``, and
                   passed directly to ``simplenoise``.

   Returns:
               (int) Returns 1 if everything worked correctly. The noiseless
               measurement set will be copied into a file with the same
               name but ending in '_no_noise.ms', while the ``mod_ms``
               file will be modified to include the requested 
               noise.








Imaging functions
=================

.. module:: simio_object

.. function:: get_mask(mask_semimajor=None, inc=None, pa=None)

   Location: ``codes/simio_clean.py``
   
   Elliptical mask for CLEAN. The emission inside this mask will be
   cleaned. If no input is specified, the parameters of the template will
   be used. The output is a CASA region.
   See `CASA Regions format <https://casa.nrao.edu/casadocs/casa-5.4.1/image-analysis/region-file-format>`_ for more information

   Args:
   :param mask_semimajor: (int,float) Semimajor axis of the ellipse in arcsec.
   :param inc: (int,float) inclination of the ellipse in degrees.
   :param pa: (int,float) position angle of the ellipse, measured from the
                  north to the east, or counter-clock wise, in degrees.
   Returns:
   :param mask_obj: (str) elliptical mask. This is a CASA region.


.. module:: simio_object

.. function:: get_mask(mask_semimajor=None, inc=None, pa=None)

   Location: ``codes/simio_clean.py``
   
   Annulus mask to calculate the residuals properties. This mask is a
   circular annulus centered on the phase-center. The inner and outer
   radius should be set such that the mask does not include any real 
   emission.

   Args:
   :param mask_rin: (int,float) Inner radius of the annulus in arcsec.
   :param mask_rout: (int,float) Outer radius of the annulus in arcsec.
   Returns:
   :param mask_obj: (str) Annulus mask. This is a CASA region.

   
.. function:: get_mask(mask_semimajor=None, inc=None, pa=None)
