"""Generate and validate a Bedrock/Composer/Vite site without cloud mutations.

Run ``python -m devops_toolset.project_types.wordpress.scaffold --help``.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from devops_toolset.project_types.wordpress import bedrock_templates as templates

SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
VERSION = re.compile(r'\d+\.\d+(?:\.\d+)?')
REQUIRED = ('config/application.php', 'web/index.php', 'web/wp-config.php',
            'docker/site.conf', 'tools/project.py', 'composer.json', 'package.json',
            'vite.config.js', 'Dockerfile', 'compose.yaml', '.env.example',
            '.dockerignore', 'wp-cli.yml', 'project.json', 'web/healthz.php',
            '.github/workflows/validate.yml')
ENV_KEYS = {'WP_ENV', 'WP_HOME', 'WP_SITEURL', 'DB_HOST', 'DB_NAME',
            'DB_USER', 'DB_PASSWORD', 'DB_PREFIX'}


def render(site: str, domain: str, theme: str, wordpress_version: str,
           php_version: str = '8.3', database_prefix: str = 'wp_', registry: str = '') -> dict[str, str]:
    """Render deterministic project sources, never credentials or lock files."""
    if not SLUG.fullmatch(site) or not SLUG.fullmatch(theme):
        raise ValueError('Site and theme names must be lowercase kebab-case slugs')
    if not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}', domain):
        raise ValueError('Domain must be a lowercase DNS name')
    if not VERSION.fullmatch(wordpress_version) or not re.fullmatch(r'8\.[3-9]', php_version):
        raise ValueError('Use an exact WordPress version and PHP 8.3 or later (8.x)')
    if not re.fullmatch(r'[A-Za-z0-9_]+', database_prefix):
        raise ValueError('Invalid database prefix')
    if registry and not re.fullmatch(r'[a-z0-9][a-z0-9.:-]*(?:/[a-z0-9_-]+)*', registry):
        raise ValueError('Invalid registry')
    composer = {
        'name': 'aheadlabs/' + site, 'type': 'project', 'license': 'proprietary',
        'description': 'Bedrock WordPress site for ' + domain,
        'repositories': [{'type': 'composer', 'url': 'https://wpackagist.org'}],
        'require': {'php': '>=' + php_version, 'composer/installers': '^2.0',
                    'roots/wordpress': wordpress_version, 'roots/wp-config': '^1.0',
                    'roots/bedrock-autoloader': '^1.0', 'vlucas/phpdotenv': '^5.6'},
        'config': {'allow-plugins': {'composer/installers': True,
                                    'roots/wordpress-core-installer': True},
                   'sort-packages': True},
        'extra': {'wordpress-install-dir': 'web/wp', 'installer-paths': {
            'web/app/mu-plugins/{$name}/': ['type:wordpress-muplugin'],
            'web/app/plugins/{$name}/': ['type:wordpress-plugin'],
            'web/app/themes/{$name}/': ['type:wordpress-theme']}}}
    package = {'name': site, 'private': True, 'type': 'module',
               'scripts': {'build': 'vite build', 'dev': 'vite --host 0.0.0.0'},
               'devDependencies': {'vite': '^6.0.0', 'sass': '^1.77.0'}}
    salts = ['AUTH_KEY', 'SECURE_AUTH_KEY', 'LOGGED_IN_KEY', 'NONCE_KEY',
             'AUTH_SALT', 'SECURE_AUTH_SALT', 'LOGGED_IN_SALT', 'NONCE_SALT']
    env = (f'WP_ENV=development\nWP_HOME=http://localhost:8080\n'
           f'WP_SITEURL=http://localhost:8080/wp\nDB_HOST=mysql\n'
           f'DB_NAME={site.replace("-", "_")}\nDB_USER=wordpress\n'
           f'DB_PASSWORD=GENERATE\nMYSQL_ROOT_PASSWORD=GENERATE\nDB_PREFIX={database_prefix}\n'
           'DB_SSL=false\n' + ''.join(key + '=GENERATE\n' for key in salts))
    theme_dir = f'web/app/themes/{theme}'
    files = {
        'composer.json': json.dumps(composer, indent=2),
        'package.json': json.dumps(package, indent=2),
        'project.json': json.dumps({'site_name': site, 'domain': domain, 'theme_name': theme,
                                   'wordpress_version': wordpress_version, 'php_version': php_version,
                                   'image_name': f'{registry}/{site}' if registry else site}, indent=2),
        'config/application.php': templates.APPLICATION,
        'web/index.php': "<?php\ndefine('WP_USE_THEMES', true);\nrequire __DIR__ . '/wp/wp-blog-header.php';\n",
        'web/wp-config.php': "<?php\nrequire dirname(__DIR__) . '/vendor/autoload.php';\nrequire dirname(__DIR__) . '/config/application.php';\nrequire ABSPATH . 'wp-settings.php';\n",
        'web/healthz.php': "<?php\nheader('Content-Type: text/plain');\necho 'ok';\n",
        'wp-cli.yml': 'path: web/wp\n',
        'web/app/mu-plugins/bedrock-autoloader.php': "<?php\n/** Plugin Name: Bedrock MU plugin loader */\nif (is_blog_installed()) { new \\Roots\\Bedrock\\Autoloader(); }\n",
        'docker/site.conf': templates.SITE_CONF,
        'Dockerfile': templates.DOCKERFILE.replace('__PHP__', php_version),
        'compose.yaml': templates.COMPOSE,
        '.dockerignore': templates.DOCKERIGNORE,
        '.env.example': env,
        '.gitignore': '.env\n.env.*\n!.env.example\nauth.json\n/vendor/\n/node_modules/\n/web/wp/\n/web/app/uploads/*\n!/web/app/uploads/.gitkeep\n/web/app/cache/\n**/dist/\n*.log\n*.sql\n.staging/\n',
        'tools/project.py': templates.PROJECT_TOOL,
        '.github/workflows/validate.yml': templates.CI,
        'vite.config.js': "import { defineConfig } from 'vite';\nexport default defineConfig({ build: { manifest: 'manifest.json', outDir: '" + theme_dir + "/dist', emptyOutDir: true, rollupOptions: { input: '" + theme_dir + "/src/main.js' } } });\n",
        theme_dir + '/style.css': f'/*\nTheme Name: {theme}\nVersion: 1.0.0\n*/\n',
        theme_dir + '/src/main.js': "import './main.scss';\n",
        theme_dir + '/src/main.scss': 'body { font-family: sans-serif; }\n',
        theme_dir + '/index.php': "<?php get_header(); ?>\n<main><?php while (have_posts()) { the_post(); the_title('<h1>', '</h1>'); the_content(); } ?></main>\n<?php get_footer(); ?>\n",
        theme_dir + '/header.php': '<!doctype html>\n<html <?php language_attributes(); ?>><head><meta charset="<?php bloginfo("charset"); ?>"><meta name="viewport" content="width=device-width, initial-scale=1"><?php wp_head(); ?></head><body <?php body_class(); ?>><?php wp_body_open(); ?>\n',
        theme_dir + '/footer.php': '<?php wp_footer(); ?></body></html>\n',
        theme_dir + '/functions.php': """<?php
add_action('after_setup_theme', function () { add_theme_support('title-tag'); });
add_action('wp_enqueue_scripts', function () {
    $path = get_template_directory() . '/dist/manifest.json';
    if (!is_file($path)) { return; }
    $manifest = json_decode(file_get_contents($path), true);
    foreach ($manifest as $asset) {
        if (empty($asset['isEntry'])) { continue; }
        foreach ($asset['css'] ?? [] as $index => $css) {
            wp_enqueue_style('site-' . $index, get_template_directory_uri() . '/dist/' . $css, [], null);
        }
        wp_enqueue_script('site', get_template_directory_uri() . '/dist/' . $asset['file'], [], null, true);
    }
});
add_filter('script_loader_tag', function ($tag, $handle) {
    return $handle === 'site' ? str_replace('<script ', '<script type="module" ', $tag) : $tag;
}, 10, 2);
""",
        'AGENTS.md': '# Site rules\n\nUse Python automation, Composer and npm locks. Promote one image digest through staging and production. Persist only uploads. Cloud lifecycle changes are VCS-driven in HCP Terraform. Production always requires manual apply approval. Never copy staging data to production. Keep credentials out of Git and image layers.\n',
        'README.md': f'# {site}\n\nWordPress site for `{domain}`. Start with [the development guide](docs/development.md).\n',
        'docs/development.md': f'''# Develop this site

Install Python 3.9+ and Docker with Compose. Run from the repository root:

```text
python tools/project.py setup
python tools/project.py test
python tools/project.py build
```

Setup generates local credentials and missing lock files, installs dependencies and starts http://localhost:8080. Complete the WordPress installer there and activate `{theme}`. Commit both lock files before opening a PR. Subsequent setup uses the existing locks; dependency updates are deliberate Composer/npm operations on a branch.

Stop with `python tools/project.py stop`. Local data deletion requires `python tools/project.py reset --confirm-reset`. Run local scheduled events with `python tools/project.py cron`. WP-CLI arguments use `python tools/project.py wp -- <arguments>`.

The production image serves Apache on 8080 as www-data. `/healthz.php` checks the HTTP process; deployment smoke tests must also verify database connectivity, public pages and uploads. Provision salts and DB settings as runtime secrets. Set WP_ENV, WP_HOME and WP_SITEURL for the target environment. The cron job uses the same digest and `wp cron event run --due-now`.

Only `web/app/uploads` is persistent. Runtime core/plugin/theme updates are disabled. Add public plugins through Composer. Add licensed premium plugins such as Divi Builder through a private Composer repository and a BuildKit secret; never commit a license or put credentials in build arguments. Premium dependencies are deliberately not installed by the generator.

CI validates/builds the application. Infrastructure and image-digest changes go through Git PRs and HCP VCS runs; production requires manual approval. Build once and promote the tested digest. CI never copies staging databases or uploads into production.
''',
        '.devcontainer/devcontainer.json': json.dumps({'name': site, 'dockerComposeFile': '../compose.yaml', 'service': 'wordpress', 'workspaceFolder': '/var/www/html'}, indent=2),
    }
    for directory in ['web/app/mu-plugins', 'web/app/plugins', 'web/app/uploads']:
        files[directory + '/.gitkeep'] = ''
    return {name: content.rstrip() + '\n' for name, content in files.items()}


def create(target: Path, files: dict[str, str], dry_run: bool = False) -> list[str]:
    """Create a new repository; never overwrite a non-empty target."""
    if target.is_symlink() or (target.exists() and (not target.is_dir() or any(target.iterdir()))):
        raise ValueError('Target must be absent or an empty directory')
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    return sorted(files)


def validate_project(root: Path, require_locks: bool = False) -> list[str]:
    """Validate generated source before setup, or locked source before CI."""
    errors = ['Missing: ' + path for path in REQUIRED if not (root / path).is_file()]
    if (root / '.env.example').is_file():
        keys = {line.split('=', 1)[0] for line in (root / '.env.example').read_text().splitlines() if '=' in line}
        errors.extend('Missing environment key: ' + key for key in sorted(ENV_KEYS - keys))
    if require_locks:
        errors.extend('Missing lock file: ' + name for name in ('composer.lock', 'package-lock.json') if not (root / name).is_file())
    for name in ('composer.json', 'package.json', 'project.json'):
        if (root / name).is_file():
            try:
                json.loads((root / name).read_text())
            except json.JSONDecodeError:
                errors.append('Invalid JSON: ' + name)
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    new = commands.add_parser('create')
    new.add_argument('--site-name', required=True)
    new.add_argument('--domain', required=True)
    new.add_argument('--theme-name', required=True)
    new.add_argument('--wordpress-version', required=True)
    new.add_argument('--php-version', default='8.3')
    new.add_argument('--database-prefix', default='wp_')
    new.add_argument('--registry', default='')
    new.add_argument('--target-dir', type=Path, default=Path('.'))
    new.add_argument('--dry-run', action='store_true')
    check = commands.add_parser('validate')
    check.add_argument('--repo', type=Path, default=Path('.'))
    check.add_argument('--require-locks', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'validate':
            errors = validate_project(args.repo, args.require_locks)
            print(json.dumps({'valid': not errors, 'errors': errors}, indent=2))
            return int(bool(errors))
        files = render(args.site_name, args.domain, args.theme_name, args.wordpress_version,
                       args.php_version, args.database_prefix, args.registry)
        print(json.dumps(create(args.target_dir, files, args.dry_run), indent=2))
        return 0
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
