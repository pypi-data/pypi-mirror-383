"""Image manipulation functions."""

import itertools as it
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias, cast

import cv2
import numpy as np
import numpy.typing as npt
import skimage.transform as trans
import xarray as xr

LOGGER = logging.getLogger(__name__)

Image: TypeAlias = npt.NDArray[np.float32]

SegmentationMask: TypeAlias = npt.NDArray[np.uint8]

Labels: TypeAlias = npt.NDArray[np.uint16]

Contour: TypeAlias = npt.NDArray[np.int32]


@dataclass
class CroppingBox:
    """Class describing a box to cut out."""

    xtl: int
    """Top-left corner X coordinate."""
    ytl: int
    """Top-left corner Y coordinate."""
    xbr: int
    """Bottom-right corner X coordinate."""
    ybr: int
    """Bottom-right corner Y coordinate."""

    @property
    def shape(self) -> tuple[int, int]:
        """Shape of the cropping box."""
        return (self.ybr - self.ytl, self.xbr - self.xtl)

    @property
    def size(self) -> int:
        """Size of the cropping box as width * height."""
        return self.shape[0] * self.shape[1]

    @classmethod
    def full(cls, image: npt.NDArray[Any]) -> "CroppingBox":
        """
        Return a cropping box set to the full size of the image.

        Parameters
        ----------
        image : np.ndarray
            Image to use as reference for the bounding box.

        Returns
        -------
        box : CroppingBox
            Cropping box adjusted to the full size of the image.
        """
        return cls(xtl=0, ytl=0, xbr=image.shape[1], ybr=image.shape[0])

    def crop(self, images: xr.DataArray) -> xr.DataArray:
        """
        Crop an image according to the cropping box.

        Pads with zeros if a part of the box falls outside of the image.

        Parameters
        ----------
        images : xr.DataArray
            Image to crop.

        Returns
        -------
        patches : xr.DataArray
            Patch cropped from the image.
        """
        return xr.apply_ufunc(
            lambda arr: CroppingBox._crop(self, arr),
            images,
            input_core_dims=[["y", "x"]],
            output_core_dims=[("yc", "xc")],
        )

    @np.vectorize(signature="(),(y,x)->(yc,xc)")
    def _crop(self, image: npt.NDArray[Any]) -> npt.NDArray[Any]:
        if image.ndim != 2:
            error_msg = "`image` must have 2 dimensions."
            raise ValueError(error_msg)
        cropped = image[
            max(self.ytl, 0) : min(self.ybr, image.shape[0]),
            max(self.xtl, 0) : min(self.xbr, image.shape[1]),
        ]
        padding = (
            (max(-self.ytl, 0), max(self.ybr - image.shape[0], 0)),
            (max(-self.xtl, 0), max(self.xbr - image.shape[1], 0)),
        )
        return np.pad(cropped, padding)

    def patch(
        self, image: npt.NDArray[Any], patch: npt.NDArray[Any]
    ) -> npt.NDArray[Any]:
        """
        Apply a patch on an image at the position specified by the box.

        Parts of the box may fall outside of the image.

        Parameters
        ----------
        image : np.ndarray
            Image to patch.
        patch : np.ndarray
            Patch to apply.

        Returns
        -------
        image : np.ndarray
            The patched image.
        """
        if image.ndim != 2 or patch.ndim != 2:
            error_msg = "`image` and `patch` must have 2 dimensions."
            raise ValueError(error_msg)
        if patch.shape != self.shape:
            error_msg = "`patch` must have the same dimensions as the cropping box."
            raise ValueError(error_msg)
        if (
            self.ybr <= 0
            or image.shape[0] <= self.ytl
            or self.xbr <= 0
            or image.shape[1] <= self.xtl
        ):
            error_msg = "`box` must fall at least partially inside the image."
            raise ValueError(error_msg)
        image[
            max(self.ytl, 0) : min(self.ybr, image.shape[0]),
            max(self.xtl, 0) : min(self.xbr, image.shape[1]),
        ] = patch[
            max(-self.ytl, 0) : min(self.ybr, image.shape[0]) - self.ytl,
            max(-self.xtl, 0) : min(self.xbr, image.shape[1]) - self.xtl,
        ]
        return image

    def resize(self, fx: float | None = None, fy: float | None = None) -> "CroppingBox":
        """
        Resize the cropping box to follow an image resizing with the same factors.

        If fi is None, the corresponding axis is left unchanged. For fi > 1, the box is enlarged.

        Parameters
        ----------
        fx : Optional[float]
            Resizing factor for the horizontal axis (column axis).
        fy : Optional[float]
            Resizing factor for the vertical axis (row axis).

        Returns
        -------
        resized_box : CroppingBox
            A copy of the resized box. The original box is left unchanged.
        """
        if any(f is not None and f < 0 for f in [fx, fy]):
            error_msg = "CroppingBox resizing parameters must be None or >=0."
            raise ValueError(error_msg)
        resized_box = CroppingBox(
            xbr=self.xbr if fx is None else round(self.xbr * fx),
            xtl=self.xtl if fx is None else round(self.xtl * fx),
            ybr=self.ybr if fy is None else round(self.ybr * fy),
            ytl=self.ytl if fy is None else round(self.ytl * fy),
        )
        return resized_box

    @staticmethod
    def tracking_box(
        contour: Contour,
        shape: tuple[int, int],
    ) -> "CroppingBox":
        """
        Get a crop box around a cell that fits the tracking target size.

        Parameters
        ----------
        contour : Contour
            Contour of the cell to track.
        shape : tuple of 2 ints
            Target shape of the cropped image.

        Returns
        -------
        cropbox : CroppingBox
            The cropbox localises the patch relatively to the source image.

        """
        cx, cy = centroid(contour)

        xtl = cx - shape[1] // 2
        xbr = xtl + shape[1]

        ytl = cy - shape[0] // 2
        ybr = ytl + shape[0]

        return CroppingBox(xtl=xtl, ytl=ytl, xbr=xbr, ybr=ybr)


def centroid(contour: Contour) -> tuple[int, int]:
    """
    Get centroid of cv2 contour.

    Parameters
    ----------
    contour : 3D numpy array
        Blob contour generated by cv2.findContours().

    Returns
    -------
    cx : int
        X-axis coordinate of centroid.
    cy : int
        Y-axis coordinate of centroid.

    """
    if contour.shape[0] > 2:  # Looks like cv2.moments treats it as an image
        # Calculate moments for each contour
        m = cv2.moments(contour)
        # Calculate x,y coordinate of center
        if m["m00"] != 0:
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
        else:
            cx, cy = 0, 0
    else:
        cx = int(np.mean(contour[:, :, 0]))
        cy = int(np.mean(contour[:, :, 1]))

    return cx, cy


def binarize_threshold(array: Image, threshold: float | None) -> SegmentationMask:
    """
    Binarize a numpy array by thresholding it.

    Parameters
    ----------
    array : 2D numpy array of floating-point numbers
        Input array/image.
    threshold : float or None
        Binarization threshold. If None, the threshold will be the middle of
        the dynamic range.

    Returns
    -------
    newi : 2D numpy array of uint8
           Binarized image.

    """
    if threshold is None:
        threshold = (array.min() + array.max()) / 2
    return (array > threshold).astype(np.uint8)


def read_reshape(
    filename: Path,
    *,
    target_size: tuple[int, int] = (256, 32),
    binarize: bool = False,
    order: int = 1,
    method: str = "resize",
) -> Image | SegmentationMask:
    """
    Read image from disk, format it and return it as an array of floating-point numbers between 0 and 1.

    Parameters
    ----------
    filename : Path
        Path to file. Only PNG, JPG or single-page TIFF files accepted
    target_size : tupe of int or None, optional
        Size to reshape the image.
        The default is (256, 32).
    binarize : bool, optional
        Use the binarize_threshold() function on the image.
        The default is False.
    order : int, optional
        interpolation order (see skimage.transform.warp doc).
        0 is nearest neighbor
        1 is bilinear
        The default is 1.
    method : "resize" or "pad"
        What to do if the image is smaller than the target size.
        In the "resize" mode, larger images will be resized too.
        The default is "resize".

    Raises
    ------
    ValueError
        Raised if image file is not a PNG, JPEG, or TIFF file.

    Returns
    -------
    i : numpy 2d array of floats
        Loaded array.

    """
    i = read_image(filename)
    assert i.ndim == 2
    if method == "pad":
        # For DeLTA 2D, black space is added if img is smaller than target_size
        fill_shape = np.maximum(np.array(target_size), np.array(i.shape))
        img = np.zeros(fill_shape, dtype=np.float32)
        img[: i.shape[0], : i.shape[1]] = i
    elif method == "resize":
        # For DeLTA mothermachine, all images are resized in 256x32
        img = trans.resize(i, target_size, anti_aliasing=True, order=order)
    else:
        error_msg = f"Resizing method not understood: {method}."
        raise ValueError(error_msg)

    if binarize:
        return binarize_threshold(img, threshold=None)

    return img


def postprocess(
    images: npt.NDArray[np.float32],
    *,
    square_size: int = 5,
    min_size: float | None = None,
    crop: bool = False,
) -> SegmentationMask:
    """
    Clean segmentation results based on mathematical morphology.

    Parameters
    ----------
    images : 2D or 3D numpy array of floating-point numbers between 0 and 1
        Input image or images stacked along axis=0.
    square_size : int, optional
        Size of the square structuring element to use for morphological opening
        The default is 5.
    min_size : float or None, optional
        Remove objects smaller than this minimum area value. If None, the
        operation is not performed.
        The default is None.
    crop : bool
        If `True`, the images are cropped (randomly in training mode and
        with overlapping tiles in evaluation mode).  If `False`, the images
        are simply resized to the target size.

    Returns
    -------
    images : 2D or 3D numpy array of uint8 (0 or 1)
        Cleaned, binarized images. Note that the dimensions are squeezed before
        return (see numpy.squeeze doc)

    """
    # Expand dims if 2D:
    if images.ndim == 2:
        images = np.expand_dims(images, axis=0)

    outputs = []
    for img in images:
        image = img

        image = binarize_threshold(image, threshold=0)
        if not crop:
            kernel = np.ones((square_size, square_size), dtype=np.uint8)
            image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        if min_size is not None:
            _, labels, stats, _ = cv2.connectedComponentsWithStats(image)
            threshold = (stats[:, cv2.CC_STAT_AREA] >= min_size).astype(np.uint8)
            threshold[0] = 0
            image = threshold[labels]
        outputs.append(image)

    return np.squeeze(outputs)


def read_image(filename: Path) -> Image:
    """
    Return the image as a numpy array of np.float32 rescaled between 0 and 1.

    Parameters
    ----------
    filename : Path
        Filename of the image to read.

    Returns
    -------
    image : np.ndarray of np.float32
    """
    image = cv2.imread(str(filename), cv2.IMREAD_ANYDEPTH)
    if image is None:
        error_msg = f"File not found or format not understood: {filename}."
        raise ValueError(error_msg)
    return rescale_image(image)


def rescale_image(img: npt.NDArray[Any]) -> Image:
    """
    Rescale an integer image to return an array of np.float32 between 0 and 1.

    Parameters
    ----------
    img: np.ndarray
        Image with integer pixel values.

    Returns
    -------
    image: rescaled image with np.float32 pixel values between 0 and 1.
    """
    for depth, dtype in [(8, np.uint8), (16, np.uint16), (32, np.uint32)]:
        if img.dtype == dtype:
            return np.asarray(img.astype(np.float32) / (2**depth - 1), dtype=np.float32)
    error_msg = f"Image depth not understood: {img.dtype}."
    raise ValueError(error_msg)


# %% Image correction


def to_integer_values(frame: Image, dtype: type[object]) -> npt.NDArray[Any]:
    """
    Return an image with integer-valued pixels of the given size.

    Parameters
    ----------
    frame : Image
        Input image with np.float32 pixels contained in [0, 1].
    dtype : numpy dtype
        Integer type of the returned image.


    """
    assert frame.max() <= 1, "The pixel values should be contained between 0 and 1."
    depth = {np.uint8: 8, np.uint16: 16, np.uint32: 32}[dtype]
    return np.asarray(frame * (2**depth - 1), dtype=dtype)


def deskew(image: Image) -> float:
    """
    Compute the rotation angle to apply to the image to remove its rotation.

    You can skip rotation correction if your chambers are about +/- 1 degrees of horizontal.

    Parameters
    ----------
    image : 2D numpy array
        Input image.

    Returns
    -------
    angle : float
        Rotation angle of the chambers for correction, in degrees.

    """
    image8 = to_integer_values(image, np.uint8)

    # enhance edges
    low_threshold = np.quantile(image8, 0.1)
    high_threshold = np.quantile(image8, 0.2)
    edges = cv2.Canny(image8, low_threshold, high_threshold, L2gradient=True)

    # Hough transform
    n = 360  # precision in degree = 90 / n (here 0.25 degree)
    theta = np.linspace(-np.pi / 4, 3 * np.pi / 4, 2 * n + 1)
    hspace, angles, distances = trans.hough_line(edges, theta=theta)

    _, corrections, _ = trans.hough_line_peaks(hspace, angles, distances, num_peaks=1)

    if corrections[0] > np.pi / 4:
        return float(np.degrees(corrections[0] - np.pi / 2))
    return float(np.degrees(corrections[0]))


def affine_transform(
    image: npt.NDArray[Any],
    *,
    zoom: float = 1.0,
    angle: float = 0.0,
    shift: tuple[float, float] = (0.0, 0.0),
    order: int,
) -> npt.NDArray[Any]:
    """
    Apply an affine transformation to an image (zoom, rotation and translation).

    Parameters
    ----------
    image : 2D numpy array
        input image.
    zoom : float
        Zoom to apply to the image.
    angle : float
        Rotation angle to apply to the image.
    shift : (float, float)
        Translation to apply to the image, in pixels (x, y).
    order : int
        Interpolation order.

    Returns
    -------
    image : 2D numpy array
        Zoomed and shifted image of same size as input.

    """
    # Center of rotation and zoom
    center = (np.array(image.shape[1::-1]) - 1) / 2
    # Affine transform matrix
    matrix = cv2.getRotationMatrix2D(center=center, angle=angle, scale=zoom)
    # Add shift
    matrix[:, 2] -= [shift[0] * zoom, shift[1] * zoom]

    kwargs = {
        "flags": [cv2.INTER_NEAREST, cv2.INTER_LINEAR][order],
        "borderMode": cv2.BORDER_REPLICATE,
    }
    new_image = cv2.warpAffine(image, matrix, image.shape[1::-1], **kwargs)
    return np.asarray(new_image)


def rotate(images: xr.DataArray, angles: xr.DataArray) -> xr.DataArray:
    """
    Rotate image.

    Parameters
    ----------
    images : xr.DataArray
        The images to rotate. Need to have at least "y" and "x" dimensions.
    angles : xr.DataArray
        Rotation angles, in degrees.

    Returns
    -------
    xr.Dataarray
        Rotated images

    """
    return xr.apply_ufunc(
        _rotate,
        images,
        angles,
        input_core_dims=[["y", "x"], []],
        output_core_dims=[("y", "x")],
    )


@np.vectorize(signature="(y,x),()->(y,x)")
def _rotate(image: Image, angle: float) -> Image:
    if image.ndim != 2:
        err = "There should be only one image."
        raise ValueError(err)

    return affine_transform(image, angle=angle, order=1)


def compute_drift(
    images: Image, box: CroppingBox, template: Image
) -> list[tuple[int, int]]:
    """
    Compute drift drift between movie frames and the reference.

    Parameters
    ----------
    images : 3D numpy array of uint8/uint16/floats
        The frames to correct drift for, of shape ``(t, y, x)``.
    box : CroppingBox
        A cropping box to extract the part of the frame to compute drift
        correction over.
    template : 2D numpy array of uint8/uint16/floats
        The template for drift correction (see drift_template()).

    Returns
    -------
    drift : list[tuple[int, int]]
        List of length ``t`` with tuples of ``(xdrift, ydrift)``.
    """
    if images.ndim != 3:
        err = "There must be several images."
        raise ValueError(err)

    template = to_integer_values(template, np.uint8)

    drift = []
    for image in images:
        image_u8 = to_integer_values(image, np.uint8)
        res = cv2.matchTemplate(image_u8, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        drift.append((max_loc[0] - box.xtl, max_loc[1] - box.ytl))

    return drift


def correct_drift(images: xr.DataArray, drifts: xr.DataArray) -> xr.DataArray:
    """
    Correct the drift for a stack of images.

    Parameters
    ----------
    images : xr.DataArray
        The images to correct drift for. Needs to have at least "y" and "x" dims.
    drift : xr.DataArray
        The pre-computed drift to apply. Needs to have at least a "xy" dim.

    Returns
    -------
    corrected : xr.DataArray
        Drift-corrected images, same dimensions as `images`.
    """
    return xr.apply_ufunc(
        _correct_drift,
        images,
        drifts,
        input_core_dims=[["y", "x"], ["xy"]],
        output_core_dims=[("y", "x")],
    )


@np.vectorize(signature="(y,x),(xy)->(y,x)")
def _correct_drift(image: Image, drift: tuple[int, int]) -> Image:
    if image.ndim != 2:
        err = "There should be only one image."
        raise ValueError(err)

    return affine_transform(image, shift=drift, order=1)


def drift_template(
    chamberboxes: list[CroppingBox], img: Image, *, whole_frame: bool = False
) -> tuple[CroppingBox, Image]:
    """
    Retrieve a region above the chambers to use as drift template.

    Parameters
    ----------
    chamberboxes : list of dictionaries
        See getROIBoxes().
    img : 2D numpy array
        The first frame of a movie to use as reference for drift correction.
    whole_frame : bool, optional
        Whether to use the whole frame as reference instead of the area above
        the chambers.

    Returns
    -------
    box : CroppingBox
        A cropping box corresponding to a region of an image to use as a template
        for drift correction.
    template : Image
        The cropped region of the image in the cropping box.

    """
    # Cutting out 2.5% of the image on each side as drift margin
    y_cut, x_cut = (round(i * 0.025) for i in img.shape)

    box = CroppingBox(
        xtl=x_cut,
        xbr=-x_cut,
        ytl=y_cut,
        ybr=-y_cut if whole_frame else max(box.ytl for box in chamberboxes) - y_cut,
    )

    return box, box.crop(img)


def filter_areas(
    image: SegmentationMask,
    min_area: float | None = 20,
    max_area: float | None = None,
) -> SegmentationMask:
    """
    Area filtering using openCV instead of skimage.

    Parameters
    ----------
    image : 2D array
        Segmentation mask.
    min_area : float or None, optional
        Minimum object area.
        The default is 20
    max_area : float or None, optional
        Maximum object area.
        The default is None.

    Returns
    -------
    image : 2D array
        Filtered mask.

    """
    # Get contours:
    contours = find_contours(image)

    # Loop through contours, flag them for deletion:
    to_remove = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if (min_area is not None and area < min_area) or (
            max_area is not None and area > max_area
        ):
            to_remove += [cnt]

    # Delete all at once:
    if len(to_remove) > 0:
        image = cv2.drawContours(image, to_remove, -1, 0, thickness=-1)

    return image


# %% Image cropping & stitching
def create_windows(
    image: npt.NDArray[Any],
    target_size: tuple[int, int] = (512, 512),
    min_overlap: int = 24,
) -> tuple[npt.NDArray[Any], npt.NDArray[np.int32], npt.NDArray[np.int32]]:
    """
    Crop input image into windows of set size.

    Parameters
    ----------
    image : 2D array
        Input image.
    target_size : tuple, optional
        Dimensions of the windows to crop out. The default is (512, 512).
    min_overlap : int, optional
        Minimum overlap between windows in pixels. Default is 24.


    Returns
    -------
    windows: 3D array
        Cropped out images to feed into U-Net. Dimensions are
        ``(nb_of_windows, *target_size)``.
    loc_y : array of shape (nsplits_y, 2)
        List of lower and upper bounds for windows over the y axis (columns).
    loc_x : array of shape (nsplits_x, 2)
        List of lower and upper bounds for windows over the x axis (rows).

    """
    # Compute how many windows we will have
    stride_x = target_size[1] - min_overlap
    stride_y = target_size[0] - min_overlap
    if stride_x <= 0 or stride_y <= 0:
        error_msg = "min_overlap must be strictly less than target_size"
        raise ValueError(error_msg)
    nsplits_x = 1 + int(np.ceil((image.shape[1] - target_size[1]) / stride_x))
    nsplits_y = 1 + int(np.ceil((image.shape[0] - target_size[0]) / stride_y))

    # Pad the image if smaller than the target size
    pad_x = max(0, target_size[1] - image.shape[1])
    pad_y = max(0, target_size[0] - image.shape[0])
    padding = ((pad_y // 2, pad_y - pad_y // 2), (pad_x // 2, pad_x - pad_x // 2))
    image = np.asarray(np.pad(image, padding), dtype=image.dtype)

    # Compute offsets
    starts_x = np.linspace(
        0, image.shape[1] - target_size[1], num=nsplits_x, endpoint=True, dtype=np.int32
    )
    starts_y = np.linspace(
        0, image.shape[0] - target_size[0], num=nsplits_y, endpoint=True, dtype=np.int32
    )

    # Store the cropped images
    tiles = np.array(
        [
            image[sy : sy + target_size[0], sx : sx + target_size[1]]
            for sy in starts_y
            for sx in starts_x
        ],
        dtype=image.dtype,
    )
    loc_x = np.vstack((starts_x, starts_x + target_size[1])) - pad_x // 2
    loc_y = np.vstack((starts_y, starts_y + target_size[0])) - pad_y // 2
    return tiles, loc_y.T, loc_x.T


def stitch_pic(
    results: npt.NDArray[Any],
    loc_y: list[tuple[int, int]] | npt.NDArray[np.int32],
    loc_x: list[tuple[int, int]] | npt.NDArray[np.int32],
) -> npt.NDArray[Any]:
    """
    Stitch segmentation back together from the windows of create_windows().

    Parameters
    ----------
    results : 3D array
        Segmentation outputs from the seg model with dimensions
        (nb_of_windows, target_size[0], target_size[1])
    loc_y : list
        List of lower and upper bounds for windows over the y axis
    loc_x : list
        List of lower and upper bounds for windows over the x axis

    Returns
    -------
    stitch_norm : 2D array
        Stitched image.

    """
    # Create an array to store segmentations into a format similar to how the image was cropped
    stitch = np.zeros((loc_y[-1][1], loc_x[-1][1]), dtype=results.dtype)

    # Compute where patches meet
    middles_y = [
        0,
        *((ly[1] + nly[0]) // 2 for ly, nly in it.pairwise(loc_y)),
        loc_y[-1][1],
    ]
    middles_x = [
        0,
        *((lx[1] + nlx[0]) // 2 for lx, nlx in it.pairwise(loc_x)),
        loc_x[-1][1],
    ]

    index = 0
    for ly, (y_start, y_end) in zip(loc_y, it.pairwise(middles_y), strict=True):
        for lx, (x_start, x_end) in zip(loc_x, it.pairwise(middles_x), strict=True):
            res_crop_y = -(ly[1] - y_end) if ly[1] - y_end > 0 else None
            res_crop_x = -(lx[1] - x_end) if lx[1] - x_end > 0 else None
            stitch[y_start:y_end, x_start:x_end] = results[
                index,
                y_start - ly[0] : res_crop_y,
                x_start - lx[0] : res_crop_x,
            ]

            index += 1

    return stitch


def find_contours(mask: SegmentationMask) -> list[Contour]:
    """
    Find contours of morphological components of a segmentation mask.

    This is a wrapper of CV2's findContours() because it keeps changing signatures.

    Parameters
    ----------
    mask : SegmentationMask
        Segmentation mask to extract contours from.

    Returns
    -------
    contours : list[Contour]
        List of cv2 type contour arrays.

    """
    # Default use:
    contours_, _ = cv2.findContours(
        mask, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE
    )

    # Some versions of cv2.findcontours return it as a tuple, not a list:
    contours = list(contours_)

    return contours


def label_seg(
    seg: SegmentationMask,
    cellnumbers: Sequence[int] | None = None,
) -> Labels:
    """
    Label cells in segmentation mask.

    Parameters
    ----------
    seg : SegmentationMask
        Cells segmentation mask.
    cellnumbers : list of ints, optional
        Numbers to attribute to each cell mask, from top to bottom of image.
        Because we are using uint16s, maximum cell number is 65535. If None is
        provided, the cells will be labeled 1,2,3,... Background is 0
        The default is None.

    Returns
    -------
    labels : 2D numpy array of uint16
        Labelled image. Each cell in the image is marked by adjacent pixels
        with values given by cellnumbers

    """
    contours = find_contours(seg)
    if cellnumbers is None:
        cellnumbers = range(1, len(contours) + 1)
    if len(cellnumbers) != len(contours):
        error_msg = "cellnumbers must have the same length as the number of cells"
        raise ValueError(error_msg)
    # Sorting according to the lowest point on the y (vertical) axis
    contours.sort(key=lambda elem: np.max(elem[:, 0, 1]))
    labels = np.zeros(seg.shape, dtype=np.uint16)
    for icell, contour in zip(cellnumbers, contours, strict=True):
        labels = cv2.fillPoly(labels, [contour], icell)
    return labels


def resize_image(image: Image, shape: tuple[int, int]) -> Image:
    """
    Resize "continuous" images (with linear interpolation).

    Parameters
    ----------
    image : Image
        Image to resize.
    shape : tuple[int, int]
        Target image shape.

    Returns
    -------
    resized_image : Image
        Resized image.
    """
    resized_image = cv2.resize(image, shape[::-1], interpolation=cv2.INTER_LINEAR)
    return np.asarray(resized_image, dtype=np.float32)


def resize_mask(
    mask: SegmentationMask, shape: tuple[int, int], *, prevent_touching: bool = True
) -> SegmentationMask:
    """
    Resize a segmentation mask.

    Parameters
    ----------
    mask : SegmentationMask
        Segmentation mask to resize.
    shape : tuple[int, int]
        Target mask shape.
    prevent_touching : bool
        If True, prevent the resized shapes from touching.
        Note that this can make some shapes disappear.
        The default is True.

    Returns
    -------
    resized_mask : SegmentationMask
        Resized mask.
    """
    labels = label_seg(mask)
    labels_resized = resize_labels(labels, shape, prevent_touching=prevent_touching)
    return np.asarray(labels_resized > 0, dtype=np.uint8)


def resize_labels(
    labels: Labels, shape: tuple[int, int], *, prevent_touching: bool = False
) -> Labels:
    """
    Resize labels.

    Parameters
    ----------
    labels : Labels
        Labels to resize.
    shape : tuple[int, int]
        Target labels shape.
    prevent_touching : bool
        If True, prevent the resized shapes from touching.
        Note that this can make some shapes disappear.
        The default is False.

    Returns
    -------
    resized_labels : Labels
        Resized labels.
    """
    contours = find_contours(np.asarray(labels > 0, dtype=np.uint8))
    factors = (np.array(shape[::-1], dtype=np.float64) - 1) / (
        np.array(labels.shape[::-1], dtype=np.float64) - 1
    )
    labels_resized = np.zeros(shape, dtype=np.uint16)
    for contour in contours:
        color = int(labels[contour[0][0][1], contour[0][0][0]])
        contour_resized = np.asarray(
            np.round(np.asarray(contour, dtype=np.float64) * factors), dtype=np.int32
        )
        cv2.drawContours(
            labels_resized,
            [contour_resized],
            contourIdx=-1,
            color=color,
            thickness=cv2.FILLED,
        )

    if prevent_touching:
        touching = detect_touching_cells(labels_resized)
        labels_resized[touching] = 0

    return np.asarray(labels_resized, dtype=np.uint16)


def smart_resize(
    image: Image | SegmentationMask,
    new_shape: tuple[int, int],
) -> Image | SegmentationMask:
    """
    Resize images with proper interpolation method, & remove touching pixels.

    Parameters
    ----------
    image : Image | SegmentationMask
        Image to resize. Can be a microscopy image, segmentation mask, or
        weight map.
    new_shape : tuple[int, int]
        Target image shape.

    Returns
    -------
    resized_image : Image | SegmentationMask
        Resized image.

    """
    if image.dtype == np.float32:
        image = cast("Image", image)  # for mypy
        return resize_image(image, new_shape)

    if image.dtype == np.uint8:
        image = cast("SegmentationMask", image)  # for mypy
        return resize_mask(image, new_shape)

    err = f"Unknown dtype: {image.dtype}"
    raise TypeError(err)


def detect_touching_cells(labels: Labels) -> npt.NDArray[bool]:
    """
    Detect pixels where cells are touching.

    Parameters
    ----------
    labels : Labels
        Labelled cells image where cells are possibly touching.

    Returns
    -------
    touching : npt.NDArray[bool]
        Pixels where cells are touching.

    """
    mask = labels > 0
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # This dilation covers lower labels with higher labels
    dilated = cv2.dilate(labels, kernel)
    touching = (dilated > labels) & mask

    # Now we want to cover higher labels with lower labels
    # So we start inverting them (and keeping the background 0)
    inv_labels = np.zeros_like(labels)
    np.invert(labels, where=mask, out=inv_labels)

    # And we repeat the same operation
    inv_dilated = cv2.dilate(inv_labels, kernel)
    inv_touching = (inv_dilated > inv_labels) & mask

    return np.asarray(touching | inv_touching, dtype=bool)


def distance_transform_labels(labels: Labels) -> Image:
    """
    Compute the distance transform for a label frame.

    Parameters
    ----------
    labels : Labels
        Labelled cells image where cells are possibly touching.

    Returns
    -------
    distance_map : Image
        For each non-zero pixel, what is the distance to the nearest
        different pixel (zero or otherwise).
    """
    labels_padded = np.pad(labels, 1)
    distance_maps = np.zeros_like(labels_padded, dtype=np.float32)

    mask = np.empty_like(labels_padded, dtype=np.uint8)
    distance_map = np.empty_like(labels_padded, dtype=np.float32)
    for label in np.unique(labels)[1:]:
        np.equal(label, labels_padded, out=mask)
        cv2.distanceTransform(
            mask,
            distanceType=cv2.DIST_L2,
            maskSize=cv2.DIST_MASK_PRECISE,
            dst=distance_map,
        )
        distance_maps += distance_map

    return distance_maps[1:-1, 1:-1]
