
Contents API
============

The Jupyter Notebook web application provides a graphical interface for
creating, opening, renaming, and deleting files in a virtual filesystem.

The :class:`ContentsManager` class defines an abstract
API for translating these interactions into operations on a particular storage
medium. The default implementation,

This section describes the interface implemented by ContentsManager subclasses.
We refer to this interface as the **Contents API**.

Data Model
----------

ContentsManager methods represent virtual filesystem entities as dictionaries,
which we refer to as **models**.

Models may contain the following entries:

+--------------------+-----------+------------------------------+
| Key                | Type      |Info                          |
+====================+===========+==============================+
|**name**            |unicode    |Basename of the entity.       |
+--------------------+-----------+------------------------------+
|**path**            |unicode    |Full                          |
|                    |           |(:ref:`API-style`)            |
|                    |           |path to the entity.           |
+--------------------+-----------+------------------------------+
|**type**            |unicode    |The entity type. One of       |
|                    |           |``"notebook"``, ``"file"`` or |
|                    |           |``"directory"``.              |
+--------------------+-----------+------------------------------+
|**created**         |datetime   |Creation date of the entity.  |
+--------------------+-----------+------------------------------+
|**last_modified**   |datetime   |Last modified date of the     |
|                    |           |entity.                       |
+--------------------+-----------+------------------------------+
|**content**         |variable   |The "content" of the entity.  |
|                    |           |(:ref:`See                    |
|                    |           |Below)                        |
+--------------------+-----------+------------------------------+
|**mimetype**        |unicode or |The mimetype of ``content``,  |
|                    |``None``   |if any.  (:ref:`kkk`)         |
+--------------------+-----------+------------------------------+
|**format**          |unicode or |The format of ``content``,    |
|                    |``None``   |if any. (:ref:`Sell`)         |
+--------------------+-----------+------------------------------+

modelcontent:

Certain model fields vary in structure depending on the ``type`` field of the
model. There are three model types: **notebook**, **file**, and **directory**.

- ``notebook`` models
    - The ``format`` field is always ``"json"``.
    - The ``mimetype`` field is always ``None``.
    - The ``content`` field contains a
    
- ``file`` models
    - The ``format`` field is either ``"text"`` or ``"base64"``.
    - The ``mimetype`` field can be any mimetype string, but defaults to 
      ``text/plain`` for text-format models and
      ``application/octet-stream`` for base64-format models. For files with
      unknown mime types (e.g. unknown file extensions), this field may be
      `None`.
    - The ``content`` field is always of type ``unicode``.  For text-format
      file models, ``content`` simply contains the file's bytes after decoding
      as UTF-8.  Non-text (``base64``) files are read as bytes, base64 encoded,
      and then decoded as UTF-8.

- ``directory`` models
    - The ``format`` field is always ``"json"``.
    - The ``mimetype`` field is always ``None``.

.. note::

   .. _contentfree:

   In certain circumstances, we don't need the full content of an entity to
   complete a Contents API request. In such cases, we omit the ``content``, and
   ``format`` keys from the model. The default values for the ``mimetype``
   field will might also not be evaluated, in which case it will be set as `None`.
   This reduced reply most commonly occurs when listing a directory, in
   which circumstance we represent files within the directory as content-less
   models to avoid having to recursively traverse and serialize the entire
   filesystem.

**Sample Models**

.. code-block:: python

    # Notebook Model with Content
    {
        'content': {
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 0,
            'cells': [
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': 'Some **Markdown**',
                },
            ],
        },
        'created': datetime(2015, 7, 25, 19, 50, 19, 19865),
        'format': 'json',
        'last_modified': datetime(2015, 7, 25, 19, 50, 19, 19865),
        'mimetype': None,
        'name': 'a.ipynb',
        'path': 'foo/a.ipynb',
        'type': 'notebook',
        'writable': True,
    }

    # Notebook Model without Content
    {
        'content': None,
        'created': datetime.datetime(2015, 7, 25, 20, 17, 33, 271931),
        'format': None,
        'last_modified': datetime.datetime(2015, 7, 25, 20, 17, 33, 271931),
        'mimetype': None,
        'name': 'a.ipynb',
        'path': 'foo/a.ipynb',
        'type': 'notebook',
        'writable': True
    }


API Paths
~~~~~~~~~
