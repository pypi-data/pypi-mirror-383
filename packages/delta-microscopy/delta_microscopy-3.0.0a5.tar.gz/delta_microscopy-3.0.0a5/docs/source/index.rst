.. module:: delta

Welcome to DeLTA's documentation!
=================================

DeLTA (Deep Learning for Time-lapse Analysis) is a deep learning-based image
processing pipeline for segmenting and tracking single cells in time-lapse
microscopy movies.

.. image:: _static/DeLTAexample.gif
    :alt: An illustration of DeLTA's performance on an agar pad movie of E. Coli
    :align: center

Getting started
---------------

You can quickly check how DeLTA performs on your data for free
by using our `Google Colab notebook <https://colab.research.google.com/drive/1UL9oXmcJFRBAm0BMQy_DMKg4VHYGgtxZ>`_


To get started on your own system, check out the :doc:`installation
instructions <usage/installation>`, and run the :doc:`pipeline
<usage/library/pipeline_desc>` on our data or your own.

See also our :doc:`example scripts <usage/library/scripts>` and
:doc:`results analysis examples <usage/analysis>`.

Finally, you can :doc:`contribute to DeLTA <usage/contribute>`.

Gitlab repository:
`https://gitlab.com/delta-microscopy/delta <https://gitlab.com/delta-microscopy/delta>`_

🐛 If you encounter bugs, have questions about the software, suggestions for
new features, or even comments about the documentation, please use Gitlab's
issue system.

The ``main`` branch of the git repository is where new features and bug fixes
are integrated after being developed on feature branches.  Stable releases
of DeLTA are tagged with git tags (and published on pypi or conda-forge).

Overview
--------
DeLTA revolves around a pipeline that can process movies of rod-shaped bacteria
growing in 2D setups
such as agarose pads, as well as movies of E. coli cells trapped in a
microfluidic device known as a "mother machine".
Our pipeline is centered around two U-Net neural networks that are used sequentially:

* To perform semantic binary segmentation of our cells as in the original U-Net paper.
* To track cells from one movie frame to the next, and to identify cell divisions and mother/daughter cells.

A third U-Net can be used to identify regions of interest in the image before performing segmentation. This is used with mother machine movies to identify single chambers, but by default only 1 ROI covering the entire field-of-view is used in the 2D version.
The U-Nets are implemented in Tensorflow 2 via the Keras API.

Citation
--------

If you use DeLTA in academic research, please cite us using one of the
following references:

Version 2:
`O’Connor OM, Alnahhas RN, Lugagne J-B, Dunlop MJ (2022) DeLTA 2.0: A deep learning pipeline for quantifying single-cell spatial and temporal dynamics. PLoS Comput Biol 18(1): e1009797 <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009797>`_

Version 1:
`Lugagne J-B, Lin H, & Dunlop MJ (2020) DeLTA: Automated cell segmentation, tracking, and lineage reconstruction using deep learning. PLoS Comput Biol 16(4): e1007673 <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007673>`_

.. The toctree needs to exist on the index page, even hidden.

.. toctree::
   :hidden:
   :caption: For users

   usage/installation
   usage/quick_start
   usage/library/index
   usage/outputs
   usage/analysis

.. toctree::
   :hidden:
   :caption: For trainers

   usage/training_quick_start
   usage/training_advanced

.. toctree::
   :hidden:
   :caption: For developers

   api
   usage/contribute
