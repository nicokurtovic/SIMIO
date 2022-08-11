
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


Optional parameter args
=======================

At this point optional parameters `cannot be generated from code`_.
However, some projects will manually do it, like so:

This example comes from `django-payments module docs`_.

.. class:: payments.dotpay.DotpayProvider(seller_id, pin[, channel=0[, lock=False], lang='pl'])

   This backend implements payments using a popular Polish gateway, `Dotpay.pl <http://www.dotpay.pl>`_.

   Due to API limitations there is no support for transferring purchased items.


   :param seller_id: Seller ID assigned by Dotpay
   :param pin: PIN assigned by Dotpay
   :param channel: Default payment channel (consult reference guide)
   :param lang: UI language
   :param lock: Whether to disable channels other than the default selected above

.. _cannot be generated from code: https://groups.google.com/forum/#!topic/sphinx-users/_qfsVT5Vxpw
.. _django-payments module docs: http://django-payments.readthedocs.org/en/latest/modules.html#payments.authorizenet.AuthorizeNetProvide

