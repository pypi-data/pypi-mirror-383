from pathlib import Path

import cv2
import numpy as np
import numpy.random as npr
import pytest

from delta import imgops

from .utils import rand_mask


class TestCroppingBox:
    @staticmethod
    @pytest.mark.parametrize("dimx", [0, 1, 2, 5])
    @pytest.mark.parametrize("dimy", [0, 1, 2, 5])
    def test_croppingbox_full(dimx, dimy):
        img = np.zeros((dimy, dimx))
        box = imgops.CroppingBox.full(img)
        assert box == imgops.CroppingBox(xtl=0, ytl=0, xbr=dimx, ybr=dimy)

    @staticmethod
    @pytest.mark.parametrize("xtl", [-1, 0])
    @pytest.mark.parametrize("xbr", [20, 21])
    @pytest.mark.parametrize("ytl", [-1, 0])
    @pytest.mark.parametrize("ybr", [10, 11])
    def test_croppingbox_full_img_crop_patch(xtl, xbr, ytl, ybr):
        rng = npr.default_rng(0)
        img = rng.random((10, 20))
        box = imgops.CroppingBox(xtl=xtl, xbr=xbr, ytl=ytl, ybr=ybr)
        patch = box.crop(img)
        assert patch.shape == box.shape
        patched_img = box.patch(np.zeros_like(img), patch)
        np.testing.assert_array_equal(patched_img, img)

    @staticmethod
    @pytest.mark.parametrize(
        "xtl, xbr, ytl, ybr",
        [
            # inside
            (2, 16, 3, 7),
            (12, 16, 3, 7),
            # corners
            (-5, 4, -10, 2),
            (5, 24, -10, 2),
            (-5, 4, 6, 22),
            (5, 24, 6, 22),
            # edges
            (-5, 24, -10, 2),
            (-5, 24, 6, 22),
            (-5, 4, -10, 22),
            (5, 24, -10, 22),
        ],
    )
    def test_croppingbox_partial_crop_patch(xtl, xbr, ytl, ybr):
        rng = npr.default_rng(0)
        img = rng.random((10, 20))
        box = imgops.CroppingBox(xtl=xtl, xbr=xbr, ytl=ytl, ybr=ybr)
        patch = box.crop(img)
        assert patch.shape == box.shape
        patched_img = box.patch(np.array(img), patch)
        np.testing.assert_array_equal(patched_img, img)

    @staticmethod
    def test_tracking_box():
        contour = np.array([[[50, 20]], [[60, 20]], [[60, 30]], [[50, 30]]])
        cb = imgops.CroppingBox.tracking_box(contour, (40, 40))
        assert cb == imgops.CroppingBox(xtl=35, ytl=5, xbr=75, ybr=45)
        cb = imgops.CroppingBox.tracking_box(contour, (50, 40))
        assert cb == imgops.CroppingBox(xtl=35, ytl=0, xbr=75, ybr=50)
        cb = imgops.CroppingBox.tracking_box(contour, (60, 40))
        assert cb == imgops.CroppingBox(xtl=35, ytl=-5, xbr=75, ybr=55)

    @staticmethod
    def test_cropping_boxes_resize():
        old_shape = (200, 200)
        new_shape = (400, 100)
        image = np.zeros((200, 200), dtype=np.uint8)
        xtl, xbr, ytl, ybr = 40, 120, 50, 150
        image[ytl : ybr + 1, xtl : xbr + 1] = 255
        resized_image = imgops.resize_image(image, new_shape)
        resized_image[resized_image > 0] = 255
        resized_image = resized_image.astype(np.uint8)
        cropping_box = imgops.CroppingBox(xtl=xtl, ytl=ytl, xbr=xbr, ybr=ybr)
        fx, fy = new_shape[1] / old_shape[1], new_shape[0] / old_shape[0]
        cropping_box_resized = cropping_box.resize(fx=fx, fy=fy)
        assert (
            cropping_box.crop(image).sum()
            == cropping_box_resized.crop(resized_image).sum()
        )


@pytest.mark.parametrize("n", range(2, 10))
def test_rotate_90(n: int):
    image = np.zeros((n, n), dtype=np.float32)
    image[0, 0] = 1
    image[1, 0] = 2
    image[1, 1] = 3
    solution = np.zeros((n, n), dtype=np.float32)
    solution[-1, 0] = 1
    solution[-1, 1] = 2
    solution[-2, 1] = 3
    rotated = imgops.rotate(image, 90)
    np.testing.assert_array_equal(rotated, solution)


def test_rotate_angle_37():
    image = np.array(
        [
            [0, 0, 1, 0],
            [4, 0, 0, 0],
            [0, 0, 0, 2],
            [0, 3, 0, 0],
        ],
        dtype=np.float32,
    )
    solution = np.array(
        [
            [0, 1, 0, 0],
            [0, 0, 0, 2],
            [4, 0, 0, 0],
            [0, 0, 3, 0],
        ],
        dtype=np.float32,
    )
    angle = np.degrees(np.arctan(1 / 3))
    rotated = imgops.rotate(image, 2 * angle)
    np.testing.assert_array_equal(rotated[solution > 0], solution[solution > 0])


def test_rotate_45():
    image = np.array(
        [
            [0, 0, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 0, 0],
            [0, 1, 0, 1],
        ],
        dtype=np.float32,
    )
    a = 0.020507813
    b = 0.7080078
    c = 0.07324219
    d = 0.390625
    e = 0.109375
    f = 0.19824219
    solution = np.array(
        [
            [0, a, b, 0.5],
            [c, d, e, f],
            [c, d, e, f],
            [0, a, b, 0.5],
        ],
        dtype=np.float32,
    )
    rotated = imgops.rotate(image, 45)
    np.testing.assert_array_equal(rotated, solution)


@pytest.mark.parametrize(
    "filename, angle0", [("angle_+0.53.tif", 0.53), ("angle_-0.32.tif", -0.32)]
)
def test_deskew(filename, angle0):
    file = Path(__file__).parent / "data/images" / filename
    image0 = imgops.read_image(file)
    image = imgops.rotate(image0, -angle0)
    assert np.abs(imgops.deskew(image)) <= 0.25
    for angle in np.linspace(-3, 3, 30):
        image = imgops.rotate(image0, angle - angle0)
        assert np.abs(imgops.deskew(image) + angle) <= 0.25


@pytest.mark.parametrize("shift_x", [1.6, 2.0, 2.4])
@pytest.mark.parametrize("shift_y", [0.6, 1.0, 1.4])
def test_affine_transform_shift_order0(shift_x, shift_y):
    img = np.array(
        [
            [1, 0, 1, 1, 0, 1, 1],
            [0, 0, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 0, 0],
        ],
        dtype=np.uint8,
    )
    actual = imgops.affine_transform(
        img,
        zoom=1.0,
        angle=0.0,
        shift=(shift_x, shift_y),
        order=0,
    )
    # 1 up, 2 left
    truth = np.array(
        [
            [1, 1, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
        ],
    )
    np.testing.assert_array_equal(actual, truth)


def test_affine_transform_zoom_order0():
    img = np.array(
        [
            [1, 0, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 1, 1, 0, 1],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 1],
            [0, 1, 1, 1, 1, 1, 0, 1],
            [0, 1, 1, 1, 1, 0, 0, 0],
        ],
        dtype=np.uint8,
    )
    actual = imgops.affine_transform(img, zoom=2.0, angle=0.0, shift=(0, 0), order=0)
    truth = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 0],
        ]
    )
    np.testing.assert_array_equal(actual, truth)


def test_affine_transform_zoomshift_order0():
    img = np.array(
        [
            [1, 0, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 1, 1, 0, 1],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 1],
            [0, 1, 1, 1, 1, 1, 0, 1],
            [0, 1, 1, 1, 1, 0, 0, 0],
        ],
        dtype=np.uint8,
    )
    actual = imgops.affine_transform(
        img,
        zoom=2.0,
        angle=0.0,
        shift=(2, 1),
        order=0,
    )
    truth = np.array(
        [
            [1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 1, 1],
            [1, 1, 1, 1, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 0, 0, 1, 1],
        ]
    )
    np.testing.assert_array_equal(actual, truth)


def test_filter_areas():
    seg = np.array(
        [
            [1, 0, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 0, 1, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 0, 0],
        ],
        dtype=np.uint8,
    )
    expected = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 1, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 0, 0],
        ],
        dtype=np.uint8,
    )
    seg_filt = imgops.filter_areas(np.array(seg), min_area=2, max_area=3)
    np.testing.assert_array_equal(seg_filt, expected)


def test_correct_drift_nodrift():
    rng = np.random.default_rng(seed=0)
    img = rng.uniform(size=(1, 100, 200)).astype(np.float32)
    box = imgops.CroppingBox(xtl=20, ytl=10, xbr=160, ybr=70)
    template = box.crop(img[0])
    drift = imgops.compute_drift(img, box, template)
    assert drift == [(0, 0)]
    corrected = imgops.correct_drift(img, drift)
    np.testing.assert_equal(img, corrected)


@pytest.mark.parametrize("path", [None, "data/images/angle_-0.32.tif"])
@pytest.mark.parametrize("seed", range(10))
def test_correct_drift(path: str | None, seed: int):
    rng = np.random.default_rng(seed)
    if path:
        img = imgops.read_image(Path(__file__).parent / path)
    else:
        img = rng.uniform(size=(100, 200)).astype(np.float32)
    xdrift = rng.integers(-10, 10, endpoint=True)
    ydrift = rng.integers(-10, 10, endpoint=True)
    shifted = imgops.affine_transform(img, shift=(xdrift, ydrift), order=1)
    shifted = np.expand_dims(shifted, axis=0)
    box = imgops.CroppingBox(xtl=20, ytl=10, xbr=160, ybr=70)
    template = box.crop(img)
    drift = imgops.compute_drift(shifted, box, template)
    assert drift == [(-xdrift, -ydrift)]
    corrected = imgops.correct_drift(shifted, drift)
    drift_total = imgops.compute_drift(corrected, box, template)
    assert drift_total == [(0, 0)]


# %% Eval create_windows


@pytest.mark.parametrize(
    "image_size, nb_tiles",
    [
        ((512, 512), 1),
        ((513, 512), 2),
        ((1000, 512), 2),
        ((1001, 512), 3),
        ((2048, 2048), 25),
        ((200, 200), 1),
        ((600, 200), 2),
        ((696, 520), 4),
    ],
)
def test_create_windows_number(image_size, nb_tiles):
    target_size = (512, 512)
    img = np.zeros(image_size)
    windows, _, _ = imgops.create_windows(img, target_size=target_size, min_overlap=24)
    assert windows.shape == (nb_tiles, *target_size)
    windows, _, _ = imgops.create_windows(
        img.T, target_size=target_size, min_overlap=24
    )
    assert windows.shape == (nb_tiles, *target_size)


# fmt: off
@pytest.mark.parametrize(
    "image_size, target_size, min_overlap, nb_tiles",
    [
        (10, 1, 0, 10),

        (10, 2, 0, 5), (10, 2, 1, 9),

        (10, 3, 0, 4), (10, 3, 1, 5), (10, 3, 2, 8),

        (10, 4, 0, 3), (10, 4, 1, 3), (10, 4, 2, 4), (10, 4, 3, 7),

        (10, 5, 0, 2), (10, 5, 1, 3), (10, 5, 2, 3), (10, 5, 3, 4),
        (10, 5, 4, 6),

        (10, 6, 0, 2), (10, 6, 1, 2), (10, 6, 2, 2), (10, 6, 3, 3),
        (10, 6, 4, 3), (10, 6, 5, 5),

        (10, 7, 0, 2), (10, 7, 1, 2), (10, 7, 2, 2), (10, 7, 3, 2),
        (10, 7, 4, 2), (10, 7, 5, 3), (10, 7, 6, 4),

        (10, 8, 0, 2), (10, 8, 1, 2), (10, 8, 2, 2), (10, 8, 3, 2),
        (10, 8, 4, 2), (10, 8, 5, 2), (10, 8, 6, 2), (10, 8, 7, 3),

        (10, 9, 0, 2), (10, 9, 1, 2), (10, 9, 2, 2), (10, 9, 3, 2),
        (10, 9, 4, 2), (10, 9, 5, 2), (10, 9, 6, 2), (10, 9, 7, 2),
        (10, 9, 8, 2),

        (10, 10, 0, 1), (10, 10, 1, 1), (10, 10, 2, 1), (10, 10, 3, 1),
        (10, 10, 4, 1), (10, 10, 5, 1), (10, 10, 6, 1), (10, 10, 7, 1),
        (10, 10, 8, 1), (10, 10, 9, 1),
    ]
)
def test_create_windows_number_1d(image_size, target_size, min_overlap, nb_tiles):
    other_dim = 20
    image = np.zeros((other_dim, image_size))
    windows, loc_y, loc_x = imgops.create_windows(
        image, target_size=(other_dim, target_size), min_overlap=min_overlap
    )
    assert len(windows) == nb_tiles
    assert len(loc_x) == nb_tiles
    np.testing.assert_array_equal(loc_y, [(0, other_dim)])
    windows, loc_y, loc_x = imgops.create_windows(
        image.T, target_size=(target_size, other_dim), min_overlap=min_overlap
    )
    assert len(windows) == nb_tiles
    assert len(loc_y) == nb_tiles
    np.testing.assert_array_equal(loc_x, [(0, other_dim)])
# fmt: on


def test_create_windows():
    image = np.arange(90).reshape((9, 10))
    windows, loc_y, loc_x = imgops.create_windows(
        image, target_size=(5, 3), min_overlap=1
    )
    pattern = np.arange(3)[np.newaxis, :] + 10 * np.arange(5)[:, np.newaxis]
    truth = (
        np.array([0, 1, 3, 5, 7, 40, 41, 43, 45, 47])[:, np.newaxis, np.newaxis]
        + pattern[np.newaxis, :, :]
    )
    np.testing.assert_array_equal(windows, truth)
    np.testing.assert_array_equal(loc_y, [(i, i + 5) for i in [0, 4]])
    np.testing.assert_array_equal(loc_x, [(i, i + 3) for i in [0, 1, 3, 5, 7]])


def test_create_windows_pad():
    image = np.arange(20).reshape((2, 10))
    windows, loc_y, loc_x = imgops.create_windows(
        image, target_size=(6, 10), min_overlap=1
    )
    truth = np.array(
        [[0] * 10, [0] * 10, image[0, :], image[1, :], [0] * 10, [0] * 10],
        dtype=np.uint32,
    )
    np.testing.assert_array_equal(windows, [truth])
    np.testing.assert_array_equal(loc_y, [(-2, 4)])
    np.testing.assert_array_equal(loc_x, [(0, 10)])


@pytest.mark.parametrize(
    "loc_y, loc_x, expected",
    [
        (
            [(0, 6), (4, 10), (8, 14)],
            [(0, 6), (2, 8)],
            [
                *[[1] * 4 + [2] * 4] * 5,
                *[[3] * 4 + [4] * 4] * 4,
                *[[5] * 4 + [6] * 4] * 5,
            ],
        ),
    ],
)
def test_stitch_pic(expected, loc_y, loc_x):
    windows = np.zeros((len(loc_y) * len(loc_x), 6, 6), dtype=np.uint8)
    for i in range(6):
        windows[i, :, :] = i + 1
    img = imgops.stitch_pic(windows, loc_y, loc_x)
    np.testing.assert_array_equal(img, expected)


@pytest.mark.parametrize(
    "image_shape",
    [
        (512, 512),
        (513, 512),
        (1000, 512),
        (1001, 512),
        (2048, 2048),
        (200, 200),
        (600, 200),
        (696, 520),
    ],
)
def test_create_windows_stitch_pic(image_shape):
    rng = npr.default_rng(0)
    image = rng.random(image_shape)
    windows, loc_y, loc_x = imgops.create_windows(
        image, target_size=(512, 512), min_overlap=24
    )
    stitched_image = imgops.stitch_pic(windows, loc_y, loc_x)
    # Currently need this cropping when the image is smaller than the target size
    stitched_image = stitched_image[0 : image_shape[0], 0 : image_shape[1]]
    np.testing.assert_array_equal(stitched_image, image)


@pytest.mark.parametrize(
    "solution",
    [
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
    ],
)
def test_label_seg(solution):
    mask = (solution > 0).astype(np.uint8)
    with pytest.raises(ValueError, match="cellnumbers must have the same length"):
        imgops.label_seg(mask, [1, 2, 3])
    np.testing.assert_array_equal(imgops.label_seg(mask), solution)
    labels = [int(x) for x in npr.default_rng(seed=1).choice(1000, solution.max())]
    for oldlabel, newlabel in enumerate(labels):
        solution[solution == oldlabel + 1] = newlabel
    assert np.array_equal(imgops.label_seg(mask, cellnumbers=labels), solution)


@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize(
    "image_size",
    [
        (512, 512),
        (2048, 2048),
        (200, 200),
        (200, 600),
        (600, 200),
        (100, 700),
        (696, 520),
        (256, 32),
    ],
)
def test_find_contours(image_size, seed):
    mask = rand_mask(image_size, seed=seed)
    contours = imgops.find_contours(mask)

    new_mask = np.zeros(image_size, dtype=np.uint8)
    new_mask = cv2.drawContours(new_mask, contours, -1, 1, thickness=-1)

    np.testing.assert_array_equal(mask, new_mask)


def test_postprocess_binarize():
    logits = np.array([[-3, -1, 1.5], [3, 0.5, -0.1]])
    mask = imgops.postprocess(logits, crop=True)
    np.testing.assert_array_equal(mask, np.array([[0, 0, 1], [1, 1, 0]]))


def test_postprocess_minsize():
    preds = np.array(
        [
            [1, 0, 1, 0, 1, 1],
            [0, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1],
            [1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0],
        ],
        dtype=np.float32,
    )
    mask = imgops.postprocess(preds, crop=True, min_size=4)
    minsize = np.array(
        [
            [0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1],
            [1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0],
        ]
    )
    np.testing.assert_array_equal(mask, minsize)


def test_postprocess_opening():
    preds = np.array(
        [
            [1, 0, 1, 1, 0, 1, 1],
            [0, 0, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 0, 0],
        ],
        dtype=np.float32,
    )
    mask = imgops.postprocess(preds, crop=False, min_size=None, square_size=3)
    minsize = np.array(
        [
            [0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 0, 0],
        ]
    )
    np.testing.assert_array_equal(mask, minsize)


def test_smart_resize():
    img = np.array(
        [
            [2, 2, 2, 2, 2, 2, 2, 0],
            [1, 2, 2, 2, 2, 2, 2, 0],
            [1, 2, 2, 2, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 2],
            [1, 1, 1, 1, 0, 0, 2, 2],
            [2, 2, 2, 1, 0, 0, 2, 2],
            [2, 2, 2, 1, 0, 0, 2, 2],
            [0, 2, 2, 1, 0, 0, 0, 2],
            [0, 2, 2, 2, 1, 0, 0, 0],
        ],
        dtype=np.uint8,
    )
    img = imgops.rescale_image(img)
    solution_seg = np.array(
        [
            [1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [1, 1, 0, 0, 1],
            [0, 1, 0, 0, 1],
        ],
        dtype=np.uint8,
    )

    seg = (img > 0).astype(np.uint8)
    assert img.shape == (10, 8)

    shape = (5, 5)
    new_img = imgops.smart_resize(img, shape)
    new_seg = imgops.smart_resize(seg, shape)

    assert new_img.shape == shape
    assert new_img.dtype == img.dtype
    assert new_seg.shape == shape
    assert new_seg.dtype == seg.dtype

    np.testing.assert_array_equal(new_seg, solution_seg)


@pytest.mark.parametrize(
    "n1, n2",
    [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
        (7, 2),
        (8, 2),
        (9, 2),
    ],
)
def test_resize_mask(n1: int, n2: int):
    mask = np.ones((9, 10), dtype=np.uint8)
    mask[3:6, :] = 0
    mask[:, n1] = 1
    solution = np.array([[1, 1, 1], [0, 0, 0], [1, 1, 1]], dtype=np.uint8)
    solution[:, n2] = 1

    resized_mask = imgops.resize_mask(mask, (3, 3))

    np.testing.assert_array_equal(resized_mask, solution)


def test_resize_labels():
    labels = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 3, 3],
            [0, 0, 0, 0, 0, 0, 3, 3, 3],
            [2, 2, 2, 0, 0, 0, 3, 3, 3],
            [2, 2, 2, 0, 0, 0, 3, 3, 3],
            [0, 2, 2, 0, 0, 0, 0, 3, 3],
            [0, 2, 2, 2, 0, 0, 0, 0, 0],
        ],
        dtype=np.uint16,
    )
    solution = np.array(
        [[1, 1, 1, 1, 0], [1, 1, 1, 0, 3], [2, 2, 0, 3, 3], [2, 2, 2, 0, 3]],
        dtype=np.uint16,
    )
    resized_labels = imgops.resize_labels(labels, (4, 5))

    np.testing.assert_array_equal(resized_labels, solution)


def test_detect_touching_cells():
    labels = np.array(
        [
            [1, 0, 0, 3, 3, 3, 0, 4, 5],
            [0, 2, 2, 3, 3, 3, 4, 0, 4],
            [0, 2, 2, 3, 3, 3, 0, 4, 0],
            [0, 0, 0, 3, 3, 3, 0, 0, 0],
            [7, 0, 0, 6, 6, 0, 0, 8, 0],
            [0, 0, 9, 6, 6, 6, 0, 0, 0],
            [0, 9, 0, 6, 6, 6, 10, 0, 0],
            [0, 9, 9, 6, 6, 6, 0, 10, 0],
            [0, 9, 0, 6, 6, 6, 0, 0, 10],
            [9, 0, 11, 11, 11, 11, 0, 10, 0],
        ],
        dtype=np.uint16,
    )

    solution = np.array(
        [
            [1, 0, 0, 1, 0, 1, 0, 1, 1],
            [0, 1, 1, 1, 0, 1, 1, 0, 1],
            [0, 0, 1, 1, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0, 1, 0, 0, 0],
            [0, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0, 0],
        ],
        dtype=bool,
    )

    touching = imgops.detect_touching_cells(labels)
    assert touching.dtype == solution.dtype
    np.testing.assert_array_equal(touching, solution)


def test_distance_transform_labels():
    labels = np.array(
        [
            [1, 0, 0, 3, 3, 3, 0, 4, 5],
            [0, 2, 2, 3, 3, 3, 4, 0, 4],
            [0, 2, 2, 3, 3, 3, 0, 4, 0],
            [0, 0, 0, 3, 3, 3, 0, 0, 0],
            [7, 0, 0, 6, 6, 0, 0, 8, 0],
            [0, 0, 9, 6, 6, 6, 0, 0, 0],
            [0, 9, 0, 6, 6, 6, 10, 0, 0],
            [0, 9, 9, 6, 6, 6, 0, 10, 0],
            [0, 9, 0, 6, 6, 6, 0, 0, 10],
            [9, 0, 11, 11, 11, 11, 0, 10, 0],
        ],
        dtype=np.uint16,
    )

    a = 1
    b = 2
    c = np.sqrt(2)
    solution = np.array(
        [
            [a, 0, 0, a, a, a, 0, a, a],
            [0, a, a, a, b, a, a, 0, a],
            [0, a, a, a, b, a, 0, a, 0],
            [0, 0, 0, a, a, a, 0, 0, 0],
            [a, 0, 0, a, a, 0, 0, a, 0],
            [0, 0, a, a, c, a, 0, 0, 0],
            [0, a, 0, a, b, a, a, 0, 0],
            [0, a, a, a, b, a, 0, a, 0],
            [0, a, 0, a, a, a, 0, 0, a],
            [a, 0, a, a, a, a, 0, a, 0],
        ],
        dtype=np.float32,
    )

    distance_map = imgops.distance_transform_labels(labels)

    assert distance_map.dtype == np.float32
    np.testing.assert_array_equal(distance_map, solution)
