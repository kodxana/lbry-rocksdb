#!/bin/sh
set -eu

python -VV
python -m pip freeze --all > /results/packages.txt
cp /wheels/*.whl /results/
cp /wheel-audit.txt /results/
python -c 'import rocksdb; print("Testing installed wheel:", rocksdb.__file__)'
python -m pytest -v --junitxml=/results/tests.xml tests
