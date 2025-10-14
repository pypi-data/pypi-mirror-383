import importlib
import tempfile
from copy import deepcopy
from enum import Enum

from graphviz import Graph

from pm4py.objects.process_tree.utils import generic
from pm4py.util import exec_utils, constants
from typing import Optional, Dict, Any, Union
from pm4py.objects.process_tree.obj import ProcessTree
import graphviz


class Parameters(Enum):
    FORMAT = "format"
    COLOR_MAP = "color_map"
    ENABLE_DEEPCOPY = "enable_deepcopy"
    FONT_SIZE = "font_size"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"


# maps the operators to the ProM strings
operators_mapping = {"->": "gate_seq", "X": "gate", "+": "gate_and", "*": "loop"}


def get_color(node, color_map):
    """
    Gets a color for a node from the color map

    Parameters
    --------------
    node
        Node
    color_map
        Color map
    """
    if node in color_map:
        return color_map[node]
    return "black"


def repr_tree_2(tree, viz, color_map, parameters):
    font_size = exec_utils.get_param_value(Parameters.FONT_SIZE, parameters, 24)
    font_size = str(font_size)

    this_node_id = str(id(tree))

    if tree.operator is None:
        if tree.label is None:
            viz.node(this_node_id, label='', style='filled', fillcolor='black', shape='square',
                     width='0.4', height='0.4', fixedsize="true")
            # viz.node(this_node_id, "tau", style='filled', fillcolor='black', shape='square', width="0.3", height='0.3', fontsize=font_size)
        else:
            node_color = get_color(tree, color_map)
            viz.node(this_node_id, str(tree.label), color=node_color, fontcolor=node_color, fontsize=font_size)
    else:
        node_color = get_color(tree, color_map)
        image = operators_mapping[str(tree.operator)]
        with importlib.resources.path("powl.visualization.powl.variants.icons", f"{image}.svg") as gimg:
            xor_image = str(gimg)
            viz.node(this_node_id, label="",
                     width='0.6', height='0.6', fixedsize="true", image=xor_image)
        # viz.node(this_node_id, operators_mapping[str(tree.operator)], color=node_color, fontcolor=node_color, fontsize=font_size)

        for child in tree.children:
            repr_tree_2(child, viz, color_map, parameters)

    if tree.parent is not None:
        viz.edge(str(id(tree.parent)), this_node_id, dirType='none', penwidth="2.0")


def apply(tree: ProcessTree, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> graphviz.Graph:
    """
    Obtain a Process Tree representation through GraphViz

    Parameters
    -----------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    gviz
        GraphViz object
    """
    if parameters is None:
        parameters = {}

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    filename.close()

    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)
    rankdir = "TB"

    viz = Graph("pt", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor, 'rankdir': rankdir})
    viz.attr('node', shape='ellipse', fixedsize='false')

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    color_map = exec_utils.get_param_value(Parameters.COLOR_MAP, parameters, {})

    enable_deepcopy = exec_utils.get_param_value(Parameters.ENABLE_DEEPCOPY, parameters, True)

    if enable_deepcopy:
        # since the process tree object needs to be sorted in the visualization, make a deepcopy of it before
        # proceeding
        tree = deepcopy(tree)
        generic.tree_sort(tree)

    repr_tree_2(tree, viz, color_map, parameters)

    viz.attr(overlap='false')
    viz.attr(splines='false')
    viz.format = image_format.replace("html", "plain-ext")

    return viz
