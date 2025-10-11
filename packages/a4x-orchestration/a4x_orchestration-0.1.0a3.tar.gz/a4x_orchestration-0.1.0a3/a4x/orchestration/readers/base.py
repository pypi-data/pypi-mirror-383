# Copyright 2025 Global Computing Lab.
# See top-level COPYRIGHT file for details.
# 
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import os
from abc import ABC, abstractmethod

from a4x.orchestration import Workflow


class BaseReader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def read(self, fpath: os.PathLike) -> Workflow:
        pass
