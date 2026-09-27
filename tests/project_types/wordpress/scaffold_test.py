"""Exercise the generator/validator contract and secret boundaries without Docker."""
import tempfile
import unittest
from pathlib import Path
from devops_toolset.project_types.wordpress import scaffold


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.files = scaffold.render('example-site', 'example.com', 'example', '6.8.2')

    def test_new_site_passes_validation_before_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold.create(root, self.files)
            self.assertEqual(scaffold.validate_project(root), [])
            self.assertEqual(len(scaffold.validate_project(root, require_locks=True)), 2)

    def test_nonempty_target_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'existing.txt').write_text('keep')
            with self.assertRaises(ValueError):
                scaffold.create(root, self.files)
            self.assertEqual((root / 'existing.txt').read_text(), 'keep')

    def test_preview_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'site'
            self.assertTrue(scaffold.create(root, self.files, dry_run=True))
            self.assertFalse(root.exists())

    def test_build_excludes_runtime_data(self):
        exclusions = self.files['.dockerignore'].splitlines()
        for value in ['.env', '.env.*', 'auth.json', 'web/app/uploads', '**/*.sql', '.git']:
            self.assertIn(value, exclusions)
        self.assertNotIn('.env', self.files)
        self.assertIn('USER www-data', self.files['Dockerfile'])
        self.assertIn('HEALTHCHECK', self.files['Dockerfile'])

    def test_bedrock_core_and_locks_have_single_owners(self):
        import json
        composer = json.loads(self.files['composer.json'])
        self.assertNotIn('roots/bedrock', composer['require'])
        self.assertEqual(composer['extra']['wordpress-install-dir'], 'web/wp')
        self.assertIn("'DISABLE_WP_CRON', true", self.files['config/application.php'])
        source = self.files['tools/project.py']
        compile(source, 'tools/project.py', 'exec')
        self.assertIn("'install', '--package-lock-only'", source)

    def test_rejects_injection_and_mutable_wordpress_versions(self):
        for version in ['latest', '^6.8', '6.8\nRUN echo fail']:
            with self.assertRaises(ValueError):
                scaffold.render('example', 'example.com', 'theme', version)
        with self.assertRaises(ValueError):
            scaffold.render('../escape', 'example.com', 'theme', '6.8.2')


if __name__ == '__main__':
    unittest.main()
