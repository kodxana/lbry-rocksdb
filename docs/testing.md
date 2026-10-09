# Build and test baseline

From a checkout with Docker available:

```sh
git submodule update --init
sh scripts/test.sh
```

On Windows, clone and run these commands with Git in WSL and a Linux Docker
daemon. A Windows Git checkout with `core.autocrlf=true` converts the submodule's
shell scripts to CRLF, which cannot execute in Linux. No database
server or blockchain node is needed; the tests create temporary databases.

The Docker image fixes Python 3.9.23 and GCC 10 through its base-image digest.
`docker/test-requirements.txt` pins CMake, Cython, packaging tools, and pytest.
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

`ci-results/` contains the wheel, test log, JUnit report, and installed package
versions. Set `TEST_OUTPUT_DIR` to choose another destination. A failed test
returns a nonzero exit status after copying its results. The container is removed
when the script exits.

CI currently establishes Linux x86-64 / Python 3.9 behavior. The wheel is a test
artifact, not a manylinux-audited release. macOS, Windows, other architectures,
and newer Python versions need separate build and runtime validation. The old
multi-interpreter wheel scripts remain for reference but are not the baseline
CI path. No package is published by these workflows.

The test image builds with Cython 0.29.37 and disables build isolation to use the
pinned tools. The package's build requirements are unchanged. Other Cython and
Python versions need their own wheel builds and runtime tests.
