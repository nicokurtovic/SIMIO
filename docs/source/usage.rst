Usage
=====

.. _installation:

Installation
------------

To use SIMIO, first install it using pip:

.. code-block:: console

   pip install lumache

Creating recipes
----------------

To retrieve a list of random ingredients,
you can use the ``SIMIO.get_random_ingredients()`` function:

.. autofunction:: SIMIO.get_random_ingredients

The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
will raise an exception.

.. autoexception:: lumache.InvalidKindError

For example:

>>> import lumache
>>> lumache.get_random_ingredients()
['shells', 'gorgonzola', 'parsley']

