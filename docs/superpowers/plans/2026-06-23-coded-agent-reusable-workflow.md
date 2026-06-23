# Coded Agent Reusable Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a reusable GitHub Actions workflow that tests and deploys UiPath coded-agent repositories through the `uip` CLI.

**Architecture:** The repository exposes one reusable workflow at `.github/workflows/uip-codedagent-ci.yml`. Supporting Python scripts handle patch-version bumping, and tests validate the script behavior plus the workflow contract without needing GitHub Actions to run locally.

**Tech Stack:** GitHub Actions reusable workflows, Bash, Python 3 standard library, `uv`, npm-installed `@uipath/cli`, `uip codedagent`.

---

### Task 1: Repo Skeleton And Contract Tests

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `tests/test_bump_pyproject_patch.py`
- Create: `tests/test_workflow_contract.py`

- [ ] **Step 1: Write failing tests for the version bump helper**

Create `tests/test_bump_pyproject_patch.py` with tests that import `scripts.bump_pyproject_patch`, create temporary `pyproject.toml` and `uv.lock` files, verify patch versions increment, verify missing project versions fail, and verify non-numeric patch versions fail.

- [ ] **Step 2: Write failing tests for the workflow contract**

Create `tests/test_workflow_contract.py` with tests that assert `.github/workflows/uip-codedagent-ci.yml` contains `workflow_call`, required inputs, required secrets, `uip login`, `uip codedagent run`, output validation, artifact upload, version bump handling, and deploy target branches.

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m unittest discover -v`

Expected: failures because `scripts/bump_pyproject_patch.py` and `.github/workflows/uip-codedagent-ci.yml` do not exist yet.

- [ ] **Step 4: Add minimal repo docs**

Create `README.md` with usage instructions for calling the reusable workflow from an agent repo.

Create `.gitignore` with Python cache and OS-generated file ignores.

### Task 2: Version Bump Helper

**Files:**
- Create: `scripts/bump_pyproject_patch.py`

- [ ] **Step 1: Implement the helper**

Create a Python script that accepts `--pyproject pyproject.toml`, finds `[project] version = "x.y.z"`, increments only `z`, preserves the rest of the file, prints `old_version=<old>` and `new_version=<new>` lines for GitHub Actions output parsing, and exits non-zero with a clear error on invalid/missing versions.

- [ ] **Step 2: Run focused tests**

Run: `python3 -m unittest tests.test_bump_pyproject_patch -v`

Expected: all version bump helper tests pass.

### Task 3: Reusable Workflow

**Files:**
- Create: `.github/workflows/uip-codedagent-ci.yml`

- [ ] **Step 1: Implement the reusable workflow**

Create a `workflow_call` workflow with inputs for `agent_root`, `python_version`, `uv_version`, `node_version`, `uip_cli_version`, `run_python_tests`, `python_test_command`, `run_codedagent_smoke`, `entrypoint`, `input_file`, `run_output_validation`, `validation_script`, `deploy`, `deploy_target`, `folder`, `version_strategy`, `version_commit_message`, `uipath_organization`, `uipath_tenant`, and `uipath_authority`.

Add required secrets `UIPATH_CLIENT_ID` and `UIPATH_CLIENT_SECRET`.

Steps must check out source, set up Python and Node, install `uv`, install `@uipath/cli`, install the `codedagent` tool, run `uv sync`, optionally run Python tests, authenticate with `uip login`, run `uip codedagent run --input-file`, upload the output artifact, run the validation script, optionally bump-and-commit patch versions, and deploy with exactly one non-interactive target.

- [ ] **Step 2: Run workflow contract tests**

Run: `python3 -m unittest tests.test_workflow_contract -v`

Expected: all workflow contract tests pass.

### Task 4: Full Verification And Git Publish

**Files:**
- No new files.

- [ ] **Step 1: Run all tests**

Run: `python3 -m unittest discover -v`

Expected: all tests pass.

- [ ] **Step 2: Check repository status**

Run: `git status --short --branch`

Expected: all intended files are untracked or staged; no generated junk files.

- [ ] **Step 3: Commit**

Run:

```bash
git add .
git commit -m "feat: add reusable UiPath coded agent workflow"
```

- [ ] **Step 4: Set remote and push**

Run:

```bash
git remote add origin https://github.com/UiPath-LAB-TEC/coded-agent-gh-action.git
git branch -M main
git push -u origin main
```
