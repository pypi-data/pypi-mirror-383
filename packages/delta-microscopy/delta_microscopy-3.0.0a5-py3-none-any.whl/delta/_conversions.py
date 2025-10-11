"""Various conversions to save objects to disk."""

import ast
import logging
from json import JSONDecodeError

import cv2
import numpy as np
import numpy.typing as npt
import xarray as xr

import delta
from delta import imgops, utils
from delta.config import Config
from delta.lineage import Pole
from delta.model import hash_model

LOGGER = logging.getLogger(__name__)


def _roi_to_xarray(roi: "delta.pipeline.ROI") -> xr.Dataset:
    # DataArray coordinates
    frames = np.arange(len(roi.img_stack), dtype=np.int32) + roi.first_frame
    y_orig = np.arange(roi.img_stack[0].shape[0], dtype=np.int16)
    x_orig = np.arange(roi.img_stack[0].shape[1], dtype=np.int16)
    tyx_orig = {"frame": frames, "y_orig": y_orig, "x_orig": x_orig}
    y_resized = np.arange(roi.seg_stack[0].shape[0], dtype=np.int16)
    x_resized = np.arange(roi.seg_stack[0].shape[1], dtype=np.int16)
    tyx_resized = {"frame": frames, "y_resized": y_resized, "x_resized": x_resized}
    cells = np.array(list(roi.lineage.cells.keys()), dtype=np.uint16)
    ct = {"cell": cells, "frame": frames}
    channels = roi.fluo_stack.channel
    edge = ["-x", "+x", "-y", "+y"]

    # Image stacks
    img_stack = xr.DataArray(
        roi.img_stack, dims=("frame", "y_orig", "x_orig"), coords=tyx_orig
    )
    fluo_stack = xr.DataArray(
        roi.fluo_stack,
        dims=("frame", "channel", "y_orig", "x_orig"),
        coords=tyx_orig | {"channel": channels},
    )
    seg_stack = xr.DataArray(
        roi.seg_stack, dims=("frame", "y_resized", "x_resized"), coords=tyx_resized
    ).astype(bool)
    label_stack = xr.DataArray(
        roi.label_stack, dims=("frame", "y_orig", "x_orig"), coords=tyx_orig
    )

    # Lineage (first define numpy arrays, then transform them into DataArrays)
    nmother = np.zeros((len(cells),), dtype=np.uint16)
    ndaughters = np.zeros((len(cells), len(frames)), dtype=np.uint16)
    nnew_pole = np.zeros((len(cells), len(frames), 2), dtype=np.int16)
    nold_pole = np.zeros((len(cells), len(frames), 2), dtype=np.int16)
    nedges = np.zeros((len(cells), len(frames), 4), dtype=bool)
    nscalars = {
        "length": np.full((len(cells), len(frames)), np.nan, dtype=np.float32),
        "width": np.full((len(cells), len(frames)), np.nan, dtype=np.float32),
        "area": np.full((len(cells), len(frames)), np.nan, dtype=np.float32),
        "perimeter": np.full((len(cells), len(frames)), np.nan, dtype=np.float32),
        "growthrate_length": np.full(
            (len(cells), len(frames)), np.nan, dtype=np.float32
        ),
        "growthrate_area": np.full((len(cells), len(frames)), np.nan, dtype=np.float32),
    }
    nfluo = np.full((len(cells), len(frames), len(channels)), np.nan, dtype=np.float32)
    for icell, cellid in enumerate(cells):
        cell = roi.lineage.cells[cellid]
        nmother[icell] = cell.motherid or 0
        for frame in cell.frames:
            features = cell.features(frame)
            ndaughters[icell, frame - roi.first_frame] = cell.daughterid(frame) or 0
            nnew_pole[icell, frame - roi.first_frame] = features.new_pole
            nold_pole[icell, frame - roi.first_frame] = features.old_pole
            for arg, narg in nscalars.items():
                narg[icell, frame - roi.first_frame] = getattr(features, arg)
            nfluo[icell, frame - roi.first_frame] = features.fluo
            for iedge, edg in enumerate(edge):
                nedges[icell, frame - roi.first_frame, iedge] = edg in features.edges

    # Transform lineage information into DataArrays
    mother = xr.DataArray(nmother, dims=("cell",), coords={"cell": cells})
    daughters = xr.DataArray(ndaughters, dims=("cell", "frame"), coords=ct)
    ctyx = ct | {"yx": ["y", "x"]}
    new_pole = xr.DataArray(nnew_pole, dims=("cell", "frame", "yx"), coords=ctyx)
    old_pole = xr.DataArray(nold_pole, dims=("cell", "frame", "yx"), coords=ctyx)
    scalars = {
        arg: xr.DataArray(narg, dims=("cell", "frame"), coords=ct)
        for arg, narg in nscalars.items()
    }
    fluo = xr.DataArray(
        nfluo, dims=("cell", "frame", "channel"), coords=ct | {"channel": channels}
    )
    edges = xr.DataArray(
        nedges, dims=("cell", "frame", "edge"), coords=ct | {"edge": edge}
    )
    first_frame = xr.DataArray(
        np.array(
            [roi.lineage.cells[cellid].first_frame for cellid in cells], dtype=np.int32
        ),
        dims=("cell",),
        coords={"cell": cells},
    )
    last_frame = xr.DataArray(
        np.array(
            [roi.lineage.cells[cellid].last_frame for cellid in cells], dtype=np.int32
        ),
        dims=("cell",),
        coords={"cell": cells},
    )

    model_hashes = {}
    for model_name, model_config in roi.config.models.items():
        try:
            h = model_config._model_hash  # type: ignore[attr-defined]
        except AttributeError:
            h = hash_model(model_config.model())
        model_hashes[f"{model_name}_model_hash"] = h

    # Create Dataset
    dataset = xr.Dataset(
        data_vars={
            "img_stack": img_stack,
            "fluo_stack": fluo_stack,
            "seg_stack": seg_stack,
            "label_stack": label_stack,
            "mother": mother,
            "daughter": daughters,
            "new_pole": new_pole,
            "old_pole": old_pole,
            "edges": edges,
            "fluo": fluo,
            "first_frame": first_frame,
            "last_frame": last_frame,
        }
        | scalars,
        attrs={
            "roi_nb": roi.roi_nb,
            "box": str(roi.box.__dict__),
            "scaling": roi.scaling,
            "config": roi.config.serialize(),
            "DeLTA_version": delta.__version__,
            "file_format_version": "0.1.0",
        }
        | model_hashes,
    )
    return dataset


def _xarray_to_roi(dataset: xr.Dataset) -> "delta.pipeline.ROI":
    box = imgops.CroppingBox(**ast.literal_eval(dataset.attrs["box"]))
    try:
        config = Config.deserialize(dataset.attrs["config"])
    except JSONDecodeError:
        LOGGER.warning(
            "The configuration stored in this nc file is deprecated. "
            "It will not be possible to read it anymore in a future DeLTA version. "
            "To avoid that, just load and save this file with this DeLTA version: "
            "`delta.pipeline.Position.load_netcdf(path).to_netcdf(path)`"
        )
        old_config = delta.config.OldConfig(**ast.literal_eval(dataset.attrs["config"]))
        config = old_config.to_tomlconfig()
    for name, model in config.models.items():
        model._model_hash = dataset.attrs[f"{name}_model_hash"]  # type: ignore[attr-defined]
    img_stack = dataset.img_stack.expand_dims({"channel": [0]}, axis=1)
    fluo_stack = dataset.fluo_stack.assign_coords(
        {"channel": dataset.fluo_stack.channel + 1}
    )
    stack = xr.concat([img_stack, fluo_stack], dim="channel")
    roi = delta.pipeline.ROI(
        stack=stack.rename({"y_orig": "yc", "x_orig": "xc"}),
        roi_nb=dataset.attrs["roi_nb"],
        first_frame=dataset.frame[0].to_numpy() if len(dataset.frame) > 0 else 0,
        box=box,
        config=config,
    )
    roi.scaling = tuple(dataset.attrs["scaling"])
    roi.seg_stack = list(dataset.seg_stack.to_numpy().astype(np.uint8))
    roi.label_stack = list(dataset.label_stack.to_numpy())
    cells = {}
    for cellid in [int(cellid) for cellid in dataset.cell]:
        xrcell = dataset.sel(cell=cellid)
        mother = int(xrcell.mother)
        frames = np.arange(xrcell.first_frame, xrcell.last_frame + 1)
        data = xrcell.sel(frame=frames)
        daughters = data.daughter.to_numpy()
        edges = [
            "".join(
                str(e.to_numpy()) if data.edges.sel(frame=frame, edge=e) else ""
                for e in data.edge
            )
            for frame in data.frame
        ]
        cells[cellid] = delta.lineage.Cell(
            motherid=mother if mother > 0 else None,
            first_frame=frames[0],
            _daughterids=[did if did > 0 else None for did in daughters],
            _features=[
                delta.lineage.CellFeatures(
                    new_pole=new_pole,
                    old_pole=old_pole,
                    length=length,
                    width=width,
                    area=area,
                    perimeter=perimeter,
                    fluo=fluo,
                    edges=edges,
                    growthrate_length=gr_l,
                    growthrate_area=gr_a,
                )
                for (
                    new_pole,
                    old_pole,
                    length,
                    width,
                    area,
                    perimeter,
                    fluo,
                    edges,
                    gr_l,
                    gr_a,
                ) in zip(
                    data.new_pole.to_numpy(),
                    data.old_pole.to_numpy(),
                    data.length.to_numpy(),
                    data.width.to_numpy(),
                    data.area.to_numpy(),
                    data.perimeter.to_numpy(),
                    data.fluo.to_numpy(),
                    edges,
                    data.growthrate_length.to_numpy(),
                    data.growthrate_area.to_numpy(),
                    strict=True,
                )
            ],
        )
    roi.lineage.cells = cells
    return roi


def _position_to_movie(
    position: "delta.pipeline.Position",
    reader: delta.utils.XPReader,
    frames: range | None = None,
    *,
    with_labels: bool = False,
) -> list[npt.NDArray[np.uint8]]:
    # Re-read trans frames:
    trans_images = reader.images(
        position=position.position_nb,
        channels=reader.channels[0],
        frames=frames,
        rotate=position.rotate,
    ).isel(channel=0)
    if frames is None:
        frames = reader.frames

    if position.config.correct_drift:
        da_drift_values = xr.DataArray(
            position.drift_values,
            coords={"frame": trans_images.frame},
            dims=("frame", "xy"),
        )
        trans_images = imgops.correct_drift(trans_images, da_drift_values)

    # Fix brightness
    ti_min = trans_images.min()
    ti_max = trans_images.max()
    trans_images = (trans_images - ti_min) / (ti_max - ti_min)
    trans_images = trans_images.to_numpy()

    movie = []

    # Run through frames, compile movie:
    for frame, init_trans_frame in zip(frames, trans_images, strict=True):
        trans_frame = init_trans_frame

        # RGB-ify:
        trans_frame = np.repeat(trans_frame[:, :, np.newaxis], 3, axis=-1)

        # Add frame number text:
        trans_frame = cv2.putText(
            trans_frame,
            text=f"frame {frame:06d}",
            org=(int(trans_frame.shape[0] * 0.05), int(trans_frame.shape[0] * 0.97)),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(1, 1, 1, 1),
            thickness=2,
        )

        for roi in position.rois:
            # Get chamber-specific variables:
            colors = utils.random_colors(
                list(roi.lineage.cells.keys()), seed=roi.roi_nb
            )
            labels = roi.get_labels(frame)
            cellids, contours = utils.cells_in_frame(labels, return_contours=True)

            xtl, ytl = (roi.box.xtl, roi.box.ytl)

            # Run through cells in labelled frame:
            for icell, cellid in enumerate(cellids):
                cell = roi.lineage.cells[cellid]
                # Draw contours:
                trans_frame = cv2.drawContours(
                    trans_frame,
                    contours,
                    icell,
                    color=colors[cellid],
                    thickness=1,
                    offset=(xtl, ytl),
                )

                if with_labels:
                    cell_y, cell_x = np.where(labels == cellid)
                    trans_frame = cv2.putText(
                        trans_frame,
                        text=str(cellid),
                        org=(
                            int(np.mean(cell_x) + xtl + 5),
                            int(np.mean(cell_y) + ytl + 5),
                        ),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(1, 1, 1, 1),
                        thickness=1,
                    )

                # Draw poles:
                oldpole = cell.features(frame).old_pole
                assert isinstance(oldpole, np.ndarray)  # for mypy
                trans_frame = _draw_pole(
                    trans_frame,
                    contours[icell],
                    oldpole,
                    (xtl, ytl),
                    color=colors[cellid],
                )

                daughter = cell.daughterid(frame)
                bornago = frame - cell.first_frame
                mother = cell.motherid

                if daughter is None and (bornago > 0 or mother is None):
                    newpole = cell.features(frame).new_pole
                    trans_frame = _draw_pole(
                        trans_frame,
                        contours[icell],
                        newpole,
                        (xtl, ytl),
                        color=(1.0, 1.0, 1.0),
                    )

                # Plot division arrow:
                if daughter is not None:
                    newpole = cell.features(frame).new_pole
                    daupole = roi.lineage.cells[daughter].features(frame).new_pole
                    # Plot arrow:
                    trans_frame = cv2.arrowedLine(
                        trans_frame,
                        (newpole[1] + xtl, newpole[0] + ytl),
                        (daupole[1] + xtl, daupole[0] + ytl),
                        color=(1, 1, 1),
                        thickness=1,
                    )

        # Add to movie array:
        movie += [imgops.to_integer_values(trans_frame, np.uint8)]

    return movie


def _draw_pole(
    image: npt.NDArray[np.float32],
    contour: npt.NDArray[np.int32],
    pole: Pole,
    offset: tuple[int, int],
    color: tuple[float, float, float],
    width: int = 7,
) -> npt.NDArray[np.float32]:
    contour = contour[:, 0, :]
    pole_ind = np.argmin(np.sum(np.abs(contour - pole[::-1]), axis=1))
    pole_cnt = contour[np.arange(pole_ind - width, pole_ind + width) % len(contour)]
    return cv2.drawContours(image, [pole_cnt[:, None, :]], -1, color, -1, offset=offset)


def _position_to_labels(
    position: "delta.pipeline.Position",
    frames: range | None = None,
    *,
    undo_corrections: bool = True,
) -> list[imgops.Labels]:
    if frames is None:
        frames = range(
            position.rois[0].first_frame,
            position.rois[0].first_frame + len(position.rois[0].label_stack),
        )

    labels = []
    for frame in frames:
        labelled = np.zeros(position.shape, dtype=np.uint16)

        for roi in position.rois:
            roi.box.patch(labelled, roi.get_labels(frame))

        # Undo drift and rotation corrections:
        if undo_corrections:
            shift = (0, 0)
            if position.config.correct_drift:
                shift = position.drift_values[frame - position.rois[0].first_frame]
                shift = (-shift[0], -shift[1])

            angle = 0.0
            if position.config.correct_rotation:
                angle = -position.rotate

            labelled = imgops.affine_transform(
                labelled, shift=shift, angle=angle, order=0
            )

        labels.append(labelled)

    return labels
