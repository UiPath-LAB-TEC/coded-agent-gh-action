from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "bump_pyproject_patch.py"


class BumpPyprojectPatchTests(unittest.TestCase):
    def run_script(self, pyproject: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--pyproject", str(pyproject)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_increments_patch_version_and_preserves_other_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pyproject = Path(temp_dir) / "pyproject.toml"
            pyproject.write_text(
                textwrap.dedent(
                    """\
                    [project]
                    name = "sample-agent"
                    version = "1.2.3"
                    description = "Sample"

                    [tool.example]
                    keep = true
                    """
                ),
                encoding="utf-8",
            )

            result = self.run_script(pyproject)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("old_version=1.2.3", result.stdout)
            self.assertIn("new_version=1.2.4", result.stdout)
            updated = pyproject.read_text(encoding="utf-8")
            self.assertIn('version = "1.2.4"', updated)
            self.assertIn("[tool.example]\nkeep = true", updated)

    def test_missing_project_version_fails_with_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pyproject = Path(temp_dir) / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "sample-agent"\n',
                encoding="utf-8",
            )

            result = self.run_script(pyproject)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[project] version", result.stderr)

    def test_non_numeric_patch_version_fails_with_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pyproject = Path(temp_dir) / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "sample-agent"\nversion = "1.2.beta"\n',
                encoding="utf-8",
            )

            result = self.run_script(pyproject)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("semantic version", result.stderr)


if __name__ == "__main__":
    unittest.main()
