"""Data manipulations and input/output operations."""

import logging
import re
from collections import defaultdict
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any, Literal, cast, overload

import cv2
import keras
import numpy as np
import numpy.random as npr
import numpy.typing as npt
import skimage.morphology as morph
from scipy import interpolate
from scipy.special import expit
from skimage import io
from skimage.measure import label

from delta import imgops, utils
from delta.imgops import Image, SegmentationMask

LOGGER = logging.getLogger(__name__)

MODE = Literal["training", "evaluation"]


# %% DATA AUGMENTATION
def data_augmentation(
    images_input: list[npt.NDArray[Any]],
    aug_par: dict[str, Any],
    order: int | list[int] | tuple[int, ...] = 0,
    rng: npr.Generator | None = None,
) -> list[npt.NDArray[Any]]:
    """
    Create an augmented sample based on data augmentation parameters.

    Parameters
    ----------
    images_input : list of 2D numpy arrays
        Images to apply augmentation operations to.
    aug_par : dict
        Augmentation operations parameters. Accepted key-value pairs:
            illumination_voodoo: bool
                Whether to apply the illumination voodoo operation.  It
                simulates a variation in illumination along the Y axis.
            histogram_voodoo: bool
                Whether to apply the histogram voodoo operation.  It performs
                an elastic deformation on the image histogram to simulate
                changes in illumination.
            elastic_deformation: dict
                If this key exists, the elastic deformation operation is
                applied.  The parameters are given as key-value pairs.  Sigma
                values are given under the sigma key, deformation points are
                given under the points key, for example ``{"sigma": 25,
                "points": 5}``.  See the :py:mod:`elasticdeform` doc for more
                info.
            gaussian_noise: float
                Apply gaussian noise to the image.  The sigma value of the
                gaussian noise is uniformly sampled between 0 and
                +gaussian_noise.
            gaussain_blur: float
                Apply gaussian blur to the image.  The sigma value is the
                standard deviation of the kernel in the x and y direction.
            horizontal_flip: bool
                Whether to flip the images horizontally.  Input images have a
                50% chance of being flipped.
            vertical_flip: bool
                Whether to flip the images vertically.  Input images have a 50%
                chance of being flipped
            rotations90d: bool
                Whether to randomly rotate the images in 90° increments.
                Each 90° rotation has a 25% chance of happening
            resize: bool
                Whether to randomly resize the image on both axes.
            rotation: int or float
                Range of random rotation to apply. The angle is uniformly
                sampled in the range ``[-rotation, +rotation]``.
            zoom: float
                Range of random "zoom" to apply.  The image is randomly zoomed
                by a factor that is sampled from an exponential distribution
                with a ``lambda`` of ``3/zoom``.  The random factor is clipped
                at +zoom.
            shiftX: int/float
                The range of random shifts to apply along X.  A uniformly
                sampled shift between ``[-shiftX, +shiftX]`` is applied.
            shiftY: int/float
                The range of random shifts to apply along Y.  A uniformly
                sampled shift between ``[-shiftY, +shiftY]`` is applied.

            Note that the same operations are applied to all inputs except for
            the timeshift ones.
    order : int or list/tuple of ints, optional
        Interpolation order to use for each image in the input stack. If order
        is a scalar, the same order is applied to all images. If a list of
        orders is provided, each image in the stack will have its own operation
        order. See the :class:`skimage.transform.wrap` doc.
        Note that the histogram voodoo operation is only applied to images with
        a non-zero order.
        The default is 0.
    rng : npr.Generator | None
        Numpy random number generator to use for data augmentation.  If None,
        one will be created from entropy with `npr.default_rng()`.
        The default is None.

    Returns
    -------
    output : list of 2D numpy arrays
        Augmented images array.

    """
    if rng is None:
        rng = npr.default_rng()

    # processing inputs / initializing variables::
    output = list(images_input)
    orderlist = [order] * len(images_input) if isinstance(order, int) else list(order)

    size_y, size_x = output[0].shape

    # Apply augmentation operations:

    if aug_par.get("illumination_voodoo"):
        output = [
            illumination_voodoo(item, rng) if order > 0 else item
            for order, item in zip(orderlist, output, strict=True)
        ]

    if aug_par.get("histogram_voodoo"):
        output = [
            histogram_voodoo(item, rng) if order > 0 else item
            for order, item in zip(orderlist, output, strict=True)
        ]

    if aug_par.get("gaussian_noise"):
        output = [
            np.clip(rng.normal(item, aug_par["gaussian_noise"]), 0, 1)
            if order > 0
            else item
            for order, item in zip(orderlist, output, strict=True)
        ]

    if aug_par.get("gaussian_blur"):
        output = [
            cv2.GaussianBlur(item, (5, 5), aug_par["gaussian_blur"])
            if order > 0
            else item
            for order, item in zip(orderlist, output, strict=True)
        ]

    if aug_par.get("elastic_deformation"):
        output = smart_elastic_deform(
            output, orderlist, rng=rng, **aug_par["elastic_deformation"]
        )

    if aug_par.get("horizontal_flip") and rng.choice(2):
        output = [np.fliplr(item) for item in output]

    if aug_par.get("vertical_flip") and rng.choice(2):
        output = [np.flipud(item) for item in output]

    if aug_par.get("rotations_90d"):
        rotation = rng.choice(4)
        output = [np.rot90(item, k=rotation) for item in output]

    # Rotation, zoom and shift are processed together
    angle = rng.uniform(-1.0, 1.0) * aug_par.get("rotation", 0.0)

    zoom = 1 + rng.exponential(aug_par.get("zoom", 0.0) / 3.0)

    shift_x = rng.uniform(-1.0, 1.0) * aug_par.get("shiftX", 0.0)
    shift_y = rng.uniform(-1.0, 1.0) * aug_par.get("shiftY", 0.0)

    output = [
        imgops.affine_transform(
            item,
            zoom=zoom,
            angle=angle,
            shift=(shift_x * size_x, shift_y * size_y),
            order=order,
        )
        for order, item in zip(orderlist, output, strict=True)
    ]

    if aug_par.get("resize"):
        fy = 2 ** rng.normal(0, 0.5)
        fx = fy * 2 ** rng.normal(0, 0.1)
        sy = int(np.round(size_y * fy))
        sx = int(np.round(size_x * fx))
        output = [
            imgops.smart_resize(item, (sy, sx))
            for order, item in zip(orderlist, output, strict=True)
        ]

    return output


def smart_elastic_deform(
    img_stack: list[npt.NDArray[Any]],
    orderlist: int | Sequence[int] = 0,
    sigma: float = 10,
    points: int | tuple[int, int] = 5,
    rng: npr.Generator | None = None,
) -> list[npt.NDArray[Any]]:
    """
    Run elastic deformation repeatably and remove touching cell pixels.

    Parameters
    ----------
    img_stack : list[npt.NDArray[Any]]
        Images to apply elastic deformation to.
    orderlist : int | Sequence[int], optional
        Interpolation order to use for each image in the input stack. See
        `data_augmentation` for more information. The default is 0.
    sigma : float, optional
        Standard deviation of the normal distribution for random displacement,
        in pixel. The default is 10.
    points : int | tuple[int, int], optional
        Number of points of the deformation grid. If a single value is given,
        the points will be (`points`, `points`). The default is 5.
    rng : npr.Generator | None, optional
        Numpy random number generator for displacement vector generation. If
        None, one will be created from entropy with `npr.default_rng()`.
        The default is None.

    Returns
    -------
    img_stack : list[npt.NDArray[Any]]
        Deformed images.

    """
    try:
        import elasticdeform  # noqa: PLC0415
    except ImportError:
        msg = "elasticdeform is only compatible with numpy 2.0 from python 3.13"
        LOGGER.warning(msg)
        return img_stack

    if isinstance(orderlist, int):
        orderlist = [orderlist] * len(img_stack)

    if rng is None:
        rng = npr.default_rng()

    if isinstance(points, int):
        points = (points, points)

    # Get displacement vector
    displacement = rng.normal(0, sigma, size=(2, *points))

    # Labelize segmentation masks:
    for i, order in enumerate(orderlist):
        if order:
            continue
        img_stack[i] = imgops.label_seg(img_stack[i])

    # Run deformation
    img_stack = elasticdeform.deform_grid(
        img_stack,
        displacement,
        # Using bicubic interpolation instead of bilinear here
        order=[i * 3 for i in orderlist],
        mode="nearest",
        axis=(0, 1),
        prefilter=False,
    )

    # Remove touching pixels:
    for i, order in enumerate(orderlist):
        if order:
            continue
        touching = imgops.detect_touching_cells(img_stack[i])
        img_stack[i] = np.logical_xor(img_stack[i] > 0, touching).astype(np.uint8)

    return img_stack


def histogram_voodoo(
    image: Image, rng: npr.Generator, num_control_points: int = 3
) -> Image:
    """
    Perform a deformation on the image histogram to simulate illumination changes.

    This function was kindly provided by Daniel Eaton from the Paulsson lab.

    Parameters
    ----------
    image : 2D numpy array
        Input image.
    rng : npr.Generator
        Pseudo-random number generator.
    num_control_points : int, optional
        Number of inflection points to use on the histogram conversion curve.
        The default is 3.

    Returns
    -------
    2D numpy array
        Modified image.

    """
    control_points = np.linspace(0, 1, num=num_control_points + 2)
    sorted_points = np.array(control_points)
    random_points = rng.uniform(low=0.1, high=0.9, size=num_control_points)
    sorted_points[1:-1] = np.sort(random_points)
    mapping = interpolate.PchipInterpolator(control_points, sorted_points)

    return np.asarray(mapping(image))


def illumination_voodoo(
    image: Image, rng: npr.Generator, num_control_points: int = 5
) -> Image:
    """
    Simulate a variation in illumination along the length of the chamber.

    This function was inspired by the one above.

    Parameters
    ----------
    image : 2D numpy array
        Input image.
    rng : npr.Generator
        Pseudo-random number generator.
    num_control_points : int, optional
        Number of inflection points to use on the illumination multiplication
        curve.
        The default is 5.

    Returns
    -------
    newimage : 2D numpy array
        Modified image.

    """
    # Create a random curve along the length of the chamber:
    control_points = np.linspace(0, image.shape[0] - 1, num=num_control_points)
    random_points = rng.uniform(low=0.1, high=0.9, size=num_control_points)
    mapping = interpolate.PchipInterpolator(control_points, random_points)
    curve = mapping(np.arange(image.shape[0]))
    # Apply this curve to the image intensity along the length of the chamebr:
    newimage = np.multiply(
        image,
        np.reshape(
            np.tile(np.reshape(curve, (*curve.shape, 1)), (1, image.shape[1])),
            image.shape,
        ),
    )
    # Rescale values to original range:
    newimage = np.interp(
        newimage, (newimage.min(), newimage.max()), (image.min(), image.max())
    )

    return newimage


# %% SEGMENTATION FUNCTIONS:


class SegmentationDataset(keras.utils.Sequence):  # type: ignore[misc]
    """Dataset used to train the segmentation model."""

    def __init__(
        self,
        dataset: tuple[list[Image], list[SegmentationMask], list[Image]],
        target_size: tuple[int, int],
        mode: MODE,
        *,
        kw_data_aug: dict[str, Any],
        crop: bool,
        rng: npr.Generator,
        stack: bool = False,
        **kwargs,
    ) -> None:
        """
        Create a new SegmentationDataset.

        Parameters
        ----------
        dataset : list[tuple[Image, SegmentationMask, Image]]
            Iterable on (image, segmentation mask, weights) tuples.
        target_size : (int, int)
            Target size of the images (input size of the neural network).
        mode : MODE
            In "training" mode, data augmentation is applied.  In "evaluation"
            mode it is not.
        kw_data_aug : dict[str, Any]
            Parameters for the data augmentation function (see `data_augmentation`).
        crop : bool
            If `True`, the images are cropped (randomly in training mode and
            with overlapping tiles in evaluation mode).  If `False`, the images
            are simply resized to the target size.
        rng : npr.Generator
            Random number generator.
        stack : bool
            If `True`, samples are shown in the form (`image`, `labels_weights`)
            where `labels_weights` is a stacked array of the labels and the
            weight map.  This is to use the custom loss and densities.
            If `False`, samples are shown in the form (`image`, `labels`, `weights`).
            The default is False.
        """
        super().__init__(**kwargs)
        self.images: list[Image] | Image
        self.masks: list[SegmentationMask] | SegmentationMask
        self.weights: list[Image] | Image
        if mode not in {"training", "evaluation"}:
            error_msg = '`mode` can only be `"training"` or `"evaluation"`'
            raise ValueError(error_msg)
        if kw_data_aug and mode == "evaluation":
            error_msg = "No data augmentation is supported in evaluation mode."
            raise ValueError(error_msg)
        if rng is None and mode == "training":
            error_msg = "A rng is required in training mode."
            raise ValueError(error_msg)
        images, masks, weights = dataset
        if crop:
            if mode == "training":
                self.images = images
                self.masks = masks
                self.weights = weights
            else:
                images = [imgops.create_windows(img, target_size)[0] for img in images]
                masks = [imgops.create_windows(seg, target_size)[0] for seg in masks]
                weights = [
                    imgops.create_windows(wei, target_size)[0] for wei in weights
                ]
                self.images = np.concatenate(images)
                self.masks = np.concatenate(masks)
                self.weights = np.concatenate(weights)
        else:
            self.images = [imgops.resize_image(img, target_size) for img in images]
            self.masks = [imgops.resize_mask(seg, target_size) for seg in masks]
            self.weights = [imgops.resize_image(wei, target_size) for wei in weights]
        self.order = np.arange(len(self.images))
        self.target_size = target_size
        self.mode = mode
        self.kw_data_aug = kw_data_aug
        self.crop = crop
        self.rng = rng
        self.stack = stack
        LOGGER.info("%s dataset with %d samples.", mode, len(self))

    def __len__(self) -> int:
        """
        Size of the dataset.

        Returns
        -------
        length : int
            Number of samples in the dataset.
        """
        return len(self.images)

    def __getitem__(
        self, idx: int
    ) -> tuple[Image, Image] | tuple[Image, SegmentationMask, Image]:
        """
        Access a given training sample.

        Arguments
        ---------
        idx : int
            Index of a training sample.

        Returns
        -------
        (image, mask, weights) if stack == False
        (image, np.dstack([mask, weights])) if stack == True
        """
        idx = self.order[idx]
        image, mask, weights = self.images[idx], self.masks[idx], self.weights[idx]
        if self.mode == "evaluation":
            if self.stack:
                return (
                    image[np.newaxis, :, :, np.newaxis],
                    np.dstack([mask, weights])[np.newaxis, :, :, :],
                )
            return (
                image[np.newaxis, :, :, np.newaxis],
                mask[np.newaxis, :, :, np.newaxis],
                weights[np.newaxis, :, :, np.newaxis],
            )
        if self.crop:
            image, mask, weights = random_crop(
                image, mask, weights, self.target_size, self.rng
            )
        image, mask, weights = data_augmentation(
            [image, mask, weights],
            aug_par=self.kw_data_aug,
            order=[1, 0, 1],
            rng=self.rng,
        )
        if self.stack:
            return (
                image[np.newaxis, :, :, np.newaxis],
                np.dstack([mask, weights])[np.newaxis, :, :, :],
            )
        return (
            image[np.newaxis, :, :, np.newaxis],
            mask[np.newaxis, :, :, np.newaxis],
            weights[np.newaxis, :, :, np.newaxis],
        )

    def on_epoch_end(self) -> None:
        """
        Shuffle the samples.

        Method executed after each epoch.
        """
        if self.mode == "training":
            self.rng.shuffle(self.order)


@overload
def load_training_dataset_seg(
    dataset_path: Path,
    target_size: tuple[int, int],
    *,
    crop: bool,
    kw_data_aug: dict[str, Any],
    validation_split: Literal[0] = 0,
    test_split: Literal[0] = 0,
    seed: int = 1,
    stack: bool = False,
) -> SegmentationDataset: ...


@overload
def load_training_dataset_seg(
    dataset_path: Path,
    target_size: tuple[int, int],
    *,
    crop: bool,
    kw_data_aug: dict[str, Any],
    validation_split: float,
    test_split: Literal[0] = 0,
    seed: int = 1,
    stack: bool = False,
) -> tuple[SegmentationDataset, SegmentationDataset]: ...


@overload
def load_training_dataset_seg(
    dataset_path: Path,
    target_size: tuple[int, int],
    *,
    crop: bool,
    kw_data_aug: dict[str, Any],
    validation_split: Literal[0] = 0,
    test_split: float,
    seed: int = 1,
    stack: bool = False,
) -> tuple[SegmentationDataset, SegmentationDataset]: ...


@overload
def load_training_dataset_seg(
    dataset_path: Path,
    target_size: tuple[int, int],
    *,
    crop: bool,
    kw_data_aug: dict[str, Any],
    validation_split: float,
    test_split: float,
    seed: int = 1,
    stack: bool = False,
) -> tuple[SegmentationDataset, SegmentationDataset, SegmentationDataset]: ...


def load_training_dataset_seg(
    dataset_path: Path,
    target_size: tuple[int, int],
    *,
    crop: bool,
    kw_data_aug: dict[str, Any],
    validation_split: float = 0,
    test_split: float = 0,
    seed: int = 1,
    stack: bool = False,
) -> (
    SegmentationDataset
    | tuple[SegmentationDataset, SegmentationDataset]
    | tuple[SegmentationDataset, SegmentationDataset, SegmentationDataset]
):
    """
    Create new segmentation datasets.

    Parameters
    ----------
    dataset_path : Path
        Path of the folder that contains `img`, `seg` and optionally `wei`.
    target_size : (int, int)
        Target size of the images (input size of the neural network).
    crop : bool
        If `True`, the images are cropped to the target size, if `False`, they
        are resized.  Typically we resize mother machine images and crop 2D pad
        images.
    kw_data_aug : dict[str, Any]
        Parameters for the data augmentation function (see `data_augmentation`).
    validation_split : float, optional
        Proportion (between 0 and 1) of the input images used for the validation set.
        The default is 0.
    test_split : float, optional
        Proportion (between 0 and 1) of the input images used for the test set.
        The default is 0.
    seed : int, optional
        Seed for the random number generator.
        The default is 1.
    stack : bool, optional
        Whether to stack the labels and weights.  This is a technicality that
        should be removed soon.  For now, specify `True` for cell segmentation
        and `False` for RoI segmentation (follow the example scripts).

    Returns
    -------
    train_ds : SegmentationDataset,
    validation_ds : SegmentationDataset, (optional)
    test_ds : SegmentationDataset, (optional)
    """
    rng = npr.default_rng(seed)

    datasets = _load_images_seg(dataset_path, validation_split, test_split, rng)

    train_ds = SegmentationDataset(
        datasets[0],
        target_size,
        mode="training",
        kw_data_aug=kw_data_aug,
        crop=crop,
        rng=rng,
        stack=stack,
    )

    if not validation_split and not test_split:
        return train_ds

    other_dss = [
        SegmentationDataset(
            other_imgs,
            target_size,
            mode="evaluation",
            kw_data_aug={},
            crop=crop,
            rng=rng,
            stack=stack,
        )
        for other_imgs in datasets[1:]
    ]

    if len(other_dss) == 1:
        return (train_ds, other_dss[0])

    assert len(other_dss) == 2
    return (train_ds, other_dss[0], other_dss[1])


def _load_images_seg(
    dataset_path: Path,
    validation_split: float,
    test_split: float,
    rng: npr.Generator,
) -> list[tuple[list[Image], list[SegmentationMask], list[Image]]]:
    """
    Load the training dataset for ROI segmentation and split it randomly into non-overlapping splits.

    Parameters
    ----------
    dataset_path: Path
        Path of the training dataset, containing `img` (input images) and `seg`
        (segmentation weights).
    validation_split : float
        Proportion of samples to be retained for the validation set (as a
        number between 0 and 1).
    test_split : float
        Proportion of samples to be retained for the test set (as a number
        between 0 and 1).
    rng : npr.Generator
        Numpy random number generator to use to randomly attribute samples to
        datasets.

    Returns
    -------
    datasets: list[tuple[list[Image], list[SegmentationMask], list[Image]]]
        The same number of datasets as requested splits.  Each dataset is a
        tuple of (original image, segmentation mask, sample weights).
    """
    with_weights = (dataset_path / "wei").is_dir()
    if with_weights:
        LOGGER.info("Found a weights directory, using it.")
    else:
        LOGGER.info("Found no weights directory (`wei/`).")

    LOGGER.info("Reading training images...")

    images = []
    masks = []
    mask_paths = defaultdict(list)
    for seg_path in (dataset_path / "seg").iterdir():
        mask_paths[seg_path.stem].append(seg_path)
    if with_weights:
        weights = []
        weight_paths = defaultdict(list)
        for wei_path in (dataset_path / "wei").iterdir():
            weight_paths[wei_path.stem].append(wei_path)
    for img_path in sorted((dataset_path / "img").iterdir()):
        image = imgops.read_image(img_path)
        if len(mask_paths[img_path.stem]) != 1:
            LOGGER.error("Mask not found for image %s", img_path.stem)
            continue
        mask = imgops.read_image(mask_paths[img_path.stem][0])
        if mask.shape != image.shape:
            LOGGER.critical("Image and mask %s don't have the same size", img_path.stem)
            raise RuntimeError
        if with_weights:
            if len(weight_paths[img_path.stem]) != 1:
                LOGGER.error("Weight map not found for image %s", img_path.stem)
                continue
            weight = imgops.read_image(weight_paths[img_path.stem][0])
            if weight.shape != image.shape:
                LOGGER.critical(
                    "Image and weights %s don't have the same size", img_path.stem
                )
                raise RuntimeError
            weights.append(weight)
        images.append(image)
        masks.append(mask.astype(np.uint8))

    LOGGER.info("Found %d training images.", len(images))

    # Create an array of indices, each of them with a frequency given by its
    # respective split, then shuffle it.
    splits = np.array([0, 1 - validation_split - test_split, 1 - test_split, 1])
    nsplits = np.diff(np.round(splits * len(images)))
    indices = np.concatenate([[i] * int(n) for i, n in enumerate(nsplits)])
    rng.shuffle(indices)

    if not with_weights:
        weights = [np.ones_like(image) for image in images]

    flags = [True, validation_split > 0, test_split > 0]
    datasets = [
        (
            [image for index, image in zip(indices, images, strict=True) if index == i],
            [mask for index, mask in zip(indices, masks, strict=True) if index == i],
            [
                weight
                for index, weight in zip(indices, weights, strict=True)
                if index == i
            ],
        )
        for i, flag in enumerate(flags)
        if flag
    ]
    return datasets


def random_crop(
    img: Image,
    seg: SegmentationMask,
    wei: Image,
    target_size: tuple[int, int],
    rng: npr.Generator,
) -> tuple[Image, SegmentationMask, Image]:
    """
    Randomly crop a tuple of (image, segmentation mask, weight map).

    It is padded with zeros if necessary.

    Parameters
    ----------
    img: Image
        Input image.
    seg: SegmentationMask
        Segmentation mask (binary image with 0 for background and 1 for cells).
    wei: Image
        Pixel-wise weights.
    target_size: tuple[int, int]
        Target size for the resizing.
    rng: npr.Generator
        Random number generator.

    Returns
    -------
    img, seg, wei: tuple[Image, SegmentationMask, Image]
        Resized training sample.
    """
    if img.shape == target_size:
        return (img, seg, wei)

    start_y = rng.integers(max(0, img.shape[0] - target_size[0]) + 1)
    start_x = rng.integers(max(0, img.shape[1] - target_size[1]) + 1)
    end_y = min(start_y + target_size[0], img.shape[0])
    end_x = min(start_x + target_size[1], img.shape[1])
    pad_y = target_size[0] - (end_y - start_y)
    pad_x = target_size[1] - (end_x - start_x)
    padding = ((pad_y // 2, pad_y - pad_y // 2), (pad_x // 2, pad_x - pad_x // 2))

    img = np.pad(img[start_y:end_y, start_x:end_x], padding)
    seg = np.pad(seg[start_y:end_y, start_x:end_x], padding)
    wei = np.pad(wei[start_y:end_y, start_x:end_x], padding)

    assert img.shape == target_size, f"{img.shape}"
    assert seg.shape == target_size, f"{seg.shape}"
    assert wei.shape == target_size, f"{wei.shape}"
    return (img, seg, wei)


def save_result_seg(
    save_path: Path,
    npyfile: npt.NDArray[Any],
    *,
    files_list: list[Path] | None = None,
    multipage: bool = False,
) -> None:
    """
    Save an array of segmentation output images to disk.

    Parameters
    ----------
    save_path : string
        Path to save folder.
    npyfile : 3D or 4D numpy array
        Array of segmentation outputs to save to individual files. If 4D, only
        the images from the first index of axis=3 will be saved.
    files_list : list of strings, optional
        Filenames to save the segmentation masks as. png, tif or jpg extensions
        work.
        The default is [].
    multipage : bool, optional
        Flag to save all output masks as a single, multi-page TIFF file. Note
        that if the file already exists, the masks will be appended to it.
        The default is False.
    """
    if files_list is None:
        files_list = []
    for i, item in enumerate(npyfile):
        img = item[:, :, 0] if item.ndim == 3 else item
        if multipage:
            filename = save_path / files_list[0]
            img_uint8 = imgops.to_integer_values(img, np.uint8)
            io.imsave(filename, img_uint8, plugin="tifffile", append=True)
        else:
            if files_list:
                filename = save_path / files_list[i].name
            else:
                filename = save_path / f"{i}_predict.png"
            cv2.imwrite(filename.as_posix(), imgops.to_integer_values(img, np.uint8))


def predict_generator_seg(
    files_path: Path,
    *,
    files_list: Sequence[Path] | None = None,
    target_size: tuple[int, int] = (256, 32),
    crop_windows: bool = False,
) -> Iterator[tuple[Image]]:
    """
    Get a generator for predicting segmentation on new image files once the segmentation U-Net has been trained.

    Parameters
    ----------
    files_path : Path
        Path to image files folder.
    files_list : list/tuple of Paths, optional
        List of file names to read in the folder. If None, all
        files in the folder will be read.
        The default is None.
    target_size : tuple of 2 ints, optional
        Size for the images to be resized.
        The default is (256,32).
    crop_windows : bool
        TODO
        The default is False.

    Returns
    -------
    mygen : generator
        Generator that will yield single image files as 4D numpy arrays of
        size (1, target_size[0], target_size[1], 1).

    """
    files_list = files_list or sorted(files_path.iterdir())

    def generator(
        files_path: Path,
        files_list: Sequence[Path],
        target_size: tuple[int, int],
    ) -> Iterator[Image]:
        for fname in files_list:
            img = imgops.read_reshape(
                files_path / fname,
                target_size=target_size,
                order=1,
                method="pad" if crop_windows else "resize",
            )
            # Tensorflow needs one extra single dimension (so that it is a 4D tensor)
            reshaped_img = np.reshape(img, (1, *img.shape))

            yield (cast("Image", reshaped_img),)  # for mypy

    mygen = generator(files_path, files_list, target_size)
    return mygen


def seg_weights(
    mask: SegmentationMask,
    classweights: tuple[float, float] = (1, 1),
    w0: float = 12,
    sigma: float = 2,
) -> Image:
    """
    Compute the weight map as described in the original U-Net paper to force the model to learn borders.

    (Slow, best to run this offline before training).

    Parameters
    ----------
    mask : 2D array
        Training output segmentation mask.
    classweights : tuple of 2 int/floats
        Weights to apply to background, foreground.
        The default is (1,1)
    w0 : int or float, optional
        Base weight to apply to smallest distance (1 pixel).
        The default is 12.
    sigma : int or float, optional
        Exponential decay rate to apply to distance weights.
        The default is 2.

    Returns
    -------
    weightmap : 2D array
        Weights map image.

    """
    # Ensure mask has {0, 255} pixel values
    mask_255 = imgops.to_integer_values(mask.astype(np.float32), np.uint8)
    # Get cell labels mask
    lblnb, lblimg = cv2.connectedComponents(mask_255)

    # Compute cell-to-cell distances
    distances = np.inf * np.ones((*mask.shape, max(lblnb, 2)))
    for i in range(lblnb - 1):
        imask = (lblimg != i + 1).astype(np.uint8)
        distances[:, :, i] = cv2.distanceTransform(
            imask, cv2.DIST_L2, cv2.DIST_MASK_PRECISE
        )

    # Put 2 smallest distances at the beginning
    distances.partition(1, axis=-1)

    # Compute weights map
    weights = w0 * np.exp(-(distances[:, :, :2].sum(-1) ** 2) / (2 * sigma**2))
    weights += classweights[0]
    weights[mask == 1] = classweights[1]

    return np.asarray(weights)


def make_weights(
    training_dataset_path: str | Path,
    weights_function: Callable[[SegmentationMask], npt.NDArray[np.float32]],
) -> None:
    """
    Create and populate the directory `training_dataset_path/wei` with the image weights for training.

    The directory `training_dataset_path` should already contain "img" with the
    input images and "seg" with the segmentation masks (images with 0 for
    background pixels and 255 for cell pixels).

    Parameters
    ----------
    training_dataset_path : str or Path
        Directory containing two directories: "img" for the images and "seg"
        for the segmentation masks.  A third directory "wei" will be created
        inside for the weights.
    weights_function : Callable[SegmentationMask, npt.NDArray[np.float32]],
        Function that takes a segmentation mask (0 for background and 1 for
        cells) and returns a weight array (non-negative floats).  The weights
        will be normalized by their maximum before being written down as images.
        Possible values are `delta.data.seg_weights` for mothermachine images,
        `delta.data.seg_weights_2D` for 2D pads, or custom functions or lambdas.
    """
    training_dataset_path = Path(training_dataset_path)
    (training_dataset_path / "wei").mkdir()
    for seg_path in sorted((training_dataset_path / "seg").iterdir()):
        LOGGER.info("Making weights for %s...", seg_path.name)
        mask = np.asarray(imgops.read_image(seg_path), dtype=np.uint8)
        weights = weights_function(mask)
        norm_weights = weights / weights.max() if weights.max() > 0 else weights
        int_weights = imgops.to_integer_values(norm_weights, np.uint8)
        cv2.imwrite(str(training_dataset_path / "wei" / seg_path.name), int_weights)


def kernel(n: int) -> SegmentationMask:
    """
    Get kernel for morphological operations.

    Parameters
    ----------
    n : Int
        Determine size of kernel.

    Returns
    -------
    kernel : Array of unit8
        Returns a kernel with size of n.

    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))
    return np.asarray(kernel)


def estimate_seg2D_classweights(  # noqa: N802
    mask_path: Path,
    sample_size: int | None = None,
    rng: npr.Generator | None = None,
) -> tuple[float, float]:
    """
    Estimate the weights to assign each class in the weight maps.

    Parameters
    ----------
    mask_path : str
        Path to folder containing segmentations.
    sample_size : int, optional
        Determines the size of the training set that will be used to calculate class weights.
        The default is None.
    rng : npr.Generator, optional
        Pseudo-random number generator used to subsample the dataset if needed.

    Returns
    -------
    class1 : float
        weight of class 1.
    class2 : float
        weight of class 2.

    """
    mask_names = utils.list_files(mask_path, {".png", ".tif"})

    # Subsample the training set to reduce computation time.
    if sample_size:
        if rng is None:
            rng = npr.default_rng()
        random_indices = rng.choice(len(mask_names), sample_size)
        mask_names = [mask_names[i] for i in random_indices]

    c1 = 0
    c2 = 0

    for mask_name in mask_names:
        mask = imgops.read_image(mask_name)

        # Extract all pixels that include the cells and its border (no background)
        border = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel(20))
        # Set all pixels that include the cells to zero to leave behind the border only
        border[mask > 0] = 0

        # Erode the segmentation to avoid putting high emphasis on edges of cells
        mask_erode = cv2.erode(mask, kernel(2))
        skel = morph.skeletonize(mask_erode)

        mask_dil = cv2.dilate(mask, kernel(3))
        border_erode = (mask_dil == 0) & (border > 0)
        skel_border = morph.skeletonize(border_erode)

        c1 += skel.sum()
        c2 += skel_border.sum()

    max12 = max(c1, c2)

    return c2 / max12, c1 / max12


def seg_weights_2D(  # noqa: N802
    mask: SegmentationMask, classweights: tuple[float, float] = (1, 1)
) -> Image:
    """
    Compute custom weightmaps designed for bacterial images where borders are difficult to distinguish.

    Parameters
    ----------
    mask : 2D array
        Training output segmentation mask.
    classweights : tuple of 2 int/floats, optional
        Weights to apply to cells and border
        The default is (1,1)

    Returns
    -------
    weightmap : 2D array
        Weights map image.

    """
    if mask.ndim == 3:
        mask = mask[:, :, 0]
    if np.max(mask) == 255:
        mask[mask > 0] = 1

    # Extract all pixels that include the cells and it's border
    border = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel(20))
    # Set all pixels that include the cells to zero to leave behind the border only
    border[mask > 0] = 0

    # Erode the segmentation to avoid putting high emphasiss on edges of cells
    mask_erode = cv2.erode(mask, kernel(2))

    # Get the skeleton of the segmentation and border
    mask_skel = morph.skeletonize(mask_erode > 0)
    border_skel = morph.skeletonize(border > 0)

    # Find the distances from the skeleton of the segmention and border
    border_dist = cv2.distanceTransform(
        imgops.to_integer_values(border_skel < 1, np.uint8),
        cv2.DIST_L2,
        cv2.DIST_MASK_PRECISE,
    )
    mask_dist = cv2.distanceTransform(
        imgops.to_integer_values(mask_skel < 1, np.uint8),
        cv2.DIST_L2,
        cv2.DIST_MASK_PRECISE,
    )

    # Use the distance from the skeletons to create a gradient towards the skeleton
    border_gra = border * (classweights[1]) / (border_dist + 1) ** 2
    mask_gra = mask / (mask_dist + 1) ** 2

    # Set up weights array
    weightmap = np.zeros((mask.shape), dtype=np.float32)

    # Add the gradients for the segmentation and border into the weights array
    weightmap[mask_erode > 0] = mask_gra[mask_erode > 0]
    weightmap[border > 0] = border_gra[border > 0]

    # Set the skeletons of the segmentation and borders to the maximum values
    weightmap[mask_skel > 0] = classweights[0]
    weightmap[border_skel > 0] = classweights[1]

    # Keep the background zero and set the erode values in the seg/border to a minimum of 1
    bkgd = np.ones(mask.shape) - mask - border
    weightmap[((weightmap == 0) * (bkgd < 1))] = 1 / 255

    return weightmap


def estimate_classweights(gene: Iterator, num_samples: int = 30) -> tuple[float, ...]:  # type: ignore[type-arg]
    """
    Estimate the class weights to use with the weighted categorical cross-entropy based on the train_generator_track output.

    Parameters
    ----------
    gene : generator
        Tracking U-Net training generator. (output of train_generator_seg/track)
    num_samples : int, optional
        Number of batches to use for estimation. The default is 30.

    Returns
    -------
    class_weights : tuple of floats
        Relative weights of each class. Note that, if 0 elements of a certain
        class are present in the samples, the weight for this class will be set
        to 0.

    """
    sample = next(gene)
    class_counts = [0] * (2 if sample[1].shape[-1] == 1 else sample[1].shape[-1])

    # Run through samples and classes/categories:
    for _ in range(num_samples):
        if sample[1].shape[-1] == 1:
            class_counts[1] += np.mean(sample[1] > 0)
            class_counts[0] += np.mean(sample[1] == 0)
        else:
            for i in range(sample[1].shape[-1]):
                class_counts[i] += np.mean(sample[1][..., i])
        sample = next(gene)

    # Warning! If 0 elements of a certain class are present in the samples, the
    # weight for this class will be set to 0. This is for the tracking case
    # (Where there are only empty daughter images in the training set)
    # Try changing the num_samples value if this is a problem

    # Normalize by nb of samples and invert to get weights, unless x == 0 to
    # avoid Infinite weights or errors
    class_weights = tuple(num_samples / x if x != 0 else 0 for x in class_counts)

    return class_weights


# %% TRACKING FUNCTIONS


def train_generator_track(
    batch_size: int,
    img_path: Path,
    seg_path: Path,
    previmg_path: Path,
    segall_path: Path,
    track_path: Path,
    weights_path: Path | Literal["online"] | None = None,
    *,
    augment_params: dict[str, Any] | None = None,
    crop_windows: bool = False,
    target_size: tuple[int, int] = (256, 32),
    shift: int = 0,
    seed: int = 1,
) -> Iterator[tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]]:
    """
    Create a generato to train the tracking U-Net.

    Parameters
    ----------
    batch_size : int
        Batch size, number of training samples to concatenate together.
    img_path : string
        Path to folder containing training input images (current timepoint).
    seg_path : string
        Path to folder containing training 'seed' images, ie mask of 1 cell
        in the previous image to track in the current image.
    previmg_path : string
        Path to folder containing training input images (previous timepoint).
    segall_path : string
        Path to folder containing training 'segall' images, ie mask of all
        cells in the current image.
    track_path : string
        Path to folder containing tracking groundtruth, ie mask of
        the seed cell and its potential daughter tracked in the current frame.
    weights_path : string or None, optional
        Path to folder containing pixel-wise weights to apply to the tracking
        groundtruth. If None, the same weight is applied to all pixels. If the
        string is 'online', weights will be generated on the fly (not
        recommended, much slower)
        The default is None.
    augment_params : dict, optional
        Data augmentation parameters. See data_augmentation() doc for more info
        The default is {}.
    target_size : tuple of 2 ints, optional
        Input and output image size.
        The default is (256,32).
    crop_windows : bool, optional
        Whether to crop out a window of size `target_size` around the seed/seg
        cell to track for all input images instead of resizing.
    shift : int, optional
        If `crop_windows` is True, a shift between [-shift, +shift]
        will be uniformly sampled for both the X and the Y axis. This shift in
        pixels will be applied only to the the cropbox for the current timepoint
        input frames (img,segall,mot_dau,wei), to simulate image drift over time.
    seed : int, optional
        Seed for numpy's random generator.
        The default is 1.

    Yields
    ------
    inputs_arr : 4D numpy array of floats
        Input images and masks for the U-Net training routine. Dimensions of
        the tensor are (batch_size, target_size[0], target_size[1], 4)
    outputs_arr : 4D numpy array of floats
        Output masks for the U-Net training routine. Dimensions of the tensor
        are (batch_size, target_size[0], target_size[1], 3). The third index
        of axis=3 contains 'background' masks, ie the part of the tracking
        output groundtruth that is not part of the mother or daughter masks
    """
    if augment_params is None:
        augment_params = {}
    resize_method = "pad" if crop_windows else "resize"

    # Initialize variables and arrays:
    image_names = utils.list_files(img_path, {".png", ".tif"})
    xs = np.empty((batch_size, *target_size, 4), dtype=np.float32)
    ys = np.empty((batch_size, *target_size, 2), dtype=np.float32)

    # Create a PNRG
    rng = npr.default_rng(seed)

    while True:
        xs[:, :, :, :] = 0
        ys[:, :, :, :] = 0

        for b in range(batch_size):
            # Pick random image file name
            filename = image_names[rng.choice(len(image_names))]

            # Read images:
            img_ = imgops.read_reshape(
                filename, target_size=target_size, order=1, method=resize_method
            )
            img: Image = cast("Image", img_)  # for mypy
            seg_ = imgops.read_reshape(
                seg_path / filename.name,
                target_size=target_size,
                binarize=True,
                order=0,
                method=resize_method,
            )
            seg: SegmentationMask = cast("SegmentationMask", seg_)  # for mypy
            previmg_ = imgops.read_reshape(
                previmg_path / filename.name,
                target_size=target_size,
                order=1,
                method=resize_method,
            )
            previmg: Image = cast("Image", previmg_)  # for mypy
            segall_ = imgops.read_reshape(
                segall_path / filename.name,
                target_size=target_size,
                binarize=True,
                order=0,
                method=resize_method,
            )
            segall: SegmentationMask = cast("SegmentationMask", segall_)  # for mypy

            track_ = imgops.read_reshape(
                track_path / filename.name,
                target_size=target_size,
                binarize=True,
                order=0,
                method=resize_method,
            )
            track: SegmentationMask = cast("SegmentationMask", track_)  # for mypy
            if weights_path is not None:
                if weights_path == "online":
                    weights = tracking_weights(track, segall)
                else:
                    weights = cast(
                        "Image",
                        imgops.read_reshape(
                            weights_path / filename.name,
                            target_size=target_size,
                            binarize=False,
                            order=0,
                            method=resize_method,
                        ),
                    )
            else:
                weights = np.ones_like(track)

            # Data augmentation:
            [img, seg, previmg, segall, track, weights] = data_augmentation(
                [img, seg, previmg, segall, track, weights],
                augment_params,
                order=[1, 0, 1, 0, 0, 0],
                rng=rng,
            )

            if crop_windows:
                cb = imgops.CroppingBox.tracking_box(seg, target_size)
                shift_y, shift_x = rng.integers(-shift, shift, size=2, endpoint=True)
            else:
                cb = imgops.CroppingBox.full(seg)
                shift_y, shift_x = 0, 0

            # Add into arrays:

            xs[b, :, :, 1] = cb.crop(seg)
            xs[b, :, :, 2] = cb.crop(previmg)

            # Shift crop box for current frame inputs
            cb.xtl += shift_x
            cb.xbr += shift_x
            cb.ytl += shift_y
            cb.ybr += shift_y

            xs[b, :, :, 0] = cb.crop(img)
            xs[b, :, :, 3] = cb.crop(segall)

            ys[b, :, :, 0] = cb.crop(track)
            ys[b, :, :, 1] = cb.crop(weights)

        # Yield batch:
        yield xs, ys


def path_from_prototype(
    prototype: str,
    fileorder: str,
    position: int | None = None,
    chamber: int | None = None,
    frame: int | None = None,
    cellnb: int | None = None,
) -> Path:
    """
    Generate full filename for specific frame based on file path, prototype, fileorder, and filenamesindexing.

    Parameters
    ----------
    prototype : str
        Filename prototype, written in c-style format. See delta.utils.xpreader
        for more details
    fileorder : str
        Filenames ordering. See delta.utils.xpreader for more details
    position : int, optional
        Position/series index (0-based indexing).
    chamber : int, optional
        Imaging chamber index (0-based indexing).
    frame : int, optional
        Frame/timepoint index (0-based indexing).
    cellnb: int, optional
        Cell index (0-based indexing).

    Returns
    -------
    string
        Filename.

    """
    filenumbers = []

    for i in fileorder:
        if i == "p":
            assert position is not None
            filenumbers.append(position)
        if i == "c":
            assert chamber is not None
            filenumbers.append(chamber)
        if i == "t":
            assert frame is not None
            filenumbers.append(frame)
        if i == "n":
            assert cellnb is not None
            filenumbers.append(cellnb)

    if cellnb is not None:
        prototype = Path(prototype).stem + "Cell%06d" + Path(prototype).suffix

    return Path(prototype % tuple(filenumbers))


def predict_compile_from_seg_track(
    img_path: Path,
    seg_path: Path,
    files_list: list[Path],
    *,
    target_size: tuple[int, int] = (256, 32),
    crop_windows: bool = False,
) -> tuple[
    npt.NDArray[np.float32],
    list[Path],
    list[imgops.CroppingBox],
]:
    """
    Compile an inputs array for tracking prediction with the tracking U-Net, directly from U-Net segmentation masks saved to disk.

    Parameters
    ----------
    img_path : Path
        Path to original single-chamber images folder. The filenames are
        expected in the printf format Position%02d_Chamber%02d_Frame%03d.png
    seg_path : Path
        Path to segmentation output masks folder. The filenames must be the
        same as in the img_path folder.
    files_list : list[Path]
        List of filenames to compile in the img_path and seg_path folders.
    target_size : tuple of 2 ints, optional
        Input and output image size.
        The default is (256,32).
    crop_windows : bool, optional
        TODO
        The default is False.

    Returns
    -------
    inputs_arr : 4D numpy array of floats
        Input images and masks for the tracking U-Net training routine.
        Dimensions of the tensor are (cells_to_track, target_size[0],
        target_size[1], 4), with cells_to_track the number of segmented cells
        in all segmentation masks of the files_list.
    seg_name_list : [Path]
        Filenames to save the tracking outputs as. The printf format is
        Position%02d_Chamber%02d_Frame%03d_Cell%02d.png, with the '_Cell%02d'
        string appended to signal which cell is being seeded/tracked (from top
        to bottom)
    boxes : list of CroppingBox
        Cropping box to re-place output prediction masks in the
        original image coordinates.


    """
    seg_name_list = []

    ind = 0

    resize_method = "pad" if crop_windows else "resize"

    # Get digits sequences in first filename
    numstrs = re.findall(r"\d+", files_list[0].name)
    # Get digits sequences in first filename
    charstrs = re.findall(r"\D+", files_list[0].name)

    # Create the string prototype to be used to generate filenames on the fly:
    if len(numstrs) == 3 and len(charstrs) == 4:
        # Order is position, chamber, frame/timepoint
        prototype = (
            f"{charstrs[0]}%0{len(numstrs[0])}d"
            f"{charstrs[1]}%0{len(numstrs[1])}d"
            f"{charstrs[2]}%0{len(numstrs[2])}d"
            f"{charstrs[3]}"
        )
        fileorder = "pct"
    elif len(numstrs) == 2 and len(charstrs) == 3:
        # Order is position, frame/timepoint
        prototype = (
            f"{charstrs[0]}%0{len(numstrs[0])}d"
            f"{charstrs[1]}%0{len(numstrs[1])}d"
            f"{charstrs[2]}"
        )
        fileorder = "pt"
    else:
        error_msg = (
            "Filename formatting error. See documentation for image sequence formatting"
        )
        raise ValueError(error_msg)
    fileordercell = fileorder + "n"

    boxes = []
    for item in files_list:
        filename = item.name
        # Get position, chamber & frame numbers:
        cha: int | None
        if fileorder == "pct":
            (pos, cha, fra) = list(map(int, re.findall(r"\d+", filename)))
        elif fileorder == "pt":
            (pos, fra) = list(map(int, re.findall(r"\d+", filename)))
            cha = None

        if fra > 1:
            prevframename = path_from_prototype(
                prototype, fileorder, position=pos, chamber=cha, frame=fra - 1
            )

            img = imgops.read_reshape(
                img_path / filename,
                target_size=target_size,
                order=1,
                method=resize_method,
            )
            segall = imgops.read_reshape(
                seg_path / filename,
                target_size=target_size,
                order=0,
                binarize=True,
                method=resize_method,
            )
            previmg = imgops.read_reshape(
                img_path / prevframename,
                target_size=target_size,
                order=1,
                method=resize_method,
            )
            prevsegall = imgops.read_reshape(
                seg_path / prevframename,
                target_size=target_size,
                order=0,
                binarize=True,
                method=resize_method,
            )

            lblimg, lblnb = label(prevsegall, connectivity=1, return_num=True)

            x = np.zeros(shape=(lblnb, *target_size, 4), dtype=np.float32)

            for lbl in range(1, lblnb + 1):
                seg = lblimg == lbl
                seg = seg.astype(np.uint8)  # Output is boolean otherwise

                # Cell-centered crop boxes:
                if crop_windows:
                    cb = imgops.CroppingBox.tracking_box(seg, target_size)
                else:
                    cb = imgops.CroppingBox.full(img)
                boxes += [cb]

                # Current image
                x[lbl - 1, :, :, 0] = cb.crop(img)

                x[lbl - 1, :, :, 1] = cb.crop(seg)

                # Previous image
                x[lbl - 1, :, :, 2] = cb.crop(previmg)

                # Segmentation of all current cells
                x[lbl - 1, :, :, 3] = cb.crop(segall)

                segfilename = path_from_prototype(
                    prototype,
                    fileordercell,
                    position=pos,
                    chamber=cha,
                    frame=fra - 1,
                    cellnb=lbl,
                )

                seg_name_list.append(segfilename)

            if ind == 0:
                inputs_arr = x
                ind = 1
            else:
                inputs_arr = np.concatenate((inputs_arr, x), axis=0)
    return inputs_arr, seg_name_list, boxes


def tracking_weights(
    track: SegmentationMask, segall: SegmentationMask, halo_distance: int = 50
) -> npt.NDArray[np.float32]:
    """
    Compute weights for tracking training sets.

    Parameters
    ----------
    track : 2D array
        Tracking output mask.
    segall : 2D array
        Segmentation mask of all cells in current image.
    halo_distance : int, optional
        Distance in pixels to emphasize other cells from tracked cell.
        The default is 50.

    Returns
    -------
    weights : 2D array
        Tracking weights map.

    """
    # Cell escaped / disappeared:
    if np.max(track) == 0:
        weights = ((segall > 0).astype(np.float32) * 20) + 1
        return weights

    # Distance from the tracked cell:
    _, dist_from = morph.medial_axis(track == 0, return_distance=True)
    dist_from = halo_distance - dist_from
    dist_from[dist_from < 1] = 1

    # Distance from border within cell:
    _, dist_in = morph.medial_axis(track > 0, return_distance=True)

    # Tracked cell skeleton:
    skel = morph.skeletonize(track, method="lee")

    # Tracked Cell weights are distance from edges + skeleton at 255 in the center
    weights = 1 + 41 * (dist_in.astype(np.float32) - dist_in.min()) / dist_in.ptp()
    weights[skel > 0] = 255

    # Rest of the image is weighed according to distance from tracked cell:
    weights += (
        63
        * (dist_from / halo_distance)
        * (segall > 0).astype(np.float32)
        * (track == 0).astype(np.float32)
    )

    weights *= 100
    weights[dist_from < 1] = 1

    return weights


def save_result_track(
    save_path: Path,
    npyfile: npt.NDArray[Any],
    files_list: list[Path] | None = None,
) -> None:
    """
    Save tracking output masks to disk.

    Parameters
    ----------
    save_path : Path
        Folder to save images to.
    npyfile : 4D numpy array
        Array of tracking outputs (logits) to save to individual files.
    files_list : tuple/list of strings, optional
        Filenames to save the masks as. Note that the `mother_` and `daughter_`
        prefixes will be added to those names. If None, numbers will be used.
        The default is None.
    """
    mothers = npyfile[:, :, :, 0]
    for i, mother in enumerate(mothers):
        if files_list:
            filename = save_path / files_list[i].name
        else:
            filename = save_path / f"tracking_{i:09d}.png"
        cv2.imwrite(
            filename.as_posix(), imgops.to_integer_values(expit(mother), np.uint8)
        )
