from importlib.metadata import PackageNotFoundError, distribution

import pytest
import rocksdb


def test_installed_distribution():
    package = distribution('lbry-rocksdb-ng')
    assert package.version == rocksdb.__version__ == '0.8.3'
    assert rocksdb.ROCKSDB_VERSION == '6.25.3'
    with pytest.raises(PackageNotFoundError):
        distribution('lbry-rocksdb')


def test_bundled_licenses():
    package = distribution('lbry-rocksdb-ng')
    for name in (
        'LICENSE.md',
        'src/rocksdb/LICENSE.Apache',
        'src/rocksdb/LICENSE.leveldb',
        'src/rocksdb/bzip2-1.0.8/LICENSE',
        'src/rocksdb/lz4-1.9.3/lib/LICENSE',
        'src/rocksdb/snappy-1.1.8/COPYING',
        'src/rocksdb/zlib-1.2.12/README',
        'src/rocksdb/zstd-1.4.9/LICENSE',
    ):
        matches = [path for path in package.files if str(path).endswith('/licenses/' + name)]
        assert len(matches) == 1, name
        assert package.locate_file(matches[0]).stat().st_size > 0
