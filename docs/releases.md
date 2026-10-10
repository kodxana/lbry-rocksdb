# Releasing lbry-rocksdb-ng

The first maintained distribution is `lbry-rocksdb-ng` 0.8.3. It retains the
`rocksdb` import and RocksDB 6.25.3 engine, with the merged database-close,
iterator and snapshot fixes. This release does not upgrade the engine or its
compression libraries. It does not make concurrent database close and use safe.

## Supported wheels

| Python | Architecture | Wheel platform |
| --- | --- | --- |
| CPython 3.9 | Linux x86-64 | manylinux_2_31 |
| CPython 3.13 | Linux x86-64 | manylinux_2_35 |

These tags describe the audited system-library requirements, including glibc
and libstdc++. They do not cover Alpine/musl, ARM, Windows, macOS, free-threaded
Python, or other Python versions. Python 3.13 binding support does not establish
Python 3.13 support for Hub or the SDK. The runtime tests use Debian Bullseye
and Bookworm respectively, not every distribution accepted by the tags.

CI installs and tests the repaired wheels offline, then checks persistence in
both directions between Python versions. Only after those checks pass does it
produce `release-wheels`, containing the two wheels, `SHA256SUMS`, release notes,
and `release.json` with the wrapper and native source commits. Per-interpreter
artifacts retain the audit output, test reports and build-tool versions.
CI artifacts are retained for 14 days; release assets provide lasting downloads.
No source distribution is uploaded: the current source build requires a
submodule checkout and prebuilt native libraries.

## Release procedure

1. Review and merge the release PR, including the version and
   `docs/release-notes.md`.
2. Tag that merged commit `v0.8.3` and push the tag. Do not move an existing
   release tag or reuse a published version.
3. The release workflow checks that the commit belongs to `master`, rebuilds
   and tests both wheels, checks persistence, and requires the tag to match
   the package version. It creates a **draft** GitHub release containing the
   tested wheels, checksums and source manifest. Only this final job has
   permission to write releases; it does not rebuild the wheels.
4. Review the run's test artifacts and the draft's assets, then publish the
   draft from GitHub. Verify the public download links and their SHA-256 hashes
   before using them in downstream dependency pins.

Normal builds and pull requests never create releases. A release job will fail
if that tag already has a release, rather than replace its assets. If an upload
fails partway through, inspect and remove only the incomplete draft before
retrying; never delete or overwrite a published release to retry a build.

## Installing a released wheel

Use a fresh environment. On the GitHub release page, download the wheels into
a `wheels/` directory and `SHA256SUMS` into its parent. From that parent, run:

```sh
sha256sum --check SHA256SUMS
```

For Linux x86-64 with Python 3.9:

```sh
python -m pip install --no-index ./wheels/lbry_rocksdb_ng-0.8.3-cp39-cp39-manylinux_2_31_x86_64.whl
```

Python 3.13 uses the `cp313-cp313-manylinux_2_35_x86_64` wheel instead.

Hub and SDK dependency updates follow publication, in separate tested PRs.
Hub can reference the versioned GitHub wheel URL with its SHA-256 hash. Replace
the old distribution requirement rather than installing both: `lbry-rocksdb`
and `lbry-rocksdb-ng` own the same `rocksdb` module. Existing environments should
be recreated to avoid overlapping package files. Until those downstream
updates land, normal Hub installs still use the old binding.

## Future PyPI publishing

The old `lbry-rocksdb` PyPI project belongs to LBRY Inc. GitHub releases require
no access to it. Publishing `lbry-rocksdb-ng` on PyPI later will require a new
project under a maintainer's account and a reviewed publishing workflow.
There is no PyPI upload or API token in the current release process.
