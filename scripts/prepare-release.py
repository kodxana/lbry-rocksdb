"""Collect the tested wheels with checksums and their source revisions."""
import email
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def main():
    os.chdir(Path(__file__).resolve().parent.parent)
    version = re.search(r'^__version__ = "([^"]+)"',
                        Path('rocksdb/__init__.py').read_text(), re.MULTILINE).group(1)
    if os.environ.get('GITHUB_REF_TYPE') == 'tag':
        if os.environ['GITHUB_REF_NAME'] != 'v' + version:
            raise ValueError('Release tag does not match the package version')

    wheels = []
    for python, abi, platform in (
        ('3.9', 'cp39', 'manylinux_2_31_x86_64'),
        ('3.13', 'cp313', 'manylinux_2_35_x86_64'),
    ):
        directory = Path('ci-results') / ('python' + python)
        expected = directory / f'lbry_rocksdb_ng-{version}-{abi}-{abi}-{platform}.whl'
        if list(directory.glob('*.whl')) != [expected]:
            raise ValueError(f'Expected exactly one wheel: {expected}')
        with zipfile.ZipFile(expected) as archive:
            prefix = f'lbry_rocksdb_ng-{version}.dist-info/'
            metadata = email.message_from_bytes(archive.read(prefix + 'METADATA'))
            tags = email.message_from_bytes(archive.read(prefix + 'WHEEL')).get_all('Tag')
            if metadata['Name'] != 'lbry-rocksdb-ng' or metadata['Version'] != version:
                raise ValueError(f'Unexpected package metadata: {expected}')
            if tags != [f'{abi}-{abi}-{platform}']:
                raise ValueError(f'Unexpected wheel tags: {expected}')
        wheels.append(expected)

    # Refuse to mix this run with stale release files.
    output = Path('dist')
    output.mkdir(exist_ok=False)
    (output / 'wheels').mkdir()
    checksums = []
    for wheel in wheels:
        target = output / 'wheels' / wheel.name
        shutil.copyfile(wheel, target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        checksums.append(f'{digest}  wheels/{wheel.name}\n')
    (output / 'SHA256SUMS').write_text(''.join(checksums))
    shutil.copyfile('docs/release-notes.md', output / 'RELEASE_NOTES.md')
    (output / 'release.json').write_text(json.dumps({
        'name': 'lbry-rocksdb-ng',
        'version': version,
        'commit': git('rev-parse', 'HEAD'),
        'rocksdb_commit': git('rev-parse', 'HEAD:src/rocksdb'),
        'workflow_run': os.environ.get('GITHUB_RUN_ID'),
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
