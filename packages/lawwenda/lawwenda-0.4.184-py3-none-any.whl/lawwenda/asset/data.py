# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Data resources.
"""
import os
import pathlib
import typing as t

import lawwenda


data_dir = pathlib.Path(__file__).parent / "-static"

lawwenda_package_dir = pathlib.Path(os.path.realpath(f"{lawwenda.__file__}/.."))

samples_dir = os.path.abspath(f"{lawwenda_package_dir}/../../samples")
if not os.path.isdir(samples_dir):
    samples_dir = None


def find_data_file(name: str, search_dirs: t.Iterable[str]|None = None) -> pathlib.Path|None:
    """
    Return the absolute path of a Lawwenda data file.

    Can return `None` if no such file exists.

    :param name: The name of the file to find.
    :param search_dirs: List of directories to look into. If not specified (as it usually should be), it looks at some
                        usual places.
    """
    if search_dirs is None:
        search_dirs = (data_dir, *((samples_dir,) if samples_dir else ()))
    for search_dir in search_dirs:
        if (path := pathlib.Path(f"{search_dir}/{name}")).exists():
            return path
    return None


def readme_pdf(culture: str) -> pathlib.Path:
    for culture in (culture, "en"):
        if (readme_pdf := data_dir / f"README/{culture}.pdf").exists():
            return readme_pdf
