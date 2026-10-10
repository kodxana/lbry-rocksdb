import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


spec = importlib.util.spec_from_file_location(
    'prepare_release', Path(__file__).resolve().parents[1] / 'prepare-release.py'
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseBundleTest(unittest.TestCase):
    def setUp(self):
        original_directory = Path.cwd()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.addCleanup(os.chdir, original_directory)
        self.root = Path(temporary.name)
        (self.root / 'rocksdb').mkdir()
        (self.root / 'rocksdb/__init__.py').write_text('__version__ = "0.8.3"\n')
        (self.root / 'docs').mkdir()
        (self.root / 'docs/release-notes.md').write_text('Release notes\n')
        self.wheels = []
        for python, abi, platform in (
            ('3.9', 'cp39', 'manylinux_2_31_x86_64'),
            ('3.13', 'cp313', 'manylinux_2_35_x86_64'),
        ):
            directory = self.root / 'ci-results' / ('python' + python)
            directory.mkdir(parents=True)
            wheel = directory / f'lbry_rocksdb_ng-0.8.3-{abi}-{abi}-{platform}.whl'
            with zipfile.ZipFile(wheel, 'w') as archive:
                prefix = 'lbry_rocksdb_ng-0.8.3.dist-info/'
                archive.writestr(prefix + 'METADATA', 'Name: lbry-rocksdb-ng\nVersion: 0.8.3\n')
                archive.writestr(prefix + 'WHEEL', f'Tag: {abi}-{abi}-{platform}\n')
            self.wheels.append(wheel)
        for mock in (
            patch.object(release, '__file__', str(self.root / 'scripts/prepare-release.py')),
            patch.object(release, 'git', side_effect=['wrapper-sha', 'native-sha']),
            patch.dict(os.environ, {'GITHUB_REF_TYPE': 'tag', 'GITHUB_REF_NAME': 'v0.8.3'}),
        ):
            mock.start()
            self.addCleanup(mock.stop)

    def test_bundle_keeps_tested_bytes_and_records_sources(self):
        release.main()
        output = self.root / 'dist'
        for wheel in self.wheels:
            self.assertEqual(wheel.read_bytes(), (output / 'wheels' / wheel.name).read_bytes())
            self.assertIn(hashlib.sha256(wheel.read_bytes()).hexdigest(),
                          (output / 'SHA256SUMS').read_text())
        manifest = json.loads((output / 'release.json').read_text())
        self.assertEqual(manifest['commit'], 'wrapper-sha')
        self.assertEqual(manifest['rocksdb_commit'], 'native-sha')

    def test_wrong_tag_cannot_create_bundle(self):
        os.environ['GITHUB_REF_NAME'] = 'v0.8.2'
        with self.assertRaisesRegex(ValueError, 'tag does not match'):
            release.main()
        self.assertFalse((self.root / 'dist').exists())

    def test_missing_or_extra_wheel_cannot_create_bundle(self):
        extra = self.wheels[0].with_name('stale.whl')
        extra.touch()
        with self.assertRaisesRegex(ValueError, 'exactly one wheel'):
            release.main()
        extra.unlink()
        self.wheels[1].unlink()
        with self.assertRaisesRegex(ValueError, 'exactly one wheel'):
            release.main()
        self.assertFalse((self.root / 'dist').exists())

    def test_renamed_old_wheel_cannot_create_bundle(self):
        with zipfile.ZipFile(self.wheels[0], 'w') as archive:
            prefix = 'lbry_rocksdb_ng-0.8.3.dist-info/'
            archive.writestr(prefix + 'METADATA', 'Name: lbry-rocksdb\nVersion: 0.8.2\n')
            archive.writestr(prefix + 'WHEEL', 'Tag: cp39-cp39-linux_x86_64\n')
        with self.assertRaisesRegex(ValueError, 'package metadata'):
            release.main()
        self.assertFalse((self.root / 'dist').exists())

    def test_existing_bundle_is_not_overwritten(self):
        release.main()
        with self.assertRaises(FileExistsError):
            release.main()
