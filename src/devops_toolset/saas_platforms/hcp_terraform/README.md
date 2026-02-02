# HCP Terraform Tools

Scripts for managing HCP Terraform (Terraform Cloud) workspaces and runs.

## Scripts

### trigger-all-runs.py

Trigger plan/apply runs across all workspaces in an organization.

```bash
python trigger-all-runs.py --filter production --apply --wait
```

### check-workspace-status.py

Check the status of all workspaces in an organization.

```bash
python check-workspace-status.py
```

### sync-variable-sets.py

Synchronize variable sets across workspaces based on tags.

```bash
python sync-variable-sets.py --variable-set "Azure credentials" --tag cloud:azure
```

### enable-submodules.py

Enable Git submodules for workspaces.

```bash
python enable-submodules.py --workspace my-workspace
```

## Authentication

Scripts use the HCP Terraform credentials file at `~/.terraform.d/credentials.tfrc.json`.

Run `terraform login` to authenticate.

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib only)
