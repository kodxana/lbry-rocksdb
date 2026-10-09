#!/bin/sh
set -eu

python -VV
python -m pip freeze > /results/packages.txt
cp /wheels/*.whl /results/
python -c 'import rocksdb; print("Testing installed wheel:", rocksdb.__file__)'
python -m pytest -v --junitxml=/results/tests.xml tests
