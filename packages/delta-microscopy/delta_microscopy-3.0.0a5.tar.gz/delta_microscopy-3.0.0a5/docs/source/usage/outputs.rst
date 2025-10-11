Output files
============

By default, the :class:`delta.pipeline.Pipeline` will save 2 files per
processed position:

* A netCDF file (``.nc``) that can be used to reload the corresponding
  ``Position`` object in memory.  It contains all the segmentation, tracking,
  lineage and cell morphology information.
* An MP4 movie file to quickly check visually the quality of the segmentation
  and tracking.

netCDF results file
-------------------

Both the :class:`delta.pipeline.ROI` and :class:`delta.pipeline.Position` (a
collection of ``ROI`` s) can be saved as netCDF files (``.nc``).  This is a
standard, open format for multidimensional data, which relies on the HDF5
backend.

.. note::
    This means that netCDF4 files are also HDF5 files!  They can be read by
    both a netCDF reader or an HDF5 reader.

While you can read the ``.nc`` files with any programming language and netCDF
library, the easiest is to use DeLTA itself, to regenerate the ``Position`` or
``ROI`` from the file.  For example, let's load a file from DeLTA's test suite:

.. code:: python

    import delta

    pos = delta.pipeline.Position.load_netcdf(
        "tests/data/movie_2D_nd2/test_expected_results/Position000000.nc"
    )

Check out :doc:`library/lineage_desc` for more information on how to access
single-cell extracted features from this position.

xarray ROI representation
-------------------------

While the :class:`delta.pipeline.ROI` is how DeLTA stores cell and lineage
information in memory, this information can also be represented differently, in
the form of a collection of multidimensional rectangular arrays.  The Python
library ``xarray`` offers a really convenient way to manipulate this format.

.. note::
    The netCDF file is actually a direct transcription of this style of
    multidimensional arrays.

Let's examine for example the first (and only) ROI of the previous position:

.. code:: python-console

    >>> roi = pos.rois[0]
    >>> # Let's draw the schematic lineage to see what the ROI looks like
    >>> print(roi.lineage)
    frames    : ..........
    cell #0001: ╺╼╼╼╼╼┮╼╼╼
    cell #0002:       ┕╼╼╼

.. code:: python-console

    >>> # Convert the ROI into an xarray dataset
    >>> dataset = roi.to_xarray()
    >>> print(dataset)
    <xarray.Dataset>
    Dimensions:            (frame: 10, y_orig: 520, x_orig: 696, channel: 0,
                            y_resized: 520, x_resized: 696, cell: 2, yx: 2, edge: 4)
    Coordinates:
      * frame              (frame) int64 0 1 2 3 4 5 6 7 8 9
      * y_orig             (y_orig) int16 0 1 2 3 4 5 6 ... 514 515 516 517 518 519
      * x_orig             (x_orig) int16 0 1 2 3 4 5 6 ... 690 691 692 693 694 695
      * channel            (channel) uint8
      * y_resized          (y_resized) int16 0 1 2 3 4 5 ... 514 515 516 517 518 519
      * x_resized          (x_resized) int16 0 1 2 3 4 5 ... 690 691 692 693 694 695
      * cell               (cell) uint16 1 2
      * yx                 (yx) <U1 'y' 'x'
      * edge               (edge) <U2 '-x' '+x' '-y' '+y'
    Data variables:
        img_stack          (frame, y_orig, x_orig) float32 0.6218 0.5829 ... 0.4563
        fluo_stack         (frame, channel, y_orig, x_orig) float64
        seg_stack          (frame, y_resized, x_resized) bool False False ... False
        label_stack        (frame, y_orig, x_orig) uint16 0 0 0 0 0 0 ... 0 0 0 0 0
        mother             (cell) uint16 0 1
        daughter           (cell, frame) uint16 0 0 0 0 0 0 2 0 ... 0 0 0 0 0 0 0 0
        new_pole           (cell, frame, yx) int16 262 344 260 345 ... 348 260 349
        old_pole           (cell, frame, yx) int16 261 366 260 367 ... 334 264 332
        edges              (cell, frame, edge) bool False False ... False False
        fluo               (cell, frame, channel) float32
        length             (cell, frame) float32 26.0 29.0 30.0 ... 20.0 22.77 25.22
        width              (cell, frame) float32 8.0 7.0 7.98 ... 7.0 8.591 7.761
        area               (cell, frame) float32 157.0 168.0 173.0 ... 139.0 144.5
        perimeter          (cell, frame) float32 60.97 66.14 68.97 ... 56.14 60.38
        growthrate_length  (cell, frame) float32 0.1469 0.07147 ... 0.116 0.08876
        growthrate_area    (cell, frame) float32 0.08691 0.04852 ... -0.000908
    Attributes:
        roi_nb:               0
        box:                  {'xtl': 0, 'ytl': 0, 'xbr': 696, 'ybr': 520}
        scaling:              [1. 1.]
        config:               {'presets': '2D', 'models': ('seg', 'track'), 'mode...
        DeLTA_version:        2.0b0.post552+git.9975e8a0.dirty
        file_format_version:  0.1.0
        seg_model_hash:       cbc41b1da67be541fa16e9d8724f7a93e6bc4ffbc4de240ee9a...
        track_model_hash:     97456c17e923a598511c8fc7d1424af5ac67b3f96061756cf08...

The coordinates include the frame number, cell number, pixel positions, and
others.  The data variables correspond to the cell features, and each one is a
rectangular array whose every axis corresponds to one of the coordinates.  They
can behave as numpy arrays, but you can also use the ``.sel`` function to make
extra sure that you don't make indexing mistakes.  For example, to select the
length of the mother cell (cellid 1) at frame 3:

.. code:: python

    ## with .sel
    assert dataset.length.sel(cell=1, frame=3) == 33
    # works in any order
    assert dataset.length.sel(frame=3, cell=1) == 33

    ## numpy style
    # length has size (cell, frame) so we give the cell first
    # but the cell coordinate starts at 1, so we give 0
    assert dataset.length[0, 3] == 33

It is also possible to make partial selections, for example to get the length
of all cells at frame 3:

.. code:: python-console

    >>> dataset.length.sel(frame=3)
    <xarray.DataArray 'length' (cell: 2)>
    array([33., nan], dtype=float32)
    Coordinates:
        frame    int64 3
      * cell     (cell) uint16 1 2

We obtain an array of shape ``(cell,)``, and values ``[33, nan]``.  The ``nan``
is for the daughter cell (cellid 2) which is not present yet at frame 3.

MATLAB
------

To read netCDF files in MATLAB, the three main functions to know are
``ncinfo``, ``ncdisp`` and ``ncreadatt``.

Let's consider for example the file
``tests/data/movie_mothermachine_tif/expected_results/Position000001.nc``.  To
understand its structure, let's use ``ncinfo``:

.. code:: matlabsession

    >> info = ncinfo("Position000001.nc");

    >> % Let's get the ROI names
    >> info.Groups.Name

    ans =

        'roi00'

    ans =

        'roi01'

    [...]

    ans =

        'roi17'

So this position has 18 ROIs labeled from ``roi00`` to ``roi18``.  Let's
display the first one, with the function ``ncdisp``:

.. code:: matlabsession

    >> ncdisp("Position000001.nc", "roi00")

    Source:
               /home/virgile/src/DeLTA/tests/data/movie_mothermachine_tif/expected_results/Position000001.nc
    Format:
               netcdf4
    /roi00/
        Attributes:
                   config              = '{'presets': 'mothermachine', 'models': ('rois', 'seg', 'track'), 'model_file_rois': None, 'model_file_seg': None, 'model_file_track': None, 'target_size_rois': (512, 512), 'target_size_seg': (256, 32), 'target_size_track': (256, 32), 'training_set_rois': None, 'training_set_seg': None, 'training_set_track': None, 'eval_movie': None, 'rotation_correction': True, 'drift_correction': True, 'whole_frame_drift': False, 'crop_windows': False, 'min_roi_area': 500, 'min_cell_area': 20, 'memory_growth_limit': None, 'pipeline_seg_batch': 1, 'pipeline_track_batch': 64, 'pipeline_chunk_size': 64, 'number_of_cores': None}'
                   seg_model_hash      = '170993419adadec9930bf5fc592088f21822260f94407ea8a3a3274e602fc2f4'
                   rois_model_hash     = '759cc9892952c9c52a784d7cfe61531b5b28d54e01b6af3017516047913c61c2'
                   box                 = '{'xtl': 21, 'ytl': 71, 'xbr': 43, 'ybr': 282}'
                   scaling             = [0.82422      0.6875]
                   roi_nb              = 0
                   DeLTA_version       = '2.0b0.post552+git.9975e8a0.dirty'
                   file_format_version = '0.1.0'
                   track_model_hash    = '22386220137936677eb652ee370ad78cc6f887df83ff65888fc74e7666d333aa'
        Dimensions:
                   frame     = 10
                   y_orig    = 211
                   x_orig    = 22
                   channel   = 1
                   y_resized = 256
                   x_resized = 32
                   cell      = 9
                   yx        = 2
                   edge      = 4
        Variables:
            frame
                   Size:       10x1
                   Dimensions: frame
                   Datatype:   int64

            [...]

            cell
                   Size:       9x1
                   Dimensions: cell
                   Datatype:   uint16
            mother
                   Size:       9x1
                   Dimensions: cell
                   Datatype:   uint16
            daughter
                   Size:       10x9
                   Dimensions: frame,cell
                   Datatype:   uint16

            [...]

            length
                   Size:       10x9
                   Dimensions: frame,cell
                   Datatype:   single
                   Attributes:
                               _FillValue = NaN

            [...]

            growthrate_area
                   Size:       10x9
                   Dimensions: frame,cell
                   Datatype:   single
                   Attributes:
                               _FillValue = NaN

You can read the attributes with the function ``ncreadatt``, and the variables
with the function ``ncread``.  A netCDF file behaves like a directory tree: if
we want the variable ``length`` from the group ``roi00``, we access it by
giving ``roi00/length`` to the function ``ncread``:

.. code:: matlabsession

    >> lengths = ncread("Position000001.nc", "roi00/length")

    lengths =

       30.0000   27.0000   24.0000   25.1104   17.0000       NaN       NaN       NaN       NaN
       32.0000   30.0000   28.0000   28.0000   21.0000       NaN       NaN       NaN       NaN
       36.0000   35.0000   30.0000   31.1268       NaN       NaN       NaN       NaN       NaN
       39.0000   18.0000   37.0000       NaN       NaN   18.0000       NaN       NaN       NaN
       43.0000   21.0000   20.0000       NaN       NaN   21.0000   19.0000       NaN       NaN
       25.0000   24.0000   26.0000       NaN       NaN   26.0000       NaN   21.0000       NaN
       27.0000   27.0000   29.0000       NaN       NaN   30.0000       NaN   24.0000       NaN
       30.0000   29.0000       NaN       NaN       NaN   36.0000       NaN   26.0000       NaN
       34.0000   34.0000       NaN       NaN       NaN   19.0000       NaN   30.0000   18.0000
       36.0000   40.0000       NaN       NaN       NaN       NaN       NaN   34.0000       NaN

From the output of ``ncdisp``, we know that the first dimension of this array
corresponds to frames, and the second to cells.  The frame numbers and cell
numbers are respectively available in the same way, with
``ncread("Position000001.nc", "roi00/frames")`` and
``ncread("Position000001.nc", "roi00/cells")``.

Finally, to iterate over ROIs, we can loop over the group names:

.. code:: MATLAB

    for group in info.Groups
        ncread("Position000001.nc", group.Name + "/length")
    end

.. dropdown:: Legacy MAT files (deprecated)

    .. warning::
        This functionality is deprecated and the information below might be outdated.
        We might even remove the possibility to create MAT files in a future release.
        To read DeLTA results with MATLAB, we strongly recommend instead
        reading the ``.nc`` file with the built-in MATLAB functions described above.

    The Matlab MAT file can be loaded in Matlab of course but also in python::

        delta_result = scipy.io.loadmat('PositionXXXXXX.mat', simplify_cells=True)

    The data structure is presented as if loaded in python here. The structure is
    generally the same if the MAT file is loaded in Matlab. The following
    equivalencies can be used for data structures:

    * float32 <=> single
    * dict <=> struct
    * list <=> cell

    Because this was originally written for Matlab only, the data structure is not optimal
    for python, especially when it comes to indexing: A lot of elements use 1-based
    indexing when python indexing is usually 0-based. We try to be as clear as
    possible about these cases here. The notes about 0-based & 1-based indexing can
    generally be ignored if the data is loaded in Matlab.

    For each position, the data structure is as follows:

    .. code-block:: text

        delta_result : dict
        DeLTA data loaded from the MAT file.
        Fields:
        |
        |
        |---moviedimensions : 1D array of int
        |       Dimensions of the experiment movie stored as [Y, X, Channels,
        |       frames].
        |
        |---tiffile : str
        |       Path to the original experiment file. Can be a tif file, nd2, czi, oib
        |       or other Bio-formats files, or a folder with an image sequence.
        |
        |---proc : dict
        |       Dictionary of data relevant to image preprocessing operations.
        |       Fields:
        |       |
        |       |---chambers : 2D array of float32
        |       |       Bounding box of detected chambers in the image, stored as
        |       |       [X top left corner, Y top left corner, width, height].
        |       |       Dimensions are chamber -by- 4.
        |       |
        |       |---rotation : float32
        |       |       Rotation angle to apply to get chambers horizontal, in degrees.
        |       |
        |       |---XYdrift : 2D array of float32
        |               Image drift estimated over time, stored as [Y, X]. Dimensions
        |               are frames -by- 2.
        |
        |---res : list of dict
                List of dictionaries containing data relevant to segmentation and
                lineages for each chamber in the FOV.
                Fields:
                |
                |---labelsstack : 3D array of uint16
                |       Stack of images containing labelled segmentation masks. Each
                |       single cell is uniquely labelled. Labels use 1-based indexing:
                |       In python, Label L in the stack corresponds to cell #L-1 in the
                |       lineage list (see below). The dimensions are frames -by-
                |       U-Net size y -by- U-Net size x.
                |
                |---labelsstack_resized : 3D array of uint16
                |       Same as labelstack above, except it has been resized from the
                |       256 -by- 32 default dimensions of the U-Nets to the original
                |       dimensions of the chamber bounding box. Dimensions are
                |       frames -by- box_height -by- box_width
                |
                |---lineage: list of dict
                        Lineage information for all cells detected and tracked in the
                        chamber.
                        Fields:
                        |
                        |---area : 1D array of float32
                        |       Cell area over time, in pixels.
                        |
                        |---daughters : 1D array of float32
                        |       Daughter cells over time. 0 if no division happened at
                        |       timepoint, otherwise daughters are indexed with 1-based
                        |       indexes: In python, daughter D corresponds to
                        |       cell/item #D-1 in lineage list.
                        |
                        |---edges : array of str
                        |       Which edges of the ROI the cell is currently touching.
                        |
                        |---fluo1/fluo2/fluo3... : 1D array of float32
                        |       Mean fluorescence value over time.
                        |
                        |---frames : 1D array of float32
                        |       Frame numbers where the cell is present.
                        |       Frame numbers use 1-based indexing: In python, Frame
                        |       number F here corresponds to frame/timepoint #F-1 in
                        |       labelsstack for example.
                        |
                        |---growthrate_area : 1D array of float32
                        |       Growth rate over time, based on cell area,
                        |       unit: 1 / frame interval. To convert to
                        |       1 / h (for example), divide these values by
                        |       the time interval between frames in hours.
                        |
                        |---growthrate_length : 1D array of float32
                        |       Growth rate over time, based on cell length,
                        |       unit: 1 / frame interval. To convert to
                        |       1 / h (for example), divide these values by
                        |       the time interval between frames in hours.
                        |
                        |---length : 1D array of float32
                        |       Cell length over time, in pixels.
                        |
                        |---mother : int
                        |       Mother cell number for this cell. 0 if no mother
                        |       detected (eg first timepoint), 1-based indexing
                        |       otherwise: In python, mother M is cell/item #M-1 in
                        |       this lineage list.
                        |
                        |---new_pole : 2D array of float32
                        |       Position of the new pole of the cell, over time.
                        |       Note that positions are given as (Y, X) vectors.
                        |       Dimensions are frames -by- 2.
                        |
                        |---old_pole : 2D array of float32
                        |       Position of the old pole of the cell, over time.
                        |       Note that positions are given as (Y, X) vectors.
                        |       Dimensions are frames -by- 2.
                        |
                        |---perimeter : 1D array of float32
                        |       Perimeter of the cell, in number of pixels.
                        |
                        |---width : 1D array of float32
                                Cell width over time, in pixels.



MP4 movie file
--------------

This one is straight-forward: An MP4 movie file with h264 codecs is saved to
disk for quick checking of outputs quality.
