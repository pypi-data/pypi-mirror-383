Training models: advanced
=========================

The command-line training is quick and convenient but not overly customizable.
If you need more control on the training process, you need to write a script,
and in order to do this, first become familiar with a few more of DeLTAs'
internals: in particular the :class:`delta.data` module.

This module offers utilities to help you retrain DeLTA on your own data:
functions and generators to read and preprocess training sets files, perform
data augmentation operations, and feed inputs into the U-Net models for
training, as well as functions and generators to preprocess inputs for
prediction.  In addition, a few functions are provided for light postprocessing
and saving results to disk.

Training generators and datasets
--------------------------------

The module contains 2 generator functions to be used for training the
segmentation and tracking U-Nets, namely
:class:`delta.data.load_training_dataset_seg` and
:class:`delta.data.train_generator_track`.

For every batch, these generators read random training samples from the
training sets folders, apply similar data augmentation operations to all images
within the same sample, and then stack these samples together to form a batch
of size ``batch_size``.

For segmentation, the structure of the training sets is:

* ``img`` folder: **phase contrast images**
    Microscopy images to use as training inputs.  So far we've been exclusively
    using phase contrast images, but these could be replaced by bright field or
    fluorescence images, or even a mix of the three.
* ``seg`` folder: **segmentation ground truth**
    Segmentation ground truth, corresponding to the images in the ``img`` folder.
* ``wei`` folder: **weight maps, optional**
    Pixel-wise weight maps.  These are used to multiply the loss in certain key
    regions of the image and force the model to focus on these regions, or on
    the contrary, make certain regions irrelevant.  The main use for them is to
    force the models to focus on small borders between cells.  These are be
    generated from the ``seg`` images by the functions
    :class:`delta.data.seg_weights` and :class:`delta.data.seg_weights_2D`.
    They can be made for a whole dataset with the function
    :class:`delta.data.make_weights`.

For tracking, the structure is:

* ``previmg`` folder: **images at previous time point**
    Microscopy images to use as training inputs for the
    previous time point, i.e. the time point that we want to predict tracking *from*.
* ``seg`` folder: **'seed' cell from previous time point**
    Images of the segmentation of a single cell from the previous time that we
    want to predict tracking for
* ``img`` folder: **images at current time point**
    Microscopy images to use as training inputs for the
    current time point, i.e. the time point that we want to predict tracking *for*.
* ``segall`` folder: **segmentation at current time point**
    Segmentation images of all cells at the current time point.
* ``mot_dau`` folder: **tracking ground truth**
    Tracking maps for the tracking U-Net to be trained against. Outlines the
    tracking of the 'seed' cell into the current time point, or if it divided,
    of both cells that resulted from the division.
* ``wei`` folder: **weight maps, optional**
    Pixel-wise weight maps. These are used to multiply the
    loss in certain key regions of the image and force the model to focus on
    these regions. The main use for them is to force the models to focus on
    the area surrounding the 'seed' cell. These can be generated from the
    ``segall`` and ``mot_dau`` images with :class:`delta.data.tracking_weights`.

.. note::
    The folder names do not need to strictly follow this nomenclature or
    even all be grouped under the same folder as the path to each folder is
    passed as an input to the training generators.

See :ref:`Training scripts <training_scripts>` for examples use of the
generators.  For an example of datasets structure, check out your downloaded
datasets: :class:`delta.assets.download_training_set`.

Data augmentation
-----------------

A key element to making the U-Nets able to generalize to completely new
experiments and images is data augmentation.  These operations modify the
original training samples in order to not only artificially inflate the size of
the training sets but also to force the models to learn to make predictions in
sub-optimal or different imaging conditions, for example via the addition of
noise or changes in the image histograms.

The main function is :class:`delta.data.data_augmentation`.  It takes as an
input a stack of images to process with the same operations, and augmentations
operations parameters dictionary of what operations to apply and with what
parameters or parameter ranges.

The operations names and their parameters are described in the documentation of
the function.

.. _prediction_gen:

Prediction generators
---------------------

To be able to rapidly assess the performance of the U-Nets after training, the
prediction generators
:class:`delta.data.predict_generator_seg` and
:class:`delta.data.predict_compile_from_seg_track`
can read and compile evaluation data to feed into the trained models.  Please
note that these are not used in any way by the :class:`delta.pipeline`
module and are only intended for quick evaluation and explanation purposes.

* ``predict_generator_seg`` simply reads an image files sequence in order from a
  folder, crops or resizes images to fit the U-Net input size, and then yields
  those images.

* ``predict_compile_from_seg_track`` is a little more complicated however.  It
  reads image sequences in both an inputs image folder, and in a segmentation
  folder.  As such it is intended to be used after segmentation predictions
  have been made and saved to disk.  The generator uses the file names to infer
  the position, roi, and time point of each sample to ensure that they are
  processed in the correct order.  The outputs are saved to disk with an
  appended ``_cellXXXXXX`` suffix their filename to keep track of which cells
  are tracked to which (cells are numbered from top of the image to bottom).

See :ref:`Evaluation scripts <eval_scripts>` for examples.
