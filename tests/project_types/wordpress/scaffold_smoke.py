"""Docker integration check, invoked explicitly by CI, not by the unit suite."""
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from devops_toolset.project_types.wordpress.scaffold import create, render, validate_project


def run(*command, cwd):
    subprocess.run(command, cwd=cwd, check=True)


def main():
    with tempfile.TemporaryDirectory(prefix='bedrock-smoke-') as directory:
        root = Path(directory)
        create(root, render('scaffold-smoke', 'example.com', 'smoke', '7.1.2'))
        tool = str(root / 'tools/project.py')
        try:
            run(sys.executable, tool, 'setup', cwd=root)
            assert not validate_project(root, require_locks=True)
            run(sys.executable, tool, 'test', cwd=root)
            run(sys.executable, tool, 'build', cwd=root)
            # Inspect the final image, not only its Dockerfile.
            run('docker', 'run', '--rm', '--entrypoint', 'php', 'scaffold-smoke:local', '-r',
                "exit(file_exists('/var/www/html/.env') || !file_exists('/var/www/html/web/wp/wp-load.php') ? 1 : 0);", cwd=root)
            run('docker', 'run', '--rm', '--entrypoint', 'sh', 'scaffold-smoke:local', '-c', 'test "$(id -u)" -ne 0', cwd=root)
            run('docker', 'compose', 'exec', '-T', 'wordpress', 'wp', '--allow-root',
                'core', 'install', '--url=http://localhost:8080', '--title=Smoke',
                '--admin_user=smoke', '--admin_password=disposable-ci-password',
                '--admin_email=smoke@example.com', '--skip-email', cwd=root)
            run('docker', 'compose', 'exec', '-T', 'wordpress', 'wp', '--allow-root',
                'theme', 'activate', 'smoke', cwd=root)
            with urllib.request.urlopen('http://127.0.0.1:8080', timeout=15) as response:
                assert response.status == 200
            run('docker', 'compose', 'exec', '-T', 'wordpress', 'wp', '--allow-root',
                'cron', 'event', 'run', '--due-now', cwd=root)
        finally:
            run('docker', 'compose', 'down', '--volumes', '--remove-orphans', cwd=root)


if __name__ == '__main__':
    main()
