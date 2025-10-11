Training models: quick start
============================

If the pre-trained DeLTA models don't perform optimally on your data, it might
be because your images are too different from DeLTA's training set.  In this
case, you might want to retrain DeLTA specifically on your own data, to achieve
optimal performance.

You can do so without writing any code, with the DeLTA command-line interface.

Creating a training dataset
---------------------------

.. note::

    We will consider in this section the case of a 2D segmentation dataset.

The first step is to create a training dataset, i.e. segmentation ground
truths.  You can do that entirely manually, but you can also clean up a decent
segmentation that you got from DeLTA or another segmentation software.

Each training sample is represented by two images:

* One input image (typically from phase contrast, grayscale, png or tif, with
  any bit depth (8, 16 or other));
* One segmentation mask, with the same dimensions and same name as the input
  image (although the extension can be different), labelled with binary values:
  0 for background pixels and 255 for cell pixels.

These images can have arbitrary names, as long as they match between input
image and segmentation mask.  To distinguish them, the input images should be
in a directory ``img/`` and the segmentation masks in a directory ``seg/``.

Your dataset should look like this:

.. code:: none

    training_dataset/
        img/
            sample-0001.tif
            sample-0002.tif
            other-sample.png
            image_from_X_lab.png
            ...
        seg/
            sample-0001.png
            sample-0002.png
            other-sample.png
            image_from_X_lab.png
            ...

Training a new segmentation model
---------------------------------

Once you are there, training a new model just requires one line:

.. code:: console

    $ delta train --config 2D --model seg --input training_dataset/ --output my_model.keras

There are other options, such as one to choose the proportion of training
samples that you want to include in the validation dataset.  To know about all
the options and explanations on their usage, run the following:

.. code:: console

    $ delta train --help
