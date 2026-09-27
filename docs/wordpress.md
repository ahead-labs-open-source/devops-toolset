# Create a WordPress repository

The Bedrock generator lives in `devops-toolset`, independently of any infrastructure repository. It creates Composer-managed WordPress, a custom theme with Vite, Docker development/production targets, WP-CLI, CI validation and Python lifecycle commands.

## Start in an empty directory

Install a version of devops-toolset containing `project_types.wordpress.scaffold` (or install the reviewed repository checkout with `python -m pip install .`). This command is not available in older published releases.

```text
python -m devops_toolset.project_types.wordpress.scaffold create --site-name my-site --domain example.com --theme-name my-theme --wordpress-version 6.8.2 --dry-run
python -m devops_toolset.project_types.wordpress.scaffold create --site-name my-site --domain example.com --theme-name my-theme --wordpress-version 6.8.2
python -m devops_toolset.project_types.wordpress.scaffold validate
python tools/project.py setup
python tools/project.py test
python tools/project.py build
```

`6.8.2` is an illustrative exact version, not a recommendation of the latest release. Select the approved WordPress version before generation. Python 3.9+ runs the generator; Docker with Compose is required for setup and build. PHP and Node run inside containers.

`--target-dir` defaults to the current directory. Non-empty directories are rejected; no force-overwrite option exists. `--php-version`, `--database-prefix` and `--registry` are optional. `--dry-run` lists generated files without writing or creating resources.

Setup creates `.env` with random local credentials, resolves missing `composer.lock` and `package-lock.json`, and uses existing locks on subsequent runs. Commit the locks and generated source. CI requires both locks. Complete the local WordPress installer at http://localhost:8080 and activate the custom theme.

## Runtime contract

- Apache serves port 8080 as `www-data` in the production target.
- `/healthz.php` checks the HTTP process; deployment checks must also cover database access, pages, forms and uploads.
- Persist only `/var/www/html/web/app/uploads`; keep code in the image.
- Provide site-specific DB credentials and salts at runtime. Do not use a database administrator as the application user.
- A separate scheduled job runs `wp cron event run --due-now` using the same image digest; request-triggered WP-Cron is disabled.
- Build once and promote the digest. Production DB/uploads are never replaced with staging data.
- Infrastructure lifecycle changes are VCS-driven; production requires manual approval.

Use `python tools/project.py wp -- <arguments>` for WP-CLI and `python tools/project.py cron` for local scheduled events. Resetting local data requires `python tools/project.py reset --confirm-reset`.

## Premium dependencies

Add Divi Builder or another licensed plugin through an approved private Composer repository. Supply credentials as a BuildKit secret:

```text
python tools/project.py build --composer-auth-file /secure/path/auth.json
```

Never commit `auth.json`, use Docker build arguments for credentials, or install dependencies manually in production. The generator deliberately does not download or license premium plugins.

## Compatibility

The older `scripts.bootstrap_repository` command supports legacy WP-CLI projects and is not the Bedrock entry point. Existing callers remain unchanged. The new generator owns its own source contract and validator; no Hispania scripts or private repositories are needed to generate a site.

For upstream behavior, use [Bedrock](https://roots.io/bedrock/docs/), [Composer](https://getcomposer.org/doc/), and [Vite](https://vite.dev/guide/).
