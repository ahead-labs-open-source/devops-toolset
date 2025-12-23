# GitHub Tools

Scripts for managing GitHub repositories and configurations.

## Scripts

### configure-branch-protection.py

Configure branch protection rules for repositories.

```bash
python configure-branch-protection.py --token YOUR_TOKEN --repo owner/repo
```

Features:
- Require PR reviews before merging
- Require status checks (CI/CD)
- Enforce linear history on main branch
- Different rules for main vs develop branches

## Authentication

Use a GitHub Personal Access Token with `repo` scope.

Set via `--token` argument or `GITHUB_TOKEN` environment variable.

## Requirements

- Python 3.8+
- PyGithub (`pip install PyGithub`)
