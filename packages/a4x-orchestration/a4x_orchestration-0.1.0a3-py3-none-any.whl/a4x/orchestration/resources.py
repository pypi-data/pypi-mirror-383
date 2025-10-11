# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from __future__ import annotations

from math import ceil
from typing import Any, Dict, Optional
from warnings import warn


class Resources:
    """
    The representation of the resource set for a workflow task.

    This class (and its companion: :py:class:`Slot`) are heavily inspired by the representation of resources for jobs
    in the Flux resource manager. For more information about how Flux represents resources, see Flux's
    `RFC 14 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_14.html#canonical-job-specification>`_.

    A set of resources consists of one or more "slots", which may be evenly divided across a number of nodes, if specified.
    A "slot" represents the resources for each process in the workflow task. In other words, the workflow management system or
    (more likely) the platform's batch scheduler will allocate out the resources for the all the slots and then assign
    one process to each slot.

    Workflow developers should not use this class directly. Instead, they should use the
    :py:meth:`a4x.orchestration.task.Task.set_resources` method.
    """

    def __init__(
        self,
        num_procs: int,
        per_proc_resources: Slot,
        num_nodes: Optional[int] = None,
        exclusive: bool = False,
    ):
        """
        Construct a set of resources.

        :param num_procs: number of processes in the workflow task
        :type num_procs: int
        :param per_proc_resources: resources needed for each process in the workflow task
        :type per_proc_resources: :py:class:`Slot`
        :param num_nodes: total number of nodes that should be allocated to the workflow task. Ignored if nodes are specified in `per_proc_resource`
        :type num_nodes: Optional[int]
        :param exclusive: if ``True``, the workflow task should have exclusive control of the nodes allocated
        :type exclusive: bool
        :raises TypeError: if any input has an invalid type
        :raises ValueError: if `num_nodes` is larger than `num_procs` because that would waste resources
        """
        if not isinstance(num_procs, int):
            raise TypeError("Total number of processes must be an int")
        if num_nodes is not None and not isinstance(num_nodes, int):
            raise TypeError(
                "Number of nodes must be an int (or None when each process gets its own exclusive node)"
            )
        if not isinstance(exclusive, bool):
            raise TypeError("The 'exclusive' parameter must be a boolean")
        if not isinstance(per_proc_resources, Slot):
            raise TypeError("The per-process resources must be of type Slot")
        procs_have_exclusive_nodes = per_proc_resources.nodes is not None
        self.resource_dict = {}
        self.total_num_procs = num_procs
        self.exclusive = exclusive
        if not procs_have_exclusive_nodes and num_nodes is not None:
            if num_nodes > num_procs:
                raise ValueError(
                    "The number of nodes cannot be greater than the number of procs without wasting resources"
                )
            if num_procs % num_nodes != 0:
                warn(
                    f"It is not possible to evenly distribute {num_procs} procs (e.g., MPI ranks) across {num_nodes}",
                    RuntimeWarning,
                )
            self.total_num_nodes = num_nodes
            total_num_slots_per_node = int(ceil(num_procs / float(num_nodes)))
            self.resource_dict = {
                "nodes": {
                    "count": self.total_num_nodes,
                    "with": {
                        "slots": {
                            "count": total_num_slots_per_node,
                            "with": per_proc_resources.copy(),
                        }
                    },
                }
            }
        elif not procs_have_exclusive_nodes:
            self.total_num_nodes = None
            self.resource_dict = {
                "slots": {"count": num_procs, "with": per_proc_resources.copy()}
            }
        else:
            self.total_num_nodes = num_procs
            self.resource_dict = {
                "slots": {"count": num_procs, "with": per_proc_resources.copy()}
            }

    def __eq__(self, other: object) -> bool:
        """
        Checks if one resource set is equal to the other

        :param other: the other resource set
        :type other: :py:class:`Resources`
        :return: ``True`` if equal, ``False`` otherwise
        :rtype: bool
        """
        if not isinstance(other, Resources):
            return False
        if self.total_num_nodes is None:
            are_equal = other.total_num_nodes is None
        else:
            are_equal = (
                other.total_num_nodes is not None
                and self.total_num_nodes == other.total_num_nodes
            )
        return (
            are_equal
            and self.total_num_procs == other.total_num_procs
            and self.resource_dict == other.resource_dict
            and self.exclusive == other.exclusive
        )

    def copy(self):
        """
        Create a new resource set with the same values as :code:`self`

        :return: a copy of the resource set
        :rtype: :py:class:`Resources`
        """
        new_resources = Resources(
            num_procs=self.num_procs,
            per_proc_resources=self.resources_per_slot,
            num_nodes=self.num_nodes,
            exclusive=self.exclusive,
        )
        return new_resources

    @property
    def num_procs(self) -> int:
        """
        Get the number of processes in the resource set

        :return: the number of processes in the resource set
        :rtype: int
        """
        return self.total_num_procs

    @property
    def num_nodes(self) -> Optional[int]:
        """
        Get the number of nodes in the resource set

        :return: the number of nodes in the resource set, or ``None`` if the number of nodes is not specified
        :rtype: Optional[int]
        """
        # If this returns None, then we don't have an explicit number of nodes requested
        return self.total_num_nodes

    @property
    def num_slots_per_node(self) -> Optional[int]:
        """
        Get the number of slots per node in the resource set

        :return: the number of slots per node in the resource set, or ``None`` if the number of nodes is not specified
        :rtype: Optional[int]
        """
        if "slots" in self.resource_dict:
            return 1 if self.total_num_nodes is not None else None
        return self.resource_dict["nodes"]["with"]["slots"]["count"]  # type: ignore

    @property
    def resources_per_slot(self) -> Slot:
        """
        Get the resources for each slot in the resource set

        :return: the resources for each slot in the resource set
        :rtype: :py:class:`Slot`
        """
        if "slots" in self.resource_dict:
            return self.resource_dict["slots"]["with"]
        return self.resource_dict["nodes"]["with"]["slots"]["with"]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the resouce set to a JSON-like dictionary representation that is roughly equivalent to a Flux resource request

        :return: the dictionary representation of the resource set
        :rtype: ``Dict[str, Any]``
        """
        resource_dict: Dict[str, Any] = {"exclusive": self.exclusive}
        resource_dict["resources"] = self.resource_dict.copy()
        if "slots" in self.resource_dict:
            resource_dict["resources"]["slots"]["with"] = self.resource_dict["slots"][
                "with"
            ].to_dict()
        else:
            resource_dict["resources"]["nodes"]["with"]["slots"]["with"] = (
                self.resource_dict["nodes"]["with"]["slots"]["with"].to_dict()
            )
        return resource_dict


class Slot:
    """
    The representation of the resource set of a single process in a workflow task.

    As described with the :py:class:`Resources` class, the concept of a "slot" is heavily inspired
    by the representation of resources for jobs in the Flux resource manager. For more information
    about how Flux represents resources, see Flux's
    `RFC 14 <https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/spec_14.html#canonical-job-specification>`_.
    """

    def __init__(
        self,
        num_nodes: Optional[int] = None,
        num_cores: Optional[int] = None,
        num_gpus: Optional[int] = None,
    ):
        """
        Create a slot with the specified resources.

        :param num_nodes: the number of nodes that each process should have access to. If not ``None``, this value should always be 1
        :type num_nodes: Optional[int]
        :param num_cores: the number of cores that each process should have access to
        :type num_cores: Optional[int]
        :param num_gpus: the number of GPUs that each process should have access to
        :type num_gpus: Optional[int]

        .. note::
           If :code:`num_nodes` is not ``None``, then :code:`num_cores` and :code:`num_gpus` should be ``None``
           because each process will get all the cores and GPUs on the node. Conversely, if :code:`num_cores`
           is not ``None``, then :code:`num_nodes` should be ``None`` because each process is getting less than
           one node's worth of resources. If :code:`num_cores` is not ``None``, then :code:`num_gpus` can either be
           ``None`` (to request no GPUs per process) or an integer (to request that number of GPUs per process).

        .. warning::
           A4X-Orchestration currently does **not** validate the resources you request. If you request more resources
           than are actually available, A4X-Orchestration will happily inject those values into your workflow configuration,
           which will cause your workflow to crash. Users should take care to not request more resources than can be feasibly
           used on the system.
        """
        if num_nodes is not None and not isinstance(num_nodes, int):
            raise TypeError(
                "The number of nodes for a process must be either an int or None"
            )
        if num_cores is not None and not isinstance(num_cores, int):
            raise TypeError(
                "The number of cores for a process must be either an int or None"
            )
        if num_gpus is not None and not isinstance(num_gpus, int):
            raise TypeError(
                "The number of GPUs for a process must be either an int or None"
            )
        if num_nodes is not None and (num_cores is not None or num_gpus is not None):
            raise RuntimeError(
                "INTERNAL ERROR: if each process is getting its own exclusive node, num_cores and num_gpus should not be provided to Slot"
            )
        if num_nodes is not None and num_nodes != 1:
            raise ValueError("Tasks cannot run on more or less than 1 node at a time")
        if num_nodes is None and (num_cores is None or num_cores <= 0):
            raise RuntimeError("INTERNAL ERROR: a process must have some CPU cores")
        if num_gpus is not None and num_gpus <= 0:
            raise ValueError("Number of GPUs must be a positive integer")
        self.num_nodes: Optional[int] = num_nodes
        self.num_cores: Optional[int] = num_cores
        self.num_gpus: Optional[int] = num_gpus

    def __eq__(self, other: object) -> bool:
        """
        Checks if one slot is equal to the other

        :param other: the other slot
        :type other: :py:class:`Slot`
        :return: ``True`` if equal, ``False`` otherwise
        :rtype: bool
        """
        if not isinstance(other, Slot):
            return False
        if self.num_nodes is None:
            are_equal = (
                other.num_nodes is None
                and self.num_cores is not None
                and other.num_cores is not None
                and self.num_cores == other.num_cores
            )
            if self.num_gpus is None:
                are_equal = are_equal and other.num_gpus is None
            else:
                are_equal = (
                    are_equal
                    and other.num_gpus is not None
                    and self.num_gpus == other.num_gpus
                )
        else:
            are_equal = (
                other.num_nodes is not None
                and self.num_nodes == other.num_nodes
                and self.num_cores is None
                and other.num_cores is None
                and self.num_gpus is None
                and other.num_gpus is None
            )
        return are_equal

    def copy(self):
        """
        Create a new slot with the same values as :code:`self`

        :return: a copy of the slot
        :rtype: :py:class:`Slot`
        """
        return Slot(num_nodes=self.nodes, num_cores=self.cores, num_gpus=self.gpus)

    @property
    def nodes(self) -> Optional[int]:
        """
        Get the number of nodes in the slot

        :return: the number of nodes in the slot, or ``None`` if the number of nodes is not specified
        :rtype: Optional[int]
        """
        return self.num_nodes

    @property
    def cores(self) -> Optional[int]:
        """
        Get the number of cores in the slot

        :return: the number of cores in the slot, or ``None`` if the number of cores is not specified
        :rtype: Optional[int]
        """
        return self.num_cores

    @property
    def gpus(self) -> Optional[int]:
        """
        Get the number of GPUs in the slot

        :return: the number of GPUs in the slot, or ``None`` if the number of GPUs is not specified
        :rtype: Optional[int]
        """
        return self.num_gpus

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the slot to a JSON-like dictionary representation that is roughly equivalent to a Flux resource request

        :return: the dictionary representation of the slot
        :rtype: ``Dict[str, Any]``
        """
        resource_dict = {}
        if self.num_nodes is not None:
            resource_dict = {"nodes": {"count": self.num_nodes}}
        else:
            resource_dict = {"cores": {"count": self.num_cores}}
            if self.num_gpus is not None:
                resource_dict.update({"gpus": {"count": self.num_gpus}})
        return resource_dict
