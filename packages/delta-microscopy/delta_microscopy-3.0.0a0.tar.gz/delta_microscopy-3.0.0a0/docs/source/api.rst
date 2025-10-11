API Reference
=============

The API of DeLTA etc.

Assets
------

.. automodule:: delta.assets

.. autosummary::
   :toctree: generated

    ~delta.assets.download_training_set
    ~delta.assets.download_demo_movie
    ~delta.assets.download_model

Configuration
-------------

.. automodule:: delta.config

.. autosummary::
   :toctree: generated

    Config
    ModelConfig
    BackendConfig

Data
----

.. automodule:: delta.data

.. autosummary::
   :toctree: generated

   ~delta.data.binarize_threshold
   ~delta.data.read_reshape
   ~delta.data.postprocess
   ~delta.data.data_augmentation
   ~delta.data.affine_transform
   ~delta.data.histogram_voodoo
   ~delta.data.illumination_voodoo
   ~delta.data.SegmentationDataset
   ~delta.data.load_training_dataset_seg
   ~delta.data.random_crop
   ~delta.data.save_result_seg
   ~delta.data.predict_generator_seg
   ~delta.data.seg_weights
   ~delta.data.make_weights
   ~delta.data.kernel
   ~delta.data.estimate_seg2D_classweights
   ~delta.data.seg_weights_2D
   ~delta.data.estimate_classweights
   ~delta.data.train_generator_track
   ~delta.data.path_from_prototype
   ~delta.data.predict_compile_from_seg_track
   ~delta.data.tracking_weights
   ~delta.data.save_result_track

Lineage
-------

.. automodule:: delta.lineage

.. autosummary::
   :toctree: generated

   ~delta.lineage.CellFeatures
   ~delta.lineage.Cell
   ~delta.lineage.Lineage

Model
-----

.. automodule:: delta.model

.. autosummary::
   :toctree: generated

   ~delta.model.pixelwise_weighted_binary_crossentropy_seg
   ~delta.model.pixelwise_weighted_binary_crossentropy_track
   ~delta.model.unstack_acc
   ~delta.model.unet
   ~delta.model.unet_seg
   ~delta.model.unet_track
   ~delta.model.unet_rois

Pipeline
--------

.. automodule:: delta.pipeline

.. autosummary::
   :toctree: generated

   ~Pipeline
   ~Position
   ~ROI

Utilities
---------

.. automodule:: delta.utils

.. autosummary::
   :toctree: generated

   ~delta.utils.CroppingBox
   ~delta.utils.XPReader
   ~delta.utils.to_integer_values
   ~delta.utils.deskew
   ~delta.utils.rotate
   ~delta.utils.correct_drift
   ~delta.utils.drift_template
   ~delta.utils.filter_areas
   ~delta.utils.create_windows
   ~delta.utils.stitch_pic
   ~delta.utils.tracking_box
   ~delta.utils.shift_values
   ~delta.utils.find_contours
   ~delta.utils.label_seg
   ~delta.utils.cells_in_frame
   ~delta.utils.centroid
   ~delta.utils.poles
   ~delta.utils.skeleton_poles
   ~delta.utils.extrema_poles
   ~delta.utils.two_poles
   ~delta.utils.extract_poles
   ~delta.utils.eucl
   ~delta.utils.track_poles
   ~delta.utils.division_poles
   ~delta.utils.tracking_scores
   ~delta.utils.attributions
   ~delta.utils.random_colors
   ~delta.utils.write_video
   ~delta.utils.roi_features
   ~delta.utils.image_edges
   ~delta.utils.cell_width_length
   ~delta.utils.cell_area
   ~delta.utils.cell_perimeter
   ~delta.utils.cell_fluo
   ~delta.utils.read_image
   ~delta.utils.list_files
   ~delta.utils.tensorboard_callback
