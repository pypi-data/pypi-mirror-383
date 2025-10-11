"""
Created on Wed Apr  6 09:47:07 2022.

@author: ooconnor
"""

from pathlib import Path

import pytest

from delta.config import Config

test_folder = Path(__file__).parent


def test_rois_script():
    script = test_folder.parent / "scripts/segmentation_rois.py"

    inputs_folder = test_folder / "data/movie_mothermachine_tif"
    parameters = {
        "config": Config.default("mothermachine"),
        "inputs_folder": inputs_folder,
    }
    _run_script(script, parameters=parameters)


@pytest.mark.parametrize(
    "presets,inputs_folder",
    [
        ("2D", test_folder / "data/movie_2D_tif"),
        (
            "mothermachine",
            test_folder / "data/movie_mothermachine_tif/cropped_rois",
        ),
    ],
)
def test_segmentation_script(presets, inputs_folder):
    config = Config.default(presets)
    parameters = {"config": config, "inputs_folder": inputs_folder}
    _run_script(test_folder.parent / "scripts/segmentation.py", parameters=parameters)


@pytest.mark.parametrize(
    "presets,inputs_folder",
    [
        ("2D", test_folder / "data/movie_2D_tif"),
        (
            "mothermachine",
            test_folder / "data/movie_mothermachine_tif/cropped_rois",
        ),
    ],
)
def test_tracking_script(presets, inputs_folder):
    config = Config.default(presets)
    parameters = {"config": config, "inputs_folder": inputs_folder}

    # Adding segmentation folder to the parameters dict based on inputs folder:
    parameters["segmentation_folder"] = parameters["inputs_folder"] / "segmentation"

    _run_script(test_folder.parent / "scripts/tracking.py", parameters=parameters)


def _run_script(scriptfile, parameters):
    """Read script & strip parameters code, set parameters, execute script."""
    # Read script, and remove parameters block:
    with Path(scriptfile).open(encoding="utf-8") as reader:
        script = _strip_parameters(reader)

    # set parameters:
    locals().update(parameters)

    # Run script:
    exec(script, globals(), locals())  # noqa: S102


def _strip_parameters(reader):
    """Remove the Parameters /Parameters block from the script."""
    parameters = None
    code = ""
    for line in reader:
        if line.rstrip() == "# Parameters:":
            parameters = True
        elif line.rstrip() == "# /Parameters":
            parameters = False

        if parameters is None or not parameters:
            code += line

    if parameters is None:
        error_msg = 'The "# Parameters:" block was not opened in the script'
        raise RuntimeError(error_msg)

    if parameters is True:
        error_msg = 'The parameters block was not closed with "# /Parameters"'
        raise RuntimeError(error_msg)

    return code
