
********
CASA API
********

Here is the description of all the functions used to generate a synthetic
observation with **SIMIO-continuum**. These functions must be executed in
a ``CASA 5.6.2`` terminal interface.

.. note::
    Please, check the tutorials to see how to utilize these functions. For
    simplicity, most of the **SIMIO-continuum** functions are made to run inside
    the ``simio_object``, and therefore you will not interact directly with them.


Main functions
==============

.. class:: simio_object(object_name, out_file_name, template, use_geom=True, distance=None, rescale_flux=None, pxsize_au=None, add_inc=0, add_pa=0, add_dRa=0, add_dDec=0)
   
   Location: ``codes/simio_obj.py``
   
   The simio_object is the main object of the simio package. It contains
   the functions and properties needed to generate the synthetic
   visibilities and images from a simulation.
   
   :param object_name: (str) Name of the project.
   :param out_file_name: (str) Name of the ``RADMC3D`` ``.out`` file, or ``.npy``
                    file name.
   :param template: (str) Template to be used as observation base.
   :param use_geom: (bool) Set to True if you want to use the geometry of the
                    template. If you set it to False, then the parameters
                    ``add_inc``, ``add_pa``, ``add_dRa``, ``add_dDec`` are
                    activated. |
                    Default: ``True``
   :param distance: (float) Distance at which your model has to be positioned, 
                    in **parsecs**. If set to None, then the distance of the
                    template will be used.
                    Default: ``None``
   :param rescale_flux: (float) Your model image is rescaled by a scalar, so
                    that the total flux is rescale_flux. The units are **Jy**.
                    If set to None, no flux rescaling is applied.
                    Default: ``None``
   :param pxsize_au: (float) Pixel size in **au**. If your input model is a ``.npy``
                    file, then this parameter is mandatory. It is not used if 
                    your file format is ``.out``.
                    Default: ``None``
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
   
   .. warning:: Use it if you want to calculate the visibilities with ``CASA ft``.
   
   :param simobj: (simio_object) **SIMIO** object containing the information of
                   the synthetic observation that will be generated.
   :param generate_ms: (bool) Set to ``True`` if the measurement set is to be 
                   generated. Set to ``False`` if only the string with the name
                   of the measurement set is needed.
                   Default: ``True``.

   Returns:
       - **mod_ms**: Name of the measurement set with the synthetic observation.


.. function:: add_noise(mod_ms, level='10.2mJy')

   Location: ``codes/simio_clean.py``
    
   Wrapper for sm.setnoise from ``CASA``. This function receives the name of
   the model measurement set (``mod_ms`` from **SIMIO** tutorials), and returns
   a measurement set with the same name, but with added simple thermal noise.
    
   .. warning:: The noise level in the measurement set will not be the same as
      you input in ``level``. After succesful execution, generate
      an image to measure the noise level in the residuals image,
      and then run **SIMIO** again to iteratively find the correct
      ``level`` for the noise desired.
    
   :param mod_ms: (str) Name of the measurement set to be modified.
   :param level: (str) Level of noise to be given to ``sm.setnoise``, and
                   passed directly to ``simplenoise``.

   Returns:
      - (int) Returns 1 if everything worked correctly. The noiseless
      measurement set will be copied into a file with the same
      name but ending in ``_no_noise.ms``, while the ``mod_ms``
      file will be modified to include the requested 
      noise.


Imaging functions
=================

.. function:: easy_mod_tclean(simobj, interactive=False, remove_end=True, manual_threshold=str(2.4e-02)+'mJy')
    
   Location: ``codes/simio_clean.py``
   
   Function wrapper of ``tclean``, ``estimate SNR``, ``JvM correction`` and
   ``delete wrapper``.
   It uses the values from the template and ``simobj`` to fill the 
   ``tclean_wrapper``.
   For a more customized clean, see ``custom_clean`` function, or 
   ``tclean_wrapper``.

   :param simobj: (simio_object) A simio object that already went through
                  the ``get_mod_ms`` function.
   :param interactive: (boolean) Interactive clean. Recommended to set ``True``.
                  Default: ``False``.
   :param remove_end: (Boolean) If ``True``, will remove the folder files after
                  finishing the imaging.
                  Default: ``True``.
   :param manual_threshold: Set the threshold for tclean. By default it cleans to
                  2sigma of DSHARP-like rms.
                  Default: ``'2.4e-02mJy'``.

   Returns:
       - **Fits files** containing the reconstructed images, including the
       residuals, psf, JvM corrected image, and non-JvM corrected images.


.. function:: custom_tclean(simobj, imsize, cellsize, robust, mask, threshold, scales=[0, 3, 8], gain=0.05, smallscalebias=0.45, cyclefactor=1.75, niter=10000, imagename=None, interactive=False, remove_end=True)
    
   Location: ``codes/simio_clean.py``
   
   Function wrapper of ``tclean``, ``estimate SNR``, ``JvM correction``
   and ``delete wrapper``.
   It allows for a more customized clean compared to ``easy_mod_tclean``.
   For more details on some of these parameters, check the tclean task in
   `tclean documentation <https://casa.nrao.edu/docs/taskref/tclean-task.html>`_

   :param simobj: (simio_object) A simio object that already went through
                    the ``get_mod_ms`` function.
   :param imsize: (int) Image size in pixels.
   :param cellsize: (float) Pixel size, must be input in arcsec.
   :param mask: (str) Mask for cleaning the emission, must be a ``CASA`` region
                    format.
   :param threshold: (float) Threshold for how deep the ``CLEAN`` should go, in mJy.
                    For JvM corrected images, set the threshold to be 4 times
                    the rms of the image.
                    For model comparison with other models, you should clean up
                    to 2 or 1 sigma.
   :param scales: (list of int) Scales to use in multiscale, in pixels.
                    Default: [0, 3, 8]
   :param gain: (float) Fraction of the source flux to subtract out of the
                    residual image for the ``CLEAN`` algorithm.
                    Default: 0.05
   :param smallscalebias: (float) Controls the bias towards smaller scales.
                    Default: 0.45
   :param cyclefactor: (float) Computes the minor-cycle stopping threshold.
                    Default: 1.75
   :param niter: (int) Total number of iterations.
                    Default: 10000
   :param imagename: (str) Sufix name for the images, it will be saved in the
                    same folder as in default.
                    Default: ``None``
   :param interactive: (boolean) Interactive clean. Recommended to set ``True``.
                    Default: ``False``
   :param remove_end: (boolean) If ``True``, will remove the folder files after
                    finishing the imaging.
                    Default: ``None``

    Returns:
       - **Fits files** containing the reconstructed images, including the
       residuals, psf, JvM corrected image, and non-JvM corrected images.


Masking functions
=================

.. mask.module:: simio_object

.. mask.function:: get_mask(mask_semimajor=None, inc=None, pa=None)

   Location: ``codes/simio_obj.py``
   
   Elliptical mask for ``CLEAN``. The emission inside this mask will be
   cleaned. If no input is specified, the parameters of the template will
   be used. The output is a ``CASA`` region.
   See `CASA Regions format <https://casa.nrao.edu/casadocs/casa-5.4.1/image-analysis/region-file-format>`_ for more information

   :param mask_semimajor: (int,float) Semimajor axis of the ellipse in arcsec.
   :param inc: (int,float) inclination of the ellipse in degrees.
   :param pa: (int,float) position angle of the ellipse, measured from the
                  north to the east, or counter-clock wise, in degrees.
   Returns:
      - **mask_obj**: (str) elliptical mask. This is a ``CASA`` region.


.. mask.function:: get_mask(mask_semimajor=None, inc=None, pa=None)

   Location: ``codes/simio_obj.py``
   
   Annulus mask to calculate the residuals properties. This mask is a
   circular annulus centered on the phase-center. The inner and outer
   radius should be set such that the mask does not include any real 
   emission.

   :param mask_rin: (int,float) Inner radius of the annulus in arcsec.
   :param mask_rout: (int,float) Outer radius of the annulus in arcsec.

   Returns:
      - **mask_res**: (str) Annulus mask. This is a ``CASA`` region.


Additional Imaging functions
============================

.. function:: delete_wrapper(imagename)

   Location: ``codes/simio_clean.py``

   Wrapper to delete the images generated by tclean.
    
   :param imagename: (str) Base name for the images to be deleted.


.. function:: write_fits(im_base_name)
   
   Location: ``codes/simio_clean.py``

   Given the ``im_base_name`` from ``tclean``, it takes the products and
   write fits files of them.
   
   :param im_base_name: (str) Base name for the images to be written in fits
                       format.


.. function:: estimate_SNR(imagename, disk_mask, noise_mask)

   Location: ``codes/simio_clean.py``

   Original from `DSHARP <https://almascience.eso.org/almadata/lp/DSHARP/>`_.
   Estimate peak SNR of source, given a mask that encompasses the emission
   and another annulus mask to calculate the noise properties.
    
   :param imagename: (str) Image name ending in ``.image``.
   :param disk_mask: (str) must be a ``CASA`` region format.
   :param noise_mask: (str) Annulus to measure image rms, in the ``CASA`` region 
                  format.
                  e.g. ``annulus[['0arcsec', '0arcsec'],['1arcsec', '2arcsec']]``.


.. function:: create_dotmodel(simobj, imagename=None)

   Location: ``codes/simio_clean.py``

   Function to create a ``.model`` image that mimics the ``.out``, with the
   coordinate information of the template.

   :param simobj: (simio_object) **SIMIO** object that will be used to generate the
                    synthetic observation.
   :param imagename: (str) Name of the image model to be generated.

   Returns:
    - **ms_mod**: (str) with the name of the ``.model`` image generated.


Additional Visibility functions
===============================


.. function:: change_geom(ms_file, inc=0., pa=0., dRa=0., dDec=0., datacolumn1='DATA', datacolumn2='DATA', inverse=False)
   
   Location: ``codes/simio_ms2ascii.py``
   
   Changes the geometry of an observation, by inclining and rotating the
   uv-points themselfs. This function modifies the input ``ms_file``.
    
   :param ms_file: (str) Name of the measurement set you want to incline, rotate
                    or shift in physical space.
   :param inc:  (float) Inclination, in **degrees**. Default: 0.
   :param pa: (float) Position angle, measured from north to east,
                    in **degrees**. Default: 0.
   :param dRa: (float) Shift in RA to be applied to the visibilities,
                    in **arcsec**. Default: 0.
   :param dDec: (float) Shift in Dec to be applied to the visibilities.
                    in **arcsec**. Default: 0.
   :param datacolumn1: ``DATA`` or ``MODEL_DATA``, column from where the data must
                       be read. Default: ``DATA``.
   :param datacolumn1: ``DATA`` or ``MODEL_DATA``, column from where the data must
                       be written. Default:``DATA``
   :param inverse (bool): Set ``False`` to deproject, or ``False`` to project.
                        Default: ``False``
    Returns:
       - Returns ``True`` if everything worked correctly. The ``ms_file`` will
       have been modified to the new visibility geometry.
