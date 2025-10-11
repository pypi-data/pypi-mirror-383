"""Utility functions and class definitions that are used in pipeline.py."""

import datetime
import heapq
import logging
import re
import subprocess  # noqa: S404
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Literal, overload

import bioio
import cv2
import ffmpeg
import keras
import numpy as np
import numpy.random as npr
import numpy.typing as npt
import scipy.signal as sig
import xarray as xr
from keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard
from scipy.special import logit
from termcolor import colored

from delta import imgops
from delta.imgops import Contour, CroppingBox, Image, Labels, SegmentationMask
from delta.lineage import CellFeatures, Pole

LOGGER = logging.getLogger(__name__)


@overload
def cells_in_frame(
    labels: Labels, *, return_contours: Literal[True]
) -> tuple[list[int], list[Contour]]: ...


@overload
def cells_in_frame(
    labels: Labels, *, return_contours: Literal[False] = False
) -> list[int]: ...


def cells_in_frame(
    labels: Labels, *, return_contours: bool = False
) -> list[int] | tuple[list[int], list[Contour]]:
    """
    Get numbers of cells present in frame, sorted along Y axis.

    Parameters
    ----------
    labels : 2D numpy array of uint16
        Single frame from labels stack.
    return_contours : bool, optional
        Flag to get cv2 contours.

    Returns
    -------
    cellids : list
        Cell ids.
    contours : list
        List of cv2 contours for each cell. Returned if return_contours==True.

    """
    cellids_, ind = np.unique(labels, return_index=True)

    # Sorting along Y axis & removing background
    cellids = [int(cellid) for cellid in cellids_[1:][np.argsort(ind[1:])]]

    if not return_contours:
        return cellids

    # Get opencv contours:
    contours = [
        imgops.find_contours((labels == cellid).astype(np.uint8))[0]
        for cellid in cellids
    ]

    return cellids, contours


# %% Poles


def find_poles(
    contour: Contour,
) -> tuple[Pole, Pole]:
    """
    Get cell poles from contour.

    Parameters
    ----------
    contour : Contour
        OpenCV contour of a cell

    Returns
    -------
    poles : (Pole, Pole)
        Two cell poles in arbitrary order

    """
    # Get smoothed curvature & first pole
    curvature = contour_curvature(contour[:, 0, :])
    p1 = np.argmin(curvature)

    # Look for second pole in other half of curvature
    other_half = np.arange(
        p1 + len(curvature) // 4,
        p1 + 3 * (len(curvature) // 4) + 1,
        dtype=np.uint16,
    ) % len(curvature)
    p2 = other_half[np.argmin(curvature[other_half])]

    pole1 = contour[p1, 0, ::-1].astype(np.int16)
    pole2 = contour[p2, 0, ::-1].astype(np.int16)

    return pole1, pole2


def contour_curvature(
    contour: Contour, stride: int | None = None
) -> npt.NDArray[np.float32]:
    """
    Compute the curvature of a cell's contour.

    Inspired by https://stackoverflow.com/a/68757937.

    Parameters
    ----------
    contour: Contour
        Cell contour to consider
    stride: int | None, optional
        Distance between contour points to compute curvature.
        If ``None`` (default), it will use the default value 5 but reduce it
        if the contour is too small.

    Returns
    -------
    npt.NDArray[np.float32]
        Curvature along the contour

    """
    if len(contour) < 4:
        err = "the contour must have at least 4 edges"
        raise ValueError(err)
    if stride is None:
        stride = min(len(contour) // 4, 5)
    elif stride < 1:
        err = "the stride must be at least 1"
        raise ValueError(err)
    if 4 * stride > len(contour):
        err = (
            "for accurate results, the stride should be less "
            "than a quarter of the contour length"
        )
        raise ValueError(err)

    contour = contour.astype(np.float64)

    kwargs = {
        "window_length": 2 * stride + 1,
        "polyorder": 2,
        "axis": 0,
        "mode": "wrap",
    }

    f1 = sig.savgol_filter(contour, deriv=1, **kwargs)
    f2 = sig.savgol_filter(contour, deriv=2, **kwargs)

    cross_product_z = f1[:, 0] * f2[:, 1] - f1[:, 1] * f2[:, 0]
    denominator = (f1**2).sum(axis=1) ** 1.5

    curvature = cross_product_z / np.maximum(denominator, 1e-6)

    return curvature


def eucl(p1: npt.NDArray[Any], p2: npt.NDArray[Any]) -> float:
    """
    Euclidean point to point distance.

    Parameters
    ----------
    p1 : 1D array
        Coordinates of first point.
    p2 : 1D array
        Coordinates of second point.

    Returns
    -------
    float
        Euclidean distance between p1 and p2.

    """
    return float(np.linalg.norm(p1 - p2))


def track_poles(features: CellFeatures, prev_old: Pole, prev_new: Pole) -> CellFeatures:
    """
    Track poles of a cell to the previous old and new poles.

    Parameters
    ----------
    features : CellFeatures
        Cell features object with possibly switched poles.
    prev_old : Pole
        Previous old pole of the cell.
    prev_new : Pole
        Previous new pole of the cell.

    Returns
    -------
    features : CellFeatures
        Cell features object with correct poles.

    """
    if (
        eucl(features.old_pole, prev_old) ** 2 + eucl(features.new_pole, prev_new) ** 2
        >= eucl(features.old_pole, prev_new) ** 2
        + eucl(features.new_pole, prev_old) ** 2
    ):
        features.swap_poles()

    return features


def division_poles(
    features1: CellFeatures,
    features2: CellFeatures,
    prev_old: Pole,
    prev_new: Pole,
) -> tuple[CellFeatures, CellFeatures, bool]:
    """
    Identify which poles belong to the mother and which to the daughter.

    Parameters
    ----------
    features1 : CellFeatures
        Features of one of the 2 cells after division (with possibly swapped poles).
    features2 : CellFeatures
        Features of the other of the 2 cells after division (with possibly swapped poles).
    prev_old : Pole
        Previous old pole of the cell.
    prev_new : Pole
        Previous new pole of the cell.

    Returns
    -------
    mother : CellFeatures
    daughter : CellFeatures
    first_cell_is_mother : bool

    """
    # Find new new poles (2 closest of the poles of the new cells):
    old1_to_2 = min(
        eucl(features1.old_pole, features2.old_pole),
        eucl(features1.old_pole, features2.new_pole),
    )
    new1_to_2 = min(
        eucl(features1.new_pole, features2.old_pole),
        eucl(features1.new_pole, features2.new_pole),
    )
    if old1_to_2 < new1_to_2:
        features1.swap_poles()
    if eucl(features1.new_pole, features2.old_pole) < eucl(
        features1.new_pole, features2.new_pole
    ):
        features2.swap_poles()
    # Now poles are correctly attributed, we will now determine which cell is the mother

    # Track poles closest to old and new pole from previous cell:
    if (
        eucl(features1.old_pole, prev_old) ** 2
        + eucl(features2.old_pole, prev_new) ** 2
        < eucl(features1.old_pole, prev_new) ** 2
        + eucl(features2.old_pole, prev_old) ** 2
    ):
        # cell 1 is mother, cell 2 is daughter
        first_cell_is_mother = True
        mother, daughter = features1, features2

    else:
        # cell 2 is mother, cell 1 is daughter
        first_cell_is_mother = False
        mother, daughter = features2, features1

    return (mother, daughter, first_cell_is_mother)


# %% Lineage


def tracking_scores(
    labels: Labels,
    logits: npt.NDArray[np.float32],
    boxes: list[CroppingBox],
) -> npt.NDArray[np.float32]:
    """
    Get overlap scores between input/target cells and tracking outputs.

    Parameters
    ----------
    labels : 2D array of np.uint16
        Labelled image (untracked) of the current frame.
    logits : 3D array of floats (previous_cells, sizex, sizey)
        Tracking U-Net output.
    boxes : list[CroppingBox]
        Cropping boxes to re-place output prediction masks in the
        original coordinates to index the labels frame.

    Returns
    -------
    scores : 2D array of floats (previous_cells, current_cells)
        Overlap scores matrix between tracking predictions and current
        segmentation mask for each new-old cell.

    """
    # Compile scores:
    scores = np.zeros([logits.shape[0], labels.max()], dtype=np.float32)
    for o, (logits_cell, box) in enumerate(zip(logits, boxes, strict=True)):
        # Find pixels with more than 5% probability
        nz_y, nz_x = list((logits_cell > logit(0.05)).nonzero())

        # Find coordinates of hits in source image coordinates
        nz_y += box.ytl
        nz_x += box.xtl

        # Clean nz hits outside of image
        to_keep_y = (0 <= nz_y) & (nz_y < labels.shape[0])  # noqa: SIM300
        to_keep_x = (0 <= nz_x) & (nz_x < labels.shape[1])  # noqa: SIM300
        nz_y = nz_y[to_keep_x & to_keep_y]
        nz_x = nz_x[to_keep_x & to_keep_y]

        # Compute number of hits per cell:
        cells, counts = np.unique(labels[nz_y, nz_x], return_counts=True)

        # Compile score for these cells:
        for icell, count in zip(cells, counts, strict=True):
            if icell > 0:
                scores[o, icell - 1] = count

    # Get areas for each cell:
    _, areas = np.unique(labels, return_counts=True)

    return scores / areas[1:]


def attributions(scores: npt.NDArray[np.float32]) -> npt.NDArray[np.bool_]:
    """
    Get attribution matrix from tracking scores.

    Parameters
    ----------
    scores : 2D array of floats
        Tracking scores matrix as produced by the tracking_scores function.

    Returns
    -------
    attrib : 2D array of bools
        Attribution matrix. Cells from the old frame (axis 0) are attributed to
        cells in the new frame (axis 1). Each old cell can be attributed to 1
        or 2 new cells.

    """
    attrib = np.zeros(scores.shape, dtype=bool)

    # Precomputing for each old cell its second best score to a new cell
    if scores.shape[1] > 1:
        two_best_new_cells = np.argpartition(scores, -2)[:, -2:]
    else:
        # If 0 new cells the loop won't execute
        # If 1 new cell it is a degenerate case
        two_best_new_cells = np.zeros_like(scores)

    for new in range(scores.shape[1]):
        # Best-to-worst score of old cells for n-th new cell
        best_old = np.argsort(-scores[:, new])
        # Run through old cells from best to worst:
        for o_best in best_old:
            # If score gets too low, stop:
            if scores[o_best, new] < 0.2:
                break
            # Check if new cell is at least 2nd best for this old cell:
            if new in two_best_new_cells[o_best]:
                attrib[o_best, new] = True
                break

    return attrib


# %% Image files


class XPReader:
    """Class to read experiment files from single files or from file sequences in folders."""

    def __init__(
        self,
        path: Path | str,
    ) -> None:
        """
        Initialize experiment reader.

        Parameters
        ----------
        path : Path or str
            Path to experiment file or template to experiment files.
            If a template, it should contain the patterns `{p}`, `{t}`, or
            `{c}` to represent respectively position numbers, frame numbers, or
            channel numbers.  The patterns can be repeated if the information
            is repeated in the file names.
            Valid examples:
            - "Pos{p}_Cha{c}_Fra{t}.tif"
            - "p{p}c{c}t{t}.tif"
            - "xy {p} - fluo {c} - timepoint {t} .TIFF"
            - "experiment_2023-05-11.nd2"
            - "multitiff_2023-05-11.tiff"

        Raises
        ------
        ValueError
            If the filenames in the experimental directory do not follow the
            correct format, a ValueError will be raised.
        """
        path = Path(path)

        # Set default parameters
        self.path = path.absolute()
        "File or folder name for the experiment"

        # Init base parameters:
        self.filetype = None
        "Type / extension of `filehandle`"
        self.filehandle: Any
        "Handle to file reader or base directory"
        self.positions: tuple[int, ...]
        "Positions in the experiment"
        self.channels: tuple[int, ...]
        "Imaging channels"
        self.channel_names: tuple[str, ...] | None = None
        "Names of the imaging channels (optional)"
        self.frames: range
        "Frame numbers in the experiment"
        self.x: int
        "Size of images along X axis"
        self.y: int
        "Size of images along Y axis"
        self.dtype: npt.DTypeLike
        "Datatype of images"

        LOGGER.info("Detecting image files...")

        if "{p}" in str(path) or "{c}" in str(path) or "{t}" in str(path):
            # Experiment is stored as individual image files in a folder
            # and self.path is a prototype
            self.filetype = "dir"

            # Determine the base directory of the images
            while "{p}" in str(path) or "{c}" in str(path) or "{t}" in str(path):
                path = path.parent
            self.filehandle = path.absolute()

            # Get the templated suffix
            spath = str(self.path.relative_to(self.filehandle))

            # Create a regular expression from the prototype to find digit groups
            regexp = re.compile(
                self.path.as_posix().format(p=r"(\d+)", c=r"(\d+)", t=r"(\d+)")
            )

            # Extract fileorder from prototype
            fileorder = [
                b
                for a, b, c in zip(spath[:-2], spath[1:-1], spath[2:], strict=True)
                if a + c == "{}"
            ]

            def parse(
                match: re.Match[str], fileorder: list[str]
            ) -> tuple[int, int, int]:
                """Associate the matched groups with fileorder labels."""
                values: dict[str, int] = {}
                for pattern, group in zip(fileorder, match.groups(), strict=True):
                    if pattern in values and values[pattern] != int(group):
                        error_msg = (
                            f"There is a file with two different values ({values[pattern]} "
                            f"and {int(group)}) for the same pattern ({pattern})."
                        )
                        raise ValueError(error_msg)
                    values[pattern] = int(group)
                return (values.get("p", 0), values.get("c", 0), values.get("t", 0))

            # Run through potential file paths, parse the arguments and
            # associate them with the full path
            self.image_paths: dict[tuple[int, int, int], Path] = {}
            try:
                for imgpath in self.filehandle.glob(spath.format(p="*", c="*", t="*")):
                    match = regexp.fullmatch(imgpath.as_posix())
                    if not match:
                        continue
                    self.image_paths[parse(match, fileorder)] = imgpath
            except ValueError as err:
                error_msg = "The prototype is not correct."
                raise ValueError(error_msg) from err

            if not self.image_paths:
                error_msg = "No images have been found. Check the prototype?"
                raise RuntimeError(error_msg)

            # Explore image_paths to determine ranges of positions, channels and frames
            # Get list of positions
            if "{p}" in spath:
                self.positions = tuple(sorted({p for p, _, _ in self.image_paths}))
            else:
                self.positions = (0,)
            # Get list of channels
            if "{c}" in spath:
                self.channels = tuple(sorted({c for _, c, _ in self.image_paths}))
            else:
                self.channels = (0,)
            # Get range of frames (needs to be a range because of tracking)
            if "{t}" in spath:
                min_frame = min(t for _, _, t in self.image_paths)
                max_frame = max(t for _, _, t in self.image_paths)
                self.frames = range(min_frame, max_frame + 1)
            else:
                self.frames = range(1)  # I guess this shouldn't really happen

            # Load any image, get image data from it
            imgpath = next(iter(self.image_paths.values()))
            bioimg = bioio.BioImage(imgpath)
        else:
            # Experiment is stored as a single file
            self.filetype = "img"
            # Use BioIO for single-file image formats
            bioimg = bioio.BioImage(self.path)
            self.positions = tuple(range(len(bioimg.scenes)))
            self.channel_names = tuple(bioimg.channel_names)
            self.channels = tuple(range(len(self.channel_names)))
            self.frames = range(bioimg.dims.T)
            self.filehandle = bioimg

        self.x = bioimg.dims.X
        self.y = bioimg.dims.Y
        self.dtype = bioimg.dtype

        LOGGER.info(
            "Found images of size %dx%d and dtype %s.", self.x, self.y, self.dtype
        )
        positions = f"{self.positions[0]}-{self.positions[-1]}"
        LOGGER.info("  %d positions (%s)", len(self.positions), positions)
        if self.channel_names is not None:
            channels = ", ".join(self.channel_names)
        else:
            channels = f"{self.channels[0]}-{self.channels[-1]}"
        LOGGER.info("  %d channels (%s)", len(self.channels), channels)
        LOGGER.info(
            "  %d time points (%d-%d)",
            len(self.frames),
            self.frames[0],
            self.frames[-1],
        )

    def __str__(self) -> str:
        """Construct a string with an informal representation of the object."""
        s = [
            "XPReader",
            f" ├─ path: {self.path}",
            f" ├─ filetype: {self.filetype}",
            f" ├─ filehandle: {self.filehandle}",
            f" ├─ positions: {self.positions}",
            f" ├─ channels: {self.channels}",
            f" ├─ channel_names: {self.channel_names}",
            f" ├─ frames: {self.frames}",
            f" ├─ image x size: {self.x}",
            f" ├─ image y size: {self.y}",
            f" └─ dtype: {self.dtype}",
        ]
        return "\n".join(s)

    def image_path(self, position: int, channel: int | str, frame: int) -> Path:
        """
        Generate full filename for specific frame based on position, channel and frame.

        Parameters
        ----------
        position : int
            Position/series index.
        channel : int | str
            Imaging channel index, index or name.
        frame : int
            Frame/timepoint index.

        Returns
        -------
        string
            Filename.

        """
        if isinstance(channel, str):
            channel = self.channels.index(channel)

        return self.image_paths[position, channel, frame]

    def images(
        self,
        position: int,
        channels: int | str | Sequence[int | str] | None = None,
        frames: range | None = None,
        rotate: float | None = None,
    ) -> xr.DataArray:
        """
        Get images from experiment.

        Parameters
        ----------
        position : int
            The position index for which the frames are requested.
        channels : int or str or sequence of ints or strs, optional
            The frames from the channel index or indexes passed as an integer,
            string, or sequence of integers or strings will be returned.
            If None is passed, all thannels are returned. The default is None.
        frames : range, optional
            Range of frames returned.  If None is passed, all frames are
            returned.
            The default is None.
        rotate : float, optional
            Rotation to apply to the image (in degrees).
            The default is None.

        Raises
        ------
        ValueError
            If channel names are not correct.

        Returns
        -------
        xarray.DataArray
            Concatenated frames as requested by the different input options.
            The array is 4-dimensional, with the shape being: (frames,
            channels, Y, X).

        """
        if channels is None:
            channels = self.channels
        elif isinstance(channels, int):
            channels = (channels,)
        elif isinstance(channels, str):
            channels = (self.channels.index(channels),)
        else:
            channels = tuple(
                c if isinstance(c, int) else self.channels.index(c) for c in channels
            )

        if frames is None:
            frames = self.frames

        # Allocate memory
        output = np.empty(
            [len(frames), len(channels), self.y, self.x], dtype=np.float32
        )

        # Set position (if single file)
        if self.filetype == "img":
            self.filehandle.set_scene(position)

        # Load images
        for ichannel, channel in enumerate(channels):
            for iframe, frame in enumerate(frames):
                if self.filetype == "dir":
                    image_path = self.image_path(position, channel, frame)
                    try:
                        image = imgops.read_image(image_path)
                    except ValueError as err:
                        err_msg = "image_path incorrect"
                        raise ValueError(err_msg) from err
                elif self.filetype == "img":
                    image = self.filehandle.get_image_data("YX", C=channel, T=frame)
                    image = imgops.rescale_image(image)

                # Add to output array
                output[iframe, ichannel, :, :] = image

        if rotate is not None:
            output = imgops.rotate(output, rotate)

        coords = {
            "frame": frames,
            "channel": list(channels),
            "y": range(self.y),
            "x": range(self.x),
        }
        dims = ("frame", "channel", "y", "x")
        da = xr.DataArray(output, coords=coords, dims=dims)
        return da


# %% Saving & Loading results


def random_colors(
    cellids: Sequence[int], seed: int = 0
) -> dict[int, tuple[float, float, float]]:
    """
    Generate list of random hsv colors.

    Parameters
    ----------
    cellids : Iterable (for example list, tuple or iterator)
        Cellids which should be assigned random colors.
    seed : int, optional
        Random seed used to shuffle colors.

    Returns
    -------
    colors : dict[int, tuple[float, float, float]]
        Dictionary of cellids to colors (RGB values in [0,1]).

    """
    if not cellids:
        return {}

    # Get colors
    gradient = np.linspace(0, 256, len(cellids), endpoint=False, dtype=np.uint8)
    colors = cv2.applyColorMap(gradient, cv2.COLORMAP_HSV).squeeze(axis=1)
    colors = colors.astype(np.float64) / 255

    # Shuffle colors
    rng = npr.default_rng(seed)
    rng.shuffle(colors)

    return {cellid: tuple(color) for cellid, color in zip(cellids, colors, strict=True)}


def write_video(
    images: list[npt.NDArray[np.uint8]],
    filename: str | Path,
    crf: int = 20,
    verbose: int = 1,
) -> None:
    """
    Write images stack to video file with h264 compression.

    Parameters
    ----------
    images : 4D numpy array
        Stack of RGB images to write to video file.
    filename : str or Path
        File name to write video to. (Overwritten if exists)
    crf : int, optional
        Compression rate. 'Sane' values are 17-28. See
        https://trac.ffmpeg.org/wiki/Encode/H.264
        The default is 20.
    verbose : int, optional
        Verbosity of console output.
        The default is 1.
    """
    # Initialize ffmpeg parameters:
    height, width, _ = images[0].shape
    if height % 2 == 1:
        height -= 1
    if width % 2 == 1:
        width -= 1
    quiet = [] if verbose else ["-loglevel", "error", "-hide_banner"]
    process = (
        ffmpeg.input(
            "pipe:",
            format="rawvideo",
            pix_fmt="rgb24",
            s=f"{width}x{height}",
            r=7,
        )
        .output(
            str(filename),
            pix_fmt="yuv420p",
            vcodec="libx264",
            crf=crf,
            preset="veryslow",
        )
        .global_args(*quiet)
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    # Write frames:
    for frame in images:
        process.stdin.write(frame[:height, :width].astype(np.uint8).tobytes())

    # Close file stream:
    process.stdin.close()

    # Wait for processing + close to complete:
    process.wait()


# %% Feature extraction


def roi_features(
    labels: Labels,
    poles: dict[int, tuple[Pole, Pole]],
    fluo_frames: Image,
) -> dict[int, CellFeatures]:
    """
    Extract single-cell morphological and fluorescence features.

    Parameters
    ----------
    labels : Labels
        Labels image of numbered cell regions.
    poles : dict[int, tuple[Pole, Pole]],
        Dict of cellid to poles.
    fluo_frames : Image
        Array of fluo frames to extract fluorescence from. Dimensions are
        (size_x, size_y, fluo_channels). The number of fluo_channels must match
        the number of fluo features to extract.

    Returns
    -------
    cell_features : dict[int, CellFeatures]
        Dictionary that associates cellids and CellFeatures.
    """
    # Cell numbers and contours:
    cellids, contours = cells_in_frame(labels, return_contours=True)

    # Compute distance map once:
    distance_map = imgops.distance_transform_labels(labels)

    cell_features = {}
    # Loop through cells in image, extract single-cell features:
    for cellid, contour in zip(cellids, contours, strict=True):
        mask = (labels == cellid).astype(np.uint8)

        fluo_values = (2**16 - 1) * cell_fluo(
            fluo_frames, mask
        )  # Does this assume we always have uint16 fluo images?

        width, length = cell_width_length(poles[cellid], distance_map)

        cell_features[cellid] = CellFeatures(
            new_pole=poles[cellid][0],  # Old vs New will be checked later
            old_pole=poles[cellid][1],
            edges=image_edges(contour, mask.shape),
            width=width,
            length=length,
            area=cell_area(contour),
            perimeter=cell_perimeter(contour),
            fluo=list(fluo_values),
        )

    return cell_features


def image_edges(contour: Contour, shape: tuple[int, int]) -> str:
    """
    Identify if cell touches image borders.

    Parameters
    ----------
    contour : list
        Single cell contour from cv2 findcontours.
    shape : tuple[int, int]
        Shape of the image.

    Returns
    -------
    edge_str : str
        String describing edges touched by the cell. Can be a combination of
        the following strs: '-x', '+x', '-y', '+y'. Empty otherwise.

    """
    edge_str = ""
    if any(contour[:, 0, 0] == 0):
        edge_str += "-x"
    if any(contour[:, 0, 0] == shape[1] - 1):
        edge_str += "+x"
    if any(contour[:, 0, 1] == 0):
        edge_str += "-y"
    if any(contour[:, 0, 1] == shape[0] - 1):
        edge_str += "+y"

    return edge_str


def cell_width_length(
    cell_poles: tuple[Pole, Pole], distance_map: Image
) -> tuple[float, float]:
    """
    Measure width and length of single cell.

    Parameters
    ----------
    cell_poles : tuple[Pole, Pole]
        Poles of the cell.
    distance_map : Image
        Distance transform of the segmentation mask.

    Returns
    -------
    width : float
        Cell width.
    length : float
        cell length.

    """
    centerline = pathfinding(1 / (distance_map + 1e-3), *cell_poles)

    width = 2 * distance_map[centerline[:, 0], centerline[:, 1]].mean()
    length = np.linalg.norm(np.diff(centerline, axis=0), axis=1).sum()

    return width, length


def cell_area(contour: Contour) -> float:
    """
    Area of a single cell.

    Parameters
    ----------
    contour : list
        Single cell contour from cv2 findcontours.

    Returns
    -------
    area : float
        Cell area

    """
    area = cv2.contourArea(contour)

    # Growth rate computation doesn't like zero areas.
    # This shouldn't happen in principle, but in the mean time
    # we can limit the damage.
    if area == 0:
        return 0.1

    return float(area)


def cell_perimeter(contour: Contour) -> float:
    """
    Get single cell perimeter.

    Parameters
    ----------
    contour : list
        Single cell contour from cv2 findcontours.

    Returns
    -------
    perimeter : int
        Cell perimeter

    """
    perimeter = cv2.arcLength(contour, closed=True)

    return float(perimeter)


def cell_fluo(
    fluo_frames: Image,
    mask: SegmentationMask,
) -> npt.NDArray[np.float32]:
    """
    Extract mean fluorescence level from mask.

    Parameters
    ----------
    fluo_frames : 3D array
        Fluorescent images to extract fluo from. Dimensions are
        (channels, size_y, size_x).
    mask : 2D numpy array of bool
        Mask of the region to extract (typically a single cell).
        Dimensions are (size_y, size_x).

    Returns
    -------
    fluo_values : array of floats
        Mean value per cell for each fluo frame.

    """
    return np.asarray((fluo_frames * mask).sum(axis=(1, 2)) / mask.sum())


def pathfinding(cost_map: Image, start: Pole, goal: Pole) -> npt.NDArray[np.int16]:
    """
    Find the shortest path between two poles that minimizes the cost map.

    Parameters
    ----------
    cost_map: Image
        Map of cost per pixel to find path through. Typically inverse of the
        distance transform. Dimensions are (size_y, size_x)
    start: Pole
        Coordinates of the starting point of the path. Typically should be a
        cell pole.
    goal: Pole
        Coordinates of the end point of the path. Typically should be a
        cell pole.

    Returns
    -------
    start : tuple[int]

    """
    start = tuple(start)
    goal = tuple(goal)

    dist = np.full_like(cost_map, np.inf)
    dist[start] = 0

    # Dictionary to track the best previous step to reach each point
    prev = {}

    # Use a priority queue to store points for processing (cost, coordinates)
    queue = [(0, start)]

    # Direction vectors for 8-way connectivity
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

    # Movement cost: 1 for straight moves, sqrt(2) for diagonal moves
    move_cost = [np.linalg.norm(direct) for direct in directions]

    while queue:
        current_dist, (x, y) = heapq.heappop(queue)
        if (x, y) == goal:
            break  # Stop if the goal is reached

        # Process all neighbors
        for idx, (dx, dy) in enumerate(directions):
            nx, ny = x + dx, y + dy
            # Ensure the neighbor is within bounds
            if 0 <= nx < cost_map.shape[0] and 0 <= ny < cost_map.shape[1]:
                # Adjust the move cost based on direction
                additional_cost = move_cost[idx] * cost_map[nx, ny]
                new_dist = current_dist + additional_cost
                if new_dist < dist[nx, ny]:
                    dist[nx, ny] = new_dist
                    prev[nx, ny] = (x, y)  # Store previous step
                    heapq.heappush(queue, (new_dist, (nx, ny)))

    # Reconstruct path from the 'prev' array
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = prev[current]
    path.append(start)
    path.reverse()

    return np.array(path, dtype=np.int16)


# %% Misc


def list_files(directory: Path, suffixes: Iterable[str]) -> list[Path]:
    """
    Return a sorted list of filenames in `directory` that have one of the specified extensions.

    Parameters
    ----------
    directory : Path
        Directory to iterate.
    suffixes : Iterable[str]
        List, tuple, set, etc. of allowed extensions.

    Returns
    -------
    [Path]
        List of matching filenames.
    """
    return sorted(p for p in directory.iterdir() if p.suffix in suffixes)


def tensorboard_callback() -> TensorBoard:
    """
    Return a callback for TensorBoard logging.

    Returns
    -------
    TensorBoard
        TensorBoard callback.
    """
    try:
        branch = (
            subprocess.check_output(
                ["git", "symbolic-ref", "--short", "HEAD"],  # noqa: S607
                cwd=Path(__file__).parent,
            )
            .rstrip()
            .decode()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        branch = ""
    date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d-%H%M%S")
    log_dir = f"logs/fit/{date}_{branch}"
    callback = TensorBoard(log_dir=log_dir, histogram_freq=1)
    return callback


def training_callbacks(model_file: str | Path, verbose: int = 1) -> list[Any]:
    """Return common callbacks convenient for training."""
    model_checkpoint = ModelCheckpoint(
        Path(model_file).as_posix(),
        monitor="loss",
        verbose=verbose,
        save_best_only=True,
    )
    early_stopping = EarlyStopping(
        monitor="loss", mode="min", verbose=verbose, patience=50
    )
    if keras.src.backend.config.backend() != "tensorflow":
        return [model_checkpoint, early_stopping]
    return [model_checkpoint, early_stopping, tensorboard_callback()]


def color_diff(prefix: str, a: Any, b: Any) -> str:  # noqa: ANN401
    """Return the string f"{prefix}{red_a} ≠ {green_b}"."""
    red_a = colored(a, color="red")
    green_b = colored(b, color="green")
    return f"{prefix}{red_a} ≠ {green_b}"


def compare_arrays(
    array1: npt.NDArray[Any], array2: npt.NDArray[Any], name: str = "array"
) -> list[str]:
    """Return a list of differences between two arrays, for use in compare."""
    diffs = [name]
    if array1.shape != array2.shape or array1.dtype != array2.dtype:
        diffs.append(f"{name}")
        if array1.shape != array2.shape:
            diffs.append(color_diff("shape: ", array1.shape, array2.shape))
        else:
            diffs.append(f"shape: {array1.shape}")
        if array1.dtype != array2.dtype:
            diffs.append(color_diff("dtype: ", array1.dtype, array2.dtype))
        else:
            diffs.append(f"dtype: {array1.dtype}")
    return diffs


def print_diffs(diffs: list[str | list], lasts: list[bool] | None = None) -> None:  # type: ignore[type-arg]
    """Print a hierarchical list of differences."""
    if lasts is None:
        lasts = []
    back_spine = "".join("    " if last else " │  " for last in lasts[:-1])
    if len(lasts) > 0:
        spine = back_spine + (" └─ " if lasts[-1] else " ├─ ")
    else:
        spine = back_spine
    back_spine = "".join("    " if last else " │  " for last in lasts)
    if len(diffs) == 1:
        print(f"{spine}{diffs[0]} =")  # noqa: T201
    else:
        print(color_diff(spine, diffs[0], diffs[0]))  # noqa: T201
        for idiff, diff in enumerate(diffs[1:]):
            if isinstance(diff, list):
                print_diffs(diff, lasts=[*lasts, idiff == len(diffs[1:]) - 1])
            else:
                spine = "└─" if idiff == len(diffs[1:]) - 1 else "├─"
                print(f"{back_spine} {spine} {diff}")  # noqa: T201
