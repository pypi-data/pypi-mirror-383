# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from __future__ import annotations

import pathlib
from enum import Enum
from typing import Union
from warnings import warn

from a4x.orchestration.utils import StrCompatPathLike


class PathType(Enum):
    UNKNOWN = 0
    LOCAL = 1
    SHARED = 2


class StorageType(Enum):
    UNKNOWN = 0
    SCRATCH = 1
    PERSISTENT = 2


class Path:
    def __init__(
        self,
        p: StrCompatPathLike,
        is_local=False,
        is_shared=False,
        is_scratch=False,
        is_persistent=False,
        is_logical=False,
    ):
        self.path = pathlib.Path(p)
        self.is_logical_attr = is_logical
        if is_logical and self.path.is_absolute():
            raise ValueError("Cannot mark an absolute path as logical")
        if is_local and is_shared:
            raise ValueError("Storage cannot be both local and shared")
        if is_local:
            self.path_type_attr = PathType.LOCAL
        elif is_shared:
            self.path_type_attr = PathType.SHARED
        else:
            self.path_type_attr = PathType.UNKNOWN
        if is_scratch and is_persistent:
            raise ValueError("Storage cannot be both scratch and persistent")
        if is_scratch:
            self.storage_type_attr = StorageType.SCRATCH
        elif is_persistent:
            self.storage_type_attr = StorageType.PERSISTENT
        else:
            self.storage_type_attr = StorageType.UNKNOWN

    @property
    def path_type(self) -> PathType:
        return self.path_type_attr

    @property
    def storage_type(self) -> StorageType:
        return self.storage_type_attr

    @property
    def is_logical(self) -> bool:
        return self.is_logical_attr

    def is_absolute(self) -> bool:
        is_abs = self.path.is_absolute()
        if is_abs and self.is_logical:
            raise ValueError("Path is absolute, but it is marked as logical")
        return is_abs

    def expanduser(self) -> Path:
        if self.is_logical:
            raise RuntimeError("Cannot call 'expanduser' on a logical path")
        new_path = self.path.expanduser()
        new_a4x_path = Path(new_path, is_logical=self.is_logical)
        if self.path_type_attr != PathType.UNKNOWN:
            new_a4x_path.path_type_attr = self.path_type_attr
        if self.storage_type_attr != StorageType.UNKNOWN:
            new_a4x_path.storage_type_attr = self.storage_type_attr
        return new_a4x_path

    def absolute(self) -> Path:
        if self.is_logical:
            raise RuntimeError("Cannot call 'absolute' on a logical path")
        new_path = self.path.absolute()
        new_a4x_path = Path(new_path, is_logical=self.is_logical)
        if self.path_type_attr != PathType.UNKNOWN:
            new_a4x_path.path_type_attr = self.path_type_attr
        if self.storage_type_attr != StorageType.UNKNOWN:
            new_a4x_path.storage_type_attr = self.storage_type_attr
        return new_a4x_path

    def resolve(self, strict=False) -> Path:
        if self.is_logical:
            raise RuntimeError("Cannot call 'absolute' on a logical path")
        new_path = self.path.resolve(strict)
        new_a4x_path = Path(new_path, is_logical=self.is_logical)
        if self.path_type_attr != PathType.UNKNOWN:
            new_a4x_path.path_type_attr = self.path_type_attr
        if self.storage_type_attr != StorageType.UNKNOWN:
            new_a4x_path.storage_type_attr = self.storage_type_attr
        return new_a4x_path

    def __truediv__(self, other: Union[StrCompatPathLike, Path]):
        other_real_path = other
        if isinstance(other, str):
            other_real_path = pathlib.Path(other)
        elif isinstance(other, Path):
            other_real_path = other.path
        merged_real_path = self.path / other_real_path  # type: ignore
        merged_path = Path(
            merged_real_path,
            is_local=False,
            is_shared=False,
            is_scratch=False,
            is_persistent=False,
            is_logical=False,
        )
        if isinstance(other, Path):
            merged_path.path_type_attr = other.path_type_attr
            merged_path.storage_type_attr = other.storage_type_attr
        else:
            merged_path.path_type_attr = PathType.UNKNOWN
            merged_path.storage_type_attr = StorageType.UNKNOWN
        if merged_path.path_type_attr == PathType.UNKNOWN:
            merged_path.path_type_attr = self.path_type_attr
        elif merged_path.path_type_attr != self.path_type_attr:
            warn(
                "Path types of left-hand side and right-hand side do not agree. You should manually set the path type with the 'set_path_type' function.",
                RuntimeWarning,
            )
        if merged_path.storage_type_attr == StorageType.UNKNOWN:
            merged_path.storage_type_attr = self.storage_type_attr
        elif merged_path.storage_type_attr != self.storage_type_attr:
            warn(
                "Storage types of left-hand side and right-hand side do not agree. You should manually set the storage type with the 'set_storage_type' function.",
                RuntimeWarning,
            )
        if merged_path.path.is_absolute():
            merged_path.is_logical_attr = False
        elif isinstance(other, Path) and self.is_logical_attr and other.is_logical_attr:
            merged_path.is_logical_attr = True
        elif self.is_logical_attr:
            merged_path.is_logical_attr = True
        else:
            merged_path.is_logical_attr = False
        return merged_path

    def __hash__(self):
        return hash(
            (
                self.path,
                self.is_logical_attr,
                self.path_type_attr,
                self.storage_type_attr,
            )
        )

    def __eq__(self, other):
        return (
            self.path == other.path
            and self.is_logical_attr == other.is_logical_attr
            and self.path_type_attr == other.path_type_attr
            and self.storage_type_attr == other.storage_type_attr
        )
