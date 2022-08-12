
********
CASA API
********

Here is the description of all the functions used to generate a synthetic
observation with SIMIO-continuum. These functions must be executed in
a CASA 5.6.2 terminal interface.

Please, check the tutorials to see how to utilize these functions. For
simplicity, most of the SIMIO-continuum functions are made to run inside
the "simio_object", and therefore you will not interact directly with them.

.. note::
    blablabla


Main functions
==============

.. class:: simio_object(object_name, out_file_name, template, use_geom=True, distance=None, rescale_flux=None, pxsize_au=None, add_inc=0, add_pa=0, add_dRa=0, add_dDec=0)
   
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


    .. function:: function simio_object get_mask(mask_semimajor=None, inc=None, pa=None)
    
        testing if this works
        
        :param testeo: aaaaa aaa aa a
        :param testeob: aaaaa aaa aa b
        :param testeoc: aaaaa aaa aa c


.. cpp:function:: simio_object.get_mask(mask_semimajor=None, inc=None, pa=None)

   const MyType Foo(const MyType bar)

   Some function type thing
   
    :param testeoa: aaaaa aaa aa a
    :param testeob: aaaaa aaa aa b
    :param testeoc: aaaaa aaa aa c


.. js:module:: simio_object

.. js:function:: get_mask(mask_semimajor=None, inc=None, pa=None)



other test

.. module:: simio_object

.. function:: get_mask(mask_semimajor=None, inc=None, pa=None)
