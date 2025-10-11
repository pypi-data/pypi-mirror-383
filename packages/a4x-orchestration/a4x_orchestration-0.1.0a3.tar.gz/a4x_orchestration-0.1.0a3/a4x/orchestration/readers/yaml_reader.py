# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import os
import pathlib

from a4x.orchestration import Path, Task, Workflow
from a4x.orchestration.readers import BaseReader
from a4x.orchestration.resources import Resources, Slot
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class YamlReader(BaseReader):
    def __init__(self):
        super().__init__()

    def read(self, fpath: os.PathLike) -> Workflow:
        config = None
        yaml = YAML()
        with open(fpath, "r") as f:
            config = yaml.load(f)
        if config is None:
            raise RuntimeError("Cannot load YAML config")
        if "workflow" not in config:
            raise KeyError("Required key 'workflow' not found in config")
        wflow_config = config["workflow"]
        if "name" not in wflow_config:
            raise KeyError("Required key 'name' not found under 'workflow' in config")
        wflow = Workflow(wflow_config["name"])
        if "description" in wflow_config:
            wflow.description = wflow_config["description"]
        if "global_environment" in wflow_config:
            wflow.environment = dict(wflow_config["global_environment"])
        forward_edges = {}
        tasks = {}
        if "tasks" not in wflow_config:
            raise KeyError("Required key 'tasks' not found under 'workflow' in config")
        for i, task_config in enumerate(wflow_config["tasks"]):
            for req_key in ("name", "exe_path"):
                if req_key not in task_config:
                    raise KeyError(
                        f"Required key '{req_key}' not found in task config {i}"
                    )
            task = Task(task_config["name"])
            if "description" in task_config:
                task.description = task_config["description"]
            if "exe_path" in task_config:
                task.set_exe(task_config["exe_path"])
                if "args" in task_config:
                    task_args = []
                    for a in task_config["args"]:
                        if isinstance(a, (dict, CommentedMap)):
                            task_args.append(
                                Path(
                                    a["path"],
                                    is_local=a.get("is_local", False),
                                    is_shared=a.get("is_shared", False),
                                    is_scratch=a.get("is_scratch", False),
                                    is_persistent=a.get("is_persistent", False),
                                    is_logical=a.get("is_logical", False),
                                )
                            )
                        else:
                            task_args.append(a)
                    task.add_args(*task_args)
            elif "command" in task_config:
                task.set_command(task_config["command"])
            else:
                raise KeyError(
                    f"Task {i} must have either an executable (in 'exe_path') or a command block (in 'command')"
                )
            if "inputs" in task_config:
                task_inputs = []
                for inp in task_config["inputs"]:
                    task_inputs.append(
                        Path(
                            inp["path"],
                            is_local=inp.get("is_local", False),
                            is_shared=inp.get("is_shared", False),
                            is_scratch=inp.get("is_scratch", False),
                            is_persistent=inp.get("is_persistent", False),
                            is_logical=inp.get("is_logical", False),
                        )
                    )
                input_extra_kwargs = {}
                if "input_extra_kwargs" in task_config:
                    input_extra_kwargs = task_config["input_extra_kwargs"]
                task.add_inputs(*task_inputs, **input_extra_kwargs)
            if "outputs" in task_config:
                task_outputs = []
                for out in task_config["outputs"]:
                    task_outputs.append(
                        Path(
                            out["path"],
                            is_local=out.get("is_local", False),
                            is_shared=out.get("is_shared", False),
                            is_scratch=out.get("is_scratch", False),
                            is_persistent=out.get("is_persistent", False),
                            is_logical=out.get("is_logical", False),
                        )
                    )
                output_extra_kwargs = {}
                if "output_extra_kwargs" in task_config:
                    output_extra_kwargs = task_config["output_extra_kwargs"]
                task.add_outputs(*task_outputs, **output_extra_kwargs)
            if "duration" in task_config:
                task.duration = task_config["duration"]
            if "queue" in task_config:
                task.queue = task_config["queue"]
            if "cwd" in task_config:
                task.cwd = pathlib.Path(task_config["cwd"])
            if "environment" in task_config:
                task.environment = task_config["environment"]
            if "stdin" in task_config:
                task.stdin = pathlib.Path(task_config["stdin"])
            if "stdout" in task_config:
                task.stdout = pathlib.Path(task_config["stdout"])
            if "stderr" in task_config:
                task.stderr = pathlib.Path(task_config["stderr"])
            nodes_per_proc = task_config.get("nodes_per_proc", None)
            cores_per_proc = task_config.get("cores_per_proc", 1)
            gpus_per_proc = task_config.get("cores_per_proc", None)
            per_proc_resources = Slot(
                num_nodes=nodes_per_proc,
                num_cores=cores_per_proc,
                num_gpus=gpus_per_proc,
            )
            if "num_procs" in task_config:
                task.jobspec_settings.resources = Resources(
                    num_procs=task_config["num_procs"],
                    per_proc_resources=per_proc_resources,
                    num_nodes=task_config.get("num_nodes", None),
                    exclusive=task_config.get("exclusive", False),
                )
            tasks[task.task_name] = task
            if "dependencies" in task_config:
                for dep_name in task_config["dependencies"]:
                    if dep_name in forward_edges:
                        forward_edges[dep_name].append(task.task_name)
                    else:
                        forward_edges[dep_name] = [task.task_name]
        wflow.add_tasks(*list(tasks.values()))
        for parent_task_name, children_task_names in forward_edges.items():
            parent_task = tasks[parent_task_name]
            for child_task_name in children_task_names:
                child_task = tasks[child_task_name]
                wflow.add_edge(parent_task, child_task)
        return wflow
