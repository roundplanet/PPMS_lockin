# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 10:36:33 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .mfli_leaf_node_info import MFLILeafNodeInfo


class MFLIDataInterpreter:
    """
    A class to interprete a nested dictionary acquired from an MFLI. With the given
    nodes that should be evaluated from the Lockin response and which standard
    deviation or length of the data should be saved, the unused entries can be
    eliminated.

    Parameters
    ----------
    nodes_to_interprete : list[MFLILeafNodeInfo]
        The list of nodes which data should be taken from the nested dictionary
        of the Lockin.
    nodes_to_evalueate_std : list[MFLILeafNodeInfo]
        The list of nodes which standard deviation of the data from the nested
        dictionary should be saved.
    nodes_to_evaluate_len : list[MFLILeafNodeInfo]
        The list of nodes which lenght of the data from the nested dictionary
        should be saved.

    Attributes
    ----------
    nodes_to_interprete : list[MFLILeafNodeInfo]
        The list of nodes which data should be taken from the nested dictionary
        of the Lockin.
    _nti_path_streaming : dict[str, MFLILeafNodeInfo]
        Maps the streaming path of a node to its MFLILeafNodeInfo item. Is
        neccessary to construct due to composite datatypes.
    nodes_to_evalueate_std : list[MFLILeafNodeInfo]
        The list of nodes which standard deviation of the data from the nested
        dictionary should be saved.
    nodes_to_evaluate_len : list[MFLILeafNodeInfo]
        The list of nodes which lenght of the data from the nested dictionary
        should be saved.

    """

    def __init__(
        self,
        nodes_to_evaluate: list[MFLILeafNodeInfo],
        nodes_to_evaluate_std: list[MFLILeafNodeInfo] | None = None,
        nodes_to_evaluate_len: list[MFLILeafNodeInfo] | None = None,
    ) -> None:

        self.nodes_to_interprete: list[MFLILeafNodeInfo] = nodes_to_evaluate
        self._nti_path_streaming: dict[str, MFLILeafNodeInfo] = {
            nti.path_streaming: nti for nti in self.nodes_to_interprete
        }
        self.nodes_to_evaluate_std: list[MFLILeafNodeInfo] = nodes_to_evaluate_std or []
        self.nodes_to_evaluate_len: list[MFLILeafNodeInfo] = nodes_to_evaluate_len or []

    def flatten_and_evaluate_nested_dict(
        self, nested_dict: dict, parent_key: str = "", sep: str = "/"
    ) -> dict[str, np.ndarray]:
        """
        Flattens the given nested dictionary and returns in the end a flat dictionary, where the
        former path is set as the key, devided with the separation key. It is designed as a
        recursive function.

        Parameters
        ----------
        nested_dict : dict
            The nested dictionary, which should be flattened.
        parent_key : str, optional
            The parent key of the dictionary so far one layer higher. The default is "".
        sep : str, optional
            The string which should separate different layers of the nested dictionary.
            The default is "/".

        Returns
        -------
        dict[str, np.ndarray]
            The flattened dictionary, where in the keys the different layers are divided by the
            separation key.
        """

        result: dict[str, np.ndarray] = {}

        for key, value in nested_dict.items():
            new_key: str = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                result.update(self.flatten_and_evaluate_nested_dict(value, new_key, sep))
            else:
                if "/" + new_key in self._nti_path_streaming.keys():
                    result["/" + new_key]: np.ndarray = value

        return result

    def interprete_nested_dict(self, nested_dict: dict) -> dict[str, float | int | str]:
        """
        Interpretes the nested dictionary. Therefore the data corresponding to the definded nodes
        in the class is read out and if neccessary, the standard deviation and the length of the
        responses are also calculated. In the end there will be a flat dictionary with the node
        streaming paths as the keys and the corresponding value.

        Parameters
        ----------
        nested_dict : dict
            The nested dictionary from the MFLI to evaluate.

        Returns
        -------
        dict[str, float | int | str]
            The flatten dictionary after interpreting.

        Raises
        ------
        ValueError
            If a type from a node is not knwon.
        """

        def determine_type(node_type: str) -> type:
            """
            Determines the type to which the value of a node should be cast from the type of the
            node.

            Parameters
            ----------
            node_type : str
                The type from the node, given by the MFLI.

            Returns
            -------
            type
                The python type to which the value of the node should be casted.

            Raises
            ------
            ValueError
                If a type from a node is not knwon.
            """

            if "Integer" in node_type:
                return int
            if "Double" in node_type:
                return float
            if "Element" in node_type:
                return float
            raise ValueError(f"Unknown node type: {node_type}")

        result: dict[str, float | int | str] = {}
        for path_streaming, value in self.flatten_and_evaluate_nested_dict(nested_dict).items():
            node: MFLILeafNodeInfo = self._nti_path_streaming[path_streaming]
            if isinstance(value, np.ndarray):
                if "String" in node.node_type:
                    result.update({node.path_streaming: str(value[-1])})
                else:
                    result.update(
                        {node.path_streaming: determine_type(node.node_type)(np.mean(value))}
                    )
                    if node in self.nodes_to_evaluate_std:
                        result.update({node.path_streaming + "_std": np.std(value)})
                    if node in self.nodes_to_evaluate_len:
                        result.update({node.path_streaming + "_len": value.shape[0]})
            else:
                if "String" in node.node_type:
                    result.update({node.path_streaming: str(value)})
                else:
                    result.update({node.path_streaming: determine_type(node.node_type)(value)})
                    if node in self.nodes_to_evaluate_std:
                        result.update({node.path_streaming + "_std": 0})
                    if node in self.nodes_to_evaluate_len:
                        result.update({node.path_streaming + "_len": 1})

        return result
