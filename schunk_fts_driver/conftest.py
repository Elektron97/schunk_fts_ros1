# Copyright 2026 SCHUNK SE & Co. KG
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
from pathlib import Path
import sys


def _prepend_python_package_paths() -> None:
    package_root = Path(__file__).resolve().parent
    workspace_root = package_root.parent
    for package_dir in ("schunk_fts_driver", "schunk_fts_library"):
        package_path = str(workspace_root / package_dir)
        if package_path not in sys.path:
            sys.path.insert(0, package_path)


_prepend_python_package_paths()

from schunk_fts_library.fixtures import sensor  # noqa: E402,F401
