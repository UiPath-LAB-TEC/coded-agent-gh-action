from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "uip-codedagent-ci.yml"


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_text = WORKFLOW.read_text(encoding="utf-8")

    def test_declares_reusable_workflow_inputs_and_secrets(self) -> None:
        text = self.workflow_text
        self.assertIn("workflow_call:", text)
        for input_name in (
            "agent_root",
            "python_version",
            "uv_version",
            "node_version",
            "uip_cli_version",
            "run_python_tests",
            "python_test_command",
            "run_codedagent_smoke",
            "entrypoint",
            "input_file",
            "prepare_input_command",
            "run_output_validation",
            "validation_script",
            "deploy",
            "deploy_target",
            "folder",
            "version_strategy",
            "version_commit_message",
            "uipath_organization",
            "uipath_tenant",
            "uipath_authority",
        ):
            self.assertIn(f"{input_name}:", text)
        self.assertIn("UIPATH_CLIENT_ID:", text)
        self.assertIn("UIPATH_CLIENT_SECRET:", text)

    def test_sets_up_uip_cli_and_codedagent_tool(self) -> None:
        text = self.workflow_text
        self.assertIn("npm install -g @uipath/cli@", text)
        self.assertIn("uip tools install codedagent", text)
        self.assertIn("uip --version", text)
        self.assertIn("uip codedagent --help", text)

    def test_logs_in_and_runs_codedagent_with_input_file(self) -> None:
        text = self.workflow_text
        self.assertIn("uip login", text)
        self.assertIn("--client-id env.UIPATH_CLIENT_ID", text)
        self.assertIn("--client-secret env.UIPATH_CLIENT_SECRET", text)
        self.assertIn('--organization "${UIPATH_ORGANIZATION}"', text)
        self.assertIn('--tenant "${UIPATH_TENANT}"', text)
        self.assertIn("uip codedagent run", text)
        self.assertIn('--input-file "${INPUT_FILE}"', text)
        self.assertIn("--output-file codedagent-output.json", text)

    def test_configures_codedagent_python_after_dependency_sync(self) -> None:
        text = self.workflow_text
        self.assertIn("Configure coded-agent Python", text)
        self.assertIn("source .venv/bin/activate", text)
        self.assertIn("uip codedagent setup --force --output json", text)

        sync_index = text.index("- name: Install agent dependencies")
        setup_index = text.index("- name: Configure coded-agent Python")
        tests_index = text.index("- name: Run optional Python tests")
        self.assertLess(sync_index, setup_index)
        self.assertLess(setup_index, tests_index)

    def test_runs_optional_prepare_input_command_after_login_before_smoke(self) -> None:
        text = self.workflow_text
        self.assertIn(
            "PREPARE_INPUT_COMMAND: ${{ inputs.prepare_input_command }}",
            text,
        )
        self.assertIn("Run prepare input command", text)
        self.assertIn('eval "${PREPARE_INPUT_COMMAND}"', text)

        login_index = text.index("- name: Log in to UiPath")
        prepare_index = text.index("- name: Run prepare input command")
        smoke_index = text.index("- name: Run coded-agent smoke test")
        self.assertLess(login_index, prepare_index)
        self.assertLess(prepare_index, smoke_index)

    def test_validates_output_and_uploads_artifacts(self) -> None:
        text = self.workflow_text
        self.assertIn("actions/upload-artifact@", text)
        self.assertIn("codedagent-output", text)
        self.assertIn('python "${VALIDATION_SCRIPT}" --output codedagent-output.json', text)
        self.assertIn("run_output_validation", text)

    def test_supports_patch_version_bump_and_noninteractive_deploy_targets(self) -> None:
        text = self.workflow_text
        self.assertIn("scripts/bump_pyproject_patch.py", text)
        self.assertIn("uv lock", text)
        self.assertIn("git commit -m", text)
        self.assertIn("git push", text)
        self.assertIn("--my-workspace", text)
        self.assertIn("--tenant", text)
        self.assertIn('--folder "${DEPLOY_FOLDER}"', text)


if __name__ == "__main__":
    unittest.main()
