"""Run native cleanup cases in a child process so a crash cannot kill pytest."""

import gc
import os
import sys
import tempfile
import weakref

import rocksdb


def assert_closed(operation, message):
    try:
        operation()
    except ValueError as error:
        assert str(error) == message, str(error)
    else:
        raise AssertionError('operation on a closed resource succeeded')


def live_iterator(path, mode, kind):
    options = rocksdb.Options(create_if_missing=True, max_open_files=32)
    primary = rocksdb.DB(path, options)
    family_options = rocksdb.ColumnFamilyOptions()
    family = primary.create_column_family(b'claims', family_options)
    for key, value in ((b'a', b'one'), (b'b', b'two')):
        primary.put(key, value, sync=True)
        primary.put((family, key), value, sync=True)

    database = primary
    if mode != 'primary':
        primary.close()
        if mode == 'secondary':
            options.max_open_files = -1
        database = rocksdb.DB(
            path, options, column_families={b'claims': family_options},
            read_only=mode == 'read-only',
            secondary_name=path + '-secondary' if mode == 'secondary' else ''
        )
        family = database.get_column_family(b'claims')

    if kind == 'bounded':
        iterator = database.iterator(start=b'a', iterate_upper_bound=b'c', column_family=family)
    elif kind.startswith('multi-'):
        iterator = getattr(database, kind[6:])([family])[0]
    else:
        iterator = getattr(database, kind.removeprefix('reverse-'))(family)
    iterator.seek_to_first()
    if kind.startswith('reverse-'):
        iterator = reversed(iterator)
    assert iterator.get() is not None
    database.close()
    database.close()  # Explicit close remains idempotent.
    assert not family.is_valid

    for operation in (
        lambda: next(iterator), iterator.get, iterator.seek_to_first,
        iterator.seek_to_last, lambda: iterator.seek(b'a'),
        lambda: iterator.seek_for_prev(b'b'),
    ):
        assert_closed(operation, 'Iterator is closed')

    # The old wrapper may remain alive while a new DB opens the same files.
    reopened = rocksdb.DB(path, options, column_families={b'claims': family_options})
    assert reopened.get(b'a') == b'one'
    assert reopened.get((reopened.get_column_family(b'claims'), b'b')) == b'two'
    del iterator
    gc.collect()
    reopened.close()


def live_snapshot(path):
    database = rocksdb.DB(path, rocksdb.Options(create_if_missing=True))
    database.put(b'key', b'old', sync=True)
    snapshot = database.snapshot()
    database.put(b'key', b'new', sync=True)
    assert database.get(b'key', snapshot=snapshot) == b'old'
    iterator = database.iteritems(snapshot=snapshot)
    iterator.seek_to_first()
    assert iterator.get() == (b'key', b'old')
    database.close()

    reopened = rocksdb.DB(path, rocksdb.Options())
    assert reopened.get(b'key') == b'new'
    assert_closed(lambda: reopened.get(b'key', snapshot=snapshot), 'Snapshot is closed')
    assert_closed(lambda: iterator.get(), 'Iterator is closed')
    del snapshot, iterator
    gc.collect()
    reopened.close()


def retained_traceback(path):
    database = rocksdb.DB(path, rocksdb.Options(create_if_missing=True))
    database.put(b'key', b'value')

    def decode():
        iterator = database.iteritems()
        iterator.seek_to_first()
        for _ in iterator:
            raise ValueError('invalid record')

    retained_error = None
    try:
        decode()
    except ValueError as error:
        retained_error = error
    assert retained_error is not None
    database.close()
    del retained_error
    gc.collect()


def closed_operations(path, method):
    database = rocksdb.DB(path, rocksdb.Options(create_if_missing=True))
    family = database.get_column_family(b'default')
    batch_context = database.write_batch()
    batch_context.__enter__().put(b'key', b'value')
    backup = rocksdb.BackupEngine(path + '-backup')
    operations = {
        'get': lambda: database.get(b'key'),
        'put': lambda: database.put(b'key', b'value'),
        'delete': lambda: database.delete(b'key'),
        'merge': lambda: database.merge(b'key', b'value'),
        'write': lambda: database.write(rocksdb.WriteBatch()),
        'multi_get': lambda: database.multi_get([b'key']),
        'key_may_exist': lambda: database.key_may_exist(b'key'),
        'iterkeys': database.iterkeys,
        'itervalues': database.itervalues,
        'iteritems': database.iteritems,
        'iterskeys': lambda: database.iterskeys([family]),
        'itersvalues': lambda: database.itersvalues([family]),
        'iterator': lambda: database.iterator(start=b'key'),
        'snapshot': database.snapshot,
        'get_property': lambda: database.get_property(b'rocksdb.estimate-num-keys'),
        'get_live_files_metadata': database.get_live_files_metadata,
        'get_column_family_meta_data': database.get_column_family_meta_data,
        'compact_range': database.compact_range,
        'create_column_family': lambda: database.create_column_family(b'new', rocksdb.ColumnFamilyOptions()),
        'drop_column_family': lambda: database.drop_column_family(family),
        'try_catch_up_with_primary': database.try_catch_up_with_primary,
        'write_batch': database.write_batch,
        'pending_batch': lambda: batch_context.__exit__(None, None, None),
        'backup': lambda: backup.create_backup(database),
    }
    database.close()
    assert_closed(operations[method], 'Database is closed')


def automatic_cleanup(path):
    options = rocksdb.Options(create_if_missing=True)
    database = rocksdb.DB(path, options)
    database.put(b'key', b'value', sync=True)
    iterator = database.iteritems()
    snapshot = database.snapshot()
    del database
    gc.collect()
    iterator.seek_to_first()
    assert iterator.get() == (b'key', b'value')
    del snapshot, iterator
    gc.collect()
    reopened = rocksdb.DB(path, options)
    assert reopened.get(b'key') == b'value'
    reopened.close()


def foreign_snapshot(path):
    first = rocksdb.DB(path, rocksdb.Options(create_if_missing=True))
    second = rocksdb.DB(path + '-other', rocksdb.Options(create_if_missing=True))
    snapshot = first.snapshot()
    assert_closed(lambda: second.get(b'key', snapshot=snapshot), 'Snapshot belongs to another database')
    second.close()
    first.close()


def cyclic_cleanup(path):
    class Comparator(rocksdb.interfaces.Comparator):
        def name(self):
            return b'cleanup-test-comparator'

        def compare(self, left, right):
            return (left > right) - (left < right)

    options = rocksdb.Options(create_if_missing=True)
    comparator = Comparator()
    options.comparator = comparator
    database = rocksdb.DB(path, options)
    database.put(b'key', b'value', sync=True)
    # DB -> options -> callback -> readers -> DB must be collectible, and the
    # readers' native cleanup must finish before the DB is destroyed.
    comparator.iterator = database.iteritems()
    comparator.snapshot = database.snapshot()
    callback_ref = weakref.ref(comparator)
    del comparator, database, options
    gc.collect()
    assert callback_ref() is None
    reopened_options = rocksdb.Options()
    reopened_options.comparator = Comparator()
    reopened = rocksdb.DB(path, reopened_options)
    assert reopened.get(b'key') == b'value'
    reopened.close()


if __name__ == '__main__':
    cases = {
        'iterator': live_iterator, 'snapshot': live_snapshot,
        'traceback': retained_traceback, 'closed': closed_operations,
        'automatic': automatic_cleanup, 'foreign-snapshot': foreign_snapshot,
        'cyclic': cyclic_cleanup,
    }
    with tempfile.TemporaryDirectory() as directory:
        cases[sys.argv[1]](os.path.join(directory, 'db'), *sys.argv[2:])
    print('cleanup complete', flush=True)
