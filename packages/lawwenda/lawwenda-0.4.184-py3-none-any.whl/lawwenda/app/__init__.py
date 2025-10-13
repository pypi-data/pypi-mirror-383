# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only


def pop_path_info(environ: dict[str, str]) -> str|None:
    path = environ.get("PATH_INFO")
    script_name = environ.get("SCRIPT_NAME", "")
    if not path:
        return None
    stripped_path = path.lstrip("/")
    script_name += "/" * (len(path) - len(stripped_path))
    segment, separator, remaining_path = stripped_path.partition("/")
    environ["PATH_INFO"] = separator + remaining_path
    environ["SCRIPT_NAME"] = script_name + segment
    return segment
