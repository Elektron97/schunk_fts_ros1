from setuptools import find_packages, setup
import os
from glob import glob

package_name = "schunk_fts_library"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test", "test.*", "tests", "*.tests", "*.tests.*"]),
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
    entry_points={
        "console_scripts": [],
    },
)
