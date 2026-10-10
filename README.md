# lbry-rocksdb-ng

A community-maintained fork of [lbry-rocksdb](https://github.com/lbryio/lbry-rocksdb), originally maintained by LBRY Inc. This project is maintained independently of LBRY Inc.; its changes and releases are community work, not official LBRY Inc. releases. Credit and license notices for the original authors are preserved.

The repository and distribution name are `lbry-rocksdb-ng`; the Python import remains `rocksdb`. The native engine remains RocksDB 6.25.3.

### Origins

This binding descends from `python-rocksdb` and `pyrocksdb`, including [updates and improvements](https://github.com/iFA88/python-rocksdb) from @iFA88 and @mosquito and the LBRY Inc. fork.


### Install a release

Version 0.8.3 is available from [GitHub Releases](https://github.com/kodxana/lbry-rocksdb-ng/releases/tag/v0.8.3).
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
    git clone https://github.com/kodxana/lbry-rocksdb-ng.git
    cd lbry-rocksdb-ng
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

### Contributing and contact

Report bugs and propose focused changes in [this repository](https://github.com/kodxana/lbry-rocksdb-ng/issues). Include a reproducer and the relevant [test results](docs/testing.md).
The fork is maintained by [@kodxana](https://github.com/kodxana) and community contributors. For suspected vulnerabilities, arrange private disclosure before sharing details; LBRY Inc. email addresses are not support contacts for this fork.

Related community projects: [LBRY SDK NG](https://github.com/kodxana/lbry-sdk-ng) and [LBRY Hub NG](https://github.com/kodxana/lbry-hub-ng).

### License

The Python binding retains its [BSD license](LICENSE.md). Bundled native libraries retain their own licenses, included with the wheels.
