# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import json
import os

from a4x.orchestration import Path, PathType, StorageType, Workflow
from a4x.orchestration.writers import BaseWriter
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class YamlWriter(BaseWriter):
    def __init__(self):
        super().__init__()

    def write(self, fpath: os.PathLike, wflow: Workflow):
        config = {"workflow": {"name": wflow.name}}
        if wflow.description is not None and wflow.description != "":
            config["workflow"]["description"] = wflow.description
        if wflow.global_environ is not None and len(wflow.global_environ) != 0:
            config["workflow"]["global_environment"] = dict(wflow.global_environ)
        input_output_map = {}
        task_inputs_outputs = []
        counter = 0
        for inp in wflow.task_inputs:
            if inp not in input_output_map:
                inp_map = CommentedMap()
                inp_map["path"] = str(inp.path)
                inp_map["is_local"] = inp.path_type == PathType.LOCAL
                inp_map["is_shared"] = inp.path_type == PathType.SHARED
                inp_map["is_scratch"] = inp.storage_type == StorageType.SCRATCH
                inp_map["is_persistent"] = inp.storage_type == StorageType.PERSISTENT
                inp_map["is_logical"] = inp.is_logical
                anchor = f"io_path_{counter}"
                inp_map.yaml_set_anchor(anchor, always_dump=True)
                input_output_map[inp] = inp_map
                task_inputs_outputs.append(inp_map)
                counter += 1

        for out in wflow.task_outputs:
            if out not in input_output_map:
                out_map = CommentedMap()
                out_map["path"] = str(out.path)
                out_map["is_local"] = out.path_type == PathType.LOCAL
                out_map["is_shared"] = out.path_type == PathType.SHARED
                out_map["is_scratch"] = out.storage_type == StorageType.SCRATCH
                out_map["is_persistent"] = out.storage_type == StorageType.PERSISTENT
                out_map["is_logical"] = out.is_logical
                anchor = f"io_path_{counter}"
                out_map.yaml_set_anchor(anchor, always_dump=True)
                input_output_map[out] = out_map
                task_inputs_outputs.append(out_map)
                counter += 1

        config["workflow"]["task_inputs_outputs"] = task_inputs_outputs

        config["workflow"]["tasks"] = []
        for key, task in wflow.graph.nodes(data="task"):
            task_config = {"name": task.task_name}
            if task.description is not None and task.description != "":
                task_config["description"] = task.description
            dependencies = list(wflow.graph.predecessors(key))
            if len(dependencies) != 0:
                task_config["dependencies"] = dependencies
            if task.exe_path is not None:
                task_config["exe_path"] = str(task.exe_path)
                task_args = []
                for a in task.args:
                    if isinstance(a, Path):
                        try:
                            task_args.append(input_output_map[a])
                        except KeyError:
                            raise KeyError(
                                f"Cannot substitute Path object in args for YAML alias for task '{key}'"
                            )
                    else:
                        task_args.append(a)
                if len(task_args) != 0:
                    task_config["args"] = task_args
            elif task.cmd is not None:
                task_config["command"] = task.cmd
            else:
                raise RuntimeError(
                    f"Task '{key}' must have either an executable or a command block"
                )
            task_inputs = []
            for inp in task.inputs:
                try:
                    task_inputs.append(input_output_map[inp])
                except KeyError:
                    raise KeyError(
                        f"Cannot substitute input for YAML alias for task '{key}'"
                    )
            if len(task_inputs) != 0:
                task_config["inputs"] = task_inputs
            task_outputs = []
            for out in task.outputs:
                try:
                    task_outputs.append(input_output_map[out])
                except KeyError:
                    raise KeyError(
                        f"Cannot substitute output for YAML alias for task '{key}'"
                    )
            if len(task_outputs) != 0:
                task_config["outputs"] = task_outputs
            if (
                task.add_input_extra_kwargs is not None
                and len(task.add_input_extra_kwargs) != 0
            ):
                task_config["input_extra_kwargs"] = task.add_input_extra_kwargs
            if (
                task.add_output_extra_kwargs is not None
                and len(task.add_output_extra_kwargs) != 0
            ):
                task_config["output_extra_kwargs"] = task.add_output_extra_kwargs
            if task.duration is not None:
                task_config["duration"] = task.duration
            if task.queue is not None:
                task_config["queue"] = task.queue
            if task.cwd is not None:
                task_config["cwd"] = str(task.cwd)
            if task.environment is not None and len(task.environment) != 0:
                task_config["environment"] = task.environment
            if task.stdin is not None:
                task_config["stdin"] = str(task.stdin)
            if task.stdout is not None:
                task_config["stdout"] = str(task.stdout)
            if task.stderr is not None:
                task_config["stderr"] = str(task.stderr)
            if task.jobspec_settings.resources is not None:
                task_config["num_procs"] = task.jobspec_settings.resources.num_procs
                task_config["num_nodes"] = task.jobspec_settings.resources.num_nodes
                task_config["exclusive"] = task.jobspec_settings.resources.exclusive
                slot = task.jobspec_settings.resources.resources_per_slot
                if slot.num_nodes is not None:
                    task_config["nodes_per_proc"] = slot.num_nodes
                if slot.num_cores is not None:
                    task_config["cores_per_proc"] = slot.num_cores
                if slot.num_gpus is not None:
                    task_config["gpus_per_proc"] = slot.num_gpusex
            config["workflow"]["tasks"].append(task_config)

        yaml = YAML()
        with open(fpath, "w") as f:
            yaml.dump(config, f)
