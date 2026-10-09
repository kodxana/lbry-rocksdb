from pathlib import Path
import tempfile
import unittest

from tests.persistence import create, update, verify


class TestPersistence(unittest.TestCase):
    def test_reopen_and_apply_serialized_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'database'
            create(path)
            update(path)
            verify(path, updated=True)
