Example scripts
===============

These scripts are not packaged with DeLTA as part of the conda-forge package,
however you can find them on our
`GitLab under scripts <https://gitlab.com/delta-microscopy/delta/-/tree/main/scripts>`_

.. tip::
    Before running these scripts, make sure that DeLTA is properly installed as
    described in :doc:`../installation`.

.. tip::
    These scripts are mostly meant to be built on, in case your situation is too
    complex to be covered by the command-line interface, described in
    :doc:`../quick_start`. Most cases (analysis or model training or evaluation)
    can be handled more easily with the CLI.

.. _run_pipeline:

Run pipeline
------------

`run_pipeline.py <https://gitlab.com/delta-microscopy/delta/-/blob/main/scripts/run_pipeline.py>`_

This script loads the default 2D configuration file and processes the
evaluation movie.

.. warning::
    This script is a simplified version of the ``__main__.py`` file, which is
    called when you run DeLTA from the command line.  So, it is intended as a
    basis if you want to use DeLTA programmatically, but if you just want to
    analyze your movies, you should first check if the command-line interface
    described in :doc:`../quick_start` already covers your case.


.. _training_scripts:

Training scripts
-----------------

We provide 3 example training scripts:

* `train_rois.py <https://gitlab.com/delta-microscopy/delta/-/blob/main/scripts/train_rois.py>`_
  can be used to train a new ROIs identification U-Net. By default it will train to
  recognize mother-machine chambers from our base training set. However this script
  can be used to either adapt the model to recognize mother machine chambers in your
  own images, or even to recognize different types of ROIs like a different type of
  microfluidic chambers.
* `train_seg.py <https://gitlab.com/delta-microscopy/delta/-/blob/main/scripts/train_seg.py>`_,
  can be used to train a new segmentation U-Net. By default it will train to segment
  *E. coli* cells from the downloaded assets 2D training set, but you can switch it
  to the mothermachine presets or use it to train on your own data.
* `train_track.py <https://gitlab.com/delta-microscopy/delta/-/blob/main/scripts/train_track.py>`_.
  can be used to train a new tracking U-Net. By default it will train to track
  *E. coli* cells from the downloaded assets 2D training set, but you can switch it
  to the mothermachine presets or use it to train on your own data.

In general we recommend merging your training set with ours for training because
it tends to improve performance. It also lowers the number of new training sample
required if the images are similar enough. See our papers for more information
on how to generate training samples. We have been working on graphical user
interfaces to streamline the process but we do not yet have an estimate for when
these would be finalized.

.. note::
    If you have developed your own training sets for any new application or
    simply to get better results better with your data and you would like to
    share them, feel free to contact us!  We would be more than happy to make
    them available to the community or merge them with our training sets and
    train our latest models on them.

.. _eval_scripts:

Evaluation scripts
------------------

We provide 3 scripts to quickly gauge the performance of the trained U-Net
models. These scripts are also intended as a way for users to gain an
understanding of how the U-Nets are used in the main pipeline, and what data
formats they take as input and produce as outputs.

* `segmentation_rois.py <https://gitlab.com/delta-microscopy/delta/-/blob/main/scripts/segmentation_rois.py>`_
  produces segmentation masks delineating the mother machine chambers present in the
  mother machine evaluation movie. In the mother machine ``Pipeline``, the predictions
  from this U-Net for the first timepoint are used to then crop out images of
  single chambers in the rest of the movie, after drift correction is applied.
* `segmentation.py <https://gitlab.com/delta-microscopy/delta/-/blob/main/scripts/segmentation.py>`_
  segments cells in the 2D evaluation movie. You can change the
  segmentation folder to any image sequence you want to evaluate. The outputs
  from the segmentation U-Net are used, in the ``Pipeline`` and ``Position`` objects,
  to generate tracking inputs. You can check out what the input data to the
  U-Net looks like with ``input_batch = next(predGene)``
* `tracking.py <https://gitlab.com/delta-microscopy/delta/-/blob/main/scripts/tracking.py>`_
  uses the outputs ``segmentation.py`` to perform single-cell tracking. The
  :ref:`predictCompilefromseg_track <prediction_gen>` generator uses the filenames
  to infer images order and to compile tracking inputs for every segmented cell
  over time.
