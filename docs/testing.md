# Build and test

From a checkout with Docker available:

```sh
git submodule update --init
sh scripts/test.sh
sh scripts/test.sh 3.13
sh scripts/test-compatibility.sh
```

On Windows, clone and run these commands with Git in WSL and a Linux Docker
daemon. A Windows Git checkout with `core.autocrlf=true` converts the submodule's
shell scripts to CRLF, which cannot execute in Linux. No database
server or blockchain node is needed; the tests create temporary databases.

The Dockerfile fixes Python 3.9.23 and 3.13.16 through base-image digests.
Both builds compile the native libraries in the Python 3.9 / GCC 10 stage. The
binding uses GCC 10 on Python 3.9 and GCC 12 on Python 3.13.
`docker/test-requirements.txt` pins CMake, packaging tools, and pytest, with
Cython 0.29.37 on Python 3.9 and Cython 3.1.8 on Python 3.13.
The RocksDB submodule remains at `752fea5d4400198bc8a591b7d795d1c8d5f12230`
(6.25.3). Its compression-library versions and SHA-256 checks are unchanged;
zlib 1.2.12 is fetched from the upstream HTTPS archive. This is a historical
compatibility baseline, not an upgrade of those native libraries.

The build uses two compiler jobs by default (`JOBS=4 sh scripts/test.sh` changes
that limit). RocksDB is built with `PORTABLE=ON` to avoid selecting instructions
from the build machine's CPU. CMake receives absolute paths to the bundled
static libraries rather than directories or system-library search results.

Tests run as an unprivileged user, without network access, in a container limited
to two CPUs and 4 GiB of memory. Those limits apply to the test container; native
compilation runs during the Docker build. Tests have a five-minute process
timeout; CI also has a 45-minute job timeout.
The test runner installs the freshly built wheel and copies only the tests into
a separate working directory. This prevents the checkout from masking missing
files in the installed package. Pytest collects both unittest classes and the
two function-based memtable tests that `unittest discover` misses.

`ci-results/python3.9/` and `ci-results/python3.13/` each contain the wheel, test
log, JUnit report, and installed package versions. Set `TEST_OUTPUT_DIR` when
running `test.sh` to choose another destination for that interpreter. A failed test
returns a nonzero exit status after copying its results. The container is removed
when the script exits.

The persistence fixture writes binary keys and values, empty keys and values,
column families, compressed SST files, WAL entries, and integer merge operands.
It closes and reopens the database, applies a saved serialized write batch, then
checks updates, deletes, iteration order, and merged values.

After both wheel builds, `test-compatibility.sh` uses those exact wheels in fresh,
network-isolated containers. Python 3.9 creates a database, Python 3.13 verifies
and updates it, and Python 3.9 verifies the result. The reverse direction runs as
well. The two directions use separate databases on a temporary Docker volume,
removed on exit. Each step is limited to two CPUs, 2 GiB, and two minutes; CI has
a 15-minute job timeout. For custom artifact locations, set `TEST_OUTPUT_DIR` to
the parent containing `python3.9/` and `python3.13/` when running this script.

CI establishes Linux x86-64 behavior on standard CPython 3.9 and 3.13 builds.
The wheels are test artifacts, not manylinux-audited releases. macOS, Windows,
other architectures, free-threaded Python, and other interpreter versions need
separate build and runtime validation. This does not establish Python 3.13
compatibility for the SDK or Hub and does not change their dependency pins. The old
multi-interpreter wheel scripts remain for reference but are not the baseline
CI path. No package is published by these workflows.

The test images disable build isolation to use the pinned tools. Package build
requirements select Cython 3.1.8 or newer on Python 3.13 and later: C++ generated
by Cython 0.29.37 fails to compile against Python 3.13's changed C API. The older
Python build requirement remains unchanged. CI tests the exact Cython versions
above; it does not validate every version allowed by the package metadata.
