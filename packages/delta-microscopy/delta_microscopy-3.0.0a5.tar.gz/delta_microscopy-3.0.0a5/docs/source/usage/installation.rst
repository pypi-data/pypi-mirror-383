Installation
============

You can try DeLTA out without installing anything on `Google Colab
<https://colab.research.google.com/drive/1UL9oXmcJFRBAm0BMQy_DMKg4VHYGgtxZ>`_.


You can also install DeLTA on your computer or your cluster easily with
`pip <https://pip.pypa.io/en/stable/>`_ or `pixi <https://pixi.sh/latest/>`_,
as described on this page.

.. note::
    Previous versions of DeLTA also offered installation via ``conda``, but we
    have been dropping support for it. You can of course still use ``conda`` for
    environment management (and we encourage you to create a dedicated
    environment to install DeLTA into), but we recommend using ``pip``/``pixi``
    for packages installation.

Hardware requirements
---------------------

DeLTA runs much faster on a GPU.  To do so you will need
`an nvidia gpu with a cuda compute capability of 3.5 or higher <https://developer.nvidia.com/cuda-gpus>`_
and `an up-to-date gpu driver <https://www.nvidia.com/Download/index.aspx?lang=en-us>`_.
If no compatible GPU/driver is found on the system, tensorflow will run on CPU.

If you do not have access to a compatible GPU, DeLTA will run fine on CPU but
will be slower. Computing clusters and cloud computing platforms are also an
alternative that has been working well for us.

Prerequisites
-------------

.. tab-set::

    .. tab-item:: Windows (WSL/WSL2)

        If you want to use DeLTA on Windows, you would need to install it
        inside WSL (Windows Subsystem for Linux).

        WSL can be seen as a Linux emulator running inside Windows. If you
        already have it installed, you can already continue with the Linux
        instructions.  Otherwise, install it, and then follow the Linux
        instructions.

        .. dropdown:: Installing WSL

            To activate WSL on Windows, first ensure that Windows Update is
            up to date, and if you have a GPU make sure you are using the
            latest drivers.

            Then, using the "Turn Windows features on or off" tool, turn on the
            `Virtual Machine Platform
            <https://support.microsoft.com/en-us/windows/enable-virtualization-on-windows-11-pcs-c5578302-6e43-4b4b-a449-8ced115f58e1>`_
            and the `Windows Subsystem for Linux` features.  You may now check
            again for Windows updates.

            Using the Microsoft app store, download the `Windows Terminal` to
            make the terminal use more agreeable.

            You next need to install a Linux distribution.  Type ``wsl --list
            --online`` in the Windows terminal to see a list of options. Debian
            is a good choice, to install it type ``wsl --install -d Debian``.
            Setup a username and a password, and you now have a fully
            functional Linux distribution running inside Windows.  Type ``wsl
            --list --verbose`` in any **Windows** terminal, and make sure that
            the version number is `2`, otherwise you will have to either update
            wsl with ``wsl --update`` or by following `these steps
            <https://learn.microsoft.com/en-us/windows/wsl/install-manual>`_.

            You can start upgrading Debian by typing the following commands in
            the **Linux** terminal:

            .. code:: console

                $ sudo apt update
                $ sudo apt upgrade

            .. note::
                The dollar sign is not a part of the command, it just
                represents the invite prompt.

            You are now ready to continue with the Linux section of this guide.

        You can from now on follow the Linux instructions, starting with this tab.

    .. tab-item:: Linux

        If you are installing with ``pip``, you will need to install ``ffmpeg``
        manually. The easiest way is to use your system's package manager (e.g
        ``sudo apt install ffmpeg`` on Debian/Ubuntu). See `python-ffmpeg's page
        <https://github.com/kkroening/ffmpeg-python?tab=readme-ov-file#installing-ffmpeg>`_
        for more information. You might also have to install the development versions of ``libxslt``
        and ``libxml``. (e.g. ``sudo apt install libxml2-dev libxslt-dev`` on
        Debian / Ubuntu).

        If you want to use your GPU, make sure you have the latest proprietary
        Nvidia drivers installed.

        Note that ``pixi`` will install all of this by itself if you choose this
        installation method.


    .. tab-item:: Mac OS

        TODO

Installation
------------

If you don't think that you will ever need to modify DeLTA's own code, choose
the "for users" option.  Otherwise, choose the "for devs" option.

Note that for ``pip`` installations, you will need to create a virtual
environment. If you know what you are doing, you can use your favorite method
for this. Otherwise, we recommend using ``conda`` `for virtual environment
creation and management only`, not for installation. To create a new environment
named ``delta_env``::

    $ conda create -n delta_env python=3.11

Make sure to use a version of python that is compatible with the current
version of DeLTA (see ``pyproject.toml``).

.. dropdown:: ``conda`` crash course

    * ``conda`` is a program able to create isolated environments and install
      packages in them, allowing to have different potentially conflicting
      versions coexisting in different environments for the needs of different
      programs.
    * In some of the commands of this documentation, to be typed in a terminal,
      we show a word in parentheses before the prompt, in general either
      ``(base)`` or ``(delta_env)``.  These refer to the currently activated
      conda environment: ``base`` is the default (when no environment has been
      manually activated), while ``delta_env`` is the environment where DeLTA
      is available to python.
    * You can activate the ``delta_env`` environment with ``conda activate
      delta_env`` and deactivate it with ``conda deactivate``.  When the
      environment is activated, every package that has been installed in
      it is available to python.

.. tab-set::

    .. tab-item:: Pip (for users)

        DeLTA is available as `a pip package
        <https://pypi.org/project/delta2/>`_ on PyPI.

        To install it, simply run the following command to install DeLTA:

        .. code:: console

            (delta_env)$ pip install delta2

        You can now ``import delta``.

        .. attention::
            Note that the ``pip`` package name is ``delta2`` but the python
            package to import is just ``delta``.


    .. tab-item:: Pip (for devs)

        First clone and enter our git repository:

        .. code:: console

            (delta_env)$ git clone https://gitlab.com/delta-microscopy/DeLTA
            (delta_env)$ cd delta

        .. note::
            This version is installed from sources and may therefore differ
            significantly from the stable versions available on PyPI.

        You can now specify your preferred deep learning library backend, and
        specify whether you would like to install the CPU or GPU version.
        To install the dependencies for ``pytorch`` and run it on GPU, run
        the following command, inside your cloned DeLTA directory:

        .. code:: console

            (delta_env)$ pip install -e .[torch-gpu]

        Available backend-hardware options are ``torch-cpu``, ``torch-gpu``,
        ``tensorflow-cpu``, ``tensorflow-gpu``, ``jax-cpu``, and ``jax-gpu``. We
        will focus testing and support efforts on the ``pytorch`` versions, but
        all 3 should work the same.

        .. note::
            The ``-e`` installs DeLTA in "editable" mode, meaning that any
            change you make to DeLTA's source code will be taken into account
            next time you ``import delta``.

    .. tab-item:: Pixi (for devs)

        First clone and enter our git repository:

        .. code:: console

            $ git clone https://gitlab.com/delta-microscopy/DeLTA
            $ cd delta

        You can now specify your preferred deep learning library backend, and
        specify whether you would like to install the CPU or GPU version.
        To install the dependencies for ``pytorch`` and run it on GPU, run
        the following command, inside your cloned DeLTA directory:

        .. code:: console

            $ pixi shell -e torch-gpu

        .. note::
            You don't need to create a special environment with ``pixi``, it
            takes care of that by itself.

        Available backend-hardware options are ``torch-cpu``, ``torch-gpu``,
        ``tensorflow-cpu``, ``tensorflow-gpu``, ``jax-cpu``, and ``jax-gpu``. We
        will focus testing and support efforts on the ``pytorch`` versions, but
        all 3 should work the same.

        To exit simply:

        .. code:: console

            $ exit

        To return to the environment simply type the same command again from
        inside the ``delta`` folder:

        .. code:: console

            $ pixi shell -e torch-gpu

        `More information on pixi <https://pixi.sh/latest/>`_.


Check installation
------------------

You can check what libraries have been installed with ``pip``:

.. code:: console

    (delta_env)$ pip list

or with pixi, after activating the pixi shell:

.. code:: console

    $ pixi list

To check that your backend is able to detect the GPU, please run the following
in the python interpreter:


.. tab-set::


    .. tab-item:: Pytorch

        .. code:: python-console

            >>> import torch
            >>> torch.cuda.is_available()

        Should return ``True``

    .. tab-item:: TensorFlow

        .. code:: python-console

            >>> import tensorflow as tf
            >>> tf.config.list_physical_devices()

        Your GPU should appear in the list.

    .. tab-item:: JAX

        .. code:: python-console

            >>> import jax
            >>> jax.devices(backend="gpu")

        Your GPU should appear in the list.


Import DeLTA
------------

You should be all set. The following line in a python interpreter should work
from anywhere on your system (it will issue a warning about not finding
elastic-deform if you didn't install it):

.. code:: python-console

    >>> import delta

.. tip::

    If python can't find DeLTA even though you are inside the DeLTA
    environment, it might be because you installed DeLTA's dependencies but not
    DeLTA itself.  You can do so either with ``pip install -e .`` as explained
    above, in the "(for devs)" tabs.

Troubleshooting
---------------

.. dropdown:: Problems with tensorflow-estimator or h5py

    We have sometimes run into issues where conda would install versions of
    `tensorflow-estimator` that did not match the version of the base
    `tensorflow` library. To check which versions got installed if you run into
    issues with `tensorflow-estimator` please run the following:

    .. code:: console

        (delta_env)$ conda list | grep tensorflow

    If the versions of the estimator and the base library are too different
    this will cause problems. You can run the following to install the correct
    version:

    .. code:: console

        (delta_env)$ conda install tensorflow-estimator==2.X

    with 'X' replaced by the version of your base tensorflow.

    Similarly for h5py, sometimes a version that is too recent or too old gets
    installed. Depending on which version was installed, try:

    .. code:: console

        (delta_env)$ conda install h5py==2.*

    or:

    .. code:: console

        (delta_env)$ conda install h5py==3.*

.. dropdown:: cuDNN (or other libraries) not loading

    We have run into OOM errors or some GPU-related libraries failing to load
    or initialize on laptops. See the "Limiting GPU memory growth" section on
    `this tensorflow help page <https://www.tensorflow.org/guide/gpu>`_.
    Setting the ``memory_growth_limit`` parameter in the :doc:`JSON config file
    <library/config_desc>` to a set value in MB (eg 1024, 2048...) should solve
    the issue.


.. dropdown:: OOM - Out of memory (GPU)

    On GPU, you might run into memory problems. This is both linked to the
    batch size and the size of the images. The batch size is straightforward to
    change, lower the value at the beginning of the :ref:`training scripts
    <training_scripts>`.  Note that lower batch sizes may mean slower training
    convergence or lower performance overall.

    The other solution would be to use a smaller image target size. However if
    the original training images and masks are for example 512×512, downsizing
    them to 256×256 will reduce the memory footprint, but it might cause some
    borders between cells in the binary masks to disappear. Instead, training
    images should be resized upstream of DeLTA to make sure that your training
    set does feature cell-to-cell borders in the segmentation masks.

    Another reason why this may happen is that the pipeline is trying to process
    too many samples at once. Try lowering ``pipeline_seg_batch``,
    ``pipeline_track_batch``, and ``pipeline_chunk_size`` in your config.
