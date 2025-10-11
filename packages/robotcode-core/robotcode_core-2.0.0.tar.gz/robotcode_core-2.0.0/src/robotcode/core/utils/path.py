import os
import re
import sys
from pathlib import Path
from typing import Any, Union


def path_is_relative_to(
    path: Union[Path, str, "os.PathLike[Any]"],
    other_path: Union[Path, str, "os.PathLike[Any]"],
) -> bool:
    try:
        Path(path).relative_to(other_path)
        return True
    except ValueError:
        return False


def try_get_relative_path(
    path: Union[str, "os.PathLike[str]"], other_path: Union[str, "os.PathLike[str]", None]
) -> Path:
    if other_path is None:
        return Path(path)
    try:
        return Path(path).relative_to(other_path)
    except ValueError:
        return Path(path)


_RE_DRIVE_LETTER_PATH = re.compile(r"^[a-zA-Z]:")


def normalized_path(path: "Union[str, os.PathLike[str]]") -> Path:
    p = os.path.normpath(os.path.abspath(path))

    if sys.platform == "win32" and _RE_DRIVE_LETTER_PATH.match(str(p)):
        return Path(p[0].upper() + p[1:])

    return Path(p)


def normalized_path_full(path: Union[str, "os.PathLike[str]"]) -> Path:
    p = normalized_path(path)

    orig_parents = list(reversed(p.parents))
    orig_parents.append(p)

    parents = []
    for index, parent in enumerate(orig_parents):
        if parent.exists():
            ps = (
                next((f.name for f in parent.parent.iterdir() if f.samefile(parent)), None)
                if parent.parent is not None and parent.parent != parent
                else parent.name or parent.anchor
            )

            parents.append(ps if ps is not None else parent.name)
        else:
            return Path(*parents, *[f.name for f in orig_parents[index:]])

    return Path(*parents)


def same_file(path1: Union[str, "os.PathLike[str]", Path], path2: Union[str, "os.PathLike[str]", Path]) -> bool:
    try:
        return os.path.samefile(path1, path2)
    except OSError:
        return False
