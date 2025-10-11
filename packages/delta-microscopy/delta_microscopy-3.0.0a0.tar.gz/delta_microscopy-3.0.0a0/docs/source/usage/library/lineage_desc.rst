Lineage and Cells
=================

`Source <https://gitlab.com/delta-microscopy/delta/-/blob/main/delta/lineage.py>`_ |
:class:`API<delta.lineage>`

The lineage module contains three essential classes:
:class:`delta.lineage.Lineage`, which is a collection of
:class:`delta.lineage.Cell` s, themselves composed of :class:`delta.lineage.CellFeatures`.

The purpose of :class:`delta.lineage.Lineage` is to store cell features (length,
area, average fluorescence, etc.) and their lineage tree (who divided into
who).  For example, let's load a position from the DeLTA test suite and see
what the lineage looks like:

.. code:: python-console

    >>> # Load the position
    >>> pos = delta.pipeline.Position.load_netcdf(
    >>>     "tests/data/movie_2D_nd2/test_expected_results/Position000000.nc"
    >>> )
    >>> # Take the lineage from the first (and only) ROI
    >>> lineage = pos.rois[0].lineage
    >>> # Print it
    >>> print(lineage)
    frames    : ..........
    cell #0001: ╺╼╼╼╼╼┮╼╼╼
    cell #0002:       ┕╼╼╼

This compact representation of the lineage shows that there was one cell that
divided into two after a few frames.

The two cells can be found in the ``cells`` dictionary of the lineage, under
their cell ids.  Let's look at them in more detail:

.. code:: python

    mother = lineage.cells[1]
    daughter = lineage.cells[2]

These objects are :class:`delta.lineage.Cell` objects.  They can be queried for
information as following:

.. code:: python

    # The mother has no mother, but the daughter does
    assert mother.motherid is None
    assert daughter.motherid == 1

    # The daughter appeared on frame 6
    assert daughter.first_frame == 6

    # Let's check this information also from the mother's side
    assert mother.daughterid(frame=5) is None
    assert mother.daughterid(frame=6) == 2
    assert mother.daughterid(frame=7) is None

Finally, the method ``features`` returns an object containing all the
morphological features of the cell at a given frame:

.. code:: python-console

    >>> print(mother.features(frame=4))
    CellFeatures(
        new_pole=array([260, 341], dtype=int16),
        old_pole=array([260, 370], dtype=int16),
        length=37.0,
        width=7.0,
        area=200.5,
        perimeter=82.38477,
        fluo=array([], dtype=float32),
        edges='',
        growthrate_length=0.084183276,
        growthrate_area=0.06813244,
    )

.. note::
    A detailed description of the individual features, their signification and
    units, is available in the documentation page of
    :class:`delta.lineage.CellFeatures`.

Individual features can be accessed by fields:

.. code:: python

    assert mother.features(frame=4).area == 200.5


The :class:`delta.lineage.Lineage` class contains several methods that allow to
manipulate the lineage in case of tracking errors.  They are described in the
documentation page for :class:`delta.lineage.Lineage`.

See also our :doc:`results analysis examples <../analysis>`
