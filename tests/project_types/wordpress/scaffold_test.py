"""Exercise the generator/validator contract and secret boundaries without Docker."""
import tempfile
import unittest
import contextlib
import io
import json
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

    def test_cli_creates_validates_and_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'site'
            args = ['create', '--site-name', 'sample', '--domain', 'example.com',
                    '--theme-name', 'sample', '--wordpress-version', '6.8.2',
                    '--target-dir', str(root)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(scaffold.main(args), 0)
                self.assertEqual(scaffold.main(['validate', '--repo', str(root)]), 0)
                self.assertEqual(scaffold.main(['validate', '--repo', str(root), '--require-locks']), 1)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                scaffold.main(args)
            self.assertEqual(error.exception.code, 2)

    def test_validator_reports_broken_source_and_missing_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scaffold.create(root, self.files)
            (root / 'composer.json').write_text('{broken')
            (root / '.env.example').write_text('WP_ENV=development\n')
            (root / 'web/index.php').unlink()
            errors = scaffold.validate_project(root)
            self.assertIn('Invalid JSON: composer.json', errors)
            self.assertIn('Missing: web/index.php', errors)
            self.assertIn('Missing environment key: DB_PASSWORD', errors)

    def test_rejects_invalid_deployment_identifiers(self):
        for settings in [{'domain': 'https://example.com'}, {'php_version': '7.4'},
                         {'database_prefix': 'wp_;DROP'}, {'registry': 'bad registry'}]:
            args = dict(site='sample', domain='example.com', theme='sample', wordpress_version='6.8.2')
            args.update(settings)
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                scaffold.render(**args)
        files = scaffold.render('sample', 'example.com', 'sample', '6.8.2', registry='example.azurecr.io')
        self.assertEqual(json.loads(files['project.json'])['image_name'], 'example.azurecr.io/sample')

    def test_symlink_target_is_rejected_without_touching_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'target'
            target.mkdir()
            link = root / 'link'
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                scaffold.create(link, self.files)
            self.assertEqual(list(target.iterdir()), [])

    def test_unsafe_outputs_are_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            for name in ['../escape', 'nested/../../escape', '/absolute',
                         'C:/escape', 'C:escape', r'..\escape', '.', '']:
                for dry_run in [False, True]:
                    root = parent / 'site'
                    with self.subTest(name=name, dry_run=dry_run), self.assertRaises(ValueError):
                        scaffold.create(root, {'valid.txt': 'safe', name: 'unsafe'}, dry_run)
                    self.assertFalse(root.exists())
                    self.assertFalse((parent / 'escape').exists())

    def test_symlink_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            destination = parent / 'destination'
            destination.mkdir()
            link = parent / 'link'
            link.symlink_to(destination, target_is_directory=True)
            with self.assertRaises(ValueError):
                scaffold.create(link / 'site', self.files)
            self.assertEqual(list(destination.iterdir()), [])

    def test_dns_label_boundaries(self):
        for domain in ['-host.example', 'host-.example', 'a..com', 'a.c',
                       'a' * 64 + '.com', 'a' * 10000, 'münchen.de', 'EXAMPLE.com']:
            with self.subTest(domain=domain[:80]):
                self.assertFalse(scaffold.valid_domain(domain))
        self.assertTrue(scaffold.valid_domain('a' * 63 + '.example'))
        self.assertTrue(scaffold.valid_domain('xn--mnchen-3ya.de'))


if __name__ == '__main__':
    unittest.main()
