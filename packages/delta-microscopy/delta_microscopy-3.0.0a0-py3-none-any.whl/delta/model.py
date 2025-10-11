"""
Model and loss/metrics functions definitions.

This module contains the declaration of the U-Nets in Keras / Tensorflow as
well as the loss function we used to train them.  See our publications for
descriptions of the models and losses.

For the seminal paper describing the structure of the U-Net model:

`Ronneberger, Olaf, Philipp Fischer, and Thomas Brox. "U-net: Convolutional networks for biomedical image segmentation." International Conference on Medical image computing and computer-assisted intervention. 2015 <https://link.springer.com/chapter/10.1007/978-3-319-24574-4_28>`_

"""

import hashlib
import logging

import keras
from keras import KerasTensor, ops
from keras.layers import (
    Concatenate,
    Conv2D,
    Dropout,
    Input,
    MaxPool2D,
    UpSampling2D,
)
from keras.models import Model
from keras.optimizers import Adam

LOGGER = logging.getLogger(__name__)


def hash_model(model: Model) -> str:
    """
    Return a hashsum of the given keras model.

    Parameters
    ----------
    model : Model
        Model to hash.

    Returns
    -------
    hash : str
        Hashsum of the model.
    """
    hasher = hashlib.sha256()
    hasher.update(str(model.get_config()).encode())
    for weights in model.get_weights():
        hasher.update(weights.data.tobytes())
    return hasher.hexdigest()


# %% Losses/metrics


def pixelwise_weighted_binary_crossentropy_seg(
    seg_weights: KerasTensor, logits: KerasTensor
) -> KerasTensor:
    """
    Pixel-wise weighted binary cross-entropy loss.

    The code is adapted from the Keras TF backend.
    (see their github).

    Parameters
    ----------
    seg_weights : Tensor
        Stack of groundtruth segmentation masks + weight maps.
    logits : Tensor
        Predicted segmentation masks.

    Returns
    -------
    Tensor
        Pixel-wise weight binary cross-entropy between inputs.

    """
    # The weights are passed as part of the seg_weights tensor:
    seg, weights = ops.unstack(seg_weights, 2, axis=-1)

    seg = ops.expand_dims(seg, -1)
    weights = ops.expand_dims(weights, -1)

    # Make background weights be equal to the model's prediction
    weights = ops.where(weights == 0, ops.sigmoid(logits), weights)

    entropy = ops.relu(logits) - logits * seg + ops.log1p(ops.exp(-ops.abs(logits)))

    loss = ops.mean(weights * entropy, axis=-1)

    loss = 1e6 * loss / ops.sqrt(ops.sum(weights))

    return loss


def pixelwise_weighted_binary_crossentropy_track(
    seg_weights: KerasTensor, logits: KerasTensor
) -> KerasTensor:
    """
    Pixel-wise weighted binary cross-entropy loss.

    The code is adapted from the Keras TF backend.
    (see their github).

    Parameters
    ----------
    seg_weights : Tensor
        Stack of groundtruth segmentation masks + weight maps.
    logits : Tensor
        Predicted segmentation masks.

    Returns
    -------
    Tensor
        Pixel-wise weight binary cross-entropy between inputs.

    """
    # The weights are passed as part of the seg_weights tensor:
    seg, weights = ops.unstack(seg_weights, 2, axis=-1)

    seg = ops.expand_dims(seg, -1)
    weights = ops.expand_dims(weights, -1)

    entropy = (
        ops.relu(logits) - logits * seg + ops.log1p(ops.exp(-ops.absolute(logits)))
    )

    loss = ops.mean(weights * entropy, axis=-1)

    loss = 1e6 * loss / ops.sqrt(ops.sum(weights))

    return loss


def unstack_acc(seg_weights: KerasTensor, logits: KerasTensor) -> KerasTensor:
    """
    Compute binary accuracy from a stacked tensor with mask and weight map.

    Parameters
    ----------
    seg_weights : Tensor
        Stack of groundtruth segmentation masks + weight maps.
    logits : Tensor
        Predicted segmentation masks.

    Returns
    -------
    Tensor
        Binary prediction accuracy.

    """
    seg, _weights = ops.unstack(seg_weights, 2, axis=-1)

    seg = ops.expand_dims(seg, -1)

    return keras.metrics.binary_accuracy(seg, logits, threshold=0)


def _unet(
    input_layer: KerasTensor,
    filters: list[int],
    levels: int,
    conv2d_kwargs: dict[str, str],
    dropout: float = 0.0,
) -> KerasTensor:
    """
    Create a U-Net recursively.

    The number of filters at each level are specified with the `filters` argument.

    Parameters
    ----------
    input_layer : KerasTensor
        The convolutional layer that is the output of the U-Net.
    filters : [int]
        Number of convolutional kernels for each level of the network.
    levels : int
        The total number of layers in the U-Net (to give the correct name to layers).
    conv2d_kwargs : dict[str, str]
        kwargs for the Conv2D layers of the block.
    dropout : float, default 0.0
        Dropout layer rate in the block. Valid range is [0,1). If 0, no dropout
        layer is added.

    Returns
    -------
    output_layer : KerasTensor
        Output layer of the U-Net (before final convolution).

    """
    name = f"Level{levels - len(filters)}"

    filters_here, *filters_next = filters

    # Initial convolutions
    conv1 = Conv2D(filters_here, 3, **conv2d_kwargs, name=f"{name}_Conv2D_1")(
        input_layer
    )
    conv2 = Conv2D(filters_here, 3, **conv2d_kwargs, name=f"{name}_Conv2D_2")(conv1)

    if dropout > 0.0:
        conv2 = Dropout(dropout, name=f"{name}_Dropout_1")(conv2)

    if not filters_next:
        # This is the last layer
        return conv2

    # Down-sampling
    pool = MaxPool2D(pool_size=(2, 2), name=f"{name}_MaxPooling2D", padding="same")(
        conv2
    )

    # Recursive unet
    output = _unet(
        pool,
        filters=filters_next,
        levels=levels,
        conv2d_kwargs=conv2d_kwargs,
        dropout=dropout,
    )

    # Up-sampling
    up = UpSampling2D(size=(2, 2), name=f"{name}_UpSampling2D")(output)
    conv3 = Conv2D(filters_here, 2, **conv2d_kwargs, name=f"{name}_Conv2D_3")(up)

    # Merge with skip connection layer
    merge = Concatenate(axis=3, name=name + "_Concatenate")([conv2, conv3])

    # Final convolutions
    conv4 = Conv2D(filters_here, 3, **conv2d_kwargs, name=f"{name}_Conv2D_4")(merge)
    conv5 = Conv2D(filters_here, 3, **conv2d_kwargs, name=f"{name}_Conv2D_5")(conv4)

    if dropout > 0.0:
        conv5 = Dropout(dropout, name=f"{name}_Dropout_2")(conv5)

    return conv5


# %% Models
# Generic unet declaration:
def unet(
    input_size: tuple[int | None, int | None, int] = (None, None, 1),
    final_activation: str = "linear",
    output_classes: int = 1,
    dropout: float = 0,
    levels: int = 5,
    filters: list[int] | None = None,
) -> Model:
    """
    Create a U-Net.

    Parameters
    ----------
    input_size : tuple of 3 ints, optional
        Dimensions of the input tensor, excluding batch size.
        The default is `(None, None, 1)`, which means that any image size is
        accepted.
    final_activation : string or function, optional
        Activation function for the final 2D convolutional layer. see
        keras.activations
        The default is "linear" (no activation: outputs logits).
    output_classes : int, optional
        Number of output classes, ie dimensionality of the output space of the
        last 2D convolutional layer.
        The default is 1.
    dropout : float, optional
        Dropout layer rate in the contracting & expanding blocks. Valid range
        is [0,1). If 0, no dropout layer is added.
        The default is 0.
    levels : int, optional
        Number of levels of the U-Net, ie number of successive contraction then
        expansion blocks are combined together. Ignored if `filters` is specified.
        The default is 5.
    filters : [int], optional
        Number of convolutional kernels at each level.  The default is
        starting with 64 and multiplying by 2 at each level.

    Returns
    -------
    model : Model
        Defined U-Net model (not compiled yet).

    """
    if None in input_size:
        LOGGER.warning(
            "A neural network was created with arbitrary input size. "
            "This is an experimental feature. You will probably have "
            "to retrain the network to obtain correct results."
        )

    # Default conv2d parameters
    conv2d_kwargs = {
        "activation": "relu",
        "padding": "same",
        "kernel_initializer": "he_normal",
    }

    if filters is None:
        filters = [64 * 2**i for i in range(levels)]
    else:
        levels = len(filters)

    # Inputs layer
    true_input = Input(input_size, name="true_input")

    output = _unet(
        true_input,
        filters=filters,
        levels=levels,
        conv2d_kwargs=conv2d_kwargs,
        dropout=dropout,
    )

    # Final output layer
    true_output = Conv2D(
        output_classes, 1, activation=final_activation, name="true_output"
    )(output)

    model = Model(inputs=true_input, outputs=true_output)

    return model


# Use the following model for segmentation:
def unet_seg(
    pretrained_weights: str | None = None,
    input_size: tuple[int, int, int] = (256, 32, 1),
    levels: int = 5,
    filters: list[int] | None = None,
) -> Model:
    """
    Cell segmentation U-Net definition function.

    Parameters
    ----------
    pretrained_weights : model file, optional
        Model will load weights from file and start training.
        The default is None
    input_size : tuple of 3 ints, optional
        Dimensions of the input tensor, without batch size.
        The default is (256,32,1).
    levels : int, optional
        Number of levels of the U-Net, ie number of successive contraction then
        expansion blocks are combined together. Ignored if `filters` is specified.
        The default is 5.
    filters : [int], optional
        Number of convolutional kernels at each level.  The default is
        starting with 64 and multiplying by 2 at each level.

    Returns
    -------
    model : Model
        Segmentation U-Net (compiled).

    """
    model = unet(
        input_size=input_size,
        final_activation="linear",
        output_classes=1,
        levels=levels,
        filters=filters,
    )

    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss=pixelwise_weighted_binary_crossentropy_seg,
        metrics=[unstack_acc],
    )

    if pretrained_weights:
        model.load_weights(pretrained_weights)

    return model


# Use the following model for tracking and lineage reconstruction:
def unet_track(
    pretrained_weights: str | None = None,
    input_size: tuple[int, int, int] = (256, 32, 4),
    levels: int = 5,
    filters: list[int] | None = None,
) -> Model:
    """
    Tracking U-Net definition function.

    Parameters
    ----------
    pretrained_weights : model file, optional
        Model will load weights from file and start training.
        The default is None
    input_size : tuple of 3 ints, optional
        Dimensions of the input tensor, without batch size.
        The default is (256,32,4).
    levels : int, optional
        Number of levels of the U-Net, ie number of successive contraction then
        expansion blocks are combined together. Ignored if `filters` is specified.
        The default is 5.
    filters : [int], optional
        Number of convolutional kernels at each level.  The default is
        starting with 64 and multiplying by 2 at each level.

    Returns
    -------
    model : Model
        Tracking U-Net (compiled).

    """
    model = unet(
        input_size=input_size,
        final_activation="linear",
        output_classes=1,
        levels=levels,
        filters=filters,
    )

    model.compile(
        optimizer=Adam(learning_rate=1e-5),
        loss=pixelwise_weighted_binary_crossentropy_track,
        metrics=[unstack_acc],
    )

    if pretrained_weights:
        model.load_weights(pretrained_weights)

    return model


# Use the following model for segmentation:
def unet_rois(
    input_size: tuple[int, int, int] = (512, 512, 1),
    levels: int = 5,
    filters: list[int] | None = None,
) -> Model:
    """
    Segmentation U-Net for ROIs.

    Parameters
    ----------
    input_size : tuple of 3 ints, optional
        Dimensions of the input tensor, without batch size.
        The default is (512,512,1).
    levels : int, optional
        Number of levels of the U-Net, ie number of successive contraction then
        expansion blocks are combined together. Ignored if `filters` is specified.
        The default is 5.
    filters : [int], optional
        Number of convolutional kernels at each level.  The default is
        starting with 64 and multiplying by 2 at each level.

    Returns
    -------
    model : Model
        ROIs ID U-Net (compiled).

    """
    model = unet(
        input_size=input_size,
        final_activation="linear",
        output_classes=1,
        levels=levels,
        filters=filters,
    )

    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss=keras.losses.BinaryCrossentropy(from_logits=True),
    )

    return model
