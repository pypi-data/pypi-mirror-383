import itertools as it
from pathlib import Path

import cv2
import numpy as np
import numpy.testing as npt
import pytest
from keras import ops

import delta
from delta import imgops


def nb_params_unet(filters: list[int]) -> int:
    nb_params = 0
    for filters_a, filters_b in it.pairwise([1, *filters]):
        nb_params += (1 + 3**2 * filters_a) * filters_b
        nb_params += (1 + 3**2 * filters_b) * filters_b
    for filters_a, filters_b in it.pairwise(filters[::-1]):
        nb_params += (1 + 2**2 * filters_a) * filters_b
        nb_params += (1 + 3**2 * filters_a) * filters_b
        nb_params += (1 + 3**2 * filters_b) * filters_b
    nb_params += 1 + filters[0]
    return nb_params


@pytest.mark.parametrize(
    "levels, nb_params",
    [
        (1, nb_params_unet([64])),
        (2, nb_params_unet([64, 128])),
        (3, nb_params_unet([64, 128, 256])),
        (4, nb_params_unet([64, 128, 256, 512])),
        (5, nb_params_unet([64, 128, 256, 512, 1024])),
    ],
)
def test_nb_params_unet(levels: int, nb_params: int):
    model = delta.model.unet(levels=levels)
    assert model.count_params() == nb_params


def test_pixelwise_weighted_binary_crossentropy_seg():
    rng = np.random.default_rng(seed=42)
    shape = (10, 20)
    labels = rng.integers(2, size=shape)
    weights = rng.uniform(size=shape)
    logits = rng.normal(size=shape)
    keras_labels_weights = ops.convert_to_tensor(np.stack([labels, weights], axis=-1))
    keras_logits = ops.convert_to_tensor(logits[:, :, np.newaxis])

    loss = delta.model.pixelwise_weighted_binary_crossentropy_seg(
        keras_labels_weights, keras_logits
    )
    npt.assert_allclose(ops.convert_to_numpy(loss).sum(), 8053870.791163433)


def test_pixelwise_weighted_binary_crossentropy_track():
    rng = np.random.default_rng(seed=42)
    shape = (10, 20)
    labels = rng.integers(2, size=shape)
    weights = rng.uniform(size=shape)
    logits = rng.normal(size=shape)
    tf_labels_weights = ops.convert_to_tensor(np.stack([labels, weights], axis=-1))
    tf_logits = ops.convert_to_tensor(logits[:, :, np.newaxis])

    loss = delta.model.pixelwise_weighted_binary_crossentropy_track(
        tf_labels_weights, tf_logits
    )
    npt.assert_allclose(ops.convert_to_numpy(loss).sum(), 8053870.791163433)


def test_moma_segmentation_canary():
    config = delta.config.Config.default("mothermachine")
    model = config.models["seg"].model()
    path = Path(__file__).parent / "data/images"
    img = imgops.read_image(path / "moma_segmentation_canary.png")
    seg = (model.predict(img[np.newaxis, :, :, np.newaxis])[0, :, :, 0] > 0).astype(
        np.uint8
    )
    lblnb, _ = cv2.connectedComponents(seg)
    assert lblnb == 6


@pytest.mark.parametrize(
    argnames="size",
    argvalues=[
        (None, None),
        (32, 256),
        (512, 512),
    ],
)
def test_unet_variable_sizes(size: tuple[int | None, int | None]):
    delta.model.unet(input_size=(*size, 1))


@pytest.mark.xfail(reason="support for odd sizes removed")
@pytest.mark.parametrize(
    argnames="size",
    argvalues=[
        (30, 250),
        (31, 251),
        (17, 250),
        (40, 301),
    ],
)
def test_unet_odd_sizes(size: tuple[int | None, int | None]):
    delta.model.unet(input_size=(*size, 1))
