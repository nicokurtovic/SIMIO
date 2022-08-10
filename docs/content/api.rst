.. module:: simio.codes
.. codes

API
===

Here we describe all the functions used to collapse the spectral cube which are
typically called by the command line interface. However, importing these into
your workflow may be useful.


.. note::
    The convolution for ``smooththreshold`` is currently experimental and is
    work in progress. If things look suspicious, please raise an issue.



Moment Maps
-----------

Implementation of traditional moment-map methods. See the `CASA documentation
<https://casa.nrao.edu/docs/CasaRef/image.moments.html>`_ for more information.

.. autofunction:: codes.simio_obj.simio_object


