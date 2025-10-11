# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from __future__ import annotations

import os
import pathlib
from collections.abc import Mapping
from typing import Any, Dict, List, Optional, Union

from a4x.orchestration.annotations import AnnotationType
from a4x.orchestration.path import Path
from a4x.orchestration.resources import Resources, Slot
from a4x.orchestration.utils import StrCompatPathLike, StrCompatPathLikeForIsInstance


class JobspecSettings:
    """
    A representation of common settings for a workflow task that may be passed to the underlying batch scheduler.

    On HPC systems, batch schedulers allow users to set various properties/settings for their jobs (e.g., a workflow task).
    A4X-Orchestration encodes some of the more common settings in this class. The specific settings encoded are:
    * :code:`duration`: the maximum allowed duration of the task. Some schedulers call this the "time limit"
    * :code:`queue`: the queue to which the task should be submitted. Some schedulers (namely Slurm) call this a "partition"
    * :code:`cwd`: the working directory of the task
    * :code:`environment`: the environment variables to set for the task
    * :code:`stdin`: the file to redirect :code:`stdin` to
    * :code:`stdin`: the file to redirect :code:`stdout` to
    * :code:`stderr`: the file to redirect :code:`stderr` to
    * :code:`resources`: the requested resources for the task
    """

    def __init__(self):
        self.duration: Optional[Union[int, str]] = None
        self.queue: Optional[str] = None
        self.cwd: Optional[pathlib.Path] = None
        self.environment: Dict[str, Any] = {}
        self.stdin: Optional[pathlib.Path] = None
        self.stdout: Optional[pathlib.Path] = None
        self.stderr: Optional[pathlib.Path] = None
        self.resources: Resources = None  # type: ignore

    def __eq__(self, other: object):
        if not isinstance(other, JobspecSettings):
            return False
        are_same = (
            self.cwd == other.cwd
            and self.environment == other.environment
            and self.resources == other.resources
        )
        for opt_member_self, opt_member_other in zip(
            [self.duration, self.queue, self.stdin, self.stdout, self.stderr],
            [other.duration, other.queue, other.stdin, other.stdout, other.stderr],
        ):
            if opt_member_self is None and opt_member_other is None:
                are_same = are_same and True
            elif opt_member_self is not None and opt_member_other is not None:
                are_same = are_same and (opt_member_self == opt_member_other)
            else:
                are_same = are_same and False
        return are_same


class Task(AnnotationType):
    def __init__(self, name: str, description=""):
        super().__init__()
        self.task_name = name
        self.description = description
        # There are two ways to store commands in a Task:
        #  1. Set the executable (i.e., set_exe) and add arguments (i.e., add_args)
        #  2. Set the entire command block with 'add_command'
        #
        # When converting to WMS-specific representation, tools can prioritize one representation
        # over the other.
        self.exe_path = None
        self.args = []
        self.cmd = None
        self.inputs = []
        self.outputs = []
        self.add_input_extra_kwargs = {}
        self.add_output_extra_kwargs = {}
        self.jobspec_settings = JobspecSettings()

    def set_exe(self, exe_path: os.PathLike, override=False):
        if override:
            self.cmd = None
        if self.cmd is not None:
            raise RuntimeError(
                "Cannot set executable when command block is already set. If you really want to set the executable, rerun with 'override=True'"
            )
        self.exe_path = exe_path
        if not isinstance(exe_path, pathlib.Path):
            self.exe_path = pathlib.Path(exe_path)
        self.exe_path.expanduser().resolve()
        return self

    def add_args(self, *args):
        if self.exe_path is None:
            raise RuntimeError("Cannot add arguments when no executable has been set")
        self.args = list(args)
        return self

    def set_command(self, shell_cmd_block: str, override=False):
        if override:
            self.exe_path = None
            self.args = []
        if self.exe_path is not None:
            raise RuntimeError(
                "Cannot set command block when executable is already set. If you really want to set the command block, rerun with 'override=True'"
            )
        self.cmd = shell_cmd_block

    def add_inputs(self, *inputs, **extra_kwargs):
        self.add_input_extra_kwargs = extra_kwargs
        self.inputs = list(inputs)
        if any([not isinstance(i, Path) for i in self.inputs]):
            raise TypeError(
                "All positional arguments to 'add_inputs' should be of type 'a4x.orchestration.path.Path'"
            )
        return self

    def add_outputs(self, *outputs, **extra_kwargs):
        self.add_output_extra_kwargs = extra_kwargs
        self.outputs = list(outputs)
        if any([not isinstance(o, Path) for o in self.outputs]):
            raise TypeError(
                "All positional arguments to 'add_outputs' should be of type 'a4x.orchestration.path.Path'"
            )
        return self

    def get_inputs(self) -> List[Path]:
        return self.inputs

    def get_outputs(self) -> List[Path]:
        return self.outputs

    @property
    def duration(self):
        return self.jobspec_settings.duration

    @duration.setter
    def duration(self, duration: Optional[Union[int, str]]):
        if duration is not None and not isinstance(duration, (int, str)):
            raise TypeError("The 'duration' property must be an int or string")
        if duration is not None and isinstance(duration, int) and duration <= 0:
            raise ValueError(
                "When the 'duration' property is an integer, its value must be positive"
            )
        self.jobspec_settings.duration = duration

    @property
    def queue(self):
        return self.jobspec_settings.queue

    @queue.setter
    def queue(self, q: Optional[str]):
        if q is not None and not isinstance(q, str):
            raise TypeError("The 'queue' property must be set to a string")
        self.jobspec_settings.queue = q

    @property
    def cwd(self):
        return self.jobspec_settings.cwd

    @cwd.setter
    def cwd(self, cwd: Optional[StrCompatPathLike]):
        if cwd is not None and not isinstance(cwd, StrCompatPathLikeForIsInstance):
            raise TypeError(
                "The 'cwd' property must be set to a path-like object or a string"
            )
        self.jobspec_settings.cwd = (
            pathlib.Path(cwd).expanduser().resolve()
            if cwd is not None
            else pathlib.Path.cwd()
        )

    @property
    def environment(self):
        return self.jobspec_settings.environment

    @environment.setter
    def environment(self, environ: Optional[Mapping]):
        if environ is not None and not isinstance(environ, Mapping):
            raise TypeError("The 'environment' property must be a mapping")
        self.jobspec_settings.environment = dict(environ) if environ is not None else {}

    @property
    def stdin(self):
        return self.jobspec_settings.stdin

    @stdin.setter
    def stdin(self, stdin: Optional[StrCompatPathLike]):
        if stdin is not None and not isinstance(stdin, StrCompatPathLikeForIsInstance):
            raise TypeError(
                "The 'stdin' property must be a path-like object or a string"
            )
        self.jobspec_settings.stdin = pathlib.Path(stdin) if stdin is not None else None

    @property
    def stdout(self):
        return self.jobspec_settings.stdout

    @stdout.setter
    def stdout(self, stdout: Optional[StrCompatPathLike]):
        if stdout is not None and not isinstance(
            stdout, StrCompatPathLikeForIsInstance
        ):
            raise TypeError(
                "The 'stdout' property must be a path-like object or a string"
            )
        self.jobspec_settings.stdout = (
            pathlib.Path(stdout) if stdout is not None else None
        )

    @property
    def stderr(self):
        return self.jobspec_settings.stderr

    @stderr.setter
    def stderr(self, stderr: Optional[StrCompatPathLike]):
        if stderr is not None and not isinstance(
            stderr, StrCompatPathLikeForIsInstance
        ):
            raise TypeError(
                "The 'stderr' property must be a path-like object or a string"
            )
        self.jobspec_settings.stderr = (
            pathlib.Path(stderr) if stderr is not None else None
        )

    def set_resources(
        self,
        num_procs: int = 1,
        cores_per_proc: Optional[int] = None,
        gpus_per_proc: Optional[int] = None,
        num_nodes: Optional[int] = None,
        allocate_nodes_exclusively: bool = False,
        exclusive_node_per_proc: bool = False,
    ):
        if not isinstance(num_procs, int) or num_procs <= 0:
            raise ValueError("num_procs must be a non-negative integer")
        if cores_per_proc is not None and (
            not isinstance(cores_per_proc, int) or cores_per_proc <= 0
        ):
            raise ValueError("cores_per_proc must be a non-negative integer or None")
        if gpus_per_proc is not None and (
            not isinstance(gpus_per_proc, int) or gpus_per_proc <= 0
        ):
            raise ValueError("gpus_per_proc must be a non-negative integer or None")
        if num_nodes is not None and (not isinstance(num_nodes, int) or num_nodes <= 0):
            raise ValueError("num_nodes must be a non-negative integer or None")
        if not isinstance(allocate_nodes_exclusively, bool):
            raise TypeError("allocate_nodes_exclusively must be a boolean")
        if not isinstance(exclusive_node_per_proc, bool):
            raise TypeError("exclusive_node_per_proc must be a boolean")
        if exclusive_node_per_proc:
            proc_resources = Slot(num_nodes=1)
            total_num_nodes = num_procs
        else:
            if cores_per_proc is None:
                cores_per_proc = 1
            proc_resources = Slot(num_cores=cores_per_proc, num_gpus=gpus_per_proc)
            total_num_nodes = num_nodes
        self.jobspec_settings.resources = Resources(
            num_procs=num_procs,
            per_proc_resources=proc_resources,
            num_nodes=total_num_nodes,
            exclusive=allocate_nodes_exclusively,
        )
        return self

    def get_resources(self):
        if self.jobspec_settings.resources is None:
            return None
        return self.jobspec_settings.resources.copy()

    def get_jobspec_settings(self):
        return self.jobspec_settings

    def __hash__(self):
        return hash(self.task_name)

    def __eq__(self, other):
        return self.task_name == other.task_name

    def __lt__(self, other):
        return self.task_name < other.task_name
