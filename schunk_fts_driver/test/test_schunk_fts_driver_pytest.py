# Copyright 2025 SCHUNK SE & Co. KG
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
import os
from pathlib import Path
import subprocess
import sys
import unittest


class PytestSuite(unittest.TestCase):
    def runTest(self):
        if "PYTEST_CURRENT_TEST" in os.environ:
            return

        package_root = Path(__file__).resolve().parents[1]
        workspace_root = package_root.parent
        test_path = package_root / "schunk_fts_driver" / "tests"
        env = os.environ.copy()
        python_path = [
            str(package_root),
            str(workspace_root / "schunk_fts_library"),
            env.get("PYTHONPATH", ""),
        ]
        env["PYTHONPATH"] = os.pathsep.join(path for path in python_path if path)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path)],
            cwd=workspace_root,
            env=env,
        )
        self.assertEqual(result.returncode, 0)
