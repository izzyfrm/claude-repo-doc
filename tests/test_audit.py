import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'plugins' / 'repo-doctor' / 'scripts' / 'repo_audit.py'
spec = importlib.util.spec_from_file_location('repo_audit', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuditTests(unittest.TestCase):
    def test_empty_project_advice(self):
        with tempfile.TemporaryDirectory() as tmp:
            codes = {f['code'] for f in module.audit(Path(tmp))['issues']}
            self.assertIn('NO_README', codes)
            self.assertIn('NO_LICENSE', codes)

    def test_broken_json_python_and_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'broken.json').write_text('{oops}', encoding='utf-8')
            (root / 'broken.py').write_text('def foo(:\n pass', encoding='utf-8')
            (root / 'a.txt').write_text('<<<<<<< HEAD\nhello\n=======\nbye\n>>>>>>> branch\n', encoding='utf-8')
            codes = [f['code'] for f in module.audit(root)['issues']]
            self.assertIn('INVALID_JSON', codes)
            self.assertIn('PYTHON_SYNTAX', codes)
            self.assertIn('MERGE_MARKER', codes)

    def test_does_not_read_nested_dependencies_or_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'bad.json').write_text('{bad}', encoding='utf-8')
            (root / 'good.json').write_text('{"a": 1}', encoding='utf-8')
            codes = [f['code'] for f in module.audit(root)['issues']]
            self.assertNotIn('INVALID_JSON', codes)
            self.assertEqual(module.audit(root)['files_examined'], 1)

    def test_env_file_warning_without_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.env').write_text('TOP_SECRET=superprivateexample', encoding='utf-8')
            result = module.audit(root)
            self.assertIn('ENV_FILE', [f['code'] for f in result['issues']])
            self.assertNotIn('superprivateexample', json.dumps(result))

    def test_json_cli_and_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'good.json').write_text('{"ok":true}', encoding='utf-8')
            proc = subprocess.run([sys.executable, str(SCRIPT), tmp, '--json'], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(json.loads(proc.stdout)['files_examined'], 1)
            (Path(tmp) / 'bad.json').write_text('{wrong', encoding='utf-8')
            proc = subprocess.run([sys.executable, str(SCRIPT), tmp, '--json'], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)


if __name__ == '__main__':
    unittest.main()
