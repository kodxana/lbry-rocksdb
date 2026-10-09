from pathlib import Path
import subprocess
import sys

import pytest


def run_case(*args):
    result = subprocess.run(
        [sys.executable, '-I', '-X', 'faulthandler',
         str(Path(__file__).with_name('close_database.py')), *args],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Exception ignored' not in result.stderr, result.stderr
    assert 'cleanup complete' in result.stdout


@pytest.mark.parametrize('mode', ('primary', 'read-only', 'secondary'))
@pytest.mark.parametrize('kind', (
    'iterkeys', 'itervalues', 'iteritems', 'reverse-iteritems',
    'multi-iterskeys', 'multi-itersvalues', 'bounded',
))
def test_close_with_live_iterator(mode, kind):
    run_case('iterator', mode, kind)


def test_close_with_live_snapshot():
    run_case('snapshot')


def test_close_with_retained_traceback():
    run_case('traceback')


@pytest.mark.parametrize('method', (
    'get', 'put', 'delete', 'merge', 'write', 'multi_get', 'key_may_exist',
    'iterkeys', 'itervalues', 'iteritems', 'iterskeys', 'itersvalues', 'iterator',
    'snapshot', 'get_property', 'get_live_files_metadata', 'get_column_family_meta_data',
    'compact_range', 'create_column_family', 'drop_column_family', 'try_catch_up_with_primary',
    'write_batch', 'pending_batch', 'backup',
))
def test_operations_after_close(method):
    run_case('closed', method)


def test_resources_keep_database_alive():
    run_case('automatic')


def test_snapshot_must_belong_to_database():
    run_case('foreign-snapshot')


def test_callback_cycle_is_collected():
    run_case('cyclic')
