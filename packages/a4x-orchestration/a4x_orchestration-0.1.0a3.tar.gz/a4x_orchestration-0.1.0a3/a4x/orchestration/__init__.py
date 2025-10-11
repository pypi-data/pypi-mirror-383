# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import sys

# Although importlib.metadata existed in versions 3.8 and 3.9,
# it was only provisional. The API of importlib.metadata was not
# standardized and made non-provisional until 3.10. So, we
# will depend on importlib_metadata for all versions of Python
# before 3.10 to ensure they all behave the same.
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from typing import List

from a4x.orchestration.path import Path, PathType, StorageType
from a4x.orchestration.task import JobspecSettings, Task
from a4x.orchestration.version import __version__
from a4x.orchestration.workflow import Workflow


def _build_factory_for_builtin_plugins():
    from a4x.orchestration.builtin_plugins.flux import FluxPlugin

    return {"flux": FluxPlugin}


builtin_plugins = _build_factory_for_builtin_plugins()

__wms_plugins = entry_points(group="wms_plugins")


def get_wms_plugin_names() -> List[str]:
    plugin_names = list(builtin_plugins.keys())
    plugin_names.extend(list(__wms_plugins.names))
    return plugin_names


def convert_to_wms_type(
    wflow: Workflow, wms_type: str, ignore_builtin_plugins=False, **kwargs
):
    wms_entrypoint = None
    if not ignore_builtin_plugins and wms_type in builtin_plugins:
        wms_entrypoint = builtin_plugins[wms_type]
    else:
        if wms_type not in __wms_plugins:
            raise KeyError(
                "Cannot convert to a WMS-specific type because there is no plugin called {}".format(
                    wms_type
                )
            )
        wms_entrypoint = __wms_plugins[wms_type].load()
    return wms_entrypoint(wflow, **kwargs)


__all__ = [
    "PathType",
    "StorageType",
    "Path",
    "JobspecSettings",
    "Task",
    "Workflow",
    "get_wms_plugin_names",
    "convert_to_wms_type",
    "__version__",
]
