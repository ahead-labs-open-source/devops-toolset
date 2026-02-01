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

### validate_environment.py

Validates that required environment variables and secrets are present in a GitHub Actions job.

**Important**: This script validates that variables/secrets **arrived correctly to the job environment**, NOT that they exist directly in GitHub Settings.

#### Validation Flow

1. User configures `vars.ARM_SUBSCRIPTION_ID` in GitHub Settings → Secrets and variables
2. Workflow declares: `ARM_SUBSCRIPTION_ID: ${{ vars.ARM_SUBSCRIPTION_ID }}`
3. GitHub Actions passes the value to job environment (or empty string if not found)
4. Script reads `os.environ["ARM_SUBSCRIPTION_ID"]` and validates it's non-empty

#### Limitation

Cannot distinguish between "doesn't exist in GitHub" vs "exists but is empty". Both cases result in an empty value in the environment.

#### Practical Result

If validation passes, you know:
- ✅ Variable/secret exists in GitHub
- ✅ Has a non-empty value
- ✅ Was passed correctly to the job

#### Usage

```bash
python -m devops_toolset.devops_platforms.github.validate_environment \
  --required ARM_SUBSCRIPTION_ID:variable:repo \
  --required ARM_TENANT_ID:variable:repo \
  --required APIM_RESOURCE_GROUP_NAME:variable:repo \
  --required ARM_CLIENT_ID:variable:env \
  --required APIM_API_ID:variable:env \
  --required POSTMAN_API_KEY:secret:repo \
  --required ARM_CLIENT_SECRET:secret:env \
  --environment staging \
  --template-path .github/workflows/secrets-and-variables.jsonc
```

#### Parameters

**--required VARIABLE_NAME:type:scope** (required, repeatable)

Format: `VARIABLE_NAME:type:scope`
- `type`: `variable` or `secret` (for display purposes only)
- `scope`: `repo` (repository-level) or `env` (environment-level) (for display purposes only)

**--environment NAME** (optional)

Environment name for logging/messages (e.g., `staging`, `production`). Cosmetic only.

**--template-path PATH** (optional)

Documentation reference path to show in error messages. Informational only.

#### Example in GitHub Actions Workflow

```yaml
- name: Preflight validation
  env:
    ARM_SUBSCRIPTION_ID: ${{ vars.ARM_SUBSCRIPTION_ID }}
    ARM_TENANT_ID: ${{ vars.ARM_TENANT_ID }}
    POSTMAN_API_KEY: ${{ secrets.POSTMAN_API_KEY }}
    ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
  run: |
    python -m devops_toolset.devops_platforms.github.validate_environment \
      --required ARM_SUBSCRIPTION_ID:variable:repo \
      --required ARM_TENANT_ID:variable:repo \
      --required POSTMAN_API_KEY:secret:repo \
      --required ARM_CLIENT_SECRET:secret:env \
      --environment staging \
      --template-path .github/workflows/secrets-and-variables.jsonc
```

## Authentication

Use a GitHub Personal Access Token with `repo` scope.

Set via `--token` argument or `GITHUB_TOKEN` environment variable.

## Requirements

- Python 3.8+
- PyGithub (`pip install PyGithub`)
