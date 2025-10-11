Contribute
==========

We gladly welcome contributions to DeLTA!

You can send us your training data if you think it will benefit the community.
Reach out via Gitlab's issue system :)

If you want to help with the development, you can fork DeLTA and submit Merge
Requests on Gitlab. If you plan on implementing significant changes, please
coordinate with us first.

Development environment
-----------------------

The easiest to start working on DeLTA is to clone the git repository, to
install `pixi <https://pixi.sh/>`_ and to run ``pixi shell -e XXX-YYY``
where ``XXX`` can be either of ``jax``, ``torch`` or ``tf`` and ``YYY`` can
be ``cpu`` or ``gpu``, depending on your hardware. This will create a
virtual environment, download the appropriate dependencies, and activate a
shell with DeLTA installed.

CI/CD pipeline
--------------

Thanks to gitlab's generous Open Source Program, we are now able to
systematically run tests for all merge requests.
This is implemented via the ``.gitlab-ci.yml`` file at the root of the
repository.

You can opt-out of the tests by adding the ``tests::block`` tag to the merge
request. Alternatively, you can force the tests to be trigger even if your
merge request does not merge into ``main`` branch by adding the
``tests::force`` tag to it. The ``tests::default`` is equivalent to not having
any tag.

Documentation
-------------

You can build the documentation locally with the following commands:

.. code:: console

    $ sphinx-build -b html docs/ wherever/

However, we use `readthedocs.org <https://readthedocs.org/>`_ to automatically
build them and host them for us:

* The ``main`` branch is monitored and publicly available under
  `delta.readthedocs.io/en/latest/ <https://delta.readthedocs.io/en/latest/>`_
* The latest tagged release is publicly available under
  `delta.readthedocs.io/en/stable/ <https://delta.readthedocs.io/en/stable/>`_
* The ``docs`` branch is monitored, but is "hidden" and is meant for us to write
  or test the docs. It is available under
  `delta.readthedocs.io/en/stable/ <https://delta.readthedocs.io/en/stable/>`_
* Each release has its own "archive" and is available under its version number,
  e.g. `delta.readthedocs.io/en/2.0.0/ <https://delta.readthedocs.io/en/2.0.0/>`_

The docs on any other branch can be built on demand from the dashboard on `the
readthedocs.org dashboard <https://readthedocs.org/dashboard>`_. To get access
to it, first create an account and one of the current maintainers needs to add
you as a maintainer under their admin menu. The file ``.readthedocs.yml``
manages settings specific to the online build and deployment of the docs.
