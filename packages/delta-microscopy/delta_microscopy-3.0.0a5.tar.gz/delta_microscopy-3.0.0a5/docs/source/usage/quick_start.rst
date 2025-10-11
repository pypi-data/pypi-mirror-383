Quick start
===========

Once DeLTA is installed, you can already use it without writing any code,
with its default configuration, through its command-line interface.

You can read the instructions to use the command-line interface by calling
``delta`` with the ``--help`` flag:

.. code:: console

    (delta_env)$ delta --help

    usage: delta [-h] {run,train,evaluate,compare} ...

    Deep Learning for Time-Lapse Analysis

    positional arguments:
      {run,train,evaluate,compare}
                            Action to perform
        run                 Segment and track an experiment
        train               Train DeLTA's models on your dataset
        evaluate            Evaluate DeLTA's performance on your dataset
        compare             Compare two nc files (for debugging)

    options:
      -h, --help            show this help message and exit


The options available for any of these commands are obtained in the same way,
for example for ``run``:

.. code:: console

    (delta_env)$ delta run --help

    usage: delta run [-h] -c CONFIG -i INPUT [-o OUTPUT] [-C KEY=VALUE] [--positions POSITIONS]
                     [--frames FRAMES] [--progress] [--label-movie]

    options:
      -h, --help            show this help message and exit
      -c, --config CONFIG   Configuration file. Can be either `2D`, `mothermachine`, or a path
                            to a previously saved custom config file.
      -i, --input INPUT     Input file or directory. Can include `{p}`, `{c}` and `{t}` as
                            placeholders for the position, channel, and frame number. Example
                            for micromanager:
                            `/path/to/folder/Pos{p}/img_channel{c}_position{p}_time{t}_z000.tif`
      -o, --output OUTPUT   Output directory (by default `delta_results` inside the input
                            directory)
      -C KEY=VALUE          Configuration option added on the fly for this run, for example
                            `min_cell_area=40`.
      --positions POSITIONS
                            Positions to process, ex.: 0-2,4,7-10 (default: all)
      --frames FRAMES       Range of frames to process, ex.: -150 (up to frame 150), 15- (from
                            frame 15), 15-30 (frames 15 to 30), 40 (just frame 40) (default:
                            all)
      --progress            Display progress bars.
      --label-movie         Label movie with cellids.


Here, the only two arguments required are ``CONFIG`` (use ``mothermachine`` if
you are using one, ``2D`` otherwise, or the path to a config file that you
previously saved), and ``INPUT``.  If your images are saved as a single file,
for example an ``nd2`` file, just provide its name, but if they are saved as
individual files inside a directory, then provide their naming pattern with the
placeholders ``{p}`` for the position number, ``{c}`` for the channel number
and ``{t}`` for the frame number.

Example uses
------------

* You recorded mothermachine images as a ``.nd2`` file: you can just launch
  DeLTA on them with

.. code:: console

    (delta_env)$ delta run -c mothermachine -i my_images.nd2

* You did an agar pad experiment where each frame is an individual ``.tif``
  image, all saved in the same directory ``images/`` with names
  ``posXXX_channelXXX_tXXX.tif``.  Then, you can launch DeLTA on them with

.. code:: console

    (delta_env)$ delta run -c 2D -i images/pos{p}_channel{c}_t{t}.tif
