"""Regression checks for compatibility fixes.

Added 2026-10-15. GNU GPL version 3 or later; see LICENSE.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import reference
import arcas_utilities
import setup_runtime


class ReferenceTests(unittest.TestCase):
    def test_mode_scalar_and_tie_behavior(self):
        self.assertEqual(reference.get_mode([3, 3, 4]), 3)
        self.assertEqual(reference.get_mode([4, 3]), 3)
        self.assertIsInstance(reference.get_mode([3]), int)

    def test_current_zip_materialization(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            with zipfile.ZipFile(folder / 'hla.dat.zip', 'w') as archive:
                archive.writestr('release/hla.dat', b'ID   sequence\n//\n')
            with mock.patch.object(reference, 'IMGTHLA', temp + '/'), mock.patch.object(reference, 'hla_dat', str(folder / 'hla.dat')):
                reference.materialize_hla_dat()
            self.assertEqual((folder / 'hla.dat').read_bytes(), b'ID   sequence\n//\n')
            self.assertFalse((folder / 'hla.dat.tmp').exists())

    def test_ambiguous_zip_does_not_overwrite_data(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'hla.dat').write_bytes(b'original')
            with zipfile.ZipFile(folder / 'hla.dat.zip', 'w') as archive:
                archive.writestr('one/hla.dat', b'first')
                archive.writestr('two/hla.dat', b'second')
            with mock.patch.object(reference, 'IMGTHLA', temp + '/'), mock.patch.object(reference, 'hla_dat', str(folder / 'hla.dat')):
                with self.assertRaises(RuntimeError):
                    reference.materialize_hla_dat()
            self.assertEqual((folder / 'hla.dat').read_bytes(), b'original')

    def test_missing_index_triggers_rebuild_even_with_sequence_data(self):
        with mock.patch.object(reference, 'isdir', return_value=True), mock.patch.object(reference, 'isfile', side_effect=lambda path: path == reference.hla_dat), mock.patch.object(reference, 'build_convert') as convert, mock.patch.object(reference, 'build_fasta') as build:
            reference.check_ref()
        convert.assert_called_once_with(False)
        build.assert_called_once_with()

    def test_existing_index_from_different_commit_triggers_rebuild(self):
        with tempfile.TemporaryDirectory() as temp:
            info = Path(temp) / 'hla.p.json'
            info.write_text(json.dumps(['old-reference', []]))
            with mock.patch.object(reference, 'hla_json', str(info)), mock.patch.object(reference, 'isdir', return_value=True), mock.patch.object(reference, 'isfile', return_value=True), mock.patch.object(reference.os.path, 'getsize', return_value=100), mock.patch.object(reference, 'hla_dat_version', return_value='new-reference'), mock.patch.object(reference, 'build_convert'), mock.patch.object(reference, 'build_fasta') as build:
                reference.check_ref()
            build.assert_called_once_with()

    def test_failed_checkout_restores_generated_sequence_file(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'hla.dat').write_bytes(b'original')
            (folder / 'hla.dat.zip').touch()
            with mock.patch.object(reference, 'IMGTHLA', temp + '/'), mock.patch.object(reference, 'hla_dat', str(folder / 'hla.dat')), mock.patch.object(reference, 'isdir', return_value=True), mock.patch.object(reference, 'run_command', side_effect=[None, RuntimeError('checkout failed')]):
                with self.assertRaisesRegex(RuntimeError, 'checkout failed'):
                    reference.checkout_version('some-version')
            self.assertEqual((folder / 'hla.dat').read_bytes(), b'original')
            self.assertFalse((folder / 'hla.dat.previous').exists())


class RuntimeTests(unittest.TestCase):
    def test_external_failure_is_reported(self):
        result = subprocess.CompletedProcess('example', 7, b'', b'dependency failed')
        with mock.patch.object(arcas_utilities, 'run', return_value=result):
            with self.assertRaisesRegex(RuntimeError, 'dependency failed'):
                arcas_utilities.run_command(['example'])

    def test_bad_download_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / 'support.tsv'
            destination.write_bytes(b'old file')
            def fake_download(url, path):
                Path(path).write_bytes(b'incorrect content')
            with mock.patch.object(setup_runtime.urllib.request, 'urlretrieve', side_effect=fake_download):
                with self.assertRaisesRegex(RuntimeError, 'SHA256 mismatch'):
                    setup_runtime.download('https://example.invalid/support', destination, hashlib.sha256(b'expected').hexdigest())
            self.assertEqual(destination.read_bytes(), b'old file')
            self.assertFalse(destination.with_name('support.tsv.download').exists())

    def test_launcher_preserves_arguments_and_uses_python_override(self):
        with tempfile.TemporaryDirectory() as temp:
            fake_python = Path(temp) / 'fake-python'
            fake_python.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
            fake_python.chmod(0o755)
            env = dict(os.environ, ARCASHLA_PYTHON=str(fake_python))
            result = subprocess.run([str(ROOT / 'arcasHLA'), 'genotype', '--help', 'input with spaces'], env=env, capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.splitlines(), [str(ROOT / 'scripts/genotype.py'), '--help', 'input with spaces'])

    def test_launcher_rejects_incompatible_kallisto(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'arcasHLA').write_bytes((ROOT / 'arcasHLA').read_bytes())
            (folder / 'arcasHLA').chmod(0o755)
            (folder / 'bin').mkdir()
            kallisto = folder / 'bin/kallisto'
            kallisto.write_text('#!/bin/sh\necho "kallisto, version 0.52.0"\n')
            kallisto.chmod(0o755)
            result = subprocess.run([str(folder / 'arcasHLA'), 'genotype', 'sample.fq.gz'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('setup_runtime.py --build-kallisto', result.stderr)


if __name__ == '__main__':
    unittest.main()
