# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pathlib

import pytest
from a4x.orchestration.path import Path, PathType, StorageType


def test_path_construct():
    tmp_path = "./test_file.dat"

    test_path = Path(tmp_path)
    assert test_path.path == pathlib.Path(tmp_path)
    assert not test_path.is_logical_attr
    assert test_path.path_type_attr == PathType.UNKNOWN
    assert test_path.storage_type_attr == StorageType.UNKNOWN

    test_path = Path(tmp_path, is_local=True)
    assert test_path.path == pathlib.Path(tmp_path)
    assert not test_path.is_logical_attr
    assert test_path.path_type_attr == PathType.LOCAL
    assert test_path.storage_type_attr == StorageType.UNKNOWN

    test_path = Path(tmp_path, is_shared=True)
    assert test_path.path == pathlib.Path(tmp_path)
    assert not test_path.is_logical_attr
    assert test_path.path_type_attr == PathType.SHARED
    assert test_path.storage_type_attr == StorageType.UNKNOWN

    test_path = Path(tmp_path, is_scratch=True)
    assert test_path.path == pathlib.Path(tmp_path)
    assert not test_path.is_logical_attr
    assert test_path.path_type_attr == PathType.UNKNOWN
    assert test_path.storage_type_attr == StorageType.SCRATCH

    test_path = Path(tmp_path, is_persistent=True)
    assert test_path.path == pathlib.Path(tmp_path)
    assert not test_path.is_logical_attr
    assert test_path.path_type_attr == PathType.UNKNOWN
    assert test_path.storage_type_attr == StorageType.PERSISTENT

    test_path = Path(tmp_path, is_logical=True)
    assert test_path.path == pathlib.Path(tmp_path)
    assert test_path.is_logical_attr
    assert test_path.path_type_attr == PathType.UNKNOWN
    assert test_path.storage_type_attr == StorageType.UNKNOWN

    with pytest.raises(ValueError):
        test_path = Path(tmp_path, is_local=True, is_shared=True)

    with pytest.raises(ValueError):
        test_path = Path(tmp_path, is_scratch=True, is_persistent=True)

    with pytest.raises(ValueError):
        test_path = Path(pathlib.Path(tmp_path).expanduser().resolve(), is_logical=True)


def test_path_type():
    tmp_path = "./test_file.dat"

    test_path = Path(tmp_path)
    assert test_path.path_type == PathType.UNKNOWN

    test_path.path_type_attr = PathType.LOCAL
    assert test_path.path_type == PathType.LOCAL

    test_path.path_type_attr = PathType.SHARED
    assert test_path.path_type == PathType.SHARED


def test_storage_type():
    tmp_path = "./test_file.dat"

    test_path = Path(tmp_path)
    assert test_path.storage_type == StorageType.UNKNOWN

    test_path.storage_type_attr = StorageType.SCRATCH
    assert test_path.storage_type == StorageType.SCRATCH

    test_path.storage_type_attr = StorageType.PERSISTENT
    assert test_path.storage_type == StorageType.PERSISTENT


def test_is_logical():
    tmp_path = "./test_file.dat"

    test_path = Path(tmp_path)
    assert not test_path.is_logical

    test_path.is_logical_attr = True
    assert test_path.is_logical

    test_path = Path(pathlib.Path(tmp_path).expanduser().resolve())
    assert not test_path.is_logical


def test_absolute():
    tmp_path = "./test_file.dat"

    test_path = Path(tmp_path)
    assert not test_path.is_absolute()

    test_path = Path(pathlib.Path(tmp_path).expanduser().resolve())
    assert test_path.is_absolute()

    # No one should do this, but just in case, test that things still properly fail
    # even if the user does really bad things with the internals
    test_path.is_logical_attr = True
    with pytest.raises(ValueError):
        test_path.is_absolute()

    tmp_path = "./test_file.dat"

    test_path = Path(tmp_path)
    abs_test_path = test_path.absolute()
    assert abs_test_path.path.is_absolute()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_local=True)
    abs_test_path = test_path.absolute()
    assert abs_test_path.path.is_absolute()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_shared=True)
    abs_test_path = test_path.absolute()
    assert abs_test_path.path.is_absolute()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_scratch=True)
    abs_test_path = test_path.absolute()
    assert abs_test_path.path.is_absolute()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_persistent=True)
    abs_test_path = test_path.absolute()
    assert abs_test_path.path.is_absolute()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_logical=True)
    with pytest.raises(RuntimeError):
        test_path.absolute()


def test_expanduser():
    tmp_path = "~/test_file.dat"

    test_path = Path(tmp_path)
    abs_test_path = test_path.expanduser()
    assert "~" not in str(abs_test_path.path)
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_local=True)
    abs_test_path = test_path.expanduser()
    assert "~" not in str(abs_test_path.path)
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_shared=True)
    abs_test_path = test_path.expanduser()
    assert "~" not in str(abs_test_path.path)
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_scratch=True)
    abs_test_path = test_path.expanduser()
    assert "~" not in str(abs_test_path.path)
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_persistent=True)
    abs_test_path = test_path.expanduser()
    assert "~" not in str(abs_test_path.path)
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_logical=True)
    with pytest.raises(RuntimeError):
        test_path.expanduser()


def test_resolve():
    tmp_path = "./test_file.dat"

    test_path = Path(tmp_path)
    abs_test_path = test_path.resolve()
    assert abs_test_path.path.is_absolute() and not abs_test_path.path.is_symlink()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_local=True)
    abs_test_path = test_path.resolve()
    assert abs_test_path.path.is_absolute() and not abs_test_path.path.is_symlink()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_shared=True)
    abs_test_path = test_path.resolve()
    assert abs_test_path.path.is_absolute() and not abs_test_path.path.is_symlink()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_scratch=True)
    abs_test_path = test_path.resolve()
    assert abs_test_path.path.is_absolute() and not abs_test_path.path.is_symlink()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_persistent=True)
    abs_test_path = test_path.resolve()
    assert abs_test_path.path.is_absolute() and not abs_test_path.path.is_symlink()
    assert not abs_test_path.is_logical_attr
    assert abs_test_path.path_type_attr == test_path.path_type_attr
    assert abs_test_path.storage_type_attr == test_path.storage_type_attr

    test_path = Path(tmp_path, is_logical=True)
    with pytest.raises(RuntimeError):
        test_path.resolve()


def test_slash_operator():
    dir_path = "test_dir"
    file_path = "test.dat"

    test_dir = Path(dir_path)
    test_file = Path(file_path)
    merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.UNKNOWN
    assert merged_path.storage_type_attr == StorageType.UNKNOWN
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path)
    test_file = Path(file_path, is_local=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.LOCAL
    assert merged_path.storage_type_attr == StorageType.UNKNOWN
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path)
    test_file = Path(file_path, is_shared=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.SHARED
    assert merged_path.storage_type_attr == StorageType.UNKNOWN
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path)
    test_file = Path(file_path, is_scratch=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.UNKNOWN
    assert merged_path.storage_type_attr == StorageType.SCRATCH
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path)
    test_file = Path(file_path, is_persistent=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.UNKNOWN
    assert merged_path.storage_type_attr == StorageType.PERSISTENT
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_local=True)
    test_file = Path(file_path)
    merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.LOCAL
    assert merged_path.storage_type_attr == StorageType.UNKNOWN
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_shared=True)
    test_file = Path(file_path)
    merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.SHARED
    assert merged_path.storage_type_attr == StorageType.UNKNOWN
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_scratch=True)
    test_file = Path(file_path)
    merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.UNKNOWN
    assert merged_path.storage_type_attr == StorageType.SCRATCH
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_persistent=True)
    test_file = Path(file_path)
    merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.UNKNOWN
    assert merged_path.storage_type_attr == StorageType.PERSISTENT
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_local=True)
    test_file = Path(file_path, is_shared=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.SHARED
    assert merged_path.storage_type_attr == StorageType.UNKNOWN
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_shared=True)
    test_file = Path(file_path, is_local=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.LOCAL
    assert merged_path.storage_type_attr == StorageType.UNKNOWN
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_scratch=True)
    test_file = Path(file_path, is_persistent=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.UNKNOWN
    assert merged_path.storage_type_attr == StorageType.PERSISTENT
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path, is_persistent=True)
    test_file = Path(file_path, is_scratch=True)
    with pytest.warns(RuntimeWarning):
        merged_path = test_dir / test_file
    assert merged_path.path == (test_dir.path / test_file.path)
    assert merged_path.path_type_attr == PathType.UNKNOWN
    assert merged_path.storage_type_attr == StorageType.SCRATCH
    assert not merged_path.is_logical_attr

    test_dir = Path(dir_path)
    test_file = Path(file_path)
    merged_path = test_dir / test_file
    assert not merged_path.is_logical

    test_dir = Path(dir_path).absolute()
    test_file = Path(file_path)
    merged_path = test_dir / test_file
    assert not merged_path.is_logical

    test_dir = Path(dir_path, is_logical=True)
    test_file = Path(file_path, is_logical=False)
    merged_path = test_dir / test_file
    assert merged_path.is_logical

    test_dir = Path(dir_path, is_logical=False)
    test_file = Path(file_path, is_logical=True)
    merged_path = test_dir / test_file
    assert not merged_path.is_logical

    test_dir = Path(dir_path, is_logical=True)
    test_file = Path(file_path, is_logical=True)
    merged_path = test_dir / test_file
    assert merged_path.is_logical

    test_dir = Path(dir_path, is_logical=True)
    merged_path = test_dir / file_path
    assert merged_path.is_logical
