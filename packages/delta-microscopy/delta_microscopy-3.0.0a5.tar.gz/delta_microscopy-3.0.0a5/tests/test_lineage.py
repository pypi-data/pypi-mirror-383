import copy
import tempfile
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import numpy.testing as npt
import pytest

import delta

# ruff: noqa: E741

DATA_PATH = Path(__file__).parent / "data"


FAKE_FEATURES = delta.lineage.CellFeatures(
    new_pole=np.array([1, 1]),
    old_pole=np.array([0, 0]),
    length=0.0,
    area=0.0,
    perimeter=0.0,
    width=0.0,
    fluo=[],
    edges="",
)


def test_str_lineage():
    l = delta.lineage.Lineage()
    l.create(0, FAKE_FEATURES)
    while l.cells[1].last_frame < 3:
        l.extend(1, FAKE_FEATURES)
    l.create(1, FAKE_FEATURES, motherid=1)
    while l.cells[2].last_frame < 5:
        l.extend(2, FAKE_FEATURES)
    l.create(2, FAKE_FEATURES, motherid=1)
    while l.cells[3].last_frame < 4:
        l.extend(3, FAKE_FEATURES)
    l.create(3, FAKE_FEATURES, motherid=2)
    while l.cells[4].last_frame < 6:
        l.extend(4, FAKE_FEATURES)
    assert str(l) == (
        "frames    : .......\n"
        "cell #0001: ╺┮┮╼\n"
        "cell #0003:  │┕╼╼\n"
        "cell #0002:  ┕╼┮╼╼\n"
        "cell #0004:    ┕╼╼╼"
    )


def test_onecell():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(4):
        l.extend(rootid, FAKE_FEATURES)
    assert len(l.cells) == 1
    assert l.cells[1].motherid is None
    assert l.cells[1].first_frame == 0
    assert l.cells[1].last_frame == 4
    assert l.cells[1]._daughterids == [None] * 5


def test_extend():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    assert len(l.cells) == 1
    assert l.cells[1].first_frame == 0
    assert l.cells[1].last_frame == 0
    l.extend(rootid, FAKE_FEATURES)
    assert len(l.cells) == 1
    assert l.cells[1].first_frame == 0
    assert l.cells[1].last_frame == 1


def test_merge():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(4):
        l.extend(rootid, FAKE_FEATURES)
    cellid = l.create(5, FAKE_FEATURES)
    for _ in range(4):
        l.extend(cellid, FAKE_FEATURES)
    assert len(l.cells) == 2
    assert l.cells[rootid].first_frame == 0
    assert l.cells[rootid].last_frame == 4
    assert l.cells[cellid].first_frame == 5
    assert l.cells[cellid].last_frame == 9
    l.merge(cellid, rootid)
    assert len(l.cells) == 1
    assert l.cells[rootid].first_frame == 0
    assert l.cells[rootid].last_frame == 9


def test_merge_cell_with_mother():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(4):
        l.extend(rootid, FAKE_FEATURES)
    motherid = l.create(0, FAKE_FEATURES)
    for _ in range(5):
        l.extend(motherid, FAKE_FEATURES)
    cellid = l.create(5, FAKE_FEATURES, motherid=motherid)
    for _ in range(4):
        l.extend(cellid, FAKE_FEATURES)
    assert len(l.cells) == 3
    assert l.cells[rootid].first_frame == 0
    assert l.cells[rootid].last_frame == 4
    assert l.cells[rootid].motherid is None
    assert l.cells[cellid].first_frame == 5
    assert l.cells[cellid].last_frame == 9
    assert l.cells[cellid].motherid == motherid
    assert l.cells[motherid].daughterid(5) == cellid
    l.merge(cellid, rootid)
    assert len(l.cells) == 2
    assert l.cells[rootid].first_frame == 0
    assert l.cells[rootid].last_frame == 9
    assert l.cells[rootid].motherid is None
    assert l.cells[motherid].daughterid(5) is None


def test_merge_cell_with_daughter():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(4):
        l.extend(rootid, FAKE_FEATURES)
    cellid = l.create(5, FAKE_FEATURES)
    for _ in range(4):
        l.extend(cellid, FAKE_FEATURES)
    daughterid = l.create(7, FAKE_FEATURES, motherid=cellid)
    assert len(l.cells) == 3
    assert l.cells[rootid].first_frame == 0
    assert l.cells[rootid].last_frame == 4
    assert l.cells[cellid].first_frame == 5
    assert l.cells[cellid].last_frame == 9
    assert l.cells[daughterid].first_frame == 7
    assert l.cells[daughterid].last_frame == 7
    assert l.cells[daughterid].motherid == cellid
    l.merge(cellid, rootid)
    assert len(l.cells) == 2
    assert l.cells[rootid].first_frame == 0
    assert l.cells[rootid].last_frame == 9
    assert l.cells[daughterid].first_frame == 7
    assert l.cells[daughterid].last_frame == 7
    assert l.cells[daughterid].motherid == rootid


def test_split():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(9):
        l.extend(rootid, FAKE_FEATURES)
    assert len(l.cells) == 1
    assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 9)
    assert l.cells[rootid].motherid is None
    assert l.cells[rootid]._daughterids == [None] * 10
    assert l.cells[rootid]._features == [FAKE_FEATURES] * 10
    cellid = l.split(rootid, frame=5)
    assert len(l.cells) == 2
    assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 4)
    assert (l.cells[cellid].first_frame, l.cells[cellid].last_frame) == (5, 9)
    assert l.cells[rootid].motherid is None
    assert l.cells[cellid].motherid is None
    assert l.cells[rootid]._daughterids == [None] * 5
    assert l.cells[cellid]._daughterids == [None] * 5
    assert l.cells[rootid]._features == [FAKE_FEATURES] * 5
    assert l.cells[cellid]._features == [FAKE_FEATURES] * 5


def test_split_cell_with_daughter_after_split():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(9):
        l.extend(rootid, FAKE_FEATURES)
    daughterid = l.create(7, FAKE_FEATURES, motherid=rootid)
    assert len(l.cells) == 2
    assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 9)
    assert (l.cells[daughterid].first_frame, l.cells[daughterid].last_frame) == (7, 7)
    assert l.cells[rootid].motherid is None
    assert l.cells[daughterid].motherid == rootid
    assert l.cells[rootid]._daughterids == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        2,
        None,
        None,
    ]
    assert l.cells[daughterid]._daughterids == [None]
    cellid = l.split(rootid, frame=5)
    assert len(l.cells) == 3
    assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 4)
    assert (l.cells[cellid].first_frame, l.cells[cellid].last_frame) == (5, 9)
    assert (l.cells[daughterid].first_frame, l.cells[daughterid].last_frame) == (7, 7)
    assert l.cells[rootid].motherid is None
    assert l.cells[cellid].motherid is None
    assert l.cells[daughterid].motherid == cellid
    assert l.cells[rootid]._daughterids == [None] * 5
    assert l.cells[cellid]._daughterids == [None, None, 2, None, None]
    assert l.cells[daughterid]._daughterids == [None]


def test_split_cell_with_daughter_during_split():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(9):
        l.extend(rootid, FAKE_FEATURES)
    daughterid = l.create(5, FAKE_FEATURES, motherid=rootid)
    assert len(l.cells) == 2
    assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 9)
    assert (l.cells[daughterid].first_frame, l.cells[daughterid].last_frame) == (5, 5)
    assert l.cells[rootid].motherid is None
    assert l.cells[daughterid].motherid == rootid
    assert l.cells[rootid]._daughterids == [
        None,
        None,
        None,
        None,
        None,
        2,
        None,
        None,
        None,
        None,
    ]
    assert l.cells[daughterid]._daughterids == [None]
    with pytest.raises(delta.lineage.CellAlreadyHasDaughterError):
        _cellid = l.split(rootid, frame=5)
    # What would happen if we would allow the split
    # assert len(l.cells) == 3
    # assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 4)
    # assert (l.cells[cellid].first_frame, l.cells[cellid].last_frame) == (5, 9)
    # assert (l.cells[daughterid].first_frame, l.cells[daughterid].last_frame) == (5, 5)
    # assert l.cells[rootid].motherid is None
    # assert l.cells[cellid].motherid is None
    # assert l.cells[daughterid].motherid == cellid
    # assert l.cells[rootid]._daughterids == [None] * 5
    # assert l.cells[cellid]._daughterids == [2, None, None, None, None]
    # assert l.cells[daughterid]._daughterids == [None]


def test_split_cell_with_daughter_before_split():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    for _ in range(9):
        l.extend(rootid, FAKE_FEATURES)
    daughterid = l.create(2, FAKE_FEATURES, motherid=rootid)
    assert len(l.cells) == 2
    assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 9)
    assert (l.cells[daughterid].first_frame, l.cells[daughterid].last_frame) == (2, 2)
    assert l.cells[rootid].motherid is None
    assert l.cells[daughterid].motherid == rootid
    assert l.cells[rootid]._daughterids == [
        None,
        None,
        2,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    assert l.cells[daughterid]._daughterids == [None]
    cellid = l.split(rootid, frame=5)
    assert len(l.cells) == 3
    assert (l.cells[rootid].first_frame, l.cells[rootid].last_frame) == (0, 4)
    assert (l.cells[cellid].first_frame, l.cells[cellid].last_frame) == (5, 9)
    assert (l.cells[daughterid].first_frame, l.cells[daughterid].last_frame) == (2, 2)
    assert l.cells[rootid].motherid is None
    assert l.cells[cellid].motherid is None
    assert l.cells[daughterid].motherid == rootid
    assert l.cells[rootid]._daughterids == [None, None, 2, None, None]
    assert l.cells[cellid]._daughterids == [None] * 5
    assert l.cells[daughterid]._daughterids == [None]


def test_adopt():
    l = delta.lineage.Lineage()
    rootid = l.create(0, FAKE_FEATURES)
    l.extend(rootid, FAKE_FEATURES)
    daughterid = l.create(1, FAKE_FEATURES)
    assert len(l.cells) == 2
    assert l.cells[rootid].motherid is None
    assert l.cells[daughterid].motherid is None
    assert l.cells[rootid].daughterid(0) is None
    assert l.cells[rootid].daughterid(1) is None
    assert l.cells[daughterid].daughterid(1) is None
    l.adopt(daughterid, rootid)
    assert len(l.cells) == 2
    assert l.cells[rootid].motherid is None
    assert l.cells[daughterid].motherid == rootid
    assert l.cells[rootid].daughterid(0) is None
    assert l.cells[rootid].daughterid(1) == daughterid
    assert l.cells[daughterid].daughterid(1) is None
    l.adopt(daughterid, None)
    assert len(l.cells) == 2
    assert l.cells[rootid].motherid is None
    assert l.cells[daughterid].motherid is None
    assert l.cells[rootid].daughterid(0) is None
    assert l.cells[rootid].daughterid(1) is None
    assert l.cells[daughterid].daughterid(1) is None


def test_pivot():
    l = delta.lineage.Lineage()
    l.create(0, FAKE_FEATURES)
    while l.cells[1].last_frame < 3:
        l.extend(1, FAKE_FEATURES)
    l.create(1, FAKE_FEATURES, motherid=1)
    while l.cells[2].last_frame < 5:
        l.extend(2, FAKE_FEATURES)
    l.create(2, FAKE_FEATURES, motherid=1)
    while l.cells[3].last_frame < 4:
        l.extend(3, FAKE_FEATURES)
    l.create(3, FAKE_FEATURES, motherid=2)
    while l.cells[4].last_frame < 6:
        l.extend(4, FAKE_FEATURES)
    assert len(l.cells) == 4
    assert (l.cells[1].first_frame, l.cells[1].last_frame) == (0, 3)
    assert (l.cells[2].first_frame, l.cells[2].last_frame) == (1, 5)
    assert (l.cells[3].first_frame, l.cells[3].last_frame) == (2, 4)
    assert (l.cells[4].first_frame, l.cells[4].last_frame) == (3, 6)
    assert [l.cells[cellid].motherid for cellid in range(1, 5)] == [None, 1, 1, 2]
    l.pivot(2)
    assert len(l.cells) == 4
    assert (l.cells[1].first_frame, l.cells[1].last_frame) == (0, 5)
    assert (l.cells[2].first_frame, l.cells[2].last_frame) == (1, 3)
    assert (l.cells[3].first_frame, l.cells[3].last_frame) == (2, 4)
    assert (l.cells[4].first_frame, l.cells[4].last_frame) == (3, 6)
    assert [l.cells[cellid].motherid for cellid in range(1, 5)] == [None, 1, 2, 1]


def test_swap_poles():
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    while l.cells[rootid].last_frame < 10:
        l.extend(rootid, copy.copy(FAKE_FEATURES))
    cell = l.cells[rootid]
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(10)
    )
    l.swap_poles(rootid)
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([1, 1]))
        for frame in range(10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([0, 0]))
        for frame in range(10)
    )


def test_swap_poles_frame():
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    while l.cells[rootid].last_frame < 10:
        l.extend(rootid, copy.copy(FAKE_FEATURES))
    cell = l.cells[rootid]
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(10)
    )
    l.swap_poles(rootid, 5)
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(5)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(5)
    )
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([1, 1]))
        for frame in range(5, 10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([0, 0]))
        for frame in range(5, 10)
    )


def test_swap_poles_frame_daughter_before():
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    while l.cells[rootid].last_frame < 10:
        l.extend(rootid, copy.copy(FAKE_FEATURES))
    daughterid = l.create(2, copy.copy(FAKE_FEATURES), motherid=rootid)
    cell = l.cells[rootid]
    daughter = l.cells[daughterid]
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(10)
    )
    assert (daughter.first_frame, daughter.last_frame) == (2, 2)
    assert all(
        np.array_equal(daughter.features(frame).old_pole, np.array([0, 0]))
        for frame in range(2, 3)
    )
    assert all(
        np.array_equal(daughter.features(frame).new_pole, np.array([1, 1]))
        for frame in range(2, 3)
    )
    l.swap_poles(rootid, 5)
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(5)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(5)
    )
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([1, 1]))
        for frame in range(5, 10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([0, 0]))
        for frame in range(5, 10)
    )
    assert (daughter.first_frame, daughter.last_frame) == (2, 2)
    assert all(
        np.array_equal(daughter.features(frame).old_pole, np.array([0, 0]))
        for frame in range(2, 3)
    )
    assert all(
        np.array_equal(daughter.features(frame).new_pole, np.array([1, 1]))
        for frame in range(2, 3)
    )


def test_swap_poles_frame_daughter_after():
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    while l.cells[rootid].last_frame < 10:
        l.extend(rootid, copy.copy(FAKE_FEATURES))
    daughterid = l.create(7, copy.copy(FAKE_FEATURES), motherid=rootid)
    cell = l.cells[rootid]
    daughter = l.cells[daughterid]
    assert (cell.first_frame, cell.last_frame) == (0, 10)
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(10)
    )
    assert (daughter.first_frame, daughter.last_frame) == (7, 7)
    assert all(
        np.array_equal(daughter.features(frame).old_pole, np.array([0, 0]))
        for frame in range(7, 8)
    )
    assert all(
        np.array_equal(daughter.features(frame).new_pole, np.array([1, 1]))
        for frame in range(7, 8)
    )
    l.swap_poles(rootid, 5)
    assert (cell.first_frame, cell.last_frame) == (0, 7)
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in [0, 1, 2, 3, 4, 7]
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in [0, 1, 2, 3, 4, 7]
    )
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([1, 1]))
        for frame in [5, 6]
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([0, 0]))
        for frame in [5, 6]
    )
    daughter = l.cells[daughterid]
    assert (daughter.first_frame, daughter.last_frame) == (7, 10)
    assert all(
        np.array_equal(daughter.features(frame).old_pole, np.array([0, 0]))
        for frame in range(7, 11)
    )
    assert all(
        np.array_equal(daughter.features(frame).new_pole, np.array([1, 1]))
        for frame in range(7, 11)
    )


def test_swap_poles_frame_daughter_during():
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    while l.cells[rootid].last_frame < 10:
        l.extend(rootid, copy.copy(FAKE_FEATURES))
    daughterid = l.create(5, copy.copy(FAKE_FEATURES), motherid=rootid)
    cell = l.cells[rootid]
    daughter = l.cells[daughterid]
    assert (cell.first_frame, cell.last_frame) == (0, 10)
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(10)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(10)
    )
    assert (daughter.first_frame, daughter.last_frame) == (5, 5)
    assert all(
        np.array_equal(daughter.features(frame).old_pole, np.array([0, 0]))
        for frame in range(5, 6)
    )
    assert all(
        np.array_equal(daughter.features(frame).new_pole, np.array([1, 1]))
        for frame in range(5, 6)
    )
    l.swap_poles(rootid, 5)
    assert (cell.first_frame, cell.last_frame) == (0, 10)
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([0, 0]))
        for frame in range(5)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([1, 1]))
        for frame in range(5)
    )
    assert all(
        np.array_equal(cell.features(frame).old_pole, np.array([1, 1]))
        for frame in range(5, 11)
    )
    assert all(
        np.array_equal(cell.features(frame).new_pole, np.array([0, 0]))
        for frame in range(5, 11)
    )
    daughter = l.cells[daughterid]
    assert (daughter.first_frame, daughter.last_frame) == (5, 5)
    assert all(
        np.array_equal(daughter.features(frame).old_pole, np.array([0, 0]))
        for frame in range(5, 6)
    )
    assert all(
        np.array_equal(daughter.features(frame).new_pole, np.array([1, 1]))
        for frame in range(5, 6)
    )


def test_growthrate_onecell_oneframe():
    # rootid is present only on frame 0,
    # we cannot compute its growthrate so we expect nan
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    l.cells[rootid].features(0).area = 3.7
    l.compute_growthrates("area")
    npt.assert_allclose(
        l.cells[rootid].features(0).growthrate_area, np.nan, equal_nan=True
    )

    # daughterid is present only on frame 1,
    # but it has a mother so we can compute its growthrate
    l.extend(rootid, copy.copy(FAKE_FEATURES))
    daughterid = l.create(1, copy.copy(FAKE_FEATURES), motherid=rootid)
    l.cells[rootid].features(1).area = 3.7 * np.exp(0.7) / 2.0
    l.cells[daughterid].features(1).area = 3.7 * np.exp(0.7) / 2.0
    l.compute_growthrates("area")
    npt.assert_allclose(l.cells[daughterid].features(1).growthrate_area, 0.7)


def test_growthrate_onecell_twoframes():
    # rootid is present only on frames 0 and 1
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    l.extend(rootid, copy.copy(FAKE_FEATURES))
    l.cells[rootid].features(0).area = 3.7
    l.cells[rootid].features(1).area = 3.7 * np.exp(0.8)
    l.compute_growthrates("area")
    npt.assert_allclose(l.cells[rootid].features(0).growthrate_area, 0.8)
    npt.assert_allclose(l.cells[rootid].features(1).growthrate_area, 0.8)


def test_growthrate_onecell_threeframes():
    # rootid is present on frames 0 to 2
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    l.extend(rootid, copy.copy(FAKE_FEATURES))
    l.extend(rootid, copy.copy(FAKE_FEATURES))
    l.cells[rootid].features(0).area = 3.7
    l.cells[rootid].features(1).area = 3.7 * np.exp(0.8)
    l.cells[rootid].features(2).area = 3.7 * np.exp(0.8) * np.exp(0.8)
    l.compute_growthrates("area")
    npt.assert_allclose(l.cells[rootid].features(0).growthrate_area, 0.8)
    npt.assert_allclose(l.cells[rootid].features(1).growthrate_area, 0.8)
    npt.assert_allclose(l.cells[rootid].features(2).growthrate_area, 0.8)


def test_growthrate_onecell_constant():
    # rootid is present on cells 0 to 5
    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    for _ in range(5):
        l.extend(rootid, copy.copy(FAKE_FEATURES))
    for frame in l.cells[rootid].frames:
        l.cells[rootid].features(frame).area = np.exp(0.8 * frame)
    l.compute_growthrates("area")
    for frame in l.cells[rootid].frames:
        npt.assert_allclose(l.cells[rootid].features(frame).growthrate_area, 0.8)


def test_growthrate_division_constant():
    # rootid has a growth rate of 0.8 per frame
    # daughterid has a growth rate of 0.7 per frame
    # with increasing smoothing, the growth rate of rootid
    # should stay the same while the growth rate of daughterid
    # should increase towards rootid's growth rate

    l = delta.lineage.Lineage()
    rootid = l.create(0, copy.copy(FAKE_FEATURES))
    for _ in range(5):
        l.extend(rootid, copy.copy(FAKE_FEATURES))
    daughterid = l.create(3, copy.copy(FAKE_FEATURES), motherid=rootid)
    for _ in range(5):
        l.extend(daughterid, copy.copy(FAKE_FEATURES))
    l.cells[rootid].features(0).area = 3.7
    for frame in l.cells[rootid].frames:
        l.cells[rootid].features(frame).area = (
            3.7 * np.exp(0.8 * frame) * (1.0 if frame < 3 else 0.3)
        )
    for frame in l.cells[daughterid].frames:
        l.cells[daughterid].features(frame).area = (
            3.7 * np.exp(0.8 * 3 + 0.7 * (frame - 3)) * 0.7
        )

    l.compute_growthrates("area", smooth_frames=3)
    for frame in l.cells[rootid].frames:
        npt.assert_allclose(l.cells[rootid].features(frame).growthrate_area, 0.8)
    grs = [0.75, 0.7, 0.7, 0.7, 0.7, 0.7]
    for frame, gr in zip(l.cells[daughterid].frames, grs, strict=True):
        npt.assert_allclose(l.cells[daughterid].features(frame).growthrate_area, gr)

    l.compute_growthrates("area", smooth_frames=5)
    for frame in l.cells[rootid].frames:
        npt.assert_allclose(l.cells[rootid].features(frame).growthrate_area, 0.8)
    grs = [0.75, 0.72, 0.7, 0.7, 0.7, 0.7]
    for frame, gr in zip(l.cells[daughterid].frames, grs, strict=True):
        npt.assert_allclose(l.cells[daughterid].features(frame).growthrate_area, gr)

    l.compute_growthrates("area", smooth_frames=7)
    for frame in l.cells[rootid].frames:
        npt.assert_allclose(l.cells[rootid].features(frame).growthrate_area, 0.8)
    grs = [0.75, 0.7285714285714288] + [0.7107142857142859] * 4
    for frame, gr in zip(l.cells[daughterid].frames, grs, strict=True):
        npt.assert_allclose(l.cells[daughterid].features(frame).growthrate_area, gr)

    l.compute_growthrates("area", smooth_frames=9)
    for frame in l.cells[rootid].frames:
        npt.assert_allclose(l.cells[rootid].features(frame).growthrate_area, 0.8)
    grs = [0.7333333333333335] * 6
    for frame, gr in zip(l.cells[daughterid].frames, grs, strict=True):
        npt.assert_allclose(l.cells[daughterid].features(frame).growthrate_area, gr)


def test_plot():
    path = DATA_PATH / "movie_mothermachine_tif/expected_results/Position000001.nc"
    pos = delta.pipeline.Position.load_netcdf(path)
    fig, axs = plt.subplots(1, len(pos.rois), figsize=(20, 6), sharey=True)
    if len(pos.rois) == 1:
        pos.rois[0].lineage.plot(ax=axs)
    else:
        for roi, ax in zip(pos.rois, axs, strict=True):
            roi.lineage.plot(ax=ax)

    with tempfile.TemporaryDirectory() as tmpdir:
        savepath = Path(tmpdir) / "figure.png"
        fig.savefig(savepath, bbox_inches="tight")
        actual = cv2.imread(savepath.as_posix(), cv2.IMREAD_ANYDEPTH)

    expected = cv2.imread(path.with_suffix(".png").as_posix(), cv2.IMREAD_ANYDEPTH)

    npt.assert_array_equal(actual, expected)
