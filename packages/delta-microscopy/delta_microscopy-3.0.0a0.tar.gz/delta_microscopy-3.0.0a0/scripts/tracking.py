#!/usr/bin/env python
"""
Run the tracking U-Net on data out of the segmentation U-Net.

Please make sure you have run the segmentation script first.

Images are processed in batches of 512, although the number of actual samples
run through the tracking U-Net will depend on the number of cells in each
image.

Format of images needs to be Position-Number-Chamber-Number-Frame-Number.fext
or Position-Number-Frame-Number.fext

If there are chambers, then it is assumed to be run in the mothermachine.
If there are no chambers, then images will be cropped as done for DeLTA 2D
@author: jblugagne
"""

from pathlib import Path

import numpy as np

from delta.config import Config
from delta.data import predict_compile_from_seg_track, save_result_track
from delta.imgops import read_image
from delta.utils import list_files

# Parameters:

# Default config ("2D" or "mothermachine")
config = Config.default("2D")
# Uncomment if you already have a config file
# config = Config.read("/path/to/your/config.toml")

# Image sequence to segment: (replace with your own)
inputs_folder = Path(__file__).parents[1] / "tests/data/movie_2D_tif"
segmentation_folder = inputs_folder / "segmentation"

# /Parameters

# Output folder:
outputs_folder = inputs_folder / "tracking"
outputs_folder.mkdir(exist_ok=True)

# List files to read
unprocessed = list_files(inputs_folder, {".png", ".tif"})

# Get original image size:
imsize = read_image(unprocessed[0]).shape

# Load up model:
model = config.models["track"].model()

# Crop windows if 2D, not if mothermachine
crop = "rois" not in config.models

# Process
while unprocessed:
    # Pop out filenames
    ps = min(5, len(unprocessed))
    to_process = unprocessed[0:ps]
    del unprocessed[0:ps]

    print("\n###### Now processing: ")
    for file in to_process:
        print(file)

    # Get data:
    inputs, seg_filenames, boxes = predict_compile_from_seg_track(
        inputs_folder,
        segmentation_folder,
        files_list=to_process,
        target_size=config.models["track"].target_size,
        crop_windows=crop,
    )

    print(f"Cells to track: {len(inputs)}")

    # Predict (have to do it in batches otherwise run into memory issues):
    results = np.empty(shape=(*inputs.shape[:3], 1), dtype=np.float32)
    for i in range(0, len(inputs), 32):
        j = min((len(inputs), i + 32))
        results[i:j] = model.predict(inputs[i:j], verbose=1, batch_size=1)

    # Paste results into masks of original imsize:
    if crop:
        _results = np.zeros(shape=(len(results), *imsize, 1), dtype=np.float32)
        for r, mask in enumerate(results):
            cb = boxes[r]
            cb.patch(_results[r, :, :, 0], mask[:, :, 0])
        results = _results

    # Save (use the filenames list from the data compiler)
    save_result_track(outputs_folder, results, files_list=seg_filenames)
