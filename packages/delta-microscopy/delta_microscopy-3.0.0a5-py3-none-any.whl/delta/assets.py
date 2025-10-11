"""
Asset downloads (model files, training sets, and demonstration movies).

We provide our trained models, training sets, and evaluation movies in `this
google drive folder
<https://drive.google.com/drive/folders/1nTRVo0rPP9CR9F6WUunVXSXrLNMT_zCP?usp=sharing>`_.
We refer to these data files as "assets".

You can of course download them manually, but shouldn't have to, because DeLTA
knows where to find them and downloads them automatically when needed, with the
`pooch library <https://www.fatiando.org/pooch/latest/>`_, which makes everything
completely transparent.

Cache location
--------------

Upon downloading the assets, DeLTA caches them in the default OS cache location
(see `the pooch documentation
<https://www.fatiando.org/pooch/latest/api/generated/pooch.os_cache.html>`_ for
details).  If you want to download them to a different location, you can
specify this path in the ``DELTA_ASSETS_CACHE`` environment variable.

For example, to set this variable permanently within your conda environment,
you can run the following command in a terminal, inside your conda environment:

.. code:: none

    (delta_env)$ conda env config vars set DELTA_ASSETS_CACHE="D:/data/delta_cache"
"""

from pathlib import Path
from typing import Literal

import pooch

from delta._version import __version__

PRESETS = Literal["2D", "mothermachine"]

MODEL = Literal["rois", "seg", "track"]

BASE_URL = "https://drive.usercontent.google.com/download?confirm=t&id="

MODEL_REGISTRY = pooch.create(
    path=pooch.os_cache("delta") / "models",
    base_url="",
    version=__version__,
    version_dev="dev",
    registry={
        "moma_rois.keras": "sha256:a4585ee1a163c6a9aa83609d84246ca30c4b1f08c4656ab289476a120830e27e",
        "moma_seg.keras": "sha256:e2428e125b013691846278224a4f607a022af41302b6dbc6c780dd97d4aa5f5a",
        "moma_track.keras": "sha256:762f20bcfda307fbc30111b6f3f5bb67fcccc60d644dc305276fd48cbe45c35e",
        "2D_seg.keras": "sha256:97941f89ed37fdd937fde8c4fb797dfec7b8f2972cfec26527786e823dda40c0",
        "2D_track.keras": "sha256:e4ed540d9e126c7d3605cb38d00332d492c38676f146f75c6b139bb73c2f9fb6",
    },
    urls={
        "moma_rois.keras": BASE_URL + "1ZeBOFPG7xdY3R7AY_Ba7lOfPNxzGYfaO",
        "moma_seg.keras": BASE_URL + "1tJuRufC12MXvKDGBE90hi8yfWEUMkNMo",
        "moma_track.keras": BASE_URL + "1MsXiNeqxXDJMoBJu-5fAfXVtMGaFcXhv",
        "2D_seg.keras": BASE_URL + "190V0tgHk1HDhxGWQN2E4W5cozvN_5wvz",
        "2D_track.keras": BASE_URL + "1wH4G7b191I9xcIdVTCwGO_qzC7MhepPl",
    },
    env="DELTA_ASSETS_CACHE",
)

TRAININGSETS_REGISTRY = pooch.create(
    path=pooch.os_cache("delta") / "training_sets",
    base_url="",
    version=__version__,
    version_dev="dev",
    registry={
        "2D_training_segmentation.zip": "sha256:28d582ce7c3e99486e7323433fbec441e48b03f651b4c123dcc805bcf85a37c4",
        "2D_training_tracking.zip": "sha256:af24c80b6a161ba67cfc4ee43ab08dd4ad1078343f55bcda4163337a8cc1890c",
        "mothermachine_training_rois.zip": "sha256:51136a5e0278ed600fb01f208f452d6dfacf4dbf540af1c85ef1e125bc1567b9",
        "mothermachine_training_segmentation.zip": "sha256:b1ec15052293ff5b16c1b8332bac8f31596f7aaa028c3c720d350fd21e7a113f",
        "mothermachine_training_tracking.zip": "sha256:75c8b7c764a9463d4ab1dcb432b464c17456ccd0e8b76b120b8eecf73364414d",
    },
    urls={
        "2D_training_segmentation.zip": BASE_URL + "1eMYwEhImt9-v8q4XlFMOAJbF6UvTkmlQ",
        "2D_training_tracking.zip": BASE_URL + "1G4Hujltlr330rlPrFX31GR-BmnxnECLQ",
        "mothermachine_training_rois.zip": BASE_URL
        + "15rg5uVZIWVy6n-trQPMHK_zSQrlcLOvl",
        "mothermachine_training_segmentation.zip": BASE_URL
        + "1P3bnx0WaKf07kj7KPh1it0f_-1P8iQlf",
        "mothermachine_training_tracking.zip": BASE_URL
        + "1XphzQzNKB97-JKPJ1QtGTI4_Wb7eY-pd",
    },
    env="DELTA_ASSETS_CACHE",
)

DEMO_REGISTRY = pooch.create(
    path=pooch.os_cache("delta") / "demo_movies",
    base_url="",
    version=__version__,
    version_dev="dev",
    registry={
        "2D_demo.zip": "sha256:dbc294aaf67f1966dacf51fb61aa7623c1d8a477f9586e71e18b0a9a42f303dc",
        "mothermachine_demo.zip": "sha256:3ce91358ea9982b17b0d3693a544bf168d3ee6385018e2607401647e62de0b71",
    },
    urls={
        "2D_demo.zip": BASE_URL + "1qtlgQRVZ0bX5DPmr4knQBv7WoDFjQqxi",
        "mothermachine_demo.zip": BASE_URL + "1jG9aV_MfwWDDZk5JMUnWz5ERySvydmiD",
    },
    env="DELTA_ASSETS_CACHE",
)


def download_training_set(presets: PRESETS, model: MODEL) -> Path:
    """
    Return the path of the training set for the currently loaded configuration.

    Depending on the current value of presets ("2D" or "mothermachine") and
    of the value of the argument `model` ("rois", "seg" or "track"), this
    function returns the path of the corresponding training set.  If necessary,
    it downloads it first and caches it under a directory that can be specified
    by the environment variable `DELTA_ASSETS_CACHE`.

    Parameters
    ----------
    presets : PRESETS
        2D or mothermachine
    model : str
        Type of training set: `rois`, `seg` or `track`.

    Returns
    -------
    path : Path
        Path of the training set.

    """
    long_model = {"rois": "rois", "seg": "segmentation", "track": "tracking"}[model]
    TRAININGSETS_REGISTRY.fetch(
        f"{presets}_training_{long_model}.zip",
        processor=pooch.Unzip(extract_dir="unzipped"),
        progressbar=True,
    )
    path = Path(TRAININGSETS_REGISTRY.path) / "unzipped"
    if presets == "mothermachine" and model in {"seg", "track"}:
        return path / f"{presets}_training_{long_model}/train_multisets"
    return path / f"{presets}_training_{long_model}"


def download_demo_movie(presets: PRESETS) -> Path:
    """
    Return the path of the demo movie for the currently loaded configuration.

    If necessary, it downloads it first and caches it under a directory that
    can be specified by the environment variable `DELTA_ASSETS_CACHE`.

    Parameters
    ----------
    presets : PRESETS
        2D or mothermachine

    Returns
    -------
    path : Path
        Path of the demo movie.
    """
    DEMO_REGISTRY.fetch(
        f"{presets}_demo.zip",
        processor=pooch.Unzip(extract_dir="unzipped"),
        progressbar=True,
    )
    if presets == "mothermachine":
        prototype = "Pos{p}Chan{c}Frames{t}.png"
    else:
        prototype = "pos{p}cha{c}fra{t}.png"
    return Path(DEMO_REGISTRY.path) / f"unzipped/{presets}_demo/{prototype}"


def download_model(presets: PRESETS, model: MODEL) -> Path:
    """
    Return the path of the downloaded model, after downloading it if needed.

    Parameters
    ----------
    presets: PRESETS
        2D or mothermachine
    model: MODEL
        seg, track or rois

    Returns
    -------
    path: Path
        Path of the downloaded model.
    """
    filename = {
        ("2D", "seg"): "2D_seg.keras",
        ("2D", "track"): "2D_track.keras",
        ("mothermachine", "rois"): "moma_rois.keras",
        ("mothermachine", "seg"): "moma_seg.keras",
        ("mothermachine", "track"): "moma_track.keras",
    }[presets, model]
    return Path(MODEL_REGISTRY.fetch(filename, progressbar=True))
