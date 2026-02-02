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
python -m devops_toolset.saas_platforms.github.validate_environment \
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
    python -m devops_toolset.saas_platforms.github.validate_environment \
      --required ARM_SUBSCRIPTION_ID:variable:repo \
      --required ARM_TENANT_ID:variable:repo \
      --required POSTMAN_API_KEY:secret:repo \
      --required ARM_CLIENT_SECRET:secret:env \
      --environment staging \
      --template-path .github/workflows/secrets-and-variables.jsonc
```

### inject_secrets_and_variables.py

Injects repository and environment-level variables and secrets into GitHub using a JSONC template file.

**Features**:
- Supports both repository-level and environment-specific variables/secrets
- Can read secret values directly from template (for dev/test) or fetch from Azure Key Vault (recommended for production)
- Dry-run mode to preview changes without executing
- Uses GitHub CLI (`gh`) for authentication and injection

#### Template Format

The script reads a JSONC template file (JSON with comments) structured as:

```jsonc
{
  "repository": {
    "variables": {
      "ARM_SUBSCRIPTION_ID": "value",
      "ARM_TENANT_ID": "value"
    },
    "secrets": {
      "POSTMAN_API_KEY": "https://kv-name.vault.azure.net/secrets/secret-name"
    }
  },
  "environments": {
    "staging": {
      "variables": {
        "ARM_CLIENT_ID": "value",
        "APIM_API_ID": "value"
      },
      "secrets": {
        "ARM_CLIENT_SECRET": "https://kv-name.vault.azure.net/secrets/secret-name"
      }
    },
    "production": {
      "variables": { },
      "secrets": { }
    }
  }
}
```

#### Usage

**Basic usage (secrets as plain text in template)**:
```bash
python -m devops_toolset.saas_platforms.github.inject_secrets_and_variables \
  --template .github/workflows/secrets-and-variables.jsonc \
  --repo owner/repo-name
```

**Fetch secrets from Azure Key Vault (recommended)**:
```bash
python -m devops_toolset.saas_platforms.github.inject_secrets_and_variables \
  --template .github/workflows/secrets-and-variables.jsonc \
  --repo owner/repo-name \
  --fetch-from-keyvault
```

**Dry run (preview without executing)**:
```bash
python -m devops_toolset.saas_platforms.github.inject_secrets_and_variables \
  --template .github/workflows/secrets-and-variables.jsonc \
  --repo owner/repo-name \
  --dry-run
```

#### Parameters

**--template PATH** (required)

Path to secrets and variables template file (JSONC format).

**--repo owner/repo-name** (required)

Target GitHub repository in format `owner/repo-name`.

**--fetch-from-keyvault** (optional)

Fetch secret values from Azure Key Vault. Requires Azure CLI authenticated. When enabled, secret values that are Azure Key Vault URLs will be fetched; plain text values are used as-is.

**--dry-run** (optional)

Print what would be done without executing commands.

#### Requirements

- GitHub CLI (`gh`) must be installed and authenticated
- Azure CLI (`az`) required if using `--fetch-from-keyvault`

## Authentication

For `validate_environment.py` and `inject_secrets_and_variables.py`:
- GitHub CLI must be authenticated: `gh auth login`
- Azure CLI must be authenticated (if fetching from Key Vault): `az login`

For `configure_branch_protection.py`:
- Use a GitHub Personal Access Token with `repo` scope
- Set via `--token` argument or `GITHUB_TOKEN` environment variable

## Requirements

- Python 3.8+
- GitHub CLI (`gh`) - for inject_secrets_and_variables.py
- Azure CLI (`az`) - optional, for Key Vault integration
- PyGithub (`pip install PyGithub`) - for configure_branch_protection.py
