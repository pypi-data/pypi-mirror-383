#!/usr/bin/env python
"""
Train the cell segmentation U-Net.

@author: jblugagne
"""

from pathlib import Path

# isort: off
from delta.assets import download_training_set
from delta.config import Config
from delta.data import load_training_dataset_seg
from delta.model import unet_seg
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
training_set = download_training_set("2D", "seg")
savefile = Path("new_segmentation_model.keras")

# Training parameters:
epochs = 600
steps_per_epoch = 300
patience = 50

# Data generator parameters:
data_gen_args = {
    "rotation": 2,
    "rotations_90d": False,
    "zoom": 0.15,
    "horizontal_flip": True,
    "vertical_flip": True,
    "illumination_voodoo": True,
    "gaussian_noise": 0.03,
    "gaussian_blur": 1,
}

# Crop windows for the 2D model, not for mothermachine
crop = "rois" not in config.models

ds_train, ds_val = load_training_dataset_seg(
    dataset_path=training_set,
    target_size=config.models["seg"].target_size,
    crop=crop,
    kw_data_aug=data_gen_args,
    validation_split=0.05,
    stack=True,
)

# Define model:
model = unet_seg(input_size=(*config.models["seg"].target_size, 1))
model.summary()

# Train:
history = model.fit(
    ds_train,
    validation_data=ds_val,
    steps_per_epoch=steps_per_epoch,
    epochs=epochs,
    callbacks=training_callbacks(savefile, verbose=2),
)
