Configuration
=============

.. note::

    This page is a high-level overview of the :class:`delta.config` module of
    DeLTA, and you can find more technical explanations by clicking on any
    link.

DeLTA can work on different kinds of images, mothermachine and 2D (agar pads).
Different steps and networks are used for that: this configuration is described
by a :class:`delta.config.Config` object.

The only places where this object needs to be explicitly manipulated is at the
creation of a :class:`delta.pipeline.Pipeline`, a
:class:`delta.pipeline.Position` or a :class:`delta.pipeline.ROI`.

DeLTA provides two base configurations, one for each setting (mothermachine and
2D), available with the method :class:`delta.config.Config.default`.  They are
good to use right away, but you would typically modify them if you want to use
your own deep learning models instead of the ones included with DeLTA.

The main :class:`delta.config.Config` contains a few general options, and also
more specific configuration objects that relate to the deep learning models
(:class:`delta.config.ModelConfig`) or to the deep learning backends
(:class:`delta.config.BackendConfig`).

.. note::

    Some backend-related configuration options are not taken into account
    until the method :class:`delta.config.Config.apply_backend_config` is
    explicitly called. The default values are usually good, so you probably
    don't need to care about this, unless you know that you are doing.

Model configuration
-------------------

There are three possible models: ``"rois"`` (to detect the chambers of mother
machines), ``"seg"`` (which performs segmentation) and ``"track"`` (which
performs tracking). Each of these is configured by a
:class:`delta.config.ModelConfig` object.

While DeLTA comes with its own pre-trained model (which are downloaded and
cached on the fly when you need them, go to :class:`delta.assets` to know
how this works), you can supply your own trained models, as following:

.. code:: python

    from pathlib import Path
    from delta.config import Config

    config = Config.default("mothermachine")
    # Here, ``config.models["rois"].model_path`` is the location of the default
    # model for ROI detection.
    # To change it, do as follows:
    config.models["rois"].model_path = Path(
        "D:/data/delta_cache/unet_momachambers_seg.keras"
    )

Saving and using a configuration file
-------------------------------------

If you want to modify a configuration object, you can always do it
programmatically by accessing its attributes, as described on the documentation
page of :class:`delta.config.Config`, for example:

.. code:: python

    from delta.config import Config

    config = Config.default("mothermachine")
    config.models["seg"].target_size = (1024, 1024)
    config.models["seg"].min_area = 0

But you might also want to save the config object as a configuration file, and
modify it with a text editor, or save it for reusing, archiving or other
purposes.

This is done with the method :class:`delta.config.Config.write` which takes as
argument the path to the toml file where you want the configuration written:

.. code:: python

    config.write("my_custom_config.toml")

To read later from this file, use the method :class:`delta.config.Config.read`:

.. code:: python

    config = delta.config.Config.read("my_custom_config.toml")
