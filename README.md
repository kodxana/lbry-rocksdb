## lbry-rocksdb

### Note
The `python-rocksdb` and `pyrocksdb` packages haven't been updated in a long time - this repo is a fork of python-rocksdb with many of the PRs to it merged, and with [bunch of updates and improvements](https://github.com/iFA88/python-rocksdb) from @iFA88 and @mosquito.


### Install from pip
    pip install lbry-rocksdb


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
