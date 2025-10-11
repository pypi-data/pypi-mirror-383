"""Main processing pipeline."""

import ast
import logging
from collections.abc import Sequence
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Literal, cast

import cv2
import keras
import netCDF4 as nc  # noqa: N813
import numpy as np
import numpy.typing as npt
import xarray as xr
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

import delta
from delta import imgops, utils
from delta._conversions import (
    _position_to_labels,
    _position_to_movie,
    _roi_to_xarray,
    _xarray_to_roi,
)
from delta.config import Config
from delta.imgops import CroppingBox, Image, Labels, SegmentationMask
from delta.lineage import Lineage

LOGGER = logging.getLogger(__name__)

MODEL = Literal["rois", "seg", "track"]

NETCDF_COMPRESS = {
    "img_stack",
    "fluo_stack",
    "seg_stack",
    "label_stack",
    "daughter",
    "new_pole",
    "old_pole",
    "length",
    "width",
    "area",
    "perimeter",
    "growthrate_length",
    "growthrate_area",
    "fluo",
    "edges",
}


class Pipeline:
    """Main Pipeline class to process all positions."""

    def __init__(
        self,
        xpreader: utils.XPReader,
        config: Config,
        resfolder: str | Path | None = None,
    ) -> None:
        """
        Initialize Pipeline.

        Parameters
        ----------
        xpreader : utils.XPReader
            XPReader object.
        config : Config
            DeLTA configuration.
        resfolder : str or Path, optional
            Path to folder to save results to.
            The default is None.
        """
        self.reader: utils.XPReader = xpreader
        "Experiment reader object"
        self.positions: dict[int, Position] = {}
        "Dict of Position objects for experiment"
        self.config: Config = config
        "Configuration parameters object"
        self.resfolder: Path
        "Folder to save results to"

        if resfolder is None:
            xpfile = self.reader.path
            assert xpfile is not None
            if self.reader.filetype == "dir":
                resfolder = self.reader.filehandle / "delta_results"
            else:
                resfolder = xpfile.with_name(xpfile.stem + "_delta_results")

        self.resfolder = Path(resfolder)

        self.resfolder.mkdir(exist_ok=True)

        # Initialize position processors:
        for position_nb in self.reader.positions:
            self.positions[position_nb] = Position(
                position_nb,
                config=self.config,
            )

    def process(
        self,
        *,
        positions: Sequence[int] | None = None,
        frames: range | slice | None = None,
        save_as: Sequence[str] = ("netCDF", "movie"),
        clear: bool = True,
        progress_bar: bool = False,
    ) -> None:
        """
        Run pipeline.

        Parameters
        ----------
        positions : list of int or None, optional
            List of positions to run. If None, all positions are run.
            The default is None.
        frames : int or None, optional
            Number of frames to run. If None, all frames are run.
            The default is None.
        save_as: Sequence[str]
            List of formats to save the results.  Can be "netCDF", "movie" or
            "labeled-movie".
            The default is ``("netCDF", "movie")``.
        clear : bool, optional
            Clear variables of each Position object after it has been processed
            and saved to disk, to prevent memory issues.
            The default is True.
        progress_bar : bool, optional (default False)
            Display a progress bar
        """
        if frames is None:
            frames = self.reader.frames
        elif isinstance(frames, slice):
            assert frames.step in {1, None}
            if frames.start is None:
                frames = slice(self.reader.frames.start, frames.stop)
            if frames.stop is None:
                frames = slice(frames.start, self.reader.frames.stop)
            frames = range(frames.start, frames.stop)

        if positions is None:
            positions = self.reader.positions

        # Run through positions
        for position_nb, position in self.positions.items():
            if position_nb not in positions:
                continue

            LOGGER.info("Starting processing of position %d...", position_nb)

            all_frames = self.reader.images(position=position_nb, frames=frames)

            # Create ROIs and distribute images
            position.preprocess(all_frames, frames=frames)

            # Segment all ROIs
            position.segment(frames=frames, progress_bar=progress_bar)

            # Track cells in all ROIs
            position.track(frames=frames, progress_bar=progress_bar)

            # Compute growthrates in all ROIs
            position.compute_growthrates(frames=frames)

            # Save to disk and clear memory
            position.save(
                filename=self.resfolder / f"Position{position_nb:06d}",
                frames=frames,
                reader=self.reader,
                save_as=save_as,
                progress_bar=progress_bar,
            )

            if clear:
                position.clear()


class Position:
    """Position-processing object."""

    def __init__(
        self,
        position_nb: int,
        config: Config,
    ) -> None:
        """
        Initialize Position.

        Parameters
        ----------
        position_nb : int
            Position index.
        config : Config
            DeLTA configuration.
        """
        self.position_nb = position_nb
        "Position index number in the experiment"
        self.shape: tuple[int, int] = (0, 0)
        "Shape of full-frame images. (Y, X) convention"
        self.rois: list[ROI] = []
        "List of ROI objects under position"
        self.drift_values: list[tuple[int, int]] = []
        "XY drift correction values over time"
        self.rotate: float = 0.0
        "Rotation angle of the position to compensate"
        self.config: Config = config
        "Configuration parameters object"

    def __str__(self) -> str:
        """Construct a string that informally represents the Position."""
        s = [
            f"Position #{self.position_nb}",
            f" ├─ {len(self.rois)} ROI(s)",
            f" ├─ shape: {self.shape}",
            f" └─ rotate: {self.rotate}",
        ]
        return "\n".join(s)

    def compare(self, other: object, level: int = 0) -> list | None:  # type: ignore[type-arg]
        """Compare this Position with another and print the differences."""
        diffs: list[str | list] = []  # type: ignore[type-arg]
        if not isinstance(other, Position):
            diffs.append(utils.color_diff("", "Position", type(other)))
        else:
            diffs.append("Position")
            if self.position_nb != other.position_nb:
                diffs.append(
                    utils.color_diff(
                        "position_nb: ", self.position_nb, other.position_nb
                    )
                )
            if self.shape != other.shape:
                diffs.append(utils.color_diff("shape: ", self.shape, other.shape))
            if len(self.rois) != len(other.rois):
                diffs.append(
                    utils.color_diff("# rois: ", len(self.rois), len(other.rois))
                )
            else:
                for iroi in range(len(self.rois)):
                    diff = self.rois[iroi].compare(other.rois[iroi], level=level + 1)
                    assert diff is not None
                    if len(diff) > 1:
                        diffs.append(diff)
            if self.rotate != other.rotate:
                diffs.append(utils.color_diff("rotate: ", self.rotate, other.rotate))
            if self.drift_values != other.drift_values:
                diffs.append(
                    utils.color_diff(
                        "drift_values: ", self.drift_values, other.drift_values
                    )
                )
        if level == 0:
            utils.print_diffs(diffs)
            return None
        return diffs

    def to_netcdf(
        self, path: Path, *, progress_bar: bool = False, **kwargs: dict[str, Any]
    ) -> None:
        """
        Save the position as a netCDF file.

        The file will contain one group per ROI, with names ``roi00``, ``roi01``, etc.

        Parameters
        ----------
        path : Path
            Path where to save the netCDF file.
        progress_bar : bool, optional (default False)
            Display a progress bar.
        kwargs : dict
            Keyword arguments passed to ``ROI.to_netcdf``.
        """
        attrs = {
            "position_nb": self.position_nb,
            "nb_rois": len(self.rois),
            "rotate": self.rotate,
            "shape": self.shape,
            "config": self.config.serialize(),
            "drift_x": [xdrift for xdrift, _ in self.drift_values],
            "drift_y": [ydrift for _, ydrift in self.drift_values],
            "DeLTA_version": delta.__version__,
            "file_format_version": "0.1.0",
        }
        xr.Dataset(attrs=attrs).to_netcdf(path, mode="w")
        with logging_redirect_tqdm():
            for roi in tqdm(
                self.rois, desc="ROIs", disable=len(self.rois) == 1 or not progress_bar
            ):
                roi.to_netcdf(path, mode="a", group=f"roi{roi.roi_nb:02}", **kwargs)

    def __eq__(self, other: object) -> bool:
        """Equality function for Position."""
        if not isinstance(other, Position):
            return NotImplemented
        eq_position_nb = self.position_nb == other.position_nb
        if not eq_position_nb:
            LOGGER.debug("Differ by position_nb")
        eq_shape = self.shape == other.shape
        if not eq_shape:
            LOGGER.debug("Differ by shape")
            LOGGER.debug(self.shape)
            LOGGER.debug(other.shape)
        eq_rois = self.rois == other.rois
        if not eq_rois:
            LOGGER.debug("Differ by rois")
        eq_drift_values = np.array_equal(self.drift_values, other.drift_values)
        if not eq_drift_values:
            LOGGER.debug("Differ by drift values")
            LOGGER.debug(self.drift_values)
            LOGGER.debug(other.drift_values)
        eq_rotate = self.rotate == other.rotate
        if not eq_rotate:
            LOGGER.debug("Differ by rotate")
            LOGGER.debug(self.rotate)
            LOGGER.debug(other.rotate)
        eqs = [
            eq_position_nb,
            eq_shape,
            eq_rois,
            eq_drift_values,
            eq_rotate,
        ]
        return all(eqs)

    def preprocess(
        self,
        all_frames: xr.DataArray,
        frames: range,
        reference: Image | None = None,
    ) -> None:
        """
        Pre-process position (Rotation correction, identify ROIs, initialize drift correction).

        Parameters
        ----------
        all_frames : xr.DataArray
            All frames for this position. Shape: (frames, channels, Y, X).
        reference : 2D array, optional
            Reference image to use to perform pre-processing. If None,
            the first image of each position will be used.
            The default is None.
        """
        LOGGER.info("Starting pre-processing")

        if set(all_frames.dims) != {"frame", "channel", "y", "x"}:
            LOGGER.critical("Invalid number of dimensions for input frames")
            error_msg = "Invalid shape for input frames."
            raise ValueError(error_msg)
        self.shape = (len(all_frames.y), len(all_frames.x))

        # If no reference frame provided, read first frame from reader
        if reference is None:
            reference = all_frames.isel(frame=0, channel=0).to_numpy()

        # Rotation correction
        if self.config.correct_rotation:
            self.rotate = imgops.deskew(reference)
            LOGGER.info("Rotation correction: %d degrees", self.rotate)

            all_frames = imgops.rotate(all_frames, self.rotate)
            reference = imgops.rotate(reference, self.rotate)

        # Find ROIs
        if "rois" in self.config.models:
            roi_boxes = Position.find_roi_boxes(reference, self.config)
            if not roi_boxes:
                LOGGER.critical("No chamber detected. Check images and settings.")
                error_msg = "No ROI detected."
                raise ValueError(error_msg)
        else:
            roi_boxes = [CroppingBox.full(reference)]

        LOGGER.info("%d RoI detected.", len(roi_boxes))

        if self.config.correct_drift:
            driftcorbox, template = imgops.drift_template(
                roi_boxes,
                reference,
                whole_frame=self.config.whole_frame_drift,
            )

            self.drift_values = imgops.compute_drift(
                all_frames[:, 0, :, :],
                driftcorbox,
                template,
            )

            da_drift_values = xr.DataArray(
                self.drift_values,
                coords={"frame": all_frames.frame},
                dims=("frame", "xy"),
            )

            all_frames = imgops.correct_drift(all_frames, da_drift_values)

        self.rois = [
            ROI(
                stack=box.crop(all_frames),
                roi_nb=iroi,
                first_frame=frames[0],
                box=box,
                config=self.config,
            )
            for iroi, box in enumerate(roi_boxes)
        ]

    @staticmethod
    def find_roi_boxes(
        reference: Image, config: Config, min_overlap_crop: int = 24
    ) -> list[CroppingBox]:
        """
        Use U-Net to detect ROIs (chambers etc...).

        Parameters
        ----------
        reference : Image
            Reference image to use to detect ROIs.
        config : Config
            DeLTA configuration object.
        min_overlap_crop : int, optional
            Minimum overlap between windows in pixels. Default is 24.

        Returns
        -------
        boxes : List[CroppingBox]
            List of ROI boxes.

        """
        model_config = config.models["rois"]
        if reference.ndim != 2:
            err = (
                f"The reference must be an image but it is of shape {reference.shape}."
            )
            raise ValueError(err)

        # Rescale pixel values between 0 and 1 for the old model
        reference = (reference - reference.min()) / (reference.max() - reference.min())

        # Resize
        if model_config.tolerable_resizing_factor < 0:
            LOGGER.critical(
                "Parameter config.tolerable_resizing_rois must be positive."
            )
            error_msg = "config.tolerable_resizing_rois is negative."
            raise ValueError(error_msg)

        new_shape = tuple(
            target
            if ref < target * (model_config.tolerable_resizing_factor + 1.0)
            else ref
            for ref, target in zip(
                reference.shape, model_config.target_size, strict=True
            )
        )
        new_shape = cast("tuple[int, int]", new_shape)  # for mypy

        if reference.shape != new_shape:
            LOGGER.info("Resizing reference from %s to %s", reference.shape, new_shape)
        reference_resized = imgops.resize_image(reference, new_shape)

        # Crop out windows
        inputs, win_y, win_x = imgops.create_windows(
            image=reference_resized,
            target_size=model_config.target_size,
            min_overlap=min_overlap_crop,
        )
        LOGGER.info("Cropped out %d window(s) for ROI identification.", inputs.shape[0])

        # Predict
        logits = model_config.model().predict(inputs[:, :, :, np.newaxis], verbose=0)
        rois_pred = imgops.stitch_pic(logits[..., 0], win_y, win_x)

        # Clean up
        rois_mask = imgops.postprocess(
            imgops.resize_image(np.squeeze(rois_pred), reference.shape),
            min_size=model_config.min_area,
        )

        # Get boxes
        # Implementation note: cv2.findContours (even including
        # cv2.boundingRect) is about twice as fast as
        # cv2.connectedComponentsWithStats here.
        roi_boxes = []
        contours = imgops.find_contours(rois_mask)
        for chamber in contours:
            xtl, ytl, boxwidth, boxheight = cv2.boundingRect(chamber)
            box = CroppingBox(
                xtl=xtl - int(0.05 * boxwidth),
                ytl=ytl - int(0.05 * boxheight),
                xbr=xtl + int(1.05 * boxwidth),
                ybr=ytl + int(1.05 * boxheight),
            )
            roi_boxes.append(box)

        # Sort the ROIs by the axes that where they are the most spread
        xrange = max(box.xtl for box in roi_boxes) - min(box.xtl for box in roi_boxes)
        yrange = max(box.ytl for box in roi_boxes) - min(box.ytl for box in roi_boxes)
        if xrange > yrange:
            roi_boxes.sort(key=lambda box: box.xtl)
        else:
            roi_boxes.sort(key=lambda box: box.ytl)

        return roi_boxes

    def segment(self, frames: range, *, progress_bar: bool = False) -> None:
        """
        Segment cells in all ROIs in position.

        Parameters
        ----------
        frames : range
            Frames to run.
        progress_bar : bool, optional (default False)
            Display a progress bar.
        """
        LOGGER.info("Starting segmentation (%d frames)", len(frames))

        segmentation_model = self.config.models["seg"].model()

        with logging_redirect_tqdm():
            for roi in tqdm(
                self.rois, desc="ROIs", disable=len(self.rois) == 1 or not progress_bar
            ):
                roi.segment(frames, segmentation_model)

    def track(self, frames: range, *, progress_bar: bool = False) -> None:
        """
        Track cells in all ROIs in position.

        Parameters
        ----------
        frames : range
            Frames to track.
        progress_bar : bool, optional (default False)
            Display a progress bar.
        """
        LOGGER.info("Starting tracking (%d frames)", len(frames))

        tracking_model = self.config.models["track"].model()

        with logging_redirect_tqdm():
            for roi in tqdm(
                self.rois, desc="ROIs", disable=len(self.rois) == 1 or not progress_bar
            ):
                roi.track(frames, tracking_model, progress_bar=progress_bar)

    def compute_growthrates(self, frames: range, smooth_frames: int = 9) -> None:
        """
        Extract features for all ROIs in frames.

        Parameters
        ----------
        frames : range
            Frames to run.
        smooth_frames : int, default 9
            Size of the centered window over which to smooth the growth rate.
        """
        LOGGER.info("Starting growthrate computation (%d frames)", len(frames))

        for roi in self.rois:
            roi.lineage.compute_growthrates("area", smooth_frames=smooth_frames)
            roi.lineage.compute_growthrates("length", smooth_frames=smooth_frames)

    def save(
        self,
        filename: str | Path | None = None,
        frames: range | None = None,
        reader: utils.XPReader | None = None,
        save_as: str | Sequence[str] = ("netCDF", "movie"),
        *,
        progress_bar: bool = False,
    ) -> None:
        """
        Save to disk.

        Parameters
        ----------
        filename : str or None, optional
            File name for save file. If None, the file will be saved to
            PositionXXXXXX in the current directory.
            The default is None.
        frames : range | None
            Range of frames to save. If None, all frames will be saved.
            The default is None.
        reader : utils.XPReader | None
            Only needed if saving as a movie.
        save_as : str or tuple of str, optional
            Formats to save the data to. Options are "netCDF", "movie" or
            "labeled-movie".
            The default is ("netCDF", "movie").
        progress_bar : bool, optional (default False)
            Display a progress bar.
        """
        if isinstance(save_as, str):
            save_as = (save_as,)

        if filename is None:
            filename = f"./Position{self.position_nb:06d}"
        filename = Path(filename)

        for save_fmt in save_as:
            if save_fmt == "netCDF":
                LOGGER.info("Saving to netCDF format: %s", filename.with_suffix(".nc"))
                self.to_netcdf(filename.with_suffix(".nc"), progress_bar=progress_bar)
            elif save_fmt in {"movie", "labeled-movie"}:
                LOGGER.info("Saving results movie: %s", filename.with_suffix(".mp4"))
                if reader is None:
                    error_msg = "If saving as movie, xpreader cannot be None."
                    raise ValueError(error_msg)
                movie = self.results_movie(
                    reader, frames, with_labels=save_fmt == "labeled-movie"
                )
                utils.write_video(movie, filename.with_suffix(".mp4"), verbose=False)
            else:
                LOGGER.error("Saving format not understood: %s.", save_fmt)

    @classmethod
    def load_netcdf(cls, filename: str | Path) -> "Position":
        """
        Load position from netCDF file.

        Parameters
        ----------
        filename : str or Path
            File name for the save file.

        Returns
        -------
        position : pipeline.Position object
            Reloaded position object.
        """
        with nc.Dataset(filename, mode="r") as data:
            position_nb = int(data.position_nb)
            rotate = float(data.rotate)
            try:
                shape = (int(data.shape[0]), int(data.shape[1]))
            except AttributeError:
                LOGGER.warning("Loading from an older version of the data")
                shape = (0, 0)
            try:
                config = delta.config.Config.deserialize(data.config)
            except JSONDecodeError:
                LOGGER.warning(
                    "The configuration stored in this nc file is deprecated. "
                    "It will not be possible to read it anymore in a future DeLTA version. "
                    "To avoid that, just load and save this file with this DeLTA version: "
                    "`delta.pipeline.Position.load_netcdf(path).to_netcdf(path)`"
                )
                old_config = delta.config.OldConfig(**ast.literal_eval(data.config))
                config = old_config.to_tomlconfig()
            if data.drift_x.ndim == 0:
                drift_values = [(data.drift_x, data.drift_y)]
            else:
                drift_values = list(zip(data.drift_x, data.drift_y, strict=True))
        position = cls(position_nb=position_nb, config=config)
        position.rotate = rotate
        position.shape = shape
        position.drift_values = drift_values
        while True:
            try:
                roi = ROI.load_netcdf(filename, group=f"roi{len(position.rois):02}")
                position.rois.append(roi)
            except OSError as err:
                if "group not found" in err.args[0]:
                    break
                error_msg = "Could not read file."
                raise OSError(error_msg) from err
        if position.shape == (0, 0):
            LOGGER.warning("Reconstructing `shape` information from rois")
            LOGGER.warning("Might be incorrect")
            min_xtl = min(roi.box.xtl for roi in position.rois)
            min_ytl = min(roi.box.ytl for roi in position.rois)
            max_xbr = max(roi.box.xbr for roi in position.rois)
            max_ybr = max(roi.box.ybr for roi in position.rois)
            position.shape = (max_ybr - min_ytl, max_xbr - min_xtl)
        return position

    def clear(self) -> None:
        """Clear Position-specific variables from memory (can be loaded back with load())."""
        LOGGER.info("Clearing variables from memory")
        for k in self.__dict__:
            setattr(self, k, None)

    def results_movie(
        self,
        reader: utils.XPReader,
        frames: range | None = None,
        *,
        with_labels: bool = False,
    ) -> list[npt.NDArray[np.uint8]]:
        """
        Generate movie illustrating segmentation and tracking.

        Parameters
        ----------
        reader : utils.XPReader
            XPReader object (needed to reconstruct the movie in case of mothermachines).
        frames : range | None
            Range of frames to use for the movie.  If None, all of them will be used.
            The default is None.
        with_labels : bool
            Add cellids to the movie next to each cell.

        Returns
        -------
        movie : list of 3D numpy arrays
            List of compiled movie frames
        """
        return _position_to_movie(self, reader, frames, with_labels=with_labels)

    def labels(
        self,
        frames: range | None = None,
        *,
        undo_corrections: bool = True,
    ) -> list[Labels]:
        """
        Generate full-size frames with labelled cells.

        Parameters
        ----------
        frames : range | None
            Range of frames indexes to generate labelled images for.
            If None, all of them will be used. The default is None.
        undo_corrections : bool
            If True, undo drift and rotation corrections to match the original
            input images. The default is True.

        Returns
        -------
        labels : list[Labels]
            List of labelled frames

        """
        return _position_to_labels(self, frames, undo_corrections=undo_corrections)


class ROI:
    """ROI processor object."""

    def __init__(
        self,
        stack: xr.DataArray,
        roi_nb: int,
        first_frame: int,
        box: CroppingBox,
        config: Config,
    ) -> None:
        """
        Initialize ROI.

        Parameters
        ----------
        stack : xr.DataArray
            Image and fluo stack. Expected dimensions: (frame, channel, y, x).
            The first channel must be phase contrast imaging (used for
            segmentation), the rest are fluorescence channels (used for feature
            extraction).
        roi_nb : int
            ROI index.
        first_frame : int
            Index of the first frame (in general 0 or 1).
        box : CroppingBox
            CroppingBox for ROI.
        config : Config
            DeLTA configuration.
        """
        self.roi_nb = roi_nb
        "The ROI index number"
        self.box = box
        "ROI crop box"
        self.first_frame = first_frame
        "Index of the first frame"
        img_stack = stack.isel(channel=0)
        img_stack_min = img_stack.min(dim=("yc", "xc"))
        img_stack_max = img_stack.max(dim=("yc", "xc"))
        self.img_stack = (img_stack - img_stack_min) / (img_stack_max - img_stack_min)
        "Input images stack"
        self.fluo_stack = stack.isel(channel=slice(1, None))
        "Fluo images stack"
        self.seg_stack: list[SegmentationMask] = []
        "Segmentation images stack"
        self.lineage = Lineage()
        "Lineage object for ROI"
        self.label_stack: list[Labels] = []
        "Labelled images stack"
        self.config: Config = config
        "Configuration parameters object"
        self.scaling: tuple[float, float]
        "Resizing ratios along Y and X"

        if self.config.models["seg"].resizing_tolerable(box.shape):
            self.scaling = (
                (box.shape[0] - 1) / (self.config.models["seg"].target_size[0] - 1),
                (box.shape[1] - 1) / (self.config.models["seg"].target_size[1] - 1),
            )
        else:
            self.scaling = (1.0, 1.0)

    def __str__(self) -> str:
        """Create an informal representation of the ROI."""
        s = [
            f"ROI #{self.roi_nb}",
            f" ├─ box: {self.box}",
            f" ├─ frames: {self.first_frame} - {self.first_frame + len(self.img_stack)}",
            f" ├─ scaling: {self.scaling}",
        ]
        for name, stack in [
            ("img", self.img_stack),
            ("fluo", self.fluo_stack),
            ("seg", self.seg_stack),
            ("label", self.label_stack),
        ]:
            if isinstance(stack, list):
                shape = (len(stack), *stack[0].shape)
            else:
                assert isinstance(stack, np.ndarray)
                shape = stack.shape
            if shape[0] > 0:
                s.append(f" ├─ {name}_stack: {shape}")
            else:
                s.append(f" ├─ {name}_stack: empty")
        s.append(f" └─ lineage: lineage with {len(self.lineage.cells)} cell(s)")
        return "\n".join(s)

    def compare(self, other: object, level: int = 0) -> list | None:  # type: ignore[type-arg]
        """Compare this ROI with another and print the differences."""
        diffs: list[str | list] = []  # type: ignore[type-arg]
        if not isinstance(other, ROI):
            diffs.append(utils.color_diff("", "ROI", type(other)))
        else:
            diffs.append(f"ROI #{self.roi_nb}")
            for key in self.__dict__:
                if key.endswith("stack"):
                    diffa = utils.compare_arrays(
                        np.array(self.__dict__[key]),
                        np.array(other.__dict__[key]),
                        name=key,
                    )
                    if len(diffa) > 1:
                        diffs.append(diffa)
                elif key == "lineage":
                    diff = self.lineage.compare(other.lineage, level=level + 1)
                    assert diff is not None
                    if len(diff) > 1:
                        diffs.append(diff)
                elif self.__dict__[key] != other.__dict__[key]:
                    diffs.append(
                        utils.color_diff(
                            f"{key}: ", self.__dict__[key], other.__dict__[key]
                        )
                    )
        if level == 0:
            utils.print_diffs(diffs)
            return None
        return diffs

    def to_xarray(self) -> xr.Dataset:
        """
        Convert the ROI into a `xarray.Dataset`.

        Returns
        -------
        dataset : xr.Dataset
        """
        return _roi_to_xarray(self)

    def to_netcdf(self, filename: str | Path, **kwargs: dict[str, Any]) -> None:
        """
        Save the ROI as a netCDF file.

        This function compresses the relevant variables, so it should be more
        space-efficient than doing ``roi.to_xarray().to_netcdf(path)``.

        Parameters
        ----------
        filename : str or Path
            Path where to save the netCDF file.
        kwargs : dict
            Keyword arguments passed to ``xarray.to_netcdf``.
        """
        LOGGER.info("Saving - ROI %s", self.roi_nb)

        kwargs["encoding"] = kwargs.get(
            "encoding", {var: {"zlib": True} for var in NETCDF_COMPRESS}
        )
        dataset = self.to_xarray()
        dataset.to_netcdf(path=filename, **kwargs)

    @classmethod
    def load_netcdf(cls, filename: str | Path, group: str | None = None) -> "ROI":
        """
        Load a ROI from a netCDF file.

        Parameters
        ----------
        filename : str or Path
            Path to the netCDF file.
        group : str | None
            netCDF group to open, for example roiXX if the file is a saved position.

        Returns
        -------
        roi : ROI
            Loaded ROI.
        """
        dataset = xr.open_dataset(filename, group=group)
        return cls.from_xarray(dataset)

    @staticmethod
    def from_xarray(dataset: xr.Dataset) -> "ROI":
        """
        Create a ROI from an ``xarray.Dataset``.

        Parameters
        ----------
        dataset : xr.Dataset
            An ``xarray.Dataset`` representing a ``ROI``.

        Returns
        -------
        roi : ROI
            The corresponding ``ROI``.
        """
        return _xarray_to_roi(dataset)

    def __eq__(self, other: object) -> bool:
        """Equality function for ROI."""
        if not isinstance(other, ROI):
            return NotImplemented
        LOGGER.debug("ROI %d", self.roi_nb)
        eq_roi_nb = self.roi_nb == other.roi_nb
        if not eq_roi_nb:
            LOGGER.debug("ROIs differ by roi_nb")
        eq_box = self.box == other.box
        if not eq_box:
            LOGGER.debug("ROIs differ by box")
            LOGGER.debug(self.box)
            LOGGER.debug(other.box)
        eq_first_frame = self.first_frame == other.__dict__.get("first_frame", 0)
        if not eq_first_frame:
            LOGGER.debug("ROIs differ by first_frame")
        eq_img_stack = np.allclose(self.img_stack, other.img_stack, atol=2e-4)
        if not eq_img_stack:
            LOGGER.debug("ROIs differ by img_stack")
            try:
                np.testing.assert_allclose(self.img_stack, other.img_stack, atol=2e-4)
            except AssertionError as err:
                LOGGER.debug(err)
        eq_fluo_stack = np.allclose(self.fluo_stack, other.fluo_stack, atol=2e-4)
        if not eq_fluo_stack:
            LOGGER.debug("ROIs differ by fluo_stack")
            try:
                np.testing.assert_allclose(self.fluo_stack, other.fluo_stack, atol=2e-4)
            except AssertionError as err:
                LOGGER.debug(err)
        eq_seg_stack = np.array_equal(self.seg_stack, other.seg_stack)
        if not eq_seg_stack:
            LOGGER.debug("ROIs differ by seg_stack")
            try:
                np.testing.assert_array_equal(self.seg_stack, other.seg_stack)
            except AssertionError as err:
                LOGGER.debug(err)
        eq_label_stack = np.array_equal(self.label_stack, other.label_stack)
        if not eq_label_stack:
            LOGGER.debug("ROIs differ by label_stack")
        eq_lineage = self.lineage == other.lineage
        if not eq_lineage:
            LOGGER.debug("ROIs differ by lineage")
        eq_scaling = self.scaling == other.scaling
        if not eq_scaling:
            LOGGER.debug("ROIs differ by scaling")
        eqs = [
            eq_roi_nb,
            eq_box,
            eq_first_frame,
            eq_img_stack,
            eq_fluo_stack,
            eq_seg_stack,
            eq_label_stack,
            eq_lineage,
            eq_scaling,
        ]
        return all(eqs)

    def get_img(self, frame: int) -> Image:
        """
        Return the ROI image at a given frame.

        Parameters
        ----------
        frame : int
            Frame index.

        Returns
        -------
        image : Image
            Image of the ROI.
        """
        return np.asarray(self.img_stack.sel(frame=frame))

    def get_fluo(self, frame: int) -> Image:
        """
        Return the ROI fluo images at a given frame.

        Parameters
        ----------
        frame : int
            Frame index.

        Returns
        -------
        image : Image
            List of fluo images of the ROI.
        """
        return np.asarray(self.fluo_stack.sel(frame=frame))

    def get_seg(self, frame: int) -> SegmentationMask:
        """
        Return the ROI segmentation mask at a given frame.

        Parameters
        ----------
        frame : int
            Frame index.

        Returns
        -------
        seg : SegmentationMask
            Segmentation mask of the ROI.
        """
        return np.asarray(self.seg_stack[frame - self.first_frame])

    def get_labels(self, frame: int) -> Labels:
        """
        Return the ROI labels at a given frame.

        Parameters
        ----------
        frame : int
            Frame index.

        Returns
        -------
        labels : Labels
            Labels frame.
        """
        return self.label_stack[frame - self.first_frame]

    @staticmethod
    def chunks_predict(
        inputs: np.ndarray,
        model: keras.Model,
        chunk_size: int,
        batch_size: int | None = 1,
    ) -> Image:
        """
        Run keras model, but by splitting the input data into "chunks".

        These chunks will be processed and then retrieved before moving on to
        the next chunk. The reason for doing this is that, especially on
        smaller GPUs or long movies, keras/TF sometimes tries to move a large
        input tensor all at once on the GPU, leading to OOMs. Note that this
        is a different problem than batch size.

        Parameters
        ----------
        inputs : np.ndarray
            Input tensor to predict on.
        model : keras.Model
            Model to use.
        chunk_size : int
        batch_size : int | None
            Batch size for model predictions. This is NOT the same thing as
            chunk size. The default is 1.

        Returns
        -------
        outputs : np.ndarray
            Predictions array.
        """
        # Indices to split input array at
        splits = np.arange(chunk_size, inputs.shape[0], chunk_size)
        split_inputs = np.split(inputs, splits)

        # Run through chunks
        outputs_ = [
            model.predict(split_input, batch_size=batch_size, verbose=0)
            for split_input in split_inputs
        ]

        # Concat and return
        outputs = np.concatenate(outputs_, axis=0)
        return np.asarray(outputs)

    def segment(self, frames: range, model: keras.Model | None = None) -> None:
        """
        Segment `img_stack` and store the results in `seg_stack`.

        Parameters
        ----------
        frames : range
            Frames to run.
        model : keras.Model | None
            Segmentation model to use.  This is to avoid having to reload it
            for every ROI.  If None, will use `self.config.models["seg"].model()`.
            The default is None.
        """
        LOGGER.info("Segmentation - ROI %d", self.roi_nb)
        model = model or self.config.models["seg"].model()

        # Run through frames and compile segmentation inputs
        imgs = []
        windowss = []
        for frame in frames:
            inputs, windows = self.get_segmentation_inputs(frame)
            windows_per_frame = len(inputs)
            imgs.append(inputs)
            windowss.append(windows)
        inputs = np.concatenate(imgs)

        # Run segmentation model
        logits = ROI.chunks_predict(
            inputs,
            model,
            chunk_size=self.config.models["seg"].chunk_size,
            batch_size=self.config.models["seg"].batch_size,
        )

        # Dispatch segmentation output to ROI
        for iframe, (frame, windows) in enumerate(zip(frames, windowss, strict=True)):
            self.process_segmentation_outputs(
                logits[iframe * windows_per_frame : (iframe + 1) * windows_per_frame],
                frame=frame,
                windows=windows,
            )

    def get_segmentation_inputs(
        self, frame: int
    ) -> tuple[Image, tuple[npt.NDArray[np.int32], npt.NDArray[np.int32]] | None]:
        """
        Compile segmentation inputs for ROI.

        Parameters
        ----------
        frame : int
            Frame number for the segmentation inputs.

        Returns
        -------
        x : 4D array
            Segmentation input array. Dimensions are
            (windows, *self.config.models["seg"].target_size, 1).
        windows : tuple of 2 lists
            y and x coordinates of crop windows if any, or None.

        """
        # Crop and scale:
        i = self.get_img(frame)

        if not self.config.models["seg"].resizing_tolerable(self.box.shape):
            # Crop out windows:
            x, windows_y, windows_x = imgops.create_windows(
                i, target_size=self.config.models["seg"].target_size
            )
            # Shape x to expected format:
            x = x[:, :, :, np.newaxis]
            return x, (windows_y, windows_x)

        # Resize to unet input size (cv2 wants the reverse size)
        x = imgops.resize_image(i, self.config.models["seg"].target_size)
        # Shape x to expected format:
        x = x[np.newaxis, :, :, np.newaxis]
        return x, None

    def process_segmentation_outputs(
        self,
        logits: npt.NDArray[np.float32],
        frame: int,
        windows: tuple[npt.NDArray[np.int32], npt.NDArray[np.int32]] | None = None,
    ) -> None:
        """
        Process outputs after they have been segmented.

        Parameters
        ----------
        logits : 4D array
            Segmentation output array. Dimensions are
            (windows, *self.config.models["seg"].target_size, 1).
        frame : int
            Frame index.
        windows : tuple of 2 lists
            y and x coordinates of crop windows if any, or None.
        """
        # Stitch windows back together (if needed):
        if windows is None:
            logits = logits[0, :, :, 0]
        else:
            logits = imgops.stitch_pic(logits[..., 0], windows[0], windows[1])

        # Binarize:
        seg = imgops.binarize_threshold(logits, threshold=0).astype(np.uint8)
        # Crop out segmentation if image was smaller than target_size
        if not self.config.models["seg"].resizing_tolerable(self.box.shape):
            seg = seg[: self.img_stack[0].shape[0], : self.img_stack[0].shape[1]]
        # Area filtering:
        seg = imgops.filter_areas(seg, min_area=self.config.models["seg"].min_area)

        # Append to segmentation results stack:
        assert len(self.seg_stack) == frame - self.first_frame
        self.seg_stack.append(seg)

    def track(
        self,
        frames: range,
        model: keras.Model | None = None,
        *,
        progress_bar: bool = False,
    ) -> None:
        """
        Track cells in the ROI.

        Parameters
        ----------
        frames : range
            Frames to track.
        model : keras.Model | None
            Tracking model to use. This is to avoid having to reload the model
            for every ROI. If None, will use `self.config.models["track"].model()`.
            The default is None.
        progress_bar : bool, optional (default False)
            Display a progress bar.
        """
        LOGGER.info("Tracking - ROI %d", self.roi_nb)
        model = model or self.config.models["track"].model()

        # Run through frames and compile inputs and references
        for frame in tqdm(frames, desc="Frames", leave=None, disable=not progress_bar):
            inputs, boxes = self.get_tracking_inputs(frame=frame)

            # Predict
            if inputs.shape[0] > 0:
                logits = ROI.chunks_predict(
                    inputs,
                    model,
                    chunk_size=self.config.models["track"].chunk_size,
                    batch_size=self.config.models["track"].batch_size,
                )
            else:
                logits = np.empty(
                    shape=(0, *self.config.models["track"].target_size, 1),
                    dtype=np.float32,
                )

            # Dispatch tracking outputs
            self.process_tracking_outputs(logits, frame=frame, boxes=boxes)

    def get_tracking_inputs(self, frame: int) -> tuple[Image, list[CroppingBox]]:
        """
        Compile tracking inputs for ROI from `seg_stack`.

        Parameters
        ----------
        frame : int
            The frame to compile for.

        Raises
        ------
        RuntimeError
            Segmentation has not been completed up to frame yet.

        Returns
        -------
        inputs : 4D array or None
            Tracking input array. Dimensions are
            (previous_cells, *self.config.models["track"].target_size, 4).
        boxes : list[CroppingBox]
            Crop boxes to re-place outputs in the ROI.

        """
        # Check if segmentation data is ready:
        if len(self.seg_stack) <= frame - self.first_frame:
            error_msg = f"Segmentation incomplete - frame {frame}"
            raise RuntimeError(error_msg)

        # Get cell contours from previous frame
        if frame == self.first_frame:
            prev_cell_contours: list[imgops.Contour] = []
        else:
            labels = imgops.label_seg(self.get_seg(frame - 1))
            _, prev_cell_contours = utils.cells_in_frame(labels, return_contours=True)

        # Allocate empty tracking inputs array:
        inputs = np.empty(
            (len(prev_cell_contours), *self.config.models["track"].target_size, 4),
            dtype=np.float32,
        )

        # Get current and previous image, used as tracking inputs and resize them if needed
        curr_img = self.get_img(frame)
        prev_img = self.get_img(frame - 1) if frame > self.first_frame else curr_img
        if self.config.models["track"].resizing_tolerable(self.box.shape):
            curr_img = imgops.resize_image(
                curr_img, self.config.models["track"].target_size
            )
            prev_img = imgops.resize_image(
                prev_img, self.config.models["track"].target_size
            )
            cb = CroppingBox.full(curr_img)
            draw_offset = None
            boxes = [cb] * len(prev_cell_contours)
        else:
            # Cell-centered crop boxes
            boxes = [
                CroppingBox.tracking_box(
                    contour, self.config.models["track"].target_size
                )
                for contour in prev_cell_contours
            ]

        # Run through contours and compile inputs:
        for icontour, (contour, cb) in enumerate(
            zip(prev_cell_contours, boxes, strict=True)
        ):
            if not self.config.models["track"].resizing_tolerable(self.box.shape):
                draw_offset = (-cb.xtl, -cb.ytl)

            # Current image
            inputs[icontour, :, :, 0] = cb.crop(curr_img)

            # Segmentation mask of one previous cell (seed)
            inputs[icontour, :, :, 1] = cv2.drawContours(
                np.zeros(self.config.models["track"].target_size, dtype=np.float32),
                [contour],
                0,
                offset=draw_offset,
                color=1.0,
                thickness=cv2.FILLED,
            )

            # Previous image
            inputs[icontour, :, :, 2] = cb.crop(prev_img)

            # Segmentation of all current cells
            inputs[icontour, :, :, 3] = cb.crop(self.get_seg(frame))

        # Return tracking inputs and cropboxes
        return inputs, boxes

    def process_tracking_outputs(
        self,
        logits: npt.NDArray[np.float32],
        frame: int,
        boxes: list[CroppingBox],
    ) -> None:
        """
        Process output from tracking U-Net.

        Get poles, update lineage and create label_stack.

        Parameters
        ----------
        logits : 4D array
            Tracking output array. Dimensions are
            (previous_cells, *self.config.models["track"].target_size, 1).
        frame : int
            The frame to process for.
        boxes : list[CroppingBox]
            Crop boxes to re-place outputs in the ROI.
        """
        # Get scores and attributions:
        # Label frame but numbered 1, 2, 3, 4, etc. (temporary labels)
        labels = imgops.label_seg(self.get_seg(frame))

        if self.config.models["track"].resizing_tolerable(self.box.shape):
            # Resize labels if not cropping
            resized_labels = imgops.resize_labels(labels, self.box.shape)
            unique_cells_before = set(np.unique(labels)[1:])
            unique_cells_after = set(np.unique(resized_labels)[1:])
            if len(unique_cells_before) != len(unique_cells_after):
                LOGGER.warning(
                    "On ROI %d, segmented cells disappeared during resizing.",
                    self.roi_nb,
                )
                LOGGER.info(
                    "Don't worry about this warning if the ROI is on the edge "
                    "of the image and partially cut."
                )
                seg = self.get_seg(frame)
                for cellid in unique_cells_before - unique_cells_after:
                    seg[labels == cellid] = 0
                    labels[labels == cellid] = 0
                labels = imgops.label_seg(self.get_seg(frame))

        scores = utils.tracking_scores(labels, logits[:, :, :, 0], boxes=boxes)

        attributions = utils.attributions(scores)
        previous_cell_nbs = (
            utils.cells_in_frame(self.get_labels(frame - 1))
            if frame > self.first_frame
            else []
        )
        assert len(previous_cell_nbs) == attributions.shape[0]

        # Extract poles before resizing
        cellids, contours = utils.cells_in_frame(labels, return_contours=True)
        poles = {
            cellid: utils.find_poles(contour)
            for cellid, contour in zip(cellids, contours, strict=True)
        }
        resized_poles = {
            cellid: (
                np.asarray(np.round(p1 * self.scaling), dtype=np.int16),
                np.asarray(np.round(p2 * self.scaling), dtype=np.int16),
            )
            for cellid, (p1, p2) in poles.items()
        }

        # Extract features
        extracted_features = utils.roi_features(
            labels
            if not self.config.models["track"].resizing_tolerable(self.box.shape)
            else resized_labels,
            resized_poles,
            fluo_frames=self.get_fluo(frame),
        )

        cell_nbs: list[int | None] = [None] * attributions.shape[1]

        # Go through old cells
        for cellid, attribs in zip(previous_cell_nbs, attributions, strict=True):
            assert self.lineage.cells[cellid].last_frame == frame - 1
            attrib = attribs.nonzero()[0]
            previous_poles = self.lineage.cells[cellid].poles(frame - 1)
            if len(attrib) == 1:
                # Simple tracking event
                [n] = attrib
                features = utils.track_poles(extracted_features[n + 1], *previous_poles)
                self.lineage.extend(cellid, features)
                cell_nbs[n] = cellid
            elif len(attrib) == 2:
                # Division event
                n0, n1 = attrib
                (
                    mother_features,
                    daughter_features,
                    first_cell_is_mother,
                ) = utils.division_poles(
                    extracted_features[n0 + 1],
                    extracted_features[n1 + 1],
                    *previous_poles,
                )
                if not first_cell_is_mother:
                    n0, n1 = n1, n0
                self.lineage.extend(cellid, mother_features)
                newcellid = self.lineage.create(
                    frame, daughter_features, motherid=cellid
                )
                cell_nbs[n0] = cellid
                cell_nbs[n1] = newcellid

        # Go through new cells
        for n, attribs in enumerate(attributions.T):
            attrib = attribs.nonzero()[0]
            if len(attrib) == 1:
                # Case already treated
                continue
            # Brand new cell event: attribute poles arbitrarily
            if (
                extracted_features[n + 1].old_pole[0]
                >= extracted_features[n + 1].new_pole[0]
            ):
                extracted_features[n + 1].swap_poles()
            cellid = self.lineage.create(
                frame, extracted_features[n + 1], motherid=None
            )
            cell_nbs[n] = cellid

        assert None not in cell_nbs
        cell_nbs_ints = cast("list[int]", cell_nbs)  # for mypy
        # Recompile label frame with new labels
        labels = imgops.label_seg((labels > 0).astype(np.uint8), cell_nbs_ints)

        # Resize image:
        if self.config.models["track"].resizing_tolerable(self.box.shape):
            shape = (
                self.box.ybr - self.box.ytl,
                self.box.xbr - self.box.xtl,
            )
            labels = imgops.resize_labels(labels, shape)

        assert len(self.label_stack) == frame - self.first_frame
        self.label_stack.append(labels)

    def merge(self, cellid: int, merge_into_cellid: int) -> None:
        """
        Rename a cell (``cellid``) to merge it into another one (``merge_into_cellid``).

        For more information, see the ``Lineage.merge`` method.

        This one also updates the labels in the label stack.
        """
        self.lineage.merge(cellid, merge_into_cellid)
        for labels in self.label_stack:
            labels[labels == cellid] = merge_into_cellid

    def split(self, cellid: int, frame: int) -> int:
        """
        Break a cell lineage into two independent cell lineages.

        For more information, see the ``Lineage.split`` method.

        This one also updates the labels in the label stack.
        """
        new_cellid = self.lineage.split(cellid, frame)
        for labels in self.label_stack[frame - self.first_frame :]:
            labels[labels == cellid] = new_cellid
        return new_cellid

    def adopt(self, cellid: int, motherid: int | None) -> None:
        """
        Attribute a new mother ``motherid`` (which can be ``None``) to the cell ``cellid``.

        For more information, see the ``Lineage.adopt` method.

        This one also updates the labels in the label stack.
        """
        self.lineage.adopt(cellid, motherid)

    def pivot(self, cellid: int) -> None:
        """
        Swap the roles between cell ``cellid`` and its mother.

        For more information, see the ``Lineage.pivot`` method.

        This one also updates the labels in the label stack.
        """
        self.lineage.pivot(cellid)
        motherid = self.lineage.cells[cellid].motherid
        first_frame = self.lineage.cells[cellid].first_frame
        for labels in self.label_stack[first_frame - self.first_frame :]:
            mother = labels == motherid
            cell = labels == cellid
            labels[mother] = cellid
            labels[cell] = motherid

    def swap_poles(self, cellid: int, frame: int | None = None) -> None:
        """
        Swap the poles of the cell ``cellid`` for all the frames or for frame ``frame`` onwards.

        For more information, see the ``Lineage.swap_poles`` method.

        This one also updates the labels in the label stack.
        """
        self.lineage.swap_poles(cellid, frame)
        cell = self.lineage.cells[cellid]
        if frame is None:
            frame = cell.first_frame
        daughterid = None
        for f in range(frame + 1, cell.last_frame + 1):
            if daughterid is None:
                daughterid = cell.daughterid(f)
            if daughterid is not None:
                labels = self.get_labels(f)
                daughter = labels == daughterid
                cell = labels == cellid
                labels[daughter] = cellid
                labels[cell] = daughterid
