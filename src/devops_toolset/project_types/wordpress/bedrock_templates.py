"""Self-contained templates for the Bedrock repository generator."""

APPLICATION = r'''<?php
use Roots\WPConfig\Config;

$root = dirname(__DIR__);
if (is_file($root . '/.env')) {
    Dotenv\Dotenv::createUnsafeImmutable($root)->load();
}
$required = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'WP_HOME', 'WP_SITEURL',
    'AUTH_KEY', 'SECURE_AUTH_KEY', 'LOGGED_IN_KEY', 'NONCE_KEY',
    'AUTH_SALT', 'SECURE_AUTH_SALT', 'LOGGED_IN_SALT', 'NONCE_SALT'];
foreach ($required as $key) {
    $value = getenv($key);
    if ($value === false || $value === '') {
        throw new RuntimeException('Missing required runtime setting: ' . $key);
    }
    Config::define($key, $value);
}
define('WP_ENV', getenv('WP_ENV') ?: 'production');
Config::define('WP_ENVIRONMENT_TYPE', WP_ENV);
Config::define('DB_HOST', getenv('DB_HOST') ?: 'mysql');
Config::define('DB_CHARSET', 'utf8mb4');
Config::define('DB_COLLATE', '');
if (filter_var(getenv('DB_SSL') ?: 'false', FILTER_VALIDATE_BOOLEAN)) {
    Config::define('MYSQL_CLIENT_FLAGS', MYSQLI_CLIENT_SSL);
}
$table_prefix = getenv('DB_PREFIX') ?: 'wp_';
Config::define('WP_CONTENT_DIR', $root . '/web/app');
Config::define('WP_CONTENT_URL', rtrim(getenv('WP_HOME'), '/') . '/app');
Config::define('DISALLOW_FILE_EDIT', true);
Config::define('DISALLOW_FILE_MODS', true);
Config::define('AUTOMATIC_UPDATER_DISABLED', true);
Config::define('DISABLE_WP_CRON', true);
Config::define('WP_DEBUG', WP_ENV === 'development');
Config::define('WP_DEBUG_DISPLAY', false);
Config::define('WP_DEBUG_LOG', '/dev/stderr');
if (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
Config::apply();
define('ABSPATH', $root . '/web/wp/');
'''

DOCKERFILE = '''# syntax=docker/dockerfile:1.10
FROM php:__PHP__-apache AS base
WORKDIR /var/www/html
RUN apt-get update && apt-get install -y --no-install-recommends git unzip libzip-dev libpng-dev libjpeg62-turbo-dev libfreetype6-dev \\
    && docker-php-ext-configure gd --with-freetype --with-jpeg \\
    && docker-php-ext-install mysqli pdo_mysql zip gd \\
    && a2enmod rewrite \\
    && sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf \\
    && rm -rf /var/lib/apt/lists/*
COPY docker/site.conf /etc/apache2/sites-available/000-default.conf
COPY --from=composer:2.8 /usr/bin/composer /usr/local/bin/composer
COPY --from=wordpress:cli /usr/local/bin/wp /usr/local/bin/wp

FROM base AS development
ENV COMPOSER_ALLOW_SUPERUSER=1

FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY package.json package-lock.json vite.config.js ./
COPY web/app/themes ./web/app/themes
RUN npm ci && npm run build

FROM base AS dependencies
COPY composer.json composer.lock ./
RUN mkdir -p web/app/mu-plugins web/app/plugins web/app/themes
RUN --mount=type=secret,id=composer_auth,env=COMPOSER_AUTH composer install --no-dev --no-interaction --prefer-dist --optimize-autoloader

FROM base AS production
COPY . /var/www/html
COPY --from=dependencies /var/www/html/vendor ./vendor
COPY --from=dependencies /var/www/html/web/wp ./web/wp
COPY --from=dependencies /var/www/html/web/app ./web/app
COPY --from=frontend /build/web/app/themes ./web/app/themes
RUN mkdir -p /tmp/apache2 /tmp/apache2-lock web/app/uploads \\
    && chown -R www-data:www-data /tmp/apache2 /tmp/apache2-lock web/app/uploads \\
    && chmod -R a-w config vendor web/wp web/app/themes web/app/plugins web/app/mu-plugins
ENV APACHE_RUN_DIR=/tmp/apache2 APACHE_LOCK_DIR=/tmp/apache2-lock APACHE_PID_FILE=/tmp/apache2/apache2.pid
USER www-data
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD ["php", "-r", "exit(@file_get_contents('http://127.0.0.1:8080/healthz.php') === 'ok' ? 0 : 1);"]
'''

COMPOSE = '''services:
  wordpress:
    build:
      context: .
      target: development
    env_file: .env
    ports: ["127.0.0.1:8080:8080"]
    volumes:
      - .:/var/www/html
      - uploads:/var/www/html/web/app/uploads
    depends_on:
      mysql:
        condition: service_healthy
  node:
    image: node:22-bookworm-slim
    working_dir: /workspace
    volumes: [".:/workspace"]
    profiles: ["tools"]
  mysql:
    image: mysql:8.4
    environment:
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes: ["mysql:/var/lib/mysql"]
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost --silent"]
      interval: 5s
      timeout: 5s
      retries: 30
volumes:
  mysql:
  uploads:
'''

SITE_CONF = '''<VirtualHost *:8080>
    DocumentRoot /var/www/html/web
    <Directory /var/www/html/web>
        AllowOverride None
        Require all granted
        DirectoryIndex index.php
        RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.php [L]
    </Directory>
    <Directory /var/www/html/web/app/uploads>
        <FilesMatch "\\.(php|phtml|phar)$">
            Require all denied
        </FilesMatch>
    </Directory>
    ErrorLog /proc/self/fd/2
    CustomLog /proc/self/fd/1 combined
</VirtualHost>
'''

DOCKERIGNORE = '''.git
.env
.env.*
!.env.example
auth.json
**/auth.json
**/*.pem
**/*.key
**/*.sql
**/*.sql.gz
**/*.sqlite
**/*.sqlite3
**/*.tfstate*
**/terraform.token
vendor
node_modules
web/wp
web/app/uploads
web/app/cache
**/*.log
.staging
backups
'''

PROJECT_TOOL = '''#!/usr/bin/env python3
"""Local application tooling; cloud infrastructure changes use VCS/HCP only."""
import argparse
import json
import os
import secrets
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*command):
    subprocess.run(list(command), cwd=ROOT, check=True)


def compose(*command):
    run('docker', 'compose', *command)


def tool_container(service, *command):
    options = ['run', '--rm', '--no-deps']
    if hasattr(os, 'getuid'):
        options.extend(['--user', f'{os.getuid()}:{os.getgid()}'])
    options.extend(['-e', 'COMPOSER_HOME=/tmp/composer', '-e', 'npm_config_cache=/tmp/npm'])
    compose(*options, service, *command)


def app(*command):
    tool_container('wordpress', *command)


def node(*command):
    tool_container('node', *command)


def setup():
    if not (ROOT / '.env').exists():
        content = (ROOT / '.env.example').read_text()
        keys = ['DB_PASSWORD', 'MYSQL_ROOT_PASSWORD', 'AUTH_KEY', 'SECURE_AUTH_KEY',
                'LOGGED_IN_KEY', 'NONCE_KEY', 'AUTH_SALT', 'SECURE_AUTH_SALT',
                'LOGGED_IN_SALT', 'NONCE_SALT']
        for key in keys:
            content = content.replace(key + '=GENERATE', key + '=' + secrets.token_hex(32))
        (ROOT / '.env').write_text(content)
    compose('build', 'wordpress')
    if not (ROOT / 'composer.lock').exists():
        app('composer', 'update', '--no-interaction', '--prefer-dist')
    else:
        app('composer', 'install', '--no-interaction', '--prefer-dist')
    if not (ROOT / 'package-lock.json').exists():
        node('npm', 'install', '--package-lock-only')
    node('npm', 'ci')
    node('npm', 'run', 'build')
    compose('up', '-d', 'wordpress')
    print('Commit composer.lock and package-lock.json; keep .env private.')


def require_locks():
    for name in ('composer.lock', 'package-lock.json'):
        if not (ROOT / name).is_file():
            raise ValueError('Run setup and commit the missing lock file: ' + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['setup', 'start', 'stop', 'reset', 'test', 'build', 'wp', 'cron'])
    parser.add_argument('--confirm-reset', action='store_true')
    parser.add_argument('--composer-auth-file', type=Path)
    parser.add_argument('arguments', nargs='*')
    args = parser.parse_args()
    if not shutil.which('docker'):
        raise ValueError('Docker with Compose is required')
    if args.command == 'setup':
        setup()
    elif args.command == 'start':
        compose('up', '-d', 'wordpress')
    elif args.command == 'stop':
        compose('down')
    elif args.command == 'reset':
        if not args.confirm_reset:
            raise ValueError('Local database/uploads deletion requires --confirm-reset')
        compose('down', '--volumes')
    elif args.command == 'test':
        require_locks()
        compose('config', '--quiet')
        # Exact WordPress pinning is intentional; keep schema and lock checks strict.
        app('composer', 'validate', '--strict', '--no-check-all')
        app('composer', 'audit')
        app('php', '-l', 'config/application.php')
        node('npm', 'ci')
        node('npm', 'run', 'build')
    elif args.command == 'build':
        require_locks()
        metadata = json.loads((ROOT / 'project.json').read_text())
        command = ['docker', 'build', '--target', 'production', '-t', metadata['image_name'] + ':local']
        if args.composer_auth_file:
            command.extend(['--secret', 'id=composer_auth,src=' + str(args.composer_auth_file.resolve())])
        run(*command, '.')
    elif args.command == 'cron':
        compose('exec', 'wordpress', 'wp', '--allow-root', 'cron', 'event', 'run', '--due-now')
    else:
        compose('exec', 'wordpress', 'wp', '--allow-root', *args.arguments)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
'''

CI = '''name: WordPress validation
on:
  pull_request:
  push:
    branches: [main, develop]
permissions:
  contents: read
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Require committed lock files
        run: python -c "from pathlib import Path; assert all(Path(p).is_file() for p in ['composer.lock', 'package-lock.json']), 'Run setup and commit lock files'"
      - run: python tools/project.py setup
      - run: python tools/project.py test
      - run: python tools/project.py build
      - name: Stop local services
        if: always()
        run: python tools/project.py stop
'''
