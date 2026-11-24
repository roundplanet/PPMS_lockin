# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 14:27:07 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mfli_node_info import MFLINodeInfo


class MFLILeafNodeInfo:
    """
    A class to hold all information of a leaf node from the MFLI. This includes nodes,
    which are 'hidden' inside composite classes like ZIDemodSample.

    Parameters
    ----------
    mfli_node_info : MFLINodeInfo
        The information node from the MFLI. For non-composite nodes, this has basically
        the same functionality as this class.
    composite_field : str
        The name of the node, if the node is part of a composite class, otherwise it's
        empty. Default is ""


    Attributes
    ----------
    mfli_node_info : MFLINodeInfo
        The information node from the MFLI. For non-composite nodes, this has basically
        the same functionality as this class.
    composite_field : str
        The name of the node, if the node is part of a composite class, otherwise it's
        empty.
    path : str
        The whole path to the leaf node. If the leaf node is not a composite node,
        then one can subscribe the DAQ to the node, otherwise one need to subscribe to
        the subscribable path.
    path_subscribable : str
        The subscribable path of the node. It's the same as the normal path for
        non-composite nodes, otherwise the path of the node to which the DAQ should be
        subscribed to get the composite data, in which the node is transfered.
    path_streaming : str
        The required path for streaming the node. For composite nodes it is the same
        as path, otherwise the path has to be expanded by '/value'. This is due to
        the polled structure of a non-composite node, which consists of the value
        and the corresponding timestamp.
    node_type : str
        The type of the node, e.g. Double, Integer, String or composite types starting
        with ZI like ZIDemodSample, ZIAuxInSample, ...
    properties : str
        The properties of the node, e.g. Read, Write, Setting or Streaming or a combination
        of these.
    unit : str
        The unit of the value of the node, if available.
    description : str
        A brief description of the node.
    readable : bool
        True if the node is readable, False if otherwise.
    composite : bool
        True if the datatype consists of further entries, False if it is a simple tpye
        like Integer, Double or String.

    """

    def __init__(self, mfli_node_info: MFLINodeInfo, composite_field: str = "") -> None:
        self.mfli_node_info: MFLINodeInfo = mfli_node_info
        self.composite_field: str = composite_field

    @property
    def path(self) -> str:
        """
        The whole path to the leaf node. If the leaf node is not a composite node,
        then one can subscribe the DAQ to the node, otherwise one need to subscribe to
        the subscribable path.

        Returns
        -------
        str
            The whole path to the leaf node.
        """

        if self.composite:
            return self.mfli_node_info.path + "/" + self.composite_field
        return self.mfli_node_info.path

    @property
    def path_subscribable(self) -> str:
        """
        The subscribable path of the node. It's the same as the normal path for
        non-composite nodes, otherwise the path of the node to which the DAQ should be
        subscribed to get the composite data, in which the node is transfered.

        Returns
        -------
        str
            The subscribable path of the node.
        """

        return self.mfli_node_info.path

    @property
    def path_streaming(self) -> str:
        """
        The required path for streaming the node. For composite nodes it is the same
        as path, otherwise the path has to be expanded by '/value'. This is due to
        the polled structure of a non-composite node, which consists of the value
        and the corresponding timestamp.

        Returns
        -------
        str
            The value address of the node in streaming mode.
        """

        if self.composite:
            return self.path
        return self.path + "/value"

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

        if self.mfli_node_info.composite:
            return f"Element of {self.mfli_node_info.node_type}"
        return self.mfli_node_info.node_type

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

        return self.mfli_node_info.properties

    @property
    def unit(self) -> str:
        """
        The unit of the value of the node, if available.

        Returns
        -------
        str
            The unit of the value of the node.
        """

        return self.mfli_node_info.unit

    @property
    def description(self) -> str:
        """
        A brief description of the node.

        Returns
        -------
        str
            A brief description of the node.
        """

        return self.mfli_node_info.description

    @property
    def readable(self) -> bool:
        """
        True if the node is readable, False if otherwise.

        Returns
        -------
        bool
            True if the node is readable, False if otherwise.
        """

        return self.mfli_node_info.readable

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

        return self.mfli_node_info.composite
