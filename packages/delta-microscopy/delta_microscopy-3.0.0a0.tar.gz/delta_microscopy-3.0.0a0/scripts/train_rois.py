#!/usr/bin/env python
"""
Train the chambers segmentation U-Net.

@author: jblugagne
"""

from pathlib import Path

import keras

from delta.assets import download_training_set
from delta.config import Config
from delta.data import load_training_dataset_seg
from delta.model import unet_rois
from delta.utils import training_callbacks

# Set tensorflow's random seed to make the training reproducible
# (only on CPU: not reproducible on GPU yet)
keras.utils.set_random_seed(1)

# Default config
config = Config.default("mothermachine")
# Uncomment if you already have a config file
# config = Config.read("/path/to/your/config.toml")

# Files:
training_set = download_training_set("mothermachine", "rois")
savefile = Path("new_rois_model.keras")

# Parameters:
epochs = 600
steps_per_epoch = 250
patience = 50

# Data generator parameters:
data_gen_args = {
    "rotation": 3,
    "shiftX": 0.1,
    "shiftY": 0.1,
    "zoom": 0.25,
    "horizontal_flip": True,
    "vertical_flip": True,
    "rotations_90d": True,
    "histogram_voodoo": True,
    "illumination_voodoo": True,
    "gaussian_noise": 0.03,
}

ds_train, ds_val = load_training_dataset_seg(
    dataset_path=training_set,
    target_size=config.models["rois"].target_size,
    crop=False,
    kw_data_aug=data_gen_args,
    validation_split=0.05,
)

# Define model:
model = unet_rois(input_size=(*config.models["rois"].target_size, 1))
model.summary()

# Train:
history = model.fit(
    ds_train,
    steps_per_epoch=steps_per_epoch,
    validation_data=ds_val,
    epochs=epochs,
    callbacks=training_callbacks(savefile),
)
