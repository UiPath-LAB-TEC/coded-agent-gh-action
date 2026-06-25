# UiPath Coded Agent GitHub Action

Reusable GitHub Actions workflow for testing and deploying UiPath coded-agent repositories with the `uip` CLI.

The workflow is designed for separate agent repositories. Each repo keeps its own `input.json`, optional Python tests, and output validator, while this repository owns the common CI/CD behavior.

## Reusable Workflow

Use `.github/workflows/uip-codedagent-ci.yml` from an agent repository:

```yaml
name: UiPath Coded Agent

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  coded-agent:
    uses: UiPath-LAB-TEC/coded-agent-gh-action/.github/workflows/uip-codedagent-ci.yml@main
    with:
      agent_root: .
      python_version: "3.12"
      input_file: input.json
      prepare_input_command: uv run python create_test_attachment.py
      run_python_tests: false
      run_output_validation: true
      validation_script: scripts/validate_codedagent_output.py
      deploy: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
      deploy_target: folder
      folder: Shared
      version_strategy: source
      uipath_organization: ${{ vars.UIPATH_ORGANIZATION }}
      uipath_tenant: ${{ vars.UIPATH_TENANT }}
    secrets: inherit
```

## Required Secrets

Each calling agent repository or organization must define:

- `UIPATH_CLIENT_ID`
- `UIPATH_CLIENT_SECRET`

The workflow passes these to `uip login` as environment-backed values:

```bash
uip login --client-id env.UIPATH_CLIENT_ID --client-secret env.UIPATH_CLIENT_SECRET
```

## Required Variables Or Inputs

Pass these through workflow inputs, usually from GitHub repository or organization variables:

- `uipath_organization`
- `uipath_tenant`

Use `uipath_authority` only for staging, alpha, or Automation Suite identity URLs.

## Test Behavior

Before tests run, the workflow installs dependencies with `uv sync`, activates
the generated `.venv`, and runs:

```bash
uip codedagent setup --force
```

The default required smoke test is:

```bash
uip codedagent run --input-file input.json --output-file codedagent-output.json
```

If `entrypoint` is supplied, it is inserted between `run` and `--input-file`.

If a repo needs to create a fresh test resource after `uip login`, set
`prepare_input_command`. It runs from `agent_root` after login and before the
smoke test:

```yaml
with:
  prepare_input_command: uv run python create_test_attachment.py
```

Python tests are optional. Enable them per repo:

```yaml
with:
  run_python_tests: true
  python_test_command: UIPATH_ACCESS_TOKEN=dummy python -m unittest discover
```

## Output Validation

Each agent repo owns its validator because output schemas differ. The default validator path is:

```text
scripts/validate_codedagent_output.py
```

The script must accept:

```bash
python scripts/validate_codedagent_output.py --output codedagent-output.json
```

Validation failures should print a clear error to stderr and exit non-zero.

## Deployment

Deployment runs only when `deploy: true` and all test steps pass.

Supported targets:

- `deploy_target: my-workspace`
- `deploy_target: tenant`
- `deploy_target: folder` plus `folder: <folder-name>`

The workflow uses `uip codedagent deploy`, which validates, packs, and publishes in one command. It does not run `uip codedagent pack` separately.

## Version Strategy

UiPath package feeds reject duplicate package versions.

- `version_strategy: source` deploys the committed `pyproject.toml` version. Duplicate versions fail and should be fixed by a source-controlled version bump.
- `version_strategy: patch-and-commit` increments only the patch version in `[project].version`, runs `uv lock`, commits the version files with `[skip ci]`, pushes the commit, then deploys.

For `patch-and-commit`, the caller workflow needs write permission:

```yaml
permissions:
  contents: write
```

If the caller uses a tag such as `@v1`, also pass the matching support script ref:

```yaml
with:
  workflow_ref: v1
```
