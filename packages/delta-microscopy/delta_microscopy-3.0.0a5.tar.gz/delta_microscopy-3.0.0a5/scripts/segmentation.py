#!/usr/bin/env python
"""
Run the segmentation U-Net.

For mother machine data, it runs on images of cropped out and resized single
chambers as fed to it in Pipeline processing.

The images are processed by batches of 4096 to prevent memory issues.

@author: jblugagne
"""

from pathlib import Path

import numpy as np

from delta import imgops
from delta.config import Config
from delta.data import predict_generator_seg, save_result_seg
from delta.utils import list_files

# Parameters:

# Default config ("2D" or "mothermachine")
config = Config.default("2D")
# Uncomment if you already have a config file
# config = Config.read("/path/to/your/config.toml")

# Image sequence to segment: (replace with your own)
inputs_folder = Path(__file__).parents[1] / "tests/data/movie_2D_tif"

# /Parameters


# Outputs folder:
outputs_folder = inputs_folder / "segmentation"
outputs_folder.mkdir(exist_ok=True)

# List files in inputs folder:
unprocessed = list_files(inputs_folder, {".tif", ".png"})

# Load up model:
model = config.models["seg"].model()

# Crop windows if 2D, not if mothermachine
crop = "rois" not in config.models

# Process
while unprocessed:
    # Pop out filenames
    ps = min(4096, len(unprocessed))  # 4096 at a time
    to_process = unprocessed[0:ps]
    del unprocessed[0:ps]

    # Input data generator:
    pred_gen = predict_generator_seg(
        inputs_folder,
        files_list=to_process,
        target_size=config.models["seg"].target_size,
        crop_windows=crop,
    )

    # mother machine: Don't crop images into windows
    if not crop:
        # Predictions:
        results = model.predict(pred_gen, steps=len(to_process), verbose=1)[:, :, :, 0]

    # 2D: Cut into overlapping windows
    else:
        img = imgops.read_reshape(
            inputs_folder / to_process[0],
            target_size=config.models["seg"].target_size,
            method="pad",
        )
        # Create array to store predictions
        results = np.zeros((len(to_process), img.shape[0], img.shape[1], 1))
        # Crop, segment, stitch and store predictions in results
        for i in range(len(to_process)):
            (image,) = next(pred_gen)
            # Crop each frame into overlapping windows:
            windows, loc_y, loc_x = imgops.create_windows(
                image[0, :, :], target_size=config.models["seg"].target_size
            )
            # We have to play around with tensor dimensions to conform to
            # tensorflow's functions:
            windows = windows[:, :, :, np.newaxis]
            # Predictions:
            pred = model.predict(windows, verbose=1, steps=windows.shape[0])
            # Stitch prediction frames back together:
            pred = imgops.stitch_pic(pred[:, :, :, 0], loc_y, loc_x)
            pred = pred[np.newaxis, :, :, np.newaxis]  # Mess around with dims

            results[i] = pred

    # Post process results (binarize + light morphology-based cleaning):
    results = imgops.postprocess(results, crop=crop)

    # Save to disk:
    save_result_seg(outputs_folder, results, files_list=to_process)
