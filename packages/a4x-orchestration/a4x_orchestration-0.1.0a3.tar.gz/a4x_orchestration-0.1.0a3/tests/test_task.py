# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pathlib

import pytest
from a4x.orchestration.path import Path
from a4x.orchestration.resources import Resources, Slot
from a4x.orchestration.task import JobspecSettings, Task


def test_task_construct():
    name = "test_task"
    description = "This is a test"
    task = Task(name, description)
    assert task.task_name == name
    assert task.description == description
    assert task.exe_path is None
    assert task.args == []
    assert task.cmd is None
    assert task.inputs == []
    assert task.outputs == []
    assert task.add_input_extra_kwargs == {}
    assert task.add_output_extra_kwargs == {}
    assert task.jobspec_settings == JobspecSettings()


def test_set_exe():
    name = "test_task"
    description = "This is a test"
    task = Task(name, description)

    task.set_exe("/usr/bin/bash")
    assert task.exe_path == pathlib.Path("/usr/bin/bash")

    task.set_exe("./test_program")
    assert task.exe_path == pathlib.Path("./test_program")

    task.cmd = "/usr/bin/bash -c 'echo \"Hello World\"'"
    with pytest.raises(RuntimeError):
        task.set_exe("/usr/bin/bash")

    task.cmd = "/usr/bin/bash -c 'echo \"Hello World\"'"
    task.set_exe("/usr/bin/bash", override=True)
    assert task.exe_path == pathlib.Path("/usr/bin/bash")
    assert task.cmd is None


def test_add_args():
    name = "test_task"
    description = "This is a test"
    task = Task(name, description)

    task.set_exe("/usr/bin/bash")
    task.add_args("-c", "'echo \"Hello World\"'")
    assert task.args == ["-c", "'echo \"Hello World\"'"]

    task.exe_path = None
    with pytest.raises(RuntimeError):
        task.add_args("-c", "'echo \"Hello World\"'")


def test_set_command():
    name = "test_task"
    description = "This is a test"
    task = Task(name, description)

    cmd_str = "/usr/bin/bash -c 'echo \"Hello World\"'"

    task.set_command(cmd_str)
    assert task.cmd == cmd_str

    task.exe_path = pathlib.Path("/usr/bin/bash")
    with pytest.raises(RuntimeError):
        task.set_command(cmd_str)

    task.exe_path = pathlib.Path("/usr/bin/bash")
    task.set_command(cmd_str, override=True)
    assert task.cmd == cmd_str
    assert task.exe_path is None
    assert task.args == []


def test_inputs():
    name = "test_task"
    description = "This is a test"
    task = Task(name, description)

    path1 = Path("test1.dat", is_logical=True)
    path2 = Path("test2.dat", is_logical=True)

    task.add_inputs(path1, path2)
    assert task.add_input_extra_kwargs == {}
    assert task.get_inputs() == [path1, path2]

    task.add_inputs(path1, path2, pegasus_dummy_config_var="val")
    assert task.add_input_extra_kwargs == {"pegasus_dummy_config_var": "val"}
    assert task.get_inputs() == [path1, path2]

    with pytest.raises(TypeError):
        task.add_inputs(path1, "test2.dat")

    with pytest.raises(TypeError):
        task.add_inputs(10, path2)

    with pytest.raises(TypeError):
        task.add_inputs(10, "test2.dat")


def test_outputs():
    name = "test_task"
    description = "This is a test"
    task = Task(name, description)

    path1 = Path("test1.dat", is_logical=True)
    path2 = Path("test2.dat", is_logical=True)

    task.add_outputs(path1, path2)
    assert task.add_output_extra_kwargs == {}
    assert task.get_outputs() == [path1, path2]

    task.add_outputs(path1, path2, pegasus_dummy_config_var="val")
    assert task.add_output_extra_kwargs == {"pegasus_dummy_config_var": "val"}
    assert task.get_outputs() == [path1, path2]

    with pytest.raises(TypeError):
        task.add_outputs(path1, "test2.dat")

    with pytest.raises(TypeError):
        task.add_outputs(10, path2)

    with pytest.raises(TypeError):
        task.add_outputs(10, "test2.dat")


def test_jobspec():
    name = "test_task"
    description = "This is a test"
    task = Task(name, description)

    task.duration = "2h"
    assert task.duration == "2h"

    task.duration = 120
    assert task.duration == 120

    task.duration = None
    assert task.duration is None

    with pytest.raises(TypeError):
        task.duration = 2.1  # type: ignore

    with pytest.raises(ValueError):
        task.duration = -1

    task.queue = "pbatch"
    assert task.queue == "pbatch"

    task.queue = None
    assert task.queue is None

    with pytest.raises(TypeError):
        task.queue = 10  # type: ignore

    task.cwd = "~"
    assert task.cwd == pathlib.Path("~").expanduser().resolve()

    task.cwd = pathlib.Path.cwd()
    assert task.cwd == pathlib.Path.cwd()

    task.cwd = None
    assert task.cwd == pathlib.Path.cwd()

    with pytest.raises(TypeError):
        task.cwd = 10  # type: ignore

    base_env = {
        "PATH": "/home/user/bin:$PATH",
        "LD_LIBRARY_PATH": "/path/to/my/lib:$LD_LIBRARY_PATH",
    }

    task.environment = base_env
    assert task.environment == base_env

    task.environment = None
    assert task.environment == {}

    task.environment = base_env
    task.environment["EXTRA_ENV"] = "this is an extra env var"
    base_env["EXTRA_ENV"] = "this is an extra env var"
    assert task.environment == base_env

    with pytest.raises(TypeError):
        task.environment = "str"  # type: ignore

    redirect_file = "file_for_redirect.txt"

    task.stdin = redirect_file
    assert task.stdin == pathlib.Path(redirect_file)

    task.stdin = None
    assert task.stdin is None

    with pytest.raises(TypeError):
        task.stdin = 10  # type: ignore

    task.stdout = redirect_file
    assert task.stdout == pathlib.Path(redirect_file)

    task.stdout = None
    assert task.stdout is None

    with pytest.raises(TypeError):
        task.stdout = 10  # type: ignore

    task.stderr = redirect_file
    assert task.stderr == pathlib.Path(redirect_file)

    task.stderr = None
    assert task.stderr is None

    with pytest.raises(TypeError):
        task.stderr = 10  # type: ignore

    task.set_resources(
        num_procs=16,
        cores_per_proc=1,
        gpus_per_proc=1,
        num_nodes=2,
        allocate_nodes_exclusively=True,
    )
    expected_resources = Resources(
        num_procs=16,
        per_proc_resources=Slot(num_cores=1, num_gpus=1),
        num_nodes=2,
        exclusive=True,
    )
    assert task.get_resources() == expected_resources

    task.set_resources(num_procs=16, exclusive_node_per_proc=True)
    expected_resources = Resources(num_procs=16, per_proc_resources=Slot(num_nodes=1))
    assert task.get_resources() == expected_resources

    task.set_resources(num_procs=16, exclusive_node_per_proc=True)
    expected_resources = Resources(
        num_procs=16,
        per_proc_resources=Slot(num_nodes=1),
    )
    assert task.get_resources() == expected_resources

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs="16",  # type: ignore
            cores_per_proc=1,
            gpus_per_proc=1,
            num_nodes=2,
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs=-16,
            cores_per_proc=1,
            gpus_per_proc=1,
            num_nodes=2,
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs=16,
            cores_per_proc="1",  # type: ignore
            gpus_per_proc=1,
            num_nodes=2,
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs=16,
            cores_per_proc=-1,
            gpus_per_proc=1,
            num_nodes=2,
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs=16,
            cores_per_proc=1,
            gpus_per_proc="1",  # type: ignore
            num_nodes=2,
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs=16,
            cores_per_proc=1,
            gpus_per_proc=-1,
            num_nodes=2,
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs=16,
            cores_per_proc=1,
            gpus_per_proc=1,
            num_nodes="2",  # type: ignore
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(ValueError):
        task.set_resources(
            num_procs=16,
            cores_per_proc=1,
            gpus_per_proc=1,
            num_nodes=-2,
            allocate_nodes_exclusively=True,
        )

    with pytest.raises(TypeError):
        task.set_resources(
            num_procs=16,
            cores_per_proc=1,
            gpus_per_proc=1,
            num_nodes=2,
            allocate_nodes_exclusively="True",  # type: ignore
        )

    with pytest.raises(TypeError):
        task.set_resources(
            num_procs=16,
            exclusive_node_per_proc="True",  # type: ignore
        )

    name = "test_task"
    description = "This is a test"
    task = Task(name, description)

    task.duration = "2h"
    task.queue = "pbatch"
    task.environment = base_env
    task.stdout = redirect_file
    task.set_resources(
        num_procs=16,
        cores_per_proc=1,
        gpus_per_proc=1,
        num_nodes=2,
        allocate_nodes_exclusively=True,
    )

    expected_jobspec_settings = JobspecSettings()
    expected_jobspec_settings.duration = "2h"
    expected_jobspec_settings.queue = "pbatch"
    expected_jobspec_settings.environment = base_env
    expected_jobspec_settings.stdout = pathlib.Path(redirect_file)
    expected_jobspec_settings.resources = Resources(
        num_procs=16,
        per_proc_resources=Slot(num_cores=1, num_gpus=1),
        num_nodes=2,
        exclusive=True,
    )

    assert task.get_jobspec_settings() != "bad string"
    assert task.get_jobspec_settings() == expected_jobspec_settings

    expected_jobspec_settings.stdout = None
    assert task.get_jobspec_settings() != expected_jobspec_settings
