First release of the maintained `lbry-rocksdb-ng` distribution, based on
`lbry-rocksdb` 0.8.2. Python code continues to use `import rocksdb`.

Database close now releases live iterators and snapshots before deleting the
native database. Operations on closed resources raise Python errors, and
foreign or closed snapshots are rejected. Callers must still synchronize close
with concurrent database operations.

The native engine remains RocksDB 6.25.3, with the existing compression-library
versions. Persistence tests cover reopening data and applying serialized write
batches in both directions between Python 3.9 and 3.13. This does not establish
support for newer Python versions in Hub or the SDK.

Available wheels:

- Standard CPython 3.9, Linux x86-64, `manylinux_2_31`.
- Standard CPython 3.13, Linux x86-64, `manylinux_2_35`.

Other operating systems, architectures, Python versions and free-threaded builds
are not covered by this release. The native libraries have not been modernized
in this release.

Use a fresh virtual environment. Do not install this alongside `lbry-rocksdb`
or `python-rocksdb`; they own the same module files. Download the wheels into
`wheels/` and `SHA256SUMS` into its parent, verify with
`sha256sum --check SHA256SUMS`, then install the wheel matching your interpreter.
`release.json` records the exact wrapper and native source commits.

Hub dependency updates are separate. Existing Hub requirements still select
the old `lbry-rocksdb` distribution until those updates are merged.
