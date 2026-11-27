# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 14:27:07 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from .mfli_node_info import MFLINodeInfo


from .abstract_mfli_node import AbstractMFLINode


class MFLILeafNode(AbstractMFLINode):

    def __init__(self, mfli_node_info: MFLINodeInfo, composite_field: str = "") -> None:
        super().__init__((mfli_node_info))
        self.composite_field: str = composite_field

    @property
    def paths(self) -> list[str]:
        result: list[str] = []
        for node in self.mfli_node_infos:
            if self.composite:
                result.append(node.path + "/" + self.composite_field)
            else:
                result.append(node.path)
        return result

    @property
    def paths_subscribable(self) -> list[str]:
        return super().paths_subscribable

    @property
    def paths_streaming(self) -> list[str]:
        result: list[str] = []
        for node in self.mfli_node_infos:
            if self.composite:
                result.append(node.path)
            else:
                result.append(node.path + "/value")
        return result

    @property
    def path_sort_key(self) -> str:
        return self.paths[0]

    @property
    def node_type(self) -> str:
        """
        The type of the node, e.g. Double, Integer, String or composite types starting
        with ZI like ZIDemodSample, ZIAuxInSample, ...

        Returns
        -------
        str
            The type of the node.
        """

        if self.composite:
            return f"Element of {self.mfli_node_infos[0].node_type}"
        return self.mfli_node_infos[0].node_type

    @property
    def properties(self) -> str:
        """
        The properties of the node, e.g. Read, Write, Setting or Streaming or a combination
        of these.

        Returns
        -------
        str
            The properties of the node.
        """

        return self.mfli_node_infos[0].properties

    @property
    def unit(self) -> str:
        """
        The unit of the value of the node, if available.

        Returns
        -------
        str
            The unit of the value of the node.
        """

        return self.mfli_node_infos[0].unit

    @property
    def description(self) -> str:
        """
        A brief description of the node.

        Returns
        -------
        str
            A brief description of the node.
        """

        return self.mfli_node_infos[0].description

    @property
    def readable(self) -> bool:
        """
        True if the node is readable, False if otherwise.

        Returns
        -------
        bool
            True if the node is readable, False if otherwise.
        """

        return self.mfli_node_infos[0].readable

    @property
    def composite(self) -> bool:
        """
        True if the datatype consists of further entries, False if it is a simple tpye
        like Integer, Double or String.

        Returns
        -------
        bool
            True if the datatype consists of further entries, False if it is a simple tpye
            like Integer, Double or String.
        """

        return self.mfli_node_infos[0].composite

    def extract_output(self, flat_dict: dict[str, np.ndarray | float]) -> np.ndarray | float:
        return flat_dict[self.paths[0]]
