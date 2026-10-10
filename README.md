## lbry-rocksdb-ng

Maintained fork of `lbry-rocksdb`. The distribution name is `lbry-rocksdb-ng`;
the Python import remains `rocksdb`.

### Note
The `python-rocksdb` and `pyrocksdb` packages haven't been updated in a long time - this repo is a fork of python-rocksdb with many of the PRs to it merged, and with [bunch of updates and improvements](https://github.com/iFA88/python-rocksdb) from @iFA88 and @mosquito.


### Install a release

Version 0.8.3 is available from [GitHub Releases](https://github.com/kodxana/lbry-rocksdb/releases/tag/v0.8.3).
Download the wheel matching your interpreter and verify it against the release's
`SHA256SUMS` before installing it. See [installation instructions](docs/releases.md#installing-a-released-wheel)
for the exact commands, or use the source build below.
`pip install lbry-rocksdb` still selects LBRY Inc's older package.

The release wheels target Linux x86-64 with standard CPython 3.9 or 3.13.
See [release instructions](docs/releases.md) for platform requirements and
the GitHub release process. No PyPI publishing setup is needed.

Use a fresh virtual environment when switching from `lbry-rocksdb` (or
`python-rocksdb`): both distributions install the same `rocksdb` files and
must not be installed together. Downstream dependencies must change to the
new distribution name; installing it does not satisfy `lbry-rocksdb==0.8.2`.


### Install for development / from source
    sudo apt install build-essential binutils
    git clone https://github.com/kodxana/lbry-rocksdb.git
    cd lbry-rocksdb
    git submodule update --init --recursive
    python -m pip install -r docker/test-requirements.txt
    make JOBS=2
    python -m pip install --no-build-isolation -e .
    python -m pytest -v tests

These development requirements select the tested tools for Python 3.9 or 3.13. Use a virtual
environment. For the isolated Linux build used in CI, install Docker and run:

    sh scripts/test.sh
    sh scripts/test.sh 3.13
    sh scripts/test-compatibility.sh

See [the testing guide](docs/testing.md) for the pinned toolchain, collected tests,
cross-version persistence checks, and limits of these test wheels.


### Quick Usage Guide
    >>> import rocksdb
    >>> db = rocksdb.DB("test.db", rocksdb.Options(create_if_missing=True))
    >>> db.put(b'a', b'data')
    >>> print(db.get(b'a'))
    b'data'
