import os
import subprocess
import sys
from glob import glob
from setuptools import Command, find_packages, setup

package_name = "schunk_fts_library"


class PyTestCommand(Command):
    description = "run pytest"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        test_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), package_name, "tests"
        )
        errno = subprocess.call([sys.executable, "-m", "pytest", test_path])
        raise SystemExit(errno)


setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "config"),
            glob(package_name + "/config/*.json"),
        ),
    ],
    install_requires=["requests==2.34.2", "psutil==7.2.2"],
    zip_safe=True,
    author="Stefan Scherzinger",
    author_email="stefan.scherzinger@de.schunk.com",
    maintainer="Fabian Reinwald",
    maintainer_email="fabian.reinwald@de.schunk.com",
    description="Low-level driver library for SCHUNK's force-torque sensors",
    license="GPL-3.0-or-later",
    tests_require=["pytest", "coverage"],
    cmdclass={"test": PyTestCommand},
    entry_points={
        "console_scripts": [],
    },
)
