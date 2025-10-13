from __future__ import absolute_import

import atexit
import os
import shutil
import tempfile

from setuptools import setup

_BUILD_DIR = None


def ensure_unique_build_dir():
    # type: () -> str
    global _BUILD_DIR
    if _BUILD_DIR is None:
        _build_dir = tempfile.mkdtemp(prefix="uninstallable-dist-build.")
        atexit.register(shutil.rmtree, _build_dir, ignore_errors=True)
        _BUILD_DIR = _build_dir
    return _BUILD_DIR


def unique_build_dir(name):
    # type: (str) -> str
    path = os.path.join(ensure_unique_build_dir(), name)
    os.mkdir(path)
    return path


if __name__ == "__main__":
    setup(
        # Keep the project root uncluttered by setuptools build artifacts.
        options={
            "build": {"build_base": unique_build_dir("build_base")},
            "bdist_wheel": {"bdist_dir": unique_build_dir("bdist_dir")},
            "editable_wheel": {"dist_dir": unique_build_dir("edist_dir")},
            "egg_info": {"egg_base": unique_build_dir("egg_base")},
            "sdist": {"dist_dir": unique_build_dir("sdist_dir")},
        },
    )
