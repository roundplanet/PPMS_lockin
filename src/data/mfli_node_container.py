# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 15:43:19 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import json

if TYPE_CHECKING:
    from zhinst.core import ziDAQServer

    from .abstract_mfli_node import AbstractMFLINode

from .mfli_leaf_node import MFLILeafNode


class MFLINodeContainer:

    def __init__(self):
        self._container: list[AbstractMFLINode] = []

    def add(self, mfli_node: AbstractMFLINode, do_sorting: bool = False) -> None:
        if mfli_node not in self._container:
            self._container.append(mfli_node)
        if do_sorting:
            self.sort_by_path()

    def fill(self, daq: ziDAQServer) -> None:
        self._container: list[AbstractMFLINode] = []
        daq_list_nodes_json: str = daq.listNodesJSON("/*")

        MFLILeafNode.populate_container(self, daq_list_nodes_json)

        self.sort_by_path()

    def sort_by_path(self) -> None:
        """
        Sorts the container by the path sort key of the elements.

        Returns
        -------
        None
        """

        self._container.sort(key=lambda node: node.path_sort_key)

    def get_subscribable_paths(self) -> list[str]:
        """
        Gets all subscribable paths inside of the container.

        Returns
        -------
        list[str]
            All subscribable paths inside of the container.
        """

        result: list[str] = []
        for node in self._container:
            result += node.paths_subscribable
        return list(set(result))

    def get_paths(self) -> list[str]:
        """
        Gets all paths inside of the container.

        Returns
        -------
        list[str]
            All paths inside of the container.
        """

        result: list[str] = []
        for node in self._container:
            result += node.paths
        return list(set(result))

    def __iter__(self) -> iter:
        """
        Overrides the internal __iter__ method to enable the iteration through
        the container.

        Returns
        -------
        iter
            The iterator over the container.
        """

        return iter(self._container)

    def __len__(self) -> int:
        """
        Overrides the __len__ method to compute the number of elements in the
        container.

        Returns
        -------
        int
            The number of elements in the container.
        """

        return len(self._container)
