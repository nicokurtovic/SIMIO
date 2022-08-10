
API
===


test to see if this worked

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

Projects
~~~~~~~~

Projects list
+++++++++++++

.. http:get:: /api/v3/projects/

    Retrieve a list of all the projects for the current logged in user.

    :query string language: language code as ``en``, ``es``, ``ru``, etc.
    :query string programming_language: programming language code as ``py``, ``js``, etc.

    The ``results`` in response is an array of project data,
    which is same as :http:get:`/api/v3/projects/(string:project_slug)/`.

    .. note::

       .. FIXME: we can't use :query string: here because it doesn't render properly

      :doc:`Read the Docs for Business </commercial/index>`, also accepts

      :Query Parameters:

         * **expand** (*string*) -- with ``organization`` and ``teams``.

