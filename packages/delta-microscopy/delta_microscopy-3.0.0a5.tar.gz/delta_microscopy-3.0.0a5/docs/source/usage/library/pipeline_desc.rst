
Pipeline
========

`Source <https://gitlab.com/delta-microscopy/delta/-/blob/main/delta/pipeline.py>`_ |
:class:`API<delta.pipeline>`

The pipeline is the core element of DeLTA: Once an :ref:`XPReader <xpreader>`
has been initialized on your experimental files, it can be passed to the
``Pipeline`` object to initialize it and then run it. Depending on which
:class:`delta.config.Config` was loaded, it will:

0. (optional) Perform an ROI (i.e. mother machine chambers) detection step, a
   rotation correction step and a drift correction step.  Then, for each ROI:
#. Segment images
#. Track segmented cells through time and reconstruct the lineage
#. Extract features such as cell length, cell fluorescence etc...
#. Save data to disk (see :doc:`../outputs`)

Basic usage
-----------

The most basic usage is::

    config = delta.config.Config.default("mothermachine")   # or "2D"
    reader = delta.utils.XPReader('/path/to/file/or/folder')
    processor = delta.pipeline.Pipeline(reader, config)
    processor.process()

This will process all frames, for all positions in the movie, and will extract
all features. The :doc:`output files <../outputs>` will be saved under
``processor.resfolder``, which by default points to a new folder within or next
to the input folder/file. You can also specify where to save results during init::

    processor = delta.pipeline.Pipeline(
        reader,
        config,
        resfolder='/path/to/results/folder/',
        )

Or after init but before processing::

    processor.resfolder = '/path/to/another/folder/'

See also the :ref:`run pipeline script <run_pipeline>` and the :ref:`XPReader class <xpreader>`

Selectively process frames, positions, and features
---------------------------------------------------

You can also specify subsamples of the data to analyze, with the arguments
``positions`` and ``frames``, the first one taking a list and the second a
range.

To process only the frames 15 (included) to 30 (excluded):

.. code:: python

    processor.process(frames=range(15, 30))

To process only the positions 1, 3 and 34:

.. code:: python

    processor.process(positions=[1, 3, 34])

Or any combination of the two.

More details
------------

The pipeline module uses 3 main classes of objects

* The higher level object is the :class:`delta.pipeline.Pipeline` class.
  Typically only one is instantiated per analysis. Its main purpose is to
  create and initialize the ``Position`` class processor objects (under the
  ``Pipeline.positions`` dictionary) and to provide a simple interface to
  process an entire multi-position experiment.
* The :class:`delta.pipeline.Position` class objects are used to process a
  single, specific position of the experiment. To process a position manually,
  the user can run for example (this is what is done by the
  :class:`delta.Pipeline.process` function):

  .. code:: python

      # Create the position object
      position = delta.pipeline.Position(position_nb=4, config=config)

      # Get image data from the reader
      all_frames = reader.getframes(position=4)

      # Create ROIs and distribute images
      position.preprocess(all_frames)

      # Segment and all ROIs
      pos.segment()
      pos.track()

      # Save netCDF file
      pos.save("/path/to/file_without_ext", save_as=("netCDF",))

  Each position will have one or more ``ROI`` class object under its
  ``Position.rois`` dictionary.  Both :class:`Position.segment` and
  :class:`Position.track` functions iterate over the ROIs of the position and
  call in turn their :class:`ROI.segment` and :class:`ROI.track` functions,
  which do all the hard work.
* The :class:`delta.pipeline.ROI` objects are dedicated to one region of
  interest in the field of view.  They will focus on one area, as defined under
  ``ROI.box``, and prepare U-Net inputs for each timepoint. Then, they run the
  models on them and record the results.

Feature extraction
------------------

Single-cell features are extracted and stored in the
:class:`delta.lineage.Lineage` object.
These include morphological features:

* | Cell area: The area of the cell, in pixels, as returned by opencv's
    ``contourArea()``. This means that corner pixels are counted as 1/4 and
    straight edge pixels are coutned as 1/2.
* | Cell edges: The edges of the image that cell is currently touching. Left,
    right, bottom, and top edges are labelled as '-x', '+x', '+y', and '-y',
    respectively.
* | Cell length: The cell length, computed by fitting a rotated bounding box
    to the segmented cell. While this technique is fast, it is not as
    accurate for bent or filamented cells.
* | Position of the old pole: The position of the old pole of the cell in the
    image. The position is given as (Y,X) coordinates, with (0,0) in the
    top left corner of the image (ie row-major ordering).
* | Position of the new pole: The position of the new pole of the cell in the
    image. The position is given as (Y,X) coordinates, with (0,0) in the
    top left corner of the image (ie row-major ordering).
* | Cell perimeter: The number of pixels of the cell's contour.
* | Cell width: The cell width, computed by fitting a rotated bounding box
    to the segmented cell. While this technique is fast, it is not as
    accurate for bent or filamented cells.

And dynamical features, such as growth rates:

* | Growth rate (area-based): The instantaneous exponential rate of increase
    of the cell area is extracted, with centered differences when the cell
    exists at both previous and next time points, and one-sided differences
    otherwise.
* | Growth rate (length-based): The instantaneous exponential rate of increase
    of the cell length is extracted, with centered differences when the cell
    exists at both previous and next time points, and one-sided differences
    otherwise.

Using central differences allows the error to decrease quadratically with the
time interval between frames.  In both cases, the growth rate computation
should behave well even during cell divisions, but tracking mistakes can affect
it negatively. Besides, imaging and segmentation noise can produce a non-smooth
growth rate which one might find suitable to smooth with an appropriate function
(such as, for example, centered moving averages).

If fluorescence channels are also provided, the pipeline will also extract
the average fluorescence for each channel. The mean intensity over all pixels
of the segmented cell's surface is computed.

See also :doc:`../outputs` and :doc:`../analysis`

Saving ROIs and Positions
-------------------------

A ROI object can be represented as an ``xarray.Dataset``, which is a structured
array format, the N-D equivalent to a Pandas DataFrame.  The netCDF file format
is particularly adapted to save this object to disk.  To save a ``Position``,
you can use the function :class:`Position.save` which iterates over the ROIs,
converts them to xarrays with the function :class:`ROI.to_xarray`, and then
save them all in a single file:

.. code:: python

    position.save("position.nc", save_as=("netCDF",))

To reload a saved position from file, use the function
:class:`Position.load_netcdf`:

.. code:: python

    position = delta.pipeline.Position.load_netcdf("position.nc")

For more information on the properties of the ``Position`` and ``ROI`` objects, and
how to use them instead of the data in the netCDF files, see :doc:`../outputs`
