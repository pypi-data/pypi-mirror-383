#!/usr/bin/env python
"""
Run the rois identification/segmentation U-Net.

To see how to extract roi images with this segmentation mask, see the
preprocessing section of pipeline.py and getROIBoxes() in utils.py

@author: jblugagne
"""

from pathlib import Path

from delta.config import Config
from delta.data import predict_generator_seg, save_result_seg
from delta.imgops import postprocess
from delta.utils import list_files

# Parameters:

# Default config
config = Config.default("mothermachine")
# Uncomment if you already have a config file
# config = Config.read("/path/to/your/config.toml")

# Image sequence to segment: (replace with your own)
inputs_folder = Path(__file__).parents[1] / "tests/data/movie_mothermachine_tif"

# /Parameters


# Output folder:
outputs_folder = inputs_folder / "roi_masks"
outputs_folder.mkdir(exist_ok=True)

# List files in inputs folder:
input_files = list_files(inputs_folder, {".tif", ".png"})

# Load up model:
model = config.models["rois"].model()

# Inputs data generator:
pred_gen = predict_generator_seg(
    inputs_folder, files_list=input_files, target_size=config.models["rois"].target_size
)

# Predictions:
results = model.predict(pred_gen, steps=len(input_files), verbose=1)

# Post process results:
results[:, :, :, 0] = postprocess(results[:, :, :, 0])

# Save to disk:
save_result_seg(outputs_folder, results, files_list=input_files)
