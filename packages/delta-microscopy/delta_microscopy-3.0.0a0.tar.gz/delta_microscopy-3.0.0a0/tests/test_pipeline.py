import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from delta import imgops
from delta.config import Config
from delta.pipeline import ROI, Position
from delta.utils import CroppingBox, XPReader

DATA_PATH = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "path",
    [
        DATA_PATH / "movie_mothermachine_tif/expected_results/Position000001.nc",
        DATA_PATH / "movie_2D_tif/expected_results/Position000001.nc",
    ],
)
def test_xarray_roundtrip_from_roi(path):
    pos = Position.load_netcdf(path)

    for roi in pos.rois:
        dataset = roi.to_xarray()
        new_roi = ROI.from_xarray(dataset)
        assert roi == new_roi


@pytest.mark.parametrize(
    "path",
    [
        DATA_PATH / "movie_mothermachine_tif/expected_results/Position000001.nc",
        DATA_PATH / "movie_2D_tif/expected_results/Position000001.nc",
    ],
)
def test_position_save(path):
    pos = Position.load_netcdf(path)

    with tempfile.TemporaryDirectory() as tempdirname:
        new_path = Path(tempdirname) / "position.nc"
        pos.to_netcdf(new_path)

        repos = Position.load_netcdf(new_path)

    assert pos == repos


def test_position_load_without_shape_info():
    path = DATA_PATH / "output_files/position_without_shape.nc"

    pos = Position.load_netcdf(path)

    assert pos.shape == (256, 32)


def test_safe_resizing():
    config = Config.default("mothermachine")
    path = DATA_PATH / "images/safe_resizing/img_frame{t}.tif"
    xpr = XPReader(path)
    pos = Position(0, config)
    all_frames = xpr.images(position=0)
    reference = imgops.read_image(path.parent / "reference.tif")
    pos.preprocess(all_frames, range(1, 3), reference)
    pos.segment(frames=range(1, 3))
    pos.track(frames=range(1, 3))


@pytest.mark.parametrize("tolerable_resizing_rois", [0.0, 0.5, 1.0, 2.0, np.inf])
def test_find_roi_boxes(tolerable_resizing_rois: float):
    def roi_box_approx_eq(b1: CroppingBox, b2: CroppingBox, abs_tol: int = 3):
        return (
            abs(b1.ytl - b2.ytl) <= abs_tol
            and abs(b1.xtl - b2.xtl) <= abs_tol
            and abs(b1.ybr - b2.ybr) <= abs_tol
            and abs(b1.xbr - b2.xbr) <= abs_tol
        )

    xpfolder = DATA_PATH / "movie_mothermachine_tif"

    xpreader = XPReader(xpfolder / "Position{p}Channel{c}Frames{t}.tif")

    # Copy the config to not modify the default (can impact other tests)
    config = Config.default("mothermachine")
    config.models["rois"].tolerable_resizing_factor = tolerable_resizing_rois

    for position_nb in xpreader.positions:
        expected_pos = Position.load_netcdf(
            xpfolder / f"expected_results/Position{position_nb:06}.nc"
        )

        reference = (
            xpreader.images(position=position_nb, channels=1, frames=range(1, 2))
            .isel(channel=0, frame=0)
            .to_numpy()
        )

        # Preprocess reference
        if config.correct_rotation:
            angle = imgops.deskew(reference)
            reference = imgops.rotate(reference, angle)

        # Generate ROI boxes
        test_roi_boxes = Position.find_roi_boxes(reference=reference, config=config)

        # Compare results
        assert len(test_roi_boxes) == len(expected_pos.rois)
        for test_box, roi in zip(test_roi_boxes, expected_pos.rois, strict=True):
            assert roi_box_approx_eq(test_box, roi.box)


def test_find_roi_boxes_negative():
    config = Config.default("mothermachine")
    config.models["rois"].tolerable_resizing_factor = -0.5
    xpfolder = DATA_PATH / "movie_mothermachine_tif"
    xpreader = XPReader(xpfolder / "Position{p}Channel{c}Frames{t}.tif")
    reference = xpreader.images(position=1, channels=1, frames=range(1, 2))[0, 0, :, :]
    with pytest.raises(ValueError, match="tolerable_resizing_rois is negative"):
        Position.find_roi_boxes(reference=reference, config=config)


@pytest.mark.parametrize(
    "path",
    [
        DATA_PATH / "movie_mothermachine_tif/expected_results/Position000001.nc",
        DATA_PATH / "movie_2D_tif/expected_results/Position000001.nc",
    ],
)
def test_labels(path):
    pos = Position.load_netcdf(path)
    labels = pos.labels()

    for frame, label in enumerate(labels):
        fname = f"labels_{frame:03d}.tif"
        cv2.imwrite(str(path.parent.parent / "delta_results" / fname), label)
        reference = cv2.imread(str(path.parent / fname), cv2.IMREAD_ANYDEPTH)
        np.testing.assert_array_equal(label, reference)


def check_labels_consistency(roi):
    for cellid, cell in roi.lineage.cells.items():
        for frame in cell.frames:
            labels = roi.get_labels(frame)
            assert labels[*cell.poles(frame)[0]] == cellid
            assert labels[*cell.poles(frame)[1]] == cellid


def test_lineage_labels():
    # frames    : ...........
    # cell #0001:  ╺╼╼╼╼┮╼╼╼╼
    # cell #0008:       ┕╼╼╼╼
    # cell #0002:  ╺╼╼┮╼╼╼╼╼╼
    # cell #0006:     ┕╼╼╼╼┮
    # cell #0009:          ┕
    # cell #0003:  ╺╼╼╼┮╼╼
    # cell #0007:      ┕
    # cell #0004:  ╺╼╼
    # cell #0005:  ╺╼
    path = DATA_PATH / "movie_mothermachine_tif/expected_results/Position000001.nc"
    pos = Position.load_netcdf(path)
    roi = pos.rois[0]

    check_labels_consistency(roi)

    new_cellid = roi.split(cellid=1, frame=4)
    check_labels_consistency(roi)

    roi.merge(cellid=new_cellid, merge_into_cellid=1)
    check_labels_consistency(roi)

    roi.adopt(cellid=8, motherid=None)
    check_labels_consistency(roi)

    roi.adopt(cellid=8, motherid=1)
    check_labels_consistency(roi)

    roi.pivot(cellid=6)
    check_labels_consistency(roi)

    roi.swap_poles(cellid=2)
    check_labels_consistency(roi)
