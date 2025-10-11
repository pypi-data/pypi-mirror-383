#!/usr/bin/env python
"""
Run the DeLTA pipeline on a demo movie.

@author: jeanbaptiste
"""

from delta.assets import download_demo_movie
from delta.config import Config
from delta.pipeline import Pipeline
from delta.utils import XPReader

# Load config ('2D' or 'mothermachine'):
config = Config.default("2D")

# Apply the config options to the deep learning backend
config.apply_backend_config()

# Use demo movie as example (or replace by a path to your own movie):
file_path = download_demo_movie("2D")

# Init reader:
xpreader = XPReader(file_path)

# Init pipeline:
xp = Pipeline(xpreader, config=config)

# Run it (you can specify which positions, which frames to run etc):
xp.process()
