# Copyright 2023-2025 Broadcom.
# SPDX-License-Identifier: Apache-2.0
#
import logging
import os
import platform
import shutil
import sys

import pytest

from relenv.common import list_archived_builds, plat_from_triplet
from relenv.create import create

log = logging.getLogger(__name__)


def get_build_version():
    if "RELENV_PY_VERSION" in os.environ:
        return os.environ["RELENV_PY_VERSION"]
    builds = list(list_archived_builds())
    versions = []
    for version, arch, plat in builds:
        sysplat = plat_from_triplet(plat)
        if sysplat == sys.platform and arch == platform.machine().lower():
            versions.append(version)
    if versions:
        version = versions[0]
        log.warning(
            "Environment RELENV_PY_VERSION not set, detected version %s", version
        )
        return version


def pytest_report_header(config):
    return f"relenv python version: {get_build_version()}"


@pytest.fixture(scope="module")
def build_version():
    return get_build_version()


@pytest.fixture(scope="module")
def minor_version():
    yield get_build_version().rsplit(".", 1)[0]


@pytest.fixture
def build(tmp_path, build_version):
    create("test", tmp_path, version=build_version)
    os.chdir(tmp_path / "test")
    try:
        yield tmp_path / "test"
    finally:
        try:
            shutil.rmtree(tmp_path)
        except Exception as exc:
            log.error("Failed to remove build directory %s", exc)


@pytest.fixture
def pipexec(build):
    if sys.platform == "win32":
        path = build / "Scripts"
    else:
        path = build / "bin"

    exe = shutil.which("pip3", path=path)
    if exe is None:
        exe = shutil.which("pip", path=path)
    if exe is None:
        pytest.fail(f"Failed to find 'pip3' and 'pip' in '{path}'")
    yield exe


@pytest.fixture
def pyexec(build):
    if sys.platform == "win32":
        path = build / "Scripts"
    else:
        path = build / "bin"

    exe = shutil.which("python3", path=path)
    if exe is None:
        exe = shutil.which("python", path=path)
    if exe is None:
        pytest.fail(f"Failed to find 'python3' and 'python' in '{path}'")
    yield exe
