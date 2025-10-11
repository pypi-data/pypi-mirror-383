Utilities module
================

`Source <https://gitlab.com/delta-microscopy/delta/-/blob/main/delta/utils.py>`_ |
:class:`API<delta.utils>`

The utilities module contains many functions used in several different parts of
the code. The most important elements are described below.

.. _xpreader:

The XPReader class
------------------

The :class:`delta.utils.XPReader` class is used to read experiment files.
This can either be
`Bio-Formats <https://www.openmicroscopy.org/bio-formats/>`_ compatible files
such as the open format OME-TIFF, Nikon's .nd2 format, Olympus's .oib format,
Zeiss's .czi format and many more. Or it can be a folder containing separate
image files for all positions, imaging channels, and frames.

.. code:: python

    reader = delta.utils.XPReader("/path/to/file.nd2")

.. note::

    We use the library `aicsimageio
    <https://allencellmodeling.github.io/aicsimageio/>`_ to read images.  By
    default, it should be able to read most general-purpose image formats, and
    a couple of microscopy-specific ones (such as Nikon's nd2), but we cannot
    install everything.  However, the library reports useful error messages if
    a component is missing: in case your are getting one of them, read it and
    install with pip or conda the suggested package to read your file format.


In order to read data from an experiment stored in a folder with one file per
frame, the XPReader object needs to be given a prototype that describes the
template used for naming files.

This argument describes the structure of the folder with three different kinds
of placeholders: ``{p}`` for position numbers, ``{c}`` for channel numbers, and
``{t}`` for frame numbers.  For example, if all image files are under the same
top-level folder with names such as ``PositionXX_ChannelXX_FrameXXXXXX.tif``
the prototype would be ``Position{p}_Channel{c}_Frame{t}.tif``. But sub-folders
can also be part of the prototype, like
``Channel{c}/Position{c}/IMG_{t}.tiff``.

The following examples are all valid:

.. code:: python

    reader = delta.utils.XPReader("/path/to/xpfolder/Position{p}_Channel{c}_Time{t}.tif")

.. code:: python

    reader = delta.utils.XPReader("/path/to/xpfolder/Time{t}/Channel{c}.png")

.. code:: python

    reader = delta.utils.XPReader(
        "/path/to/xpfolder/Channel{c}/Position{p}_Time{t}/IMG_{t}.tif"
    )

If the filenames do not in fact correspond to the prototype, fileorder, and
indexing, the XPReader may still initialize without raising an exception. To
make sure it has identified files in the folder properly, check that the
following properties are correct:

.. code:: python

    reader.positions  # list of integers
    reader.channels  # list of integers
    reader.frames  # range of integers
    readers.y  # number of rows of an image
    readers.x  # number of columns of an image

See also our :doc:`results analysis examples <../analysis>`
