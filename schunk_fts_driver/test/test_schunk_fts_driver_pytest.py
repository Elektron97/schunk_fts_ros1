import os
import subprocess
import sys
import unittest
from pathlib import Path


class PytestSuite(unittest.TestCase):
    def runTest(self):
        if "PYTEST_CURRENT_TEST" in os.environ:
            return

        package_root = Path(__file__).resolve().parents[1]
        test_path = package_root / "schunk_fts_driver" / "tests"
        result = subprocess.run([sys.executable, "-m", "pytest", str(test_path)])
        self.assertEqual(result.returncode, 0)
