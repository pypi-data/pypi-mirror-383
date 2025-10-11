# This file is part of REANA.
# Copyright (C) 2022, 2023 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Utilities to manage files in a workspace."""

import errno
import os
import re
import stat
from pathlib import Path
from typing import Generator, Union

import wcmatch.glob

from reana_commons.errors import REANAWorkspaceError

# O_NOFOLLOW: do not follow symlinks
# O_NONBLOCK: do not block when opening special files (e.g. pipes)
SAFE_FLAGS = os.O_NOFOLLOW | os.O_NONBLOCK
"""Flags needed to open a fd without following symlinks."""

READ_SAFE_FLAGS = os.O_RDONLY | SAFE_FLAGS
"""Flags to open a fd in read-only mode without following symlinks."""

PathLike = Union[str, Path]


def _validate_path_component(component: str) -> None:
    """Check that a component of a path is valid."""
    if (
        not component
        or os.sep in component
        or os.path.sep in component
        or component in [".", ".."]
    ):
        raise REANAWorkspaceError(f"'{component}' is not a valid path component")


def _open_single_component(name: str, dir_fd: int, flags: int = READ_SAFE_FLAGS) -> int:
    """Open a file contained in a directory."""
    _validate_path_component(name)
    try:
        fd = os.open(name, flags | SAFE_FLAGS, dir_fd=dir_fd)
    except OSError as e:
        if e.errno == errno.ELOOP:
            raise REANAWorkspaceError(f"Opening symlink '{name}' is not allowed")
        raise
    return fd


def open_fd(workspace: PathLike, path: PathLike, flags=READ_SAFE_FLAGS) -> int:
    """Open a fd inside a workspace."""
    path = Path(path)
    fd = os.open(workspace, READ_SAFE_FLAGS)
    for i, part in enumerate(path.parts):
        # parent directories are always opened in read-only mode
        curr_flags = READ_SAFE_FLAGS
        if i + 1 == len(path.parts):
            # the last component of the path is opened with the provided flags
            curr_flags = flags
        try:
            new_fd = _open_single_component(part, dir_fd=fd, flags=curr_flags)
        finally:
            os.close(fd)
        fd = new_fd
    return fd


def open_file(workspace: PathLike, path: PathLike, mode: str = "r"):
    """Open a file inside a workspace."""

    def opener(path, flags):
        fd = open_fd(workspace, path, flags)
        st_mode = os.fstat(fd).st_mode
        if not stat.S_ISREG(st_mode):
            os.close(fd)
            raise REANAWorkspaceError(f"'{path}' is not a regular file")
        return fd

    return open(path, mode=mode, opener=opener)


def delete(workspace: PathLike, path: PathLike) -> int:
    """Delete a file or an empty directory inside a workspace."""
    path = Path(path)
    parent_fd = open_fd(workspace, path.parent)
    try:
        st = os.lstat(path.name, dir_fd=parent_fd)
        st_mode = st.st_mode
        st_size = st.st_size
        if stat.S_ISREG(st_mode) or stat.S_ISLNK(st_mode):
            os.unlink(path.name, dir_fd=parent_fd)
        elif stat.S_ISDIR(st_mode):
            os.rmdir(path.name, dir_fd=parent_fd)
        else:
            raise REANAWorkspaceError(f"'{path}' should be a file or a directory")
    finally:
        os.close(parent_fd)
    return st_size


def move(workspace: PathLike, src: PathLike, dst: PathLike) -> None:
    """Move the file or directory `src` to `dst`."""
    src = Path(src)
    dst = Path(dst)

    # If `dst` already exists and it is a directory, we move `src` inside it
    if is_directory(workspace, dst):
        dst_fd = open_fd(workspace, dst)
        dst_name = src.name
    else:
        dst_fd = open_fd(workspace, dst.parent)
        dst_name = dst.name

    src_fd = None
    try:
        src_fd = open_fd(workspace, src.parent)
        os.replace(src.name, dst_name, src_dir_fd=src_fd, dst_dir_fd=dst_fd)
    finally:
        if src_fd is not None:
            os.close(src_fd)
        if dst_fd is not None:
            os.close(dst_fd)


def lstat(workspace: PathLike, path: PathLike) -> os.stat_result:
    """Get the stat of a file inside a workspace."""
    path = Path(path)
    dir_fd = open_fd(workspace, path.parent)
    try:
        st = os.lstat(path.name, dir_fd=dir_fd)
    finally:
        os.close(dir_fd)
    return st


def makedirs(workspace: PathLike, path: PathLike) -> None:
    """Recursively create directories inside a workspace."""
    path = Path(path)
    fd = os.open(workspace, READ_SAFE_FLAGS)
    for part in path.parts:
        try:
            _validate_path_component(part)
            try:
                os.mkdir(part, dir_fd=fd)
            except FileExistsError:
                pass
            new_fd = _open_single_component(part, dir_fd=fd)
            # TODO: check this is actually a directory?
        finally:
            os.close(fd)
        fd = new_fd
    os.close(fd)


def is_directory(workspace: PathLike, path: PathLike) -> bool:
    """Check whether a path refers to a directory."""
    try:
        st = lstat(workspace, path)
        if stat.S_ISDIR(st.st_mode):
            return True
    except Exception:
        pass
    return False


def walk(
    workspace: PathLike,
    path: PathLike = "",
    topdown: bool = True,
    include_dirs: bool = True,
) -> Generator[str, None, None]:
    """Get the list of entries inside a workspace."""
    root_fd = open_fd(workspace, path)
    path = Path(path)
    try:
        for dirpath, dirnames, filenames, dirfd in os.fwalk(
            dir_fd=root_fd, topdown=topdown
        ):
            for dirname in dirnames:
                if include_dirs:
                    yield str(path.joinpath(dirpath, dirname))
                else:
                    # dirname could be a symlink, if so we return it even if
                    # include_dirs is False, given that we treat symlinks as files
                    try:
                        st = os.lstat(dirname, dir_fd=dirfd)
                    except FileNotFoundError:
                        # we skip this path, as it does not exist anymore
                        continue
                    if stat.S_ISLNK(st.st_mode):
                        yield str(path.joinpath(dirpath, dirname))
            for filename in filenames:
                yield str(path.joinpath(dirpath, filename))
    finally:
        os.close(root_fd)


def iterdir(workspace: PathLike, path: PathLike) -> Generator[str, None, None]:
    """Iterate over the contents of a directory."""
    dir_fd = open_fd(workspace, path)
    path = Path(path)
    try:
        for filename in os.listdir(dir_fd):
            yield str(path / filename)
    finally:
        os.close(dir_fd)


def glob(
    workspace: PathLike, pattern: str, topdown: bool = True, include_dirs: bool = True
) -> Generator[str, None, None]:
    """Get the list of entries in a workspace that match a given pattern."""
    # `wcmatch` returns two lists of regexps, one for "include" and the other
    # for "exclude" patterns. We are only interested in the "include" patterns.
    include_regex, exclude_regex = wcmatch.glob.translate(
        pattern, flags=wcmatch.glob.GLOBSTAR | wcmatch.glob.DOTGLOB
    )
    if len(include_regex) != 1 or len(exclude_regex) != 0:
        raise REANAWorkspaceError("The provided pattern is not valid")
    compiled_regex = re.compile(include_regex.pop())
    for filepath in walk(workspace, topdown=topdown, include_dirs=include_dirs):
        if compiled_regex.match(filepath):
            yield filepath


def glob_or_walk_directory(
    workspace: PathLike,
    path_or_pattern: str,
    topdown: bool = True,
    include_dirs: bool = True,
) -> Generator[str, None, None]:
    """Get the list of entries inside a directory or that match a given pattern."""
    if is_directory(workspace, path_or_pattern):
        yield from walk(workspace, path_or_pattern, topdown, include_dirs)
    else:
        yield from glob(workspace, path_or_pattern, topdown, include_dirs)
