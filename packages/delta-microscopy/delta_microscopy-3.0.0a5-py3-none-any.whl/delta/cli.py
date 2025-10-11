"""Command-line interface of DeLTA."""

import argparse
import logging
from pathlib import Path
from typing import cast, get_args

import keras

import delta
from delta.config import MODEL, PRESETS, Config

LOGGER = logging.getLogger(__name__)


def to_int_list(list_spec: str) -> list[int]:
    """
    Convert a list string specification ("0-2,4,7-10") to a list of integers.

    Parameters
    ----------
    list_spec : str
        List string specification.

    Returns
    -------
    int_list : list[int]
        List of integers.
    """
    int_list = []
    for group in list_spec.split(","):
        if "-" not in group:
            int_list.append(int(group))
        else:
            start, end = (int(x) for x in group.split("-"))
            int_list += list(range(start, end + 1))
    return int_list


def to_interval(interval_spec: str) -> slice:
    """
    Convert an interval string specification ("35-150") to a slice.

    Parameters
    ----------
    interval_spec: str
        Interval string specification.

    Returns
    -------
    interval : slice
        Interval.
    """
    if "-" not in interval_spec:
        only_value = int(interval_spec)
        return slice(only_value, only_value + 1)
    start, end = interval_spec.split("-")
    if not start:
        return slice(int(end) + 1)
    if not end:
        return slice(int(start), None)
    return slice(int(start), int(end) + 1)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """
    Parse a list of arguments, typically given on the commandline.

    Parameters
    ----------
    args : list[str] | None
        List of command-line arguments.

    Returns
    -------
    namespace : argparse.Namespace
        Parsed and typed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="delta",
        description="Deep Learning for Time-Lapse Analysis",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Action to perform")
    # Run
    run = subparsers.add_parser("run", help="Segment and track an experiment")
    run.add_argument(
        "-c",
        "--config",
        help="Configuration file.  Can be either `2D`, `mothermachine`, "
        "or a path to a previously saved custom config file.",
        required=True,
    )
    run.add_argument(
        "-i",
        "--input",
        help="Input file or directory. Can include `{p}`, `{c}` and `{t}` as "
        "placeholders for the position, channel, and frame number.  "
        "Example for micromanager: "
        "`/path/to/folder/Pos{p}/img_channel{c}_position{p}_time{t}_z000.tif`",
        required=True,
    )
    run.add_argument(
        "-o",
        "--output",
        help="Output directory (by default `delta_results` inside the input directory)",
    )
    run.add_argument(
        "-C",
        action="append",
        metavar="KEY=VALUE",
        help="Configuration option added on the fly for this run, for example `min_cell_area=40`.",
    )
    run.add_argument(
        "--positions",
        type=to_int_list,
        help="Positions to process, ex.: 0-2,4,7-10 (default: all)",
    )
    run.add_argument(
        "--frames",
        type=to_interval,
        help="Range of frames to process, ex.: -150 (up to frame 150), "
        "15- (from frame 15), 15-30 (frames 15 to 30), 40 (just frame 40) (default: all)",
    )
    run.add_argument(
        "--progress",
        action="store_true",
        help="Display progress bars.",
    )
    run.add_argument(
        "--label-movie",
        action="store_true",
        help="Label movie with cellids.",
    )
    # Train
    train = subparsers.add_parser("train", help="Train DeLTA's models on your dataset")
    train.add_argument(
        "-c",
        "--config",
        help="Configuration file.  Can be either `2D`, `mothermachine`, "
        "or a path to a previously saved custom config file.",
        required=True,
    )
    train.add_argument(
        "-m",
        "--model",
        choices=get_args(MODEL),
        help="Model to train.",
        required=True,
    )
    train.add_argument(
        "-i",
        "--input",
        help="Input folder, containing the training dataset. "
        "For example for a segmentation dataset, `img/` and `seg/` are required. "
        "If absent, will use the original DeLTA dataset.",
    )
    train.add_argument(
        "-o",
        "--output",
        help="Output file for the model (by default `model_{model}.keras`).",
    )
    train.add_argument(
        "-C",
        action="append",
        metavar="KEY=VALUE",
        help="Configuration option added on the fly for this run, for example `pipeline_seg_batch=1`.",
    )
    train.add_argument(
        "--epochs",
        type=int,
        default=1000,
        help="Number of epochs to train.  Default: 1000.",
    )
    train.add_argument(
        "--steps-per-epoch",
        type=int,
        help="Number of samples seen per epoch. "
        "Default: number of samples in the training set.",
    )
    train.add_argument(
        "--vsplit",
        type=float,
        default=0.05,
        help="Proportion of the training set to be used for the validation dataset. "
        "Default: 0.05.",
    )
    # Evaluate
    evaluate = subparsers.add_parser(
        "evaluate",
        help="Evaluate DeLTA's performance on your dataset",
        description="Use this subcommand to evaluate a model performance on your "
        "dataset. It will evaluate it both on the training set, with data "
        "augmentation, and with the validation set, without data augmentation. "
        "If you have a test set, it is probably stored separately, and you don't want "
        "to evaluate it with data augmentation. In this case, you can just specify "
        "`--vsplit 1` on your test set, so all of it will be run without data "
        "augmentation.",
    )
    evaluate.add_argument(
        "-c",
        "--config",
        help="Configuration file.  Can be either `2D`, `mothermachine`, "
        "or a path to a previously saved custom config file.",
        required=True,
    )
    evaluate.add_argument(
        "-m",
        "--model",
        choices=get_args(MODEL),
        help="Model to evaluate.",
        required=True,
    )
    evaluate.add_argument(
        "-i",
        "--input",
        help="Input folder, containing the training dataset. "
        "For example for a segmentation dataset, `img/` and `seg/` are required. "
        "If absent, will use the original DeLTA dataset.",
    )
    evaluate.add_argument(
        "-C",
        action="append",
        metavar="KEY=VALUE",
        help="Configuration option added on the fly for this run, for example `model_file_seg=filename.keras`.",
    )
    evaluate.add_argument(
        "--steps",
        type=int,
        help="Number of samples seen in the dataset. "
        "Default: number of samples in the training set.",
    )
    evaluate.add_argument(
        "--vsplit",
        type=float,
        default=0.05,
        help="Proportion of the training set to be used for the validation dataset. "
        "Default: 0.05.",
    )
    # Compare
    compare = subparsers.add_parser(
        "compare", help="Compare two nc files (for debugging)"
    )
    compare.add_argument("file1", type=Path, help="First file.")
    compare.add_argument("file2", type=Path, help="Second file.")

    return parser.parse_args(args)


def _build_config(presets: str, extra_args: list[str] | None) -> Config:
    if presets in get_args(PRESETS):
        presets = cast("PRESETS", presets)
        config = Config.default(presets)
    else:
        config = Config.read(presets)

    if isinstance(extra_args, list):
        for key_val in extra_args:
            key, value = key_val.split("=")
            config.update(key, value)

    return config


def _run(args: argparse.Namespace) -> None:
    config = _build_config(args.config, args.C)

    if keras.src.backend.config.backend() == "tensorflow":
        config.apply_backend_config()

    xpreader = delta.utils.XPReader(args.input)

    xp = delta.pipeline.Pipeline(xpreader, config=config, resfolder=args.output)

    save_as = ("netCDF", "labeled-movie" if args.label_movie else "movie")

    xp.process(
        positions=args.positions,
        frames=args.frames,
        save_as=save_as,
        progress_bar=args.progress,
    )


def _train(args: argparse.Namespace) -> None:
    config = _build_config(args.config, args.C)

    if keras.src.backend.config.backend() == "tensorflow":
        config.apply_backend_config()

    input_dir = (
        delta.assets.download_training_set(args.C, args.model)
        if args.input is None
        else Path(args.input)
    )
    model_file = Path(
        f"model_{args.model}.keras" if args.output is None else args.output
    )
    epochs = 1000 if args.epochs is None else args.epochs
    steps_per_epoch = args.steps_per_epoch
    if steps_per_epoch is None and args.input is None:
        steps_per_epoch = 300

    if args.model == "seg" and not (input_dir / "wei").is_dir():
        LOGGER.info("No weight maps detected for segmentation.  Creating them now.")
        if "rois" in config.models:
            delta.data.make_weights(input_dir, delta.data.seg_weights)
        else:
            delta.data.make_weights(input_dir, delta.data.seg_weights_2D)

    # Set tensorflow's random seed to make the training reproducible (only on
    # CPU: not reproducible on GPU yet)
    keras.utils.set_random_seed(1)

    if args.model == "rois":
        _train_rois(
            config,
            input_dir,
            model_file,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            validation_split=args.vsplit,
        )
    elif args.model == "seg":
        _train_seg(
            config,
            input_dir,
            model_file,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            validation_split=args.vsplit,
        )
    elif args.model == "track":
        _train_track(
            config,
            input_dir,
            model_file,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
        )
    else:
        error_msg = "model type not understood (should be `rois`, `seg` or `track`)"
        raise ValueError(error_msg)


def _evaluate(args: argparse.Namespace) -> None:
    config = _build_config(args.config, args.C)

    if keras.src.backend.config.backend() == "tensorflow":
        config.apply_backend_config()

    input_dir = (
        delta.assets.download_training_set(args.C, args.model)
        if args.input is None
        else Path(args.input)
    )
    steps = args.steps
    if steps is None and args.input is None:
        steps = 300

    if args.model == "seg" and not (input_dir / "wei").is_dir():
        LOGGER.info("No weight maps detected for segmentation.  Creating them now.")
        if "rois" in config.models:
            delta.data.make_weights(input_dir, delta.data.seg_weights)
        else:
            delta.data.make_weights(input_dir, delta.data.seg_weights_2D)

    if args.model == "rois":
        model = config.models["rois"].model()
        _evaluate_rois(
            model, config, input_dir, steps=steps, validation_split=args.vsplit
        )
    elif args.model == "seg":
        model = config.models["seg"].model()
        _evaluate_seg(
            model, config, input_dir, steps=steps, validation_split=args.vsplit
        )
    elif args.model == "track":
        LOGGER.critical("Evaluation not implemented yet for tracking model.")
        raise NotImplementedError


DATA_AUGMENTATION_ROIS = {
    "rotation": 3,
    "shiftX": 0.1,
    "shiftY": 0.1,
    "zoom": 0.25,
    "horizontal_flip": True,
    "vertical_flip": True,
    "rotations_90d": True,
    "histogram_voodoo": True,
    "illumination_voodoo": True,
    "gaussian_noise": 0.03,
}

DATA_AUGMENTATION_SEG = {
    "rotation": 2,
    "rotations_90d": False,
    "zoom": 0.15,
    "horizontal_flip": True,
    "vertical_flip": True,
    "illumination_voodoo": True,
    "gaussion_noise": 0.03,
    "gaussian_blur": 1,
}

DATA_AUGMENTATION_TRACK = {
    "rotation": 1,
    "zoom": 0.15,
    "horizontal_flip": True,
    "histogram_voodoo": True,
    "illumination_voodoo": True,
}


def _evaluate_rois(
    model: keras.Model,
    config: Config,
    input_dir: Path,
    steps: int | None = None,
    validation_split: float = 0.05,
) -> None:
    ds_train, ds_val = delta.data.load_training_dataset_seg(
        dataset_path=input_dir,
        target_size=config.models["rois"].target_size,
        crop=False,
        kw_data_aug=DATA_AUGMENTATION_ROIS,
        validation_split=validation_split,
        stack=False,
    )

    model.compile(
        optimizer=keras.optimizers.Adam(1e-4),
        loss=keras.losses.BinaryCrossentropy(from_logits=True),
        metrics=[
            keras.metrics.BinaryAccuracy(threshold=0.0),
            keras.metrics.BinaryIoU(threshold=0.0),
        ],
    )

    for dataset, name in [(ds_train, "training"), (ds_val, "validation")]:
        data_aug = {"training": "WITH", "validation": "NO"}[name]
        real_steps = len(dataset) if steps is None else min(steps, len(dataset))

        LOGGER.info(
            "Evaluating on %d %s set samples (%s data augmentation)...",
            real_steps,
            name,
            data_aug,
        )

        metrics = model.evaluate(dataset, steps=real_steps, return_dict=True, verbose=0)

        for key, value in metrics.items():
            LOGGER.info("    %s: %f", key, value)


def _evaluate_seg(
    model: keras.Model,
    config: Config,
    input_dir: Path,
    steps: int | None = None,
    validation_split: float = 0.05,
) -> None:
    ds_train, ds_val = delta.data.load_training_dataset_seg(
        dataset_path=input_dir,
        target_size=config.models["seg"].target_size,
        crop=False,
        kw_data_aug=DATA_AUGMENTATION_SEG,
        validation_split=validation_split,
        stack=False,
    )

    acc = keras.metrics.BinaryAccuracy(threshold=0)
    iou = keras.metrics.BinaryIoU(threshold=0)

    model.compile(
        optimizer=keras.optimizers.Adam(1e-4),
        loss=keras.losses.BinaryCrossentropy(from_logits=True),
        metrics=[acc, iou],
        weighted_metrics=[acc, iou],
    )

    for dataset, name in [(ds_train, "training"), (ds_val, "validation")]:
        data_aug = {"training": "WITH", "validation": "NO"}[name]
        real_steps = len(dataset) if steps is None else min(steps, len(dataset))

        LOGGER.info(
            "Evaluating on %d %s set samples (%s data augmentation)...",
            real_steps,
            name,
            data_aug,
        )

        metrics = model.evaluate(dataset, steps=real_steps, return_dict=True, verbose=0)

        for key, value in metrics.items():
            LOGGER.info("    %s: %f", key, value)


def _train_rois(
    config: Config,
    input_dir: Path,
    model_file: Path,
    steps_per_epoch: int | None = None,
    epochs: int = 600,
    validation_split: float = 0.05,
) -> None:
    ds_train, ds_val = delta.data.load_training_dataset_seg(
        dataset_path=input_dir,
        target_size=config.models["rois"].target_size,
        crop=False,
        kw_data_aug=DATA_AUGMENTATION_ROIS,
        validation_split=validation_split,
        stack=False,
    )

    if steps_per_epoch is not None:
        steps_per_epoch = min(steps_per_epoch, len(ds_train))

    model = delta.model.unet_rois(input_size=(*config.models["rois"].target_size, 1))
    model.summary()

    _history = model.fit(
        ds_train,
        steps_per_epoch=steps_per_epoch,
        validation_data=ds_val,
        epochs=epochs,
        callbacks=delta.utils.training_callbacks(model_file, verbose=1),
    )


def _train_seg(
    config: Config,
    input_dir: Path,
    model_file: Path,
    steps_per_epoch: int | None = None,
    epochs: int = 600,
    validation_split: float = 0.05,
) -> None:
    crop = "rois" not in config.models
    ds_train, ds_val = delta.data.load_training_dataset_seg(
        dataset_path=input_dir,
        target_size=config.models["seg"].target_size,
        crop=crop,
        kw_data_aug=DATA_AUGMENTATION_SEG,
        validation_split=validation_split,
        stack=True,
    )

    if steps_per_epoch is not None:
        steps_per_epoch = min(steps_per_epoch, len(ds_train))

    model = delta.model.unet_seg(input_size=(*config.models["seg"].target_size, 1))
    model.summary()

    _history = model.fit(
        ds_train,
        steps_per_epoch=steps_per_epoch,
        validation_data=ds_val,
        epochs=epochs,
        callbacks=delta.utils.training_callbacks(model_file, verbose=2),
    )


def _train_track(
    config: Config,
    input_dir: Path,
    model_file: Path,
    steps_per_epoch: int | None = None,
    epochs: int = 600,
) -> None:
    crop = "rois" not in config.models
    my_gene = delta.data.train_generator_track(
        batch_size=2,
        img_path=input_dir / "img",
        seg_path=input_dir / "seg",
        previmg_path=input_dir / "previmg",
        segall_path=input_dir / "segall",
        track_path=input_dir / "mot_dau",
        weights_path=input_dir / "wei",
        augment_params=DATA_AUGMENTATION_TRACK,
        crop_windows=crop,
        target_size=config.models["track"].target_size,
        shift=5,
    )

    model = delta.model.unet_track(input_size=(*config.models["track"].target_size, 4))
    model.summary()

    _history = model.fit(
        my_gene,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,
        callbacks=delta.utils.training_callbacks(model_file, verbose=1),
    )


def _compare(args: argparse.Namespace) -> None:
    pos1 = delta.pipeline.Position.load_netcdf(args.file1)
    pos2 = delta.pipeline.Position.load_netcdf(args.file2)
    pos1.compare(pos2)


def main() -> None:
    """Entry-point of the `delta` command-line tool."""
    args = delta.cli.parse_args()
    subcommands = {
        "run": _run,
        "train": _train,
        "evaluate": _evaluate,
        "compare": _compare,
    }
    if args.subcommand is None:
        delta.cli.parse_args(["--help"])
    else:
        subcommands[args.subcommand](args)
