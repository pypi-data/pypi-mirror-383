"""
Created on Tue Oct 19 15:01:05 2021.

@author: ooconnor
"""

from pathlib import Path

import cv2
import numpy as np
import numpy.random as npr
import numpy.typing as npt
import pytest
import scipy.optimize as opt
from scipy.special import logit

from delta import imgops, utils
from delta.lineage import CellFeatures

from .utils import rand_mask

LABELS = np.array(
    [
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 0, 0],
        [4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
        [4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0],
        [0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0],
        [0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        [0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    ]
)


@pytest.mark.parametrize(
    "labels, cellids",
    [
        (
            np.array(
                [
                    [1, 1, 1, 0, 2, 2],
                    [1, 1, 1, 0, 0, 2],
                    [0, 0, 0, 0, 2, 2],
                    [3, 3, 0, 0, 0, 0],
                    [3, 3, 0, 5, 5, 0],
                    [0, 0, 0, 0, 5, 0],
                    [0, 4, 4, 0, 5, 5],
                    [0, 0, 0, 0, 0, 5],
                ],
                dtype=np.uint16,
            ),
            [1, 2, 3, 5, 4],
        ),
        (
            np.array(
                [
                    [2, 2, 0, 0, 0],
                    [2, 2, 0, 1, 1],
                    [2, 2, 0, 0, 0],
                    [0, 2, 0, 0, 3],
                    [0, 0, 0, 0, 3],
                    [4, 4, 4, 0, 3],
                    [0, 0, 4, 0, 0],
                    [6, 0, 0, 0, 5],
                    [6, 6, 0, 0, 0],
                ],
                dtype=np.uint16,
            ),
            [2, 1, 3, 4, 6, 5],
        ),
    ],
)
def test_cells_in_frame(labels, cellids):
    actual = utils.cells_in_frame(labels, return_contours=False)
    np.testing.assert_array_equal(actual, cellids)
    actual, contours = utils.cells_in_frame(labels, return_contours=True)
    np.testing.assert_array_equal(actual, cellids)
    assert len(actual) == len(contours)


def test_cell_perimeter():
    mask = np.array(
        [[0, 1, 1], [1, 1, 0], [0, 1, 0]],
        dtype=np.uint8,
    )
    perimeter = 2 + 3 * np.sqrt(2)
    contours = imgops.find_contours(mask)
    np.testing.assert_allclose(utils.cell_perimeter(contours[0]), perimeter)


# %% Eval find_contours


def test_find_poles():
    labels = LABELS
    solution = {
        1: [np.array([0, 0]), np.array([10, 10])],
        2: [np.array([11, 15]), np.array([0, 15])],
        4: [np.array([17, 19]), np.array([12, 0])],
    }
    cellids, contours = utils.cells_in_frame(labels, return_contours=True)
    for cellid, contour in zip(cellids, contours, strict=True):
        poles = utils.find_poles(contour)
        a = np.array_equal(poles, solution[cellid])
        b = np.array_equal(poles, solution[cellid][::-1])
        assert a or b


def test_curvature_positive():
    t = np.linspace(0, 2 * np.pi, 20, endpoint=False)
    contour = np.column_stack((np.cos(t), np.sin(t)))
    curvature = utils.contour_curvature(contour, stride=3)
    assert np.all(curvature > 0)


def test_curvature_negative():
    t = np.linspace(0, 2 * np.pi, 20, endpoint=False)[::-1]
    contour = np.column_stack((np.cos(t), np.sin(t)))
    curvature = utils.contour_curvature(contour, stride=3)
    assert np.all(curvature < 0)


@pytest.mark.parametrize("stride", range(3, 20))
@pytest.mark.parametrize("radius", range(10, 100, 20))
@pytest.mark.parametrize("nb_points", range(12, 30, 3))
def test_curvature_circle(radius, stride, nb_points):
    t = np.linspace(0, 2 * np.pi, nb_points, endpoint=False)
    contour = radius * np.column_stack((np.cos(t), np.sin(t)))
    if 4 * stride > nb_points:
        with pytest.raises(ValueError, match="less than a quarter"):
            utils.contour_curvature(contour, stride=stride)
        return
    curve = utils.contour_curvature(contour, stride=stride)
    assert curve.shape == (nb_points,)
    np.testing.assert_allclose(curve, 1 / radius, rtol=0.6)


@pytest.mark.parametrize("offset_x", [0, 1, 3, 10, 100])
@pytest.mark.parametrize("offset_y", [0, 1, 3, 10, 100])
def test_curvature_cell(offset_x, offset_y):
    # fmt: off
    contour = (
        [62, 0], [61, 1], [60, 1], [59, 1], [58, 2], [57, 2], [56, 3],
        [55, 4], [54, 4], [53, 5], [52, 5], [51, 6], [50, 6], [49, 7],
        [48, 7], [47, 7], [46, 8], [45, 8], [44, 8], [43, 9], [42, 9],
        [41, 9], [40, 10], [39, 10], [38, 10], [37, 11], [36, 11], [35, 11],
        [34, 12], [33, 12], [32, 12], [31, 13], [30, 13], [29, 13], [28, 14],
        [27, 14], [26, 15], [25, 15], [24, 15], [23, 16], [22, 16], [21, 16],
        [20, 17], [19, 17], [18, 17], [17, 17], [16, 18], [15, 18], [14, 18],
        [13, 18], [12, 19], [11, 19], [10, 19], [9, 20], [8, 20], [7, 20],
        [6, 21], [5, 21], [4, 22], [3, 22], [2, 23], [1, 24], [1, 25],
        [0, 26], [0, 27], [0, 28], [0, 29], [0, 30], [1, 31], [1, 32],
        [2, 33], [3, 33], [4, 34], [5, 34], [6, 35], [7, 35], [8, 35],
        [9, 35], [10, 34], [11, 34], [12, 34], [13, 34], [14, 33], [15, 33],
        [16, 33], [17, 32], [18, 32], [19, 32], [20, 31], [21, 31], [22, 31],
        [23, 30], [24, 30], [25, 30], [26, 29], [27, 29], [28, 29], [29, 28],
        [30, 28], [31, 28], [32, 28], [33, 27], [34, 27], [35, 27], [36, 27],
        [37, 26], [38, 26], [39, 26], [40, 25], [41, 25], [42, 25], [43, 24],
        [44, 24], [45, 24], [46, 23], [47, 23], [48, 22], [49, 22], [50, 22],
        [51, 21], [52, 21], [53, 20], [54, 20], [55, 19], [56, 19], [57, 18],
        [58, 18], [59, 17], [60, 17], [61, 16], [62, 15], [63, 14], [64, 13],
        [65, 13], [66, 12], [67, 11], [68, 10], [68, 9], [69, 8], [69, 7],
        [70, 6], [70, 5], [70, 4], [69, 3], [69, 2], [68, 1], [67, 1],
        [66, 0], [65, 0], [64, 0], [63, 0],
    )
    expected = [
        -1.07644230e-01, -8.78647612e-02, -6.72811771e-02, -5.19755443e-02,
        -3.69964430e-02, -2.42554100e-02, -1.35233191e-02, -5.92924009e-03,
         2.37448459e-03, 6.25548366e-03, 1.02815188e-02, 1.33937855e-02,
         1.53811331e-02, 1.68428377e-02, 1.65173825e-02, 1.40343682e-02,
         9.96051451e-03, 8.90248870e-03, 6.56136967e-03, 3.50482235e-03,
         4.79088242e-03, -1.77133582e-04, 1.77133581e-04, -7.40328773e-14,
        -1.77133582e-04, 1.77133581e-04, -4.79088242e-03, -3.50482235e-03,
        -1.87985243e-03, -5.67593972e-03, -3.42955531e-03, -9.96516647e-04,
        -4.10559729e-03, -1.36179371e-03, 1.44140730e-03, 3.32047894e-03,
         4.70647573e-03, 6.20588702e-03, 6.78807592e-03, 1.17503071e-02,
         1.04428358e-02, 8.34532053e-03, 1.08143749e-02, 7.04344797e-03,
         2.57829518e-03, 2.90603499e-03, -2.90603499e-03, -2.57829518e-03,
        -7.04344797e-03, -1.08143749e-02, -1.31220309e-02, -1.83192773e-02,
        -2.81480891e-02, -3.31466889e-02, -4.09017512e-02, -5.13973569e-02,
        -6.47290575e-02, -7.38643953e-02, -8.91829796e-02, -1.04632441e-01,
        -1.26341884e-01, -1.44500999e-01, -1.66429427e-01, -1.90758156e-01,
        -2.03224925e-01, -2.12078313e-01, -2.16185743e-01, -2.09688875e-01,
        -2.07934787e-01, -1.99278212e-01, -1.85083164e-01, -1.67522066e-01,
        -1.58696960e-01, -1.40916657e-01, -1.24945487e-01, -1.12807556e-01,
        -9.72236337e-02, -8.03378574e-02, -6.89613743e-02, -5.52602228e-02,
        -4.22146187e-02, -3.57584333e-02, -2.40528747e-02, -1.49444141e-02,
        -8.53802195e-03, -5.67658391e-03, -2.11109118e-03, -3.57987938e-03,
        -4.68476298e-03, 8.15205552e-14, 4.68476298e-03, 3.57987938e-03,
         2.11109118e-03, 5.67658391e-03, 8.53802195e-03, 4.70571323e-03,
         6.27428431e-03, 7.41917592e-03, 2.10911752e-03, 2.57829518e-03,
         2.90603499e-03, -2.90603499e-03, -2.57829518e-03, -2.10911752e-03,
        -7.41917592e-03, -6.27428431e-03, -9.56821193e-03, -1.18817525e-02,
        -7.72231123e-03, -7.80073649e-03, -6.80888819e-03, -1.04634248e-02,
        -7.33248982e-03, -7.91327487e-03, -7.26057954e-03, -1.09805618e-02,
        -8.28270575e-03, -9.33936087e-03, -9.59047383e-03, -8.58515567e-03,
        -1.05474201e-02, -1.52287027e-02, -1.68756877e-02, -1.62969830e-02,
        -1.85269614e-02, -1.83198634e-02, -1.98960580e-02, -2.09769165e-02,
        -2.26332802e-02, -2.79474431e-02, -2.93165438e-02, -3.39668981e-02,
        -3.75005180e-02, -4.75227380e-02, -5.55601276e-02, -7.01981046e-02,
        -8.57707061e-02, -1.09217523e-01, -1.34676185e-01, -1.68668681e-01,
        -2.04201768e-01, -2.35873694e-01, -2.67451549e-01, -2.84197793e-01,
        -2.83774055e-01, -2.74489248e-01, -2.46788054e-01, -2.21897477e-01,
        -1.91055503e-01, -1.59554464e-01, -1.32481540e-01
    ]
    # fmt: on
    contour = np.array(
        [[c[0] + offset_y, c[1] + offset_x] for c in contour], dtype=np.int32
    )
    curve = utils.contour_curvature(contour, stride=10)
    np.testing.assert_allclose(curve, expected, atol=1e-5)


def test_roi_features():
    poles = {
        1: [np.array([0, 0]), np.array([10, 10])],
        2: [np.array([11, 15]), np.array([0, 15])],
        4: [np.array([17, 19]), np.array([12, 0])],
    }
    fluo = np.expand_dims(LABELS.copy() / 4, axis=0)
    features = utils.roi_features(LABELS, poles, fluo)
    expected = {
        1: CellFeatures(
            new_pole=np.array([0, 0]),
            old_pole=np.array([10, 10]),
            length=14.142135623730953,
            width=3.936814069747925,
            area=41.5,
            perimeter=31.213203072547913,
            fluo=[16383.75],
            edges="-x-y",
            growthrate_length=np.nan,
            growthrate_area=np.nan,
        ),
        2: CellFeatures(
            new_pole=np.array([11, 15]),
            old_pole=np.array([0, 15]),
            length=11.0,
            width=4.7750468254089355,
            area=41.0,
            perimeter=28.82842707633972,
            fluo=[32767.5],
            edges="-y",
            growthrate_length=np.nan,
            growthrate_area=np.nan,
        ),
        4: CellFeatures(
            new_pole=np.array([17, 19]),
            old_pole=np.array([12, 0]),
            length=21.07106781186548,
            width=4.7494049072265625,
            area=72.0,
            perimeter=46.14213538169861,
            fluo=[65535.0],
            edges="-x+x+y",
            growthrate_length=np.nan,
            growthrate_area=np.nan,
        ),
    }
    assert features.keys() == expected.keys()
    for cell, cell_features in expected.items():
        assert cell_features == features[cell]


@pytest.mark.parametrize("seed", range(1000))  # Run it 1000 times
def test_track_poles(seed):
    rng = npr.default_rng(seed)
    # Random previous old pole:
    prev_old = rng.integers(low=0, high=2**15, size=2, dtype=np.int16)
    # Random previous new pole is some small random distance away:
    while True:
        increment = rng.normal(loc=0, scale=20, size=2).astype(np.int16)
        dist = np.linalg.norm(increment)
        if dist < 10:  # At least 10 pixels between poles
            continue
        prev_new = prev_old + increment
        if np.all(prev_new >= 0):
            break

    while True:
        # Simulate whole cell shift:
        cell_shift = rng.gamma(shape=2, scale=2, size=2)

        # Simulate small pole shifts:
        increment = rng.uniform(low=-3, high=3, size=2)
        new_new = prev_new + cell_shift + increment

        # Simulate small pole shifts:
        increment = rng.uniform(low=-3, high=3, size=2)
        new_old = prev_old + cell_shift + increment

        new_new = new_new.astype(np.int16)
        new_old = new_old.astype(np.int16)
        if np.all(new_new >= 0) and np.all(new_old >= 0):
            break

    features = CellFeatures(
        old_pole=new_old,
        new_pole=new_new,
        length=0.0,
        width=0.0,
        area=0.0,
        perimeter=0.0,
        fluo=[],
        edges="",
    )
    if rng.random() < 0.5:
        features.swap_poles()

    feats = utils.track_poles(features, prev_old, prev_new)

    assert np.all(feats.old_pole == new_old)
    assert np.all(feats.new_pole == new_new)


@pytest.mark.parametrize("seed", range(1000))  # Run it 1000 times
def test_division_poles(seed):
    rng = npr.default_rng(seed)
    # Random previous old pole:
    prev_old = rng.integers(low=0, high=2**15, size=2, dtype=np.int16)
    # Random previous new pole is some small random distance away:
    while True:
        increment = rng.normal(loc=0, scale=20, size=2).astype(np.int16)
        dist = np.linalg.norm(increment)
        if dist < 20:  # At least 20 pixels between poles
            continue
        prev_new = prev_old + increment
        if np.all(prev_new >= 0):
            break

    # Generate shift poles to create "current frame"
    while True:
        # Simulate whole cell shift:
        cell_shift = rng.gamma(shape=2, scale=2, size=2)

        # Simulate small pole shifts:
        increment = rng.uniform(low=-3, high=3, size=2)
        daughter_old = prev_new + cell_shift + increment

        # Simulate small pole shifts:
        increment = rng.uniform(low=-3, high=3, size=2)
        mother_old = prev_old + cell_shift + increment

        daughter_old = daughter_old.astype(np.int16)
        mother_old = mother_old.astype(np.int16)
        if np.all(daughter_old >= 0) and np.all(mother_old >= 0):
            break

    # Generate septum and new poles:
    septum = mother_old / 2 + daughter_old / 2

    # Shift by 2 pixels towards mother to get mother's new pole
    sep2mot = 2 * (septum - mother_old) / np.linalg.norm(septum - mother_old)
    mother_new = (mother_old + sep2mot).astype(np.int16)

    # Shift by 2 pixels towards mother to get mother's new pole
    sep2dau = 2 * (septum - daughter_old) / np.linalg.norm(septum - daughter_old)
    daughter_new = (daughter_old + sep2dau).astype(np.int16)

    # Randomly assign poles to the input lists:
    mother = CellFeatures(
        old_pole=mother_old,
        new_pole=mother_new,
        length=0.0,
        width=0.0,
        area=0.0,
        perimeter=0.0,
        fluo=[],
        edges="",
    )
    if rng.random() < 0.5:
        mother.swap_poles()

    daughter = CellFeatures(
        old_pole=daughter_old,
        new_pole=daughter_new,
        length=0.0,
        width=0.0,
        area=0.0,
        perimeter=0.0,
        fluo=[],
        edges="",
    )
    if rng.random() < 0.5:
        daughter.swap_poles()

    if rng.random() > 0.5:
        first_cell_is_mother_t = True
        features1 = mother
        features2 = daughter
    else:
        first_cell_is_mother_t = False
        features2 = mother
        features1 = daughter

    # Run division poles:
    mother_out, daughter_out, first_cell_is_mother = utils.division_poles(
        features1, features2, prev_old, prev_new
    )

    # Assertions:
    assert first_cell_is_mother == first_cell_is_mother_t
    assert np.all(mother_old == mother_out.old_pole)
    assert np.all(mother_new == mother_out.new_pole)
    assert np.all(daughter_old == daughter_out.old_pole)
    assert np.all(daughter_new == daughter_out.new_pole)


# %% Make sure contour coloring and cv2 colormap work
def _base_test_color(max_dots, seed=None):
    # Get random mask and RGB frame:
    mask = rand_mask((2048, 2048), max_dots=max_dots, seed=seed)
    frame = np.repeat(mask[:, :, np.newaxis].astype(np.float32), 3, axis=2)

    # Get cells numbers and contours:
    cells, contours = utils.cells_in_frame(imgops.label_seg(mask), return_contours=True)

    # Get random colors:
    colors = utils.random_colors(cells, seed=seed)

    # Color cells contours:
    for c, cell in enumerate(cells):
        frame = cv2.drawContours(
            frame,
            contours,
            c,
            color=colors[cell],
            thickness=1,
        )

    return mask, frame


def _evaluate_color_nb(mask, frame):
    # Get cell contours:
    contours = imgops.find_contours(mask)

    # Get colors present in frame:
    colors = np.unique(
        np.reshape(frame, (frame.shape[0] * frame.shape[1], frame.shape[2])), axis=0
    )

    # Assert that we have the right nb of colors:
    assert colors.shape[0] == len(contours) + np.unique(mask).shape[0]


@pytest.mark.parametrize("seed", range(5))  # Run it 5 times
@pytest.mark.parametrize("max_dots", [0, 1, 2, 100])
def test_color_contours(max_dots, seed):
    mask, frame = _base_test_color(max_dots, seed=seed)
    _evaluate_color_nb(mask, frame)


# %% Test XPReader


class TestXPReader:
    data_path: Path = Path(__file__).parent / "data"

    def test_movie_2D_tif(self):  # noqa: N802
        movie_path = self.data_path / "movie_2D_tif/Position{p}Channel{c}Frame{t}.tif"

        # Init reader
        xpreader = utils.XPReader(movie_path)

        assert xpreader.positions == (1,)
        assert xpreader.channels == (1,)
        assert xpreader.channel_names is None
        assert xpreader.frames == range(1, 21)

    def test_moma_tif_xpreader(self):
        movie_path = (
            self.data_path
            / "movie_mothermachine_tif/Position{p}Channel{c}Frames{t}.tif"
        )

        xpreader = utils.XPReader(movie_path)

        assert xpreader.positions == (1, 2)
        assert xpreader.channels == (1, 2)
        assert xpreader.channel_names is None
        assert xpreader.frames == range(1, 11)

    def test_moma_2D_nd2(self):  # noqa: N802
        movie_path = self.data_path / "movie_2D_nd2/test.nd2"

        xpreader = utils.XPReader(movie_path)

        assert xpreader.positions == (0,)
        assert xpreader.channels == (0,)
        assert xpreader.channel_names == ("Trans",)
        assert xpreader.frames == range(10)


UNTRACKED_LABELS = np.array(
    [
        [0, 0, 1, 0],
        [0, 2, 1, 0],
        [0, 2, 1, 0],
        [0, 2, 3, 3],
    ],
    dtype=np.uint16,
)

TRACKING_OUTPUTS = logit(
    np.array(
        [
            [  # Cell tracked to label 2
                [0.00, 0.06, 0.00, 0.00],
                [0.02, 0.72, 0.10, 0.01],
                [0.03, 0.68, 0.06, 0.02],
                [0.12, 0.89, 0.04, 0.00],
            ],
            [  # Cell tracked to label 1
                [0.00, 0.07, 0.43, 0.00],
                [0.00, 0.02, 0.78, 0.13],
                [0.01, 0.10, 0.82, 0.07],
                [0.00, 0.25, 0.92, 0.04],
            ],
        ]
    )
)


def test_tracking_scores_no_old_cells():
    labels = UNTRACKED_LABELS
    outputs = np.zeros((0, labels.shape[0], labels.shape[1]), dtype=np.float32)
    boxes = [utils.CroppingBox.full(labels) for _ in range(len(outputs))]
    scores = utils.tracking_scores(labels, outputs, boxes)
    np.testing.assert_allclose(scores, np.zeros((0, 3), dtype=np.float32))


def test_tracking_scores_no_new_cells():
    labels = np.zeros_like(UNTRACKED_LABELS)
    outputs = TRACKING_OUTPUTS
    boxes = [utils.CroppingBox.full(labels) for _ in range(len(outputs))]
    scores = utils.tracking_scores(labels, outputs, boxes)
    np.testing.assert_allclose(scores, np.zeros((2, 0), dtype=np.float32))


def test_tracking_scores_no_hits():
    labels = UNTRACKED_LABELS
    outputs = TRACKING_OUTPUTS - 100
    boxes = [utils.CroppingBox.full(labels) for _ in range(len(outputs))]
    scores = utils.tracking_scores(labels, outputs, boxes)
    np.testing.assert_allclose(scores, [[0, 0, 0], [0, 0, 0]])


def test_tracking_scores():
    labels = UNTRACKED_LABELS
    outputs = TRACKING_OUTPUTS
    boxes = [utils.CroppingBox.full(labels) for _ in range(len(outputs))]
    scores = utils.tracking_scores(labels, outputs, boxes)
    np.testing.assert_allclose(scores, [[2 / 3, 1, 0], [1, 2 / 3, 1 / 2]])


def test_cell_fluo():
    fluo_frames = np.array(
        [
            [
                [0, 1, 2, 3, 4],
                [5, 6, 7, 8, 9],
                [10, 11, 12, 13, 14],
                [15, 16, 17, 18, 19],
            ],
            [
                [100, 101, 102, 103, 104],
                [105, 106, 107, 108, 109],
                [110, 111, 112, 113, 114],
                [115, 116, 117, 118, 119],
            ],
        ],
        dtype=np.float32,
    )
    mask = np.array(
        [
            [False, True, True, True, False],
            [False, False, True, False, False],
            [False, False, True, True, False],
            [False, True, True, False, False],
        ],
        dtype=bool,
    )
    fluos = utils.cell_fluo(fluo_frames, mask)
    expected = (1 + 2 + 3 + 7 + 12 + 13 + 16 + 17) / 8
    np.testing.assert_allclose(fluos, [expected, expected + 100])


def test_attributions_smoketest():
    scores = np.array(
        [
            [0.45, 0.05, 0.10, 0.15, 0.25],
            [0.40, 0.10, 0.30, 0.10, 0.10],
            [0.30, 0.15, 0.25, 0.15, 0.15],
        ]
    )
    attributions = np.array(
        [
            [True, False, False, False, True],
            [False, False, True, False, False],
            [False, False, False, False, False],
        ]
    )
    np.testing.assert_equal(utils.attributions(scores), attributions)


def test_attributions_dont_attribute_three():
    scores = np.array([[1.0, 1.0, 1.0]])
    attributions = utils.attributions(scores)
    assert attributions.sum() == 2


def attributions_linear(scores: npt.NDArray[np.float32]) -> npt.NDArray[np.bool_]:
    """Do the same as utils.attributions but with linear programming."""
    scores = np.array(scores)
    nb_old, nb_new = scores.shape
    for iold in range(nb_old):
        worst = np.argsort(scores[iold, :])[:-2]
        scores[iold, worst] = -0.01
    scores[scores < 0.2] = -0.01
    c = scores.flatten()
    A_ub_ = []  # noqa: N806
    for inew in range(nb_new):
        a = np.zeros_like(scores)
        a[:, inew] = 1
        A_ub_.append(a.flatten())
    for iold in range(nb_old):
        a = np.zeros_like(scores)
        a[iold, :] = 1
        A_ub_.append(a.flatten())
    A_ub = np.vstack(A_ub_)  # noqa: N806
    b_ub = [1] * nb_new + [2] * nb_old
    res = opt.linprog(-c, A_ub=A_ub, b_ub=b_ub, bounds=(0, 1), method="highs")
    return np.asarray(res.x.reshape((nb_old, nb_new)) > 0.5)


@pytest.mark.parametrize("seed", range(100))  # Run it 100 times
def test_attributions(seed):
    rng = np.random.default_rng(seed)
    nb_old, nb_new = rng.integers(low=1, high=100, size=2)
    scores = rng.exponential(size=(nb_old, nb_new))
    attributions = utils.attributions(scores)
    attributions_lin = attributions_linear(scores)
    np.testing.assert_equal(attributions, attributions_lin)
