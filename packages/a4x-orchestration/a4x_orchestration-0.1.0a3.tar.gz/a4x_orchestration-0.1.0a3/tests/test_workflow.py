# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import networkx as nx
import pytest
from a4x.orchestration.workflow import Workflow


def test_workflow_construct():
    name = "test_wflow"
    description = "This is a test"
    wflow = Workflow(name, description)
    assert wflow.name == name
    assert wflow.description == description
    assert isinstance(wflow.task_inputs, set) and len(wflow.task_inputs) == 0
    assert isinstance(wflow.task_outputs, set) and len(wflow.task_outputs) == 0
    assert isinstance(wflow.global_environ, dict) and len(wflow.global_environ) == 0
    assert isinstance(wflow.annotations_attr, dict) and len(wflow.annotations_attr) == 0
    assert isinstance(wflow.graph, nx.DiGraph)
    assert len(wflow.graph.nodes) == 0
    assert len(wflow.graph.edges) == 0


def test_workflow_add_tasks(maestro_lulesh_workflow):
    tasks, _, _ = maestro_lulesh_workflow

    wflow = Workflow("add_tasks_test")

    with pytest.raises(
        TypeError, match="Tasks provided to 'add_task' must be of type 'Task'"
    ):
        wflow.add_task("this is not a task")

    wflow.add_tasks(*tasks)

    added_tasks = [n[1] for n in wflow.graph.nodes(data="task")]

    assert len(wflow.graph.nodes) == len(tasks)
    assert sorted(added_tasks) == sorted(tasks)


def test_workflow_add_edge(maestro_lulesh_workflow):
    tasks, edges, _ = maestro_lulesh_workflow
    wflow = Workflow("add_edges_test")

    expected_edges = []
    for src, dests in edges.items():
        for dst in dests:
            wflow.add_edge(src, dst)
            expected_edges.append((src.task_name, dst.task_name))

    added_tasks = [n[1] for n in wflow.graph.nodes(data="task")]

    assert len(wflow.graph.nodes) == len(tasks)
    assert sorted(added_tasks) == sorted(tasks)

    assert len(wflow.graph.edges) == len(expected_edges)
    assert sorted(wflow.graph.edges) == sorted(expected_edges)


def test_workflow_add_dependency(maestro_lulesh_workflow, pegasus_diamond_workflow):
    tasks, edges, _ = maestro_lulesh_workflow
    wflow = Workflow("add_dependency_test")

    expected_edges = []
    for src, dests in edges.items():
        for dst in dests:
            expected_edges.append((src.task_name, dst.task_name))

    bad_src = "this is not a task"
    bad_dests = ["this", "is", "not", "a", "task"]
    with pytest.raises(TypeError):
        wflow.add_dependency(bad_src, [], [])
    with pytest.raises(TypeError):
        wflow.add_dependency(tasks[0], bad_dests, [])
    with pytest.raises(TypeError):
        wflow.add_dependency(tasks[0], [], bad_dests)

    for src, dests in edges.items():
        wflow.add_dependency(src, [], dests)

    added_tasks = [n[1] for n in wflow.graph.nodes(data="task")]

    assert len(wflow.graph.nodes) == len(tasks)
    assert sorted(added_tasks) == sorted(tasks)

    assert len(wflow.graph.edges) == len(expected_edges)
    assert sorted(wflow.graph.edges) == sorted(expected_edges)

    tasks, _, rev_edges = pegasus_diamond_workflow
    wflow2 = Workflow("add_dependency_test_2")

    expected_edges = []
    for dst, srcs in rev_edges.items():
        for src in srcs:
            expected_edges.append((src.task_name, dst.task_name))

    for dst, srcs in rev_edges.items():
        wflow2.add_dependency(dst, srcs, [])

    added_tasks = [n[1] for n in wflow2.graph.nodes(data="task")]

    assert len(wflow2.graph.nodes) == len(tasks)
    assert sorted(added_tasks) == sorted(tasks)

    assert len(wflow2.graph.edges) == len(expected_edges)
    assert sorted(wflow2.graph.edges) == sorted(expected_edges)


def test_workflow_generate_dependencies(pegasus_diamond_workflow):
    tasks, edges, _ = pegasus_diamond_workflow

    wflow = Workflow("generate_dependencies_test")

    wflow.add_tasks(*tasks)

    expected_edges = []
    for src, dests in edges.items():
        for dst in dests:
            wflow.add_edge(src, dst)
            expected_edges.append((src.task_name, dst.task_name))

    with pytest.raises(RuntimeError):
        wflow.generate_dependencies_from_task_inputs_outputs(override=False)

    wflow.generate_dependencies_from_task_inputs_outputs()

    added_tasks = [n[1] for n in wflow.graph.nodes(data="task")]

    assert len(wflow.graph.nodes) == len(tasks)
    assert sorted(added_tasks) == sorted(tasks)

    assert len(wflow.graph.edges) == len(expected_edges)
    assert sorted(wflow.graph.edges) == sorted(expected_edges)


def test_workflow_get_task_by_name(maestro_lulesh_workflow):
    tasks, edges, _ = maestro_lulesh_workflow
    wflow = Workflow("get_task_by_name_test")

    for src, dests in edges.items():
        for dst in dests:
            wflow.add_edge(src, dst)

    task_dict = {t.task_name: t for t in tasks}

    for task_name, task in task_dict.items():
        assert wflow.get_task_by_name(task_name) == task


def test_workflow_size_properties(maestro_lulesh_workflow):
    tasks, edges, _ = maestro_lulesh_workflow
    wflow = Workflow("size_properties_test")

    expected_edges = []
    for src, dests in edges.items():
        for dst in dests:
            wflow.add_edge(src, dst)
            expected_edges.append((src.task_name, dst.task_name))

    assert wflow.num_nodes == len(tasks)
    assert wflow.num_edges == len(expected_edges)
    assert len(wflow) == len(tasks)


def test_workflow_task_inputs_outputs(maestro_lulesh_workflow):
    tasks, edges, _ = maestro_lulesh_workflow
    wflow = Workflow("task_inputs_outputs_test")

    all_inputs = set()
    all_outputs = set()
    per_task_inputs = {t.task_name: t.inputs for t in tasks}
    per_task_outputs = {t.task_name: t.outputs for t in tasks}

    for src, dests in edges.items():
        for dst in dests:
            wflow.add_edge(src, dst)
            all_inputs.update(src.inputs)
            all_inputs.update(dst.inputs)
            all_outputs.update(src.outputs)
            all_outputs.update(dst.outputs)

    assert wflow.task_inputs == all_inputs
    assert wflow.task_outputs == all_outputs
    assert wflow.task_inputs_from_graph == per_task_inputs
    assert wflow.task_outputs_from_graph == per_task_outputs


def test_workflow_root_and_leaf_tasks(maestro_lulesh_workflow):
    _, edges, _ = maestro_lulesh_workflow
    wflow = Workflow("root_and_leaf_tasks_test")

    for src, dests in edges.items():
        for dst in dests:
            wflow.add_edge(src, dst)

    assert wflow.root_tasks == list(edges.keys())
    assert wflow.leaf_tasks == list(edges.values())[0]


def test_workflow_environment():
    wflow = Workflow("environment_test")

    with pytest.raises(
        TypeError, match="The 'environment' property must be a mapping type"
    ):
        wflow.environment = 10

    env = {"PATH": "/home/user/bin"}

    wflow.environment = env.copy()

    assert wflow.environment == env


def test_workflow_annotations():
    wflow = Workflow("annotations_test")

    with pytest.raises(
        TypeError, match="Cannot store a non-Mapping object as annotations"
    ):
        wflow.annotations = 10

    annotations = {"pegasus.dir.useTimestamp": True}

    wflow.annotations = annotations.copy()

    assert wflow.annotations == annotations
