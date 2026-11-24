# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 13:43:22 2026

@author: Administrator
"""


class MFLINodeInfo:
    """
    A class to hold all information of a node from the MFLI to which the DAQ can subscribe to.

    Parameters
    ----------
    path : str
        The path of the node which can be subscribed to or get data from.
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


    Attributes
    ----------
    path : str
        The path of the node which can be subscribed to or get data from.
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

    def __init__(
        self, path: str, node_type: str, properties: str, unit: str, description: str
    ) -> None:
        self.path: str = path
        self.node_type: str = node_type
        self.properties: str = properties
        self.unit: str = unit
        self.description: str = description

    @classmethod
    def from_dict(cls, info_dict: dict[str, str]) -> MFLINodeInfo:
        """
        Alternative constructor to initialize the class from a information dictonary.

        Parameters
        ----------
        info_dict : dict[str, str]
            The information dictionary the DAQ gives after listing all nodes.

        Returns
        -------
        MFLINodeInfo
            The constructed class.
        """

        return cls(
            info_dict["Node"].lower(),
            info_dict["Type"],
            info_dict["Properties"],
            info_dict["Unit"],
            info_dict["Description"],
        )

    @property
    def readable(self) -> bool:
        """
        Returns if the node is readable or not.

        Returns
        -------
        bool
            True if the node is readable, False if otherwise.
        """

        return "Read" in self.properties

    @property
    def composite(self) -> bool:
        """
        Returns if the datatype consists of further nodes or if it is a simple tpye
        like Integer, Double or String.

        Returns
        -------
        bool
            True if it is a composite datatype, False if otherwise.
        """

        return self.node_type.startswith("ZI")
