"""DeLTA."""

import importlib.util
import logging
import os
import sys

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

LOGGER = logging.getLogger(__name__)

if "TF_CPP_MIN_LOG_LEVEL" not in os.environ:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

if "KERAS_BACKEND" not in os.environ:
    for backend in ("torch", "tensorflow", "jax"):  # Order of preference
        if importlib.util.find_spec(backend) is not None:
            os.environ["KERAS_BACKEND"] = backend
            break
    else:
        LOGGER.critical(
            "No deep learning backend has been found. At least one library "
            "among torch, tensorflow or jax should be installed. "
            "You can then select the library by passing its name to "
            "the KERAS_BACKEND environment variable."
        )
        sys.exit(1)

# isort: off

from delta import assets, config
from delta import cli, data, imgops, lineage, model, pipeline, utils
from delta._version import __version__

# isort: on

__all__ = (
    "__version__",
    "assets",
    "cli",
    "config",
    "data",
    "lineage",
    "model",
    "pipeline",
    "utils",
)
