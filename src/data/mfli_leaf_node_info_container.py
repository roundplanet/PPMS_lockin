# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 15:43:19 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import json
from pathlib import Path

from .mfli_node_info import MFLINodeInfo
from .mfli_leaf_node_info import MFLILeafNodeInfo

if TYPE_CHECKING:
    from zhinst.core import ziDAQServer


class MFLILeafNodeInfoContainer:
    """
    A class to hold and organize MFLILeafNodeInfo instances.

    Attributes
    ----------
    _container : list[MFLILeafNodeInfo]
        The container which holds all elements.
    _composite_classes : dict[str, list[str]]
        A dictionary to the elements inside a composite class. It will be loaded
        from a .json file.

    """

    def __init__(self):
        self._container: list[MFLILeafNodeInfo] = []
        self._composite_classes: dict[str, list[str]] = json.loads(
            Path(__file__).with_name("type_fields.json").read_text(encoding="utf-8")
        )

    def add(self, mfli_leaf_node_info: MFLILeafNodeInfo, do_sorting: bool = False) -> None:
        """
        Adds a MFLILeafNodeInfo element to the container if it is not already inside.

        Parameters
        ----------
        mfli_leaf_node_info : MFLILeafNodeInfo
            The MFLILeafNodeInfo element, which should be added.
        do_sorting : bool, optional
            If the container should be sorted after adding the element. The default is False.

        Returns
        -------
        None
        """
        if mfli_leaf_node_info not in self._container:
            self._container.append(mfli_leaf_node_info)
        if do_sorting:
            self.sort_by_path()

    def fill(self, daq: ziDAQServer) -> None:
        """
        Empties the conatiner and fills the container again with all available nodes.

        Parameters
        ----------
        daq : zhinst.core.ziDAQServer
            The DAQ server which is connected towards the data server from which the
            data should be retrieved.

        Returns
        -------
        None
        """
        self._container: list[MFLILeafNodeInfo] = []
        daq_list_nodes_json: str = daq.listNodesJSON("/*")
        if daq_list_nodes_json[-4:] == ",\n}\n":
            daq_list_nodes_json: str = daq_list_nodes_json[:-4] + daq_list_nodes_json[-3:]
        for info_dict in json.loads(daq_list_nodes_json).values():
            mfli_node_info: MFLINodeInfo = MFLINodeInfo.from_dict(info_dict)
            if mfli_node_info.composite:
                try:
                    for composite_field in self._composite_classes[mfli_node_info.node_type]:
                        self.add(MFLILeafNodeInfo(mfli_node_info, composite_field))
                except KeyError:
                    print(f"Don't know the data-type: {mfli_node_info.node_type}")
            else:
                self.add(MFLILeafNodeInfo(mfli_node_info))
        self.sort_by_path()

    def sort_by_path(self) -> None:
        """
        Sorts the container by the path of the elements.

        Returns
        -------
        None
        """

        self._container.sort(key=lambda node: node.path.casefold())

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
            if node.path_subscribable not in result:
                result.append(node.path_subscribable)
        return result

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
            if node.path_subscribable not in result:
                result.append(node.path)
        return result

    def get_composite_fields(self) -> list[str]:
        """
        Gets all the paths of composite fields inside of the container.

        Returns
        -------
        list[str]
            All the paths of composite fields inside of the container.
        """

        result: list[str] = []
        for node in self._container:
            if node.composite:
                result.append(node.path)
        return result

    def get_integer_nodes(self) -> list[str]:
        """
        Gets all the paths of integer nodes inside of the container.

        Returns
        -------
        list[str]
            All the paths of integer nodes inside of the container.
        """

        result: list[str] = []
        for node in self._container:
            if "Integer" in node.node_type:
                result.append(node.path)
        return result

    def get_double_nodes(self) -> list[str]:
        """
        Gets all the paths of double nodes inside of the container.

        Returns
        -------
        list[str]
            All the paths of double nodes inside of the container.
        """

        result: list[str] = []
        for node in self._container:
            if "Double" in node.node_type:
                result.append(node.path)
        return result

    def get_string_nodes(self) -> list[str]:
        """
        Gets all the paths of string nodes inside of the container.

        Returns
        -------
        list[str]
            All the paths of string nodes inside of the container.
        """

        result: list[str] = []
        for node in self._container:
            if "String" in node.node_type:
                result.append(node.path)
        return result

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
