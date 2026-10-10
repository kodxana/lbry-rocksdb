Installing
==========
.. highlight:: bash

Release wheels
**************

Community releases are available from
`GitHub Releases <https://github.com/kodxana/lbry-rocksdb-ng/releases>`_.
Follow the `release installation guide <https://github.com/kodxana/lbry-rocksdb-ng/blob/master/docs/releases.md#installing-a-released-wheel>`_
to choose a compatible wheel and verify its checksum.

Use a fresh virtual environment. The legacy ``lbry-rocksdb`` package on PyPI
is not this fork; both packages install the same ``rocksdb`` module and must
not be installed together.

From source (ubuntu)
********************
.. code-block:: bash

    sudo apt install build-essential binutils
    git clone https://github.com/kodxana/lbry-rocksdb-ng.git
    cd lbry-rocksdb-ng
    git submodule update --init --recursive
    python -m pip install -r docker/test-requirements.txt
    make JOBS=2
    python -m pip install --no-build-isolation -e .
    python -m pytest -v tests

These commands assume a virtual environment with CPython 3.9 or 3.13.
See the `testing guide <https://github.com/kodxana/lbry-rocksdb-ng/blob/master/docs/testing.md>`_
for the isolated Docker builds used by CI.
