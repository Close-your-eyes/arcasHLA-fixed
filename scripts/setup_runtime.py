#!/usr/bin/env python3
"""Download runtime data or build private Kallisto; no data is bundled.

Added 2026-10-15. GNU GPL version 3 or later; see LICENSE.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
KALLISTO_URL = 'https://codeload.github.com/pachterlab/kallisto/tar.gz/v0.48.0'
KALLISTO_SHA256 = '1797ac4d1f0771e3f1f25dd7972bded735fcb43f853cf52184d3d9353a6269b0'


def download(url, destination, checksum):
    """Replace a file only after verifying its SHA256 checksum."""
    destination = Path(destination)
    if destination.is_file():
        with destination.open('rb') as handle:
            verified = hashlib.file_digest(handle, 'sha256').hexdigest() == checksum
        if verified:
            print('Already verified:', destination.relative_to(ROOT), flush=True)
            return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.download')
    print('Downloading:', url, flush=True)
    try:
        urllib.request.urlretrieve(url, temporary)
        with temporary.open('rb') as handle:
            actual = hashlib.file_digest(handle, 'sha256').hexdigest()
        if actual != checksum:
            raise RuntimeError('SHA256 mismatch for ' + url)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def fetch_support(groups):
    manifest = json.loads((ROOT / 'support-files.json').read_text())
    ref = manifest['upstream_ref']
    for destination, item in manifest['files'].items():
        if item['group'] not in groups:
            continue
        host = 'https://media.githubusercontent.com/media' if item.get('lfs') else 'https://raw.githubusercontent.com'
        url = f"{host}/RabadanLab/arcasHLA/{ref}/{item['path']}"
        download(url, ROOT / destination, item['sha256'])


def run(arguments, **kwargs):
    print('+', ' '.join(str(x) for x in arguments), flush=True)
    return subprocess.run([str(x) for x in arguments], check=True, **kwargs)


def build_kallisto(jobs):
    for executable in ('cmake', 'make', 'autoconf', 'autoheader', 'automake'):
        if not shutil.which(executable):
            raise RuntimeError('Missing build dependency: ' + executable)
    build_root = ROOT / 'build'
    archive = build_root / 'kallisto-0.48.0.tar.gz'
    download(KALLISTO_URL, archive, KALLISTO_SHA256)
    source = build_root / 'kallisto-0.48.0'
    if not source.exists():
        with tarfile.open(archive, 'r:gz') as tar:
            tar.extractall(build_root, filter='data')
    automake = subprocess.check_output(['automake', '--print-libdir'], text=True).strip()
    hts = source / 'ext/htslib'
    for name in ('config.guess', 'config.sub'):
        shutil.copy2(Path(automake) / name, hts / name)
    host = subprocess.check_output(['sh', str(hts / 'config.guess')], text=True).strip()
    cmake_file = source / 'CMakeLists.txt'
    content = cmake_file.read_text()
    original = '--prefix=${PREFIX} --disable-bz2'
    if original in content:
        content = content.replace(original, '--prefix=${PREFIX} --host=' + host + ' --disable-bz2')
    cmake_file.write_text(content)
    source_cmake = source / 'src/CMakeLists.txt'
    content = source_cmake.read_text()
    if 'add_dependencies(kallisto htslib)' not in content:
        content += '\nadd_dependencies(kallisto htslib)\n'
    source_cmake.write_text(content)
    prefix = os.environ.get('CONDA_PREFIX', sys.prefix)
    build = build_root / 'kallisto-build'
    command = ['cmake', '-S', source, '-B', build, '-DUSE_HDF5=ON',
               '-DCMAKE_POLICY_VERSION_MINIMUM=3.5', '-DCMAKE_POLICY_DEFAULT_CMP0074=NEW',
               '-DCMAKE_PREFIX_PATH=' + prefix, '-DHDF5_ROOT=' + prefix,
               '-DZLIB_ROOT=' + prefix]
    if platform.system() == 'Darwin':
        command += ['-DCMAKE_OSX_ARCHITECTURES=' + platform.machine()]
    run(command)
    # Build HTSlib first because this old release references its archive by path.
    run(['cmake', '--build', build, '--target', 'htslib', '--parallel', jobs])
    run(['cmake', '--build', build, '--parallel', jobs])
    destination = ROOT / 'bin/kallisto'
    destination.parent.mkdir(exist_ok=True)
    shutil.copy2(build / 'src/kallisto', destination)
    notices = ROOT / 'bin/licenses'
    notices.mkdir(exist_ok=True)
    shutil.copy2(source / 'license.txt', notices / 'KALLISTO.txt')
    shutil.copy2(hts / 'LICENSE', notices / 'HTSLIB.txt')
    run([destination, 'version'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', action='store_true', help='download typing frequency table')
    parser.add_argument('--test-data', action='store_true', help='download upstream test fixtures')
    parser.add_argument('--quant-data', action='store_true', help='download optional quantification support data')
    parser.add_argument('--build-kallisto', action='store_true', help='build private native Kallisto 0.48.0')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be positive')
    if not any((args.data, args.test_data, args.quant_data, args.build_kallisto)):
        parser.print_help()
        return
    groups = {name for enabled, name in [(args.data, 'typing'), (args.test_data, 'test'), (args.quant_data, 'quant')] if enabled}
    if groups:
        fetch_support(groups)
    if args.build_kallisto:
        build_kallisto(args.jobs)


if __name__ == '__main__':
    main()
