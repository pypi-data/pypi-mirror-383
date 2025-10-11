# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import os
from pathlib import Path
from typing import Dict, Tuple

from a4x.orchestration import Task, Workflow
from jinja2 import Environment, FileSystemLoader


class FluxPlugin:
    def __init__(self, wflow: Workflow):
        self.wflow = wflow
        template_dir = (Path(__file__).parent / "templates").expanduser().resolve()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            lstrip_blocks=True,
            trim_blocks=True,
        )
        self.multi_proc_script_template = self.jinja_env.get_template(
            "multi_proc_script.sh.in"
        )
        self.single_proc_script_template = self.jinja_env.get_template(
            "single_proc_script.sh.in"
        )
        self.batch_script_py_template = self.jinja_env.get_template(
            "batch_script.py.in"
        )

    def generate(
        self, script_out_dir: os.PathLike, use_shell_launcher=False, exist_ok=False
    ):
        out_dir = Path(script_out_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=exist_ok)
        shell_path = str(self.wflow.annotations.get("shell", "/usr/bin/env bash"))
        out_file_map = {}
        for task_tuple in self.wflow.graph.nodes(data="task"):
            _, task = task_tuple
            if task.exe_path is not None:
                task_name, out_file = self._generate_multi_proc_task(
                    out_dir, task, shell_path
                )
                out_file_map[task_name] = out_file
            elif task.cmd is not None:
                task_name, out_file = self._generate_single_proc_task(
                    out_dir, task, shell_path
                )
                out_file_map[task_name] = out_file
            else:
                raise ValueError(
                    f"Either the executable path or command block must be set in the task '{task.task_name}'"
                )
        self._generate_batch_submit_script(
            out_dir, out_file_map, use_shell_launcher, shell_path
        )

    def _generate_multi_proc_task(
        self,
        script_out_dir: Path,
        task: Task,
        shell_path: str,
    ) -> Tuple[str, Path]:
        out_file = script_out_dir / f"{task.task_name}_script.sh"
        resources = task.get_resources()
        resources_dict = None
        if resources is not None:
            resources_dict = {}
            resources_dict["num_procs"] = resources.num_procs
            resources_dict["num_cores"] = resources.resources_per_slot.cores
            resources_dict["num_gpus"] = resources.resources_per_slot.gpus
            resources_dict["num_nodes"] = resources.num_nodes
            resources_dict["exclusive"] = resources.exclusive
            resources_dict["input"] = (
                str(task.stdin) if task.stdin is not None else None
            )
        config = {
            "command": [str(task.exe_path), *task.args],
            "resources": resources_dict,
            "shell": shell_path,
        }
        rendered_script = self.multi_proc_script_template.render(config)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(rendered_script)
        return task.task_name, out_file

    def _generate_single_proc_task(
        self, script_out_dir: Path, task: Task, shell_path: str
    ):
        out_file = script_out_dir / f"{task.task_name}_script.sh"
        config = {
            "cmd": task.cmd.strip(),
            "shell": shell_path,
        }
        rendered_script = self.single_proc_script_template.render(config)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(rendered_script)
        return task.task_name, out_file

    def _generate_batch_submit_script(
        self,
        script_out_dir: Path,
        out_file_map: Dict[str, Path],
        use_shell_launcher: bool,
        shell_path: str,
    ):
        if use_shell_launcher:
            raise NotImplementedError(
                "Shell script generation of driver is not yet supported"
            )
        config = {
            "tasks": [],
            "task_submit_info": [],
        }
        for task_dict in self.wflow.get_tasks_in_topological_order():
            task_dict_vals = list(task_dict.values())
            assert len(task_dict_vals) == 1
            task = task_dict_vals[0]
            resources = task.get_resources()
            if resources is None:
                num_slots = 1
                num_cores = None
                num_gpus = None
                num_nodes = None
                exclusive = False
                duration = None
                environment = None
                cwd = None
                task_output = None
                task_error = None
                queue = None
                bank = None
            else:
                try:
                    num_slots = resources.num_slots_per_node * resources.num_nodes
                except Exception:
                    raise ValueError(
                        "Number of nodes and slots are required to use the Flux plugin"
                    )
                num_cores = resources.resources_per_slot.cores
                num_gpus = resources.resources_per_slot.gpus
                num_nodes = resources.num_nodes
                exclusive = resources.exclusive
                duration = (
                    task.duration
                    if isinstance(task.duration, int)
                    else f'"{task.duration}"'
                )
                environment = (
                    task.environment
                    if isinstance(task.environment, dict) and len(task.environment) > 0
                    else None
                )
                cwd = task.cwd
                task_output = str(task.stdout) if task.stdout is not None else None
                task_error = str(task.stderr) if task.stderr is not None else None
                queue = task.queue
                bank = None  # TODO add support for banks in 'Task'
            task_config = {
                "script": str(out_file_map[task.task_name]),
                "num_slots": num_slots,
                "task_name": task.task_name,
                "num_cores": num_cores,
                "num_gpus": num_gpus,
                "num_nodes": num_nodes,
                "exclusive": exclusive,
                "duration": duration,
                "environment": environment,
                "cwd": cwd,
                "output": task_output,
                "error": task_error,
                "queue": queue,
                "bank": bank,
            }
            task_info = {
                "task_name": task.task_name,
                "dependencies": list(self.wflow.graph.predecessors(task.task_name)),
            }
            config["tasks"].append(task_config)
            config["task_submit_info"].append(task_info)
        rendered_script = self.batch_script_py_template.render(config)
        with open(script_out_dir / "launch.py", "w", encoding="utf-8") as f:
            f.write(rendered_script)
