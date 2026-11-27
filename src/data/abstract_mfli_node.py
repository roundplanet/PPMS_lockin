# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 14:05:29 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from functools import cached_property

if TYPE_CHECKING:
    import numpy as np
    from .mfli_node_info import MFLINodeInfo
    from .mfli_leaf_node_info_container import MFLILeafNodeInfoContainer


class AbstractMFLINode:

    def __init__(self, mfli_node_infos: tuple[MFLINodeInfo] | None = None) -> None:
        self.mfli_node_infos: tuple[MFLINodeInfo] = mfli_node_infos or ()

    @classmethod
    def populate_container(cls, container: MFLILeafNodeInfoContainer):
        raise NotImplementedError

    @cached_property
    def paths(self) -> list[str]:
        result: list[str] = []
        for node in self.mfli_node_infos:
            result.append(node.path)
        return result

    @cached_property
    def paths_subscribable(self) -> list[str]:
        result: list[str] = []
        for node in self.mfli_node_infos:
            result.append(node.path)
        return result

    @cached_property
    def paths_streaming(self) -> list[str]:
        result: list[str] = []
        for node in self.mfli_node_infos:
            result.append(node.path + "/value")
        return result

    @cached_property
    def path_sort_key(self) -> str:
        raise NotImplementedError

    @cached_property
    def node_type(self) -> str:
        raise NotImplementedError

    @cached_property
    def properties(self) -> str:
        raise NotImplementedError

    @cached_property
    def unit(self) -> str:
        raise NotImplementedError

    @cached_property
    def readable(self) -> str:
        raise NotImplementedError

    def extract_output(self, flat_dict: dict[str, np.ndarray | float]) -> np.ndarray | float:
        raise NotImplementedError
