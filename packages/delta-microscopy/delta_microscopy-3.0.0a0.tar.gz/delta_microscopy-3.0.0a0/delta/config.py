"""Define, read and write DeLTA's configuration."""

import dataclasses
import json
import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import keras
import tomli_w

from delta import assets

LOGGER = logging.getLogger(__name__)

MODEL = Literal["rois", "seg", "track"]

PRESETS = Literal["2D", "mothermachine"]


@dataclass
class ModelConfig:
    """Configuration class containing Model parameters."""

    model_path: Path
    """Path to the model file."""
    target_size: tuple[int, int]
    """Input size of the images for this model."""
    min_area: float
    """Minimal size of objects detected by this model, smaller objects will be
    removed (ROI and segmentation models only)."""
    tolerable_resizing_factor: float
    """Maximum tolerable resizing factor of the input image to scale it to
    ``target_size``. On either axes (x and y), resizing only happens if ``ref
    < target * (tolerable_resizing_rois + 1)`` where ``ref`` is the size of the
    reference image on one axis, and ``target`` is the input size of the neural
    network defined in the config as ``target_size_rois`` on the same axis.  If
    the reference image is larger than that, it is cropped."""
    batch_size: int
    """Number of images processed at the same time by the model. If running
    into OOM issues with the pipeline, try lowering this value.  You can also
    increase it to improve speed."""
    chunk_size: int
    """Number of images processed at the same time by the model. If running
    into OOM issues with the pipeline, try lowering this value.  You can also
    increase it to improve speed."""

    @classmethod
    def _default_without_model(cls, model: MODEL, presets: PRESETS) -> "ModelConfig":
        target_size = {
            "rois": {"mothermachine": (512, 512)},
            "seg": {"2D": (512, 512), "mothermachine": (256, 32)},
            "track": {"2D": (256, 256), "mothermachine": (256, 32)},
        }
        min_area = {"rois": 500, "seg": 20, "track": 0}
        tolerable_resizing_factor = {"rois": 4, "seg": 1, "track": 1}
        batch_size = {
            "rois": {"mothermachine": 1},
            "seg": {"mothermachine": 1, "2D": 1},
            "track": {"mothermachine": 64, "2D": 1},
        }
        chunk_size = {"rois": 1, "seg": 64, "track": 64}
        config = cls(
            model_path=Path(),
            target_size=target_size[model][presets],
            min_area=min_area[model],
            tolerable_resizing_factor=tolerable_resizing_factor[model],
            batch_size=batch_size[model][presets],
            chunk_size=chunk_size[model],
        )
        return config

    @classmethod
    def default(cls, model: MODEL, presets: PRESETS) -> "ModelConfig":
        """
        Return the default config for this model and preset.

        Parameters
        ----------
        model : MODEL
            Can be "rois", "seg" or "track".
        presets : PRESETS
            Can be "2D" or "mothermachine".

        Returns
        -------
        config : ModelConfig
            Config object.
        """
        config = cls._default_without_model(model, presets)
        config.model_path = assets.download_model(presets, model)
        return config

    def model(self) -> keras.Model:
        """
        Return the keras model for the specified preset and model type.

        If the variable "model_file_(rois|seg|track)" is non-empty in the
        configuration, it is assumed to be the filename of the model.  If this
        variable is empty, we download the default model of DeLTA and cache it
        under a directory that can be optionally specified with the environment
        variable `DELTA_ASSETS_CACHE`.

        Parameters
        ----------
        model : str
            Model type ("rois", "segmentation", or "tracking").

        Returns
        -------
        model : keras.Model
            The required model.
        """
        keras_model = keras.models.load_model(self.model_path, compile=False)

        # In order to be able to use the old models that had a sigmoid as a final activation
        keras_model.layers[-1].activation = keras.activations.linear

        return keras_model

    def resizing_tolerable(self, shape: tuple[int, int]) -> bool:
        """
        Determine if resizing is tolerable for an image of this size.

        Parameters
        ----------
        shape : tuple[int, int]
            Shape of the image.
        """
        y, x = shape
        yt, xt = self.target_size
        y_ok = y / yt < self.tolerable_resizing_factor
        x_ok = x / xt < self.tolerable_resizing_factor
        return y_ok and x_ok

    def update(self, key: str, value) -> None:  # noqa: ANN001
        """
        Update in place the configuration with the given key and value.

        Parameters
        ----------
        key : str
            Config key to update.
        value : Any
            Value for the given key.
        """
        if key not in self.__dataclass_fields__:
            msg = f"{key} is not a field of ModelConfig"
            raise ValueError(msg)
        setattr(self, key, value)


@dataclass
class BackendConfig:
    """Configuration class containing Backend parameters."""

    number_of_cores: int | None
    """This will limit the number of cores the backend can use. Default value
    of this will have the backend determine the number of cores."""
    memory_growth_limit: int | None
    """If running into OOM issues or having trouble with CuDNN loading, try
    setting this to a value in MB: 1024, 2048, etc."""

    def update(self, key: str, value: int) -> None:
        """
        Update in place the configuration with the given key and value.

        Parameters
        ----------
        key : str
            Config key to update.
        value : Any
            Value for the given key.
        """
        if key not in self.__dataclass_fields__:
            msg = f"{key} is not a field of BackendConfig"
            raise ValueError(msg)
        setattr(self, key, value)

    def apply_config(self) -> None:
        """Apply this configuration to the keras backend."""
        keras_backend = keras.src.backend.config.backend()
        if keras_backend == "tensorflow":
            self._apply_tensorflow()

    def _apply_tensorflow(self) -> None:
        import tensorflow as tf  # noqa: PLC0415

        # If running into OOM issues or having trouble with cuDNN loading, try setting
        # memory_growth_limit to a value in MB: (eg 1024, 2048...)
        gpus = tf.config.experimental.list_physical_devices("GPU")
        if self.memory_growth_limit is not None and gpus:
            # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
            try:
                vdconf = tf.config.experimental.VirtualDeviceConfiguration(
                    memory_limit=self.memory_growth_limit
                )
                tf.config.experimental.set_virtual_device_configuration(
                    gpus[0], [vdconf]
                )
                logical_gpus = tf.config.experimental.list_logical_devices("GPU")
                LOGGER.info(
                    "%d physical GPUs, %d logical GPUs",
                    len(gpus),
                    len(logical_gpus),
                )
            except RuntimeError:
                error_msg = "Virtual devices must be set before GPUs are initialized"
                LOGGER.exception(error_msg)

        # TensorFlow will determine the max number of cores if not set in the config
        tf.config.threading.set_inter_op_parallelism_threads(self.number_of_cores)
        tf.config.threading.set_intra_op_parallelism_threads(self.number_of_cores)


@dataclass
class Config:
    """Configuration class containing DeLTA parameters."""

    models: dict[str, ModelConfig]
    """Sub-configs for the deep learning models."""
    backends: dict[str, BackendConfig]
    """Sub-configs for the deep learning backends."""
    correct_rotation: bool
    """Whether or not to correct for image rotation (mothermachine only)."""
    correct_drift: bool
    """Whether or not to correct for drift over time (mothermachine only)."""
    whole_frame_drift: bool = False
    """If correcting for drift, use the entire frame instead of the region
    above the chambers (mothermachine only)."""

    @classmethod
    def default(cls, presets: PRESETS) -> "Config":
        """
        Return the default config for this preset.

        Parameters
        ----------
        presets : PRESETS
            Can be "2D" or "mothermachine".

        Returns
        -------
        config : Config
            Config object.
        """
        models: dict[PRESETS, tuple[MODEL, ...]] = {
            "2D": ("seg", "track"),
            "mothermachine": ("rois", "seg", "track"),
        }
        config = cls(
            models={
                model: ModelConfig.default(model, presets) for model in models[presets]
            },
            backends={},
            correct_rotation=presets == "mothermachine",
            correct_drift=presets == "mothermachine",
        )
        return config

    @staticmethod
    def read(path: str | Path) -> "Config":
        """
        Read a configuration file.

        Parameters
        ----------
        path : str | Path
            Path to specific configuration file.

        Returns
        -------
        config : Config
            Loaded config object.

        """
        return read_toml(Path(path))

    def update(self, key: str, value) -> None:  # noqa: ANN001
        """
        Update in place the configuration with the given key and value.

        Parameters
        ----------
        key : str
            Config key to update.
        value : Any
            Value for the given key.
        """
        if key.startswith("models."):
            _, model, subkey = key.split(".", maxsplit=2)
            self.models[model].update(subkey, value)
        elif key.startswith("backends."):
            _, backend, subkey = key.split(".", maxsplit=2)
            self.backends[backend].update(subkey, value)
        else:
            if key not in self.__dataclass_fields__:
                msg = f"{key} is not a field of Config"
                raise ValueError(msg)
            setattr(self, key, value)

    def write(self, path: str | Path) -> None:
        """
        Write a configuration file.

        Parameters
        ----------
        path : str | Path
            Path to configuration file to write.
        """
        return write_toml(self, Path(path))

    def _as_dict(self) -> dict[str, dict[str, str | tuple[int, int] | int] | bool]:
        dict_config = dataclasses.asdict(self)
        for name in self.models:
            dict_config["models"][name]["model_path"] = str(
                self.models[name].model_path
            )

        return dict_config

    def serialize(self) -> str:
        """Return a JSON string describing the configuration."""
        return json.dumps(self._as_dict())

    @classmethod
    def deserialize(cls, json_str: str) -> "Config":
        """
        Build a configuration from a JSON string.

        Parameters
        ----------
        json_str : str
            JSON string containing a serialized configuration.
        """
        c = json.loads(json_str)
        c["models"] = {
            name: ModelConfig(**model_config)
            for name, model_config in c["models"].items()
        }
        for model_config in c["models"].values():
            model_config.model_path = Path(model_config.model_path)
            model_config.target_size = tuple(model_config.target_size)
        c["backends"] = {
            name: BackendConfig(**backend_config)
            for name, backend_config in c["backends"].items()
        }
        return cls(**c)

    def apply_backend_config(self) -> None:
        """Apply the relevant config settings to the keras backend."""
        keras_backend = keras.src.backend.config.backend()
        if keras_backend in self.backends:
            self.backends[keras_backend].apply_config()


@dataclass
class OldConfig:
    """Deprecated configuration class kept for retro-compatibility."""

    presets: PRESETS
    """Type of analysis: can be '2D' or 'mothermachine'."""
    models: tuple[MODEL, ...]
    """Which models need to be loaded ('rois', 'seg' or 'track')."""
    model_file_rois: Path | None
    """Path to the model file for ROI segmentation."""
    model_file_seg: Path | None
    """Path to the model file for cell segmentation."""
    model_file_track: Path | None
    """Path to the model file for cell tracking."""
    target_size_rois: tuple[int, int]
    """Input size of the ROI segmentation model."""
    target_size_seg: tuple[int, int]
    """Input size of the cell segmentation model."""
    target_size_track: tuple[int, int]
    """Input size of the cell tracking model."""
    training_set_rois: Path | None
    """Path to the ROI segmentation training set."""
    training_set_seg: Path | None
    """Path to the cell segmentation training set."""
    training_set_track: Path | None
    """Path to the cell tracking training set."""
    eval_movie: Path | None
    """Path to the evaluation movie."""
    rotation_correction: bool
    """Whether or not to correct for image rotation (mothermachine only)."""
    drift_correction: bool
    """Whether or not to correct for drift over time (mothermachine only)."""
    whole_frame_drift: bool
    """If correcting for drift, use the entire frame instead of the region
    above the chambers."""
    crop_windows: bool
    """If True, crop input images into windows of size target_size_seg for
    segmentation, otherwise resize them."""
    min_roi_area: int
    """Minimum area of detected ROIs in pixels (mothermachine only)."""
    min_cell_area: int
    """Minimum area of detected cells in pixels."""
    memory_growth_limit: int | None
    """If running into OOM issues or having troupble with CuDNN loading, try
    setting this to a value in MB: 1024, 2048, etc."""
    pipeline_seg_batch: int
    """If running into OOM issues during segmentation with the pipeline, try
    lowering this value.  You can also increase it to improve speed."""
    pipeline_track_batch: int
    """If running into OOM issues during segmentation with the pipeline, try
    lowering this value.  You can also increase it to improve speed."""
    pipeline_chunk_size: int
    """If running into OOM issues during segmentation with the pipeline, try
    lowering this value.  You can also increase it to improve speed."""
    number_of_cores: int | None
    """This will limit the number of cores TensorFlow can use. Default value
    of this will have TensorFlow determine the number of cores."""
    tolerable_resizing_rois: float
    """Maximum tolerable resizing factor of the template for ROI
    identification.  On either axes (x and y), resizing only happens if
    ``ref < target * (tolerable_resizing_rois + 1)`` where ``ref`` is the size
    of the reference image on one axis, and ``target`` is the input size of the
    neural network defined in the config as ``target_size_rois`` on the same
    axis.  If the reference image is larger than that, it is cropped."""

    @classmethod
    def read(cls, path: str | Path) -> "OldConfig":
        """
        Read a configuration file.

        Parameters
        ----------
        path : str | Path
            Path to specific configuration file.

        Returns
        -------
        config : Config
            Loaded config object.

        """
        try:
            return cls(**read_json(Path(path)))
        except TypeError as err:
            error_msg = (
                "The config file has too many or is missing some parameters. "
                "This is most likely because the config file was generated for "
                "an earlier version of DeLTA. Please update your config based "
                "on the current one, detailed in `delta.config.Config`."
            )
            raise ValueError(error_msg) from err

    def to_tomlconfig(self) -> Config:
        """Convert this config object into a newer modular config."""
        models = {}
        if "rois" in self.models:
            models["rois"] = ModelConfig(
                model_path=Path(self.model_file_rois or ""),
                target_size=self.target_size_rois,
                min_area=self.min_roi_area,
                tolerable_resizing_factor=self.tolerable_resizing_rois,
                batch_size=self.pipeline_seg_batch,
                chunk_size=self.pipeline_chunk_size,
            )
        models["seg"] = ModelConfig(
            model_path=Path(self.model_file_seg or ""),
            target_size=self.target_size_seg,
            min_area=self.min_cell_area,
            tolerable_resizing_factor=self.tolerable_resizing_rois,
            batch_size=self.pipeline_seg_batch,
            chunk_size=self.pipeline_chunk_size,
        )
        models["track"] = ModelConfig(
            model_path=Path(self.model_file_track or ""),
            target_size=self.target_size_track,
            min_area=self.min_cell_area,
            tolerable_resizing_factor=self.tolerable_resizing_rois,
            batch_size=self.pipeline_track_batch,
            chunk_size=self.pipeline_chunk_size,
        )

        config = Config(
            models=models,
            backends={},
            correct_rotation=self.rotation_correction,
            correct_drift=self.drift_correction,
            whole_frame_drift=self.whole_frame_drift,
        )

        return config


def read_toml(path: Path) -> Config:
    """
    Read a toml file containing a configuration.

    This function converts the lists to tuples and the paths to ``Path``s.

    Parameters
    ----------
    path : Path
        Path of the file to read.

    Returns
    -------
    config : Config
        Configuration.
    """
    LOGGER.info("Loading configuration from: %s", path)

    with path.open("rb") as file:
        variables: dict[str, Any] = tomllib.load(file)

    models = {}
    for name, params in variables["models"].items():
        # It does not matter if we choose 2D or mothermachine here
        # because the specific fields will be erased later
        model = ModelConfig._default_without_model(model=name, presets="mothermachine")
        model = dataclasses.replace(model, **params)
        model.model_path = Path(params["model_path"])
        model.target_size = tuple(params["target_size"])

        models[name] = model

    backends = {}
    for name, params in variables["backends"].items():
        backend = BackendConfig(
            number_of_cores=params.get("number_of_cores", 0),
            memory_growth_limit=params.get("memory_growth_limit", 0),
        )
        backends[name] = backend

    config = Config(
        models=models,
        backends=backends,
        correct_rotation=variables.get("correct_rotation", False),
        correct_drift=variables.get("correct_drift", False),
        whole_frame_drift=variables.get("whole_frame_drift", False),
    )
    return config


def write_toml(config: Config, path: Path) -> None:
    """
    Write a configuration to a toml file.

    This function transforms the ``Path``s to ``str``.

    Parameters
    ----------
    config : Config
        Configuration file to write.
    path : Path
        Path of the file to write.
    """
    LOGGER.info("Writing configuration to: %s", path)

    with path.open(mode="wb") as file:
        tomli_w.dump(config._as_dict(), file)


def read_json(path: Path) -> dict[str, Any]:
    """
    Read a JSON file containing a configuration.

    This function converts the lists to tuples and the paths to ``Path``s.

    Parameters
    ----------
    path : Path
        Path of the file to read.

    Returns
    -------
    variables : dict[str, Any]
        Dictionary representing the JSON.
    """
    LOGGER.info("Loading configuration from: %s", path)
    # Load file:
    with path.open(mode="r", encoding="utf8") as file:
        variables: dict[str, Any] = json.load(file)

    # Type cast:
    for key, value in variables.items():
        if isinstance(value, list):
            # Always use tuples, not lists in config
            variables[key] = tuple(value)
        elif key.startswith(("model_file", "training_set", "eval_movie")) and value:
            variables[key] = Path(value)
    return variables
