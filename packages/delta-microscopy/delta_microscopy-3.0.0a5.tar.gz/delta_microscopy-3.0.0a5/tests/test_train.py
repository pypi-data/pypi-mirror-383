"""
Created on Tue Nov  9 16:40:02 2021.

@author: jeanbaptiste
"""

import tempfile
from pathlib import Path

import pytest

import delta
from delta.config import Config


def test_train_moma_rois():
    # Load config
    config = Config.default("mothermachine")
    # Files
    training_set = delta.assets.download_training_set("mothermachine", "rois")
    savefile = Path(tempfile.gettempdir()) / "test_mothermachine_rois.keras"

    delta.cli._train_rois(config, training_set, savefile, steps_per_epoch=10, epochs=3)


@pytest.mark.parametrize("presets", ["2D", "mothermachine"])
def test_train_seg(presets):
    # Load config
    config = Config.default(presets)
    # Files
    training_set = delta.assets.download_training_set("mothermachine", "seg")
    savefile = Path(tempfile.gettempdir()) / f"test_{presets}_seg.keras"

    delta.cli._train_seg(config, training_set, savefile, steps_per_epoch=10, epochs=3)


@pytest.mark.parametrize("presets", ["2D", "mothermachine"])
def test_train_track(presets):
    # Load config
    config = Config.default(presets)
    # Files
    training_set = delta.assets.download_training_set("mothermachine", "track")
    savefile = Path(tempfile.gettempdir()) / f"test_{presets}_track.keras"

    delta.cli._train_track(config, training_set, savefile, steps_per_epoch=10, epochs=3)
