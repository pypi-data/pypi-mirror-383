#!/usr/bin/env python
"""
Train the tracking U-Net.

@author: jblugagne
"""

from pathlib import Path

# isort: off
from delta.assets import download_training_set
from delta.config import Config
from delta.data import train_generator_track
from delta.model import unet_track
from delta.utils import training_callbacks

import keras
# isort: on

# Set tensorflow's random seed to make the training reproducible
# (only on CPU: not reproducible on GPU yet)
keras.utils.set_random_seed(1)

# Default config
config = Config.default("2D")
# Uncomment if you already have a config file
# config = Config.read("/path/to/your/config.toml")
config.apply_backend_config()
# Files:
training_set = download_training_set("2D", "track")
savefile = Path("new_tracking_model.keras")

# Training parameters:
batch_size = 2
epochs = 500
steps_per_epoch = 300
patience = 50

# Data generator parameters:
data_gen_args = {
    "rotation": 1,
    "zoom": 0.15,
    "horizontal_flip": True,
    "histogram_voodoo": True,
    "illumination_voodoo": True,
}

# Crop windows for the 2D model, not for mothermachine
crop = "rois" not in config.models

# Generator init:
my_gen = train_generator_track(
    batch_size,
    training_set / "img",
    training_set / "seg",
    training_set / "previmg",
    training_set / "segall",
    training_set / "mot_dau",
    training_set / "wei",
    augment_params=data_gen_args,
    target_size=config.models["track"].target_size,
    crop_windows=crop,
    shift=5,
)


# Define model:
model = unet_track(input_size=(*config.models["track"].target_size, 4))
model.summary()

# Train:
history = model.fit(
    my_gen,
    steps_per_epoch=steps_per_epoch,
    epochs=epochs,
    callbacks=training_callbacks(savefile, verbose=1),
)
