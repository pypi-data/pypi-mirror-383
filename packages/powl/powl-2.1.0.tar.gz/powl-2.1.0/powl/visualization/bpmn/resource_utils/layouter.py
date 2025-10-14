import ast
import itertools
from collections import defaultdict

import subprocess
import shutil
from importlib.resources import files

from enum import Enum
from itertools import product
from typing import Dict, List, Set, Tuple

import networkx as nx
import shapely
from lxml import etree

from powl.visualization.bpmn.resource_utils.pools import Pool
from powl.visualization.bpmn.resource_utils.lanes import Lane


class DockingDirection(Enum):
    """
    This class is used to define the docking directions for the elements
    """

    LEFT = "l"
    RIGHT = "r"
    TOP = "t"
    BOTTOM = "b"


def apply_layouting(content_diagram: str) -> str:
    """
    Apply BPMN auto-layout using the bundled JS script.
    Requires Node.js to be installed and accessible on PATH.
    """

    # Ensure Node.js is available
    node = shutil.which("node")
    if not node:
        raise RuntimeError(
            "Node.js is required but was not found on PATH. "
            "Please install Node.js from https://nodejs.org/."
        )

    # Locate the bundled JS file inside powl/js/
    js_bundle = files("powl") / "js" / "layout.bundle.cjs"

    if not js_bundle.exists():
        raise FileNotFoundError(
            f"Could not find {js_bundle}. "
            "Make sure you ran `npm run build` and copied the bundle into powl/js/."
        )

    # 3. Run Node process with stdin/stdout
    process = subprocess.Popen(
        [node, str(js_bundle)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate(input=content_diagram)

    if process.returncode != 0:
        raise RuntimeError(f"Auto-layout failed (exit {process.returncode}): {stderr.strip()}")

    return stdout


def __pools_to_tasks(
    pools: Dict[str, str], lane_data: Dict[str, str]
) -> Dict[str, set]:
    """
    Convert pools to tasks based on the lane data.

    :param pools: A dictionary where keys are pool names and values are sets of node contents.
    :param lanes: A dictionary where keys are lane names and values are lists of task names.
    :return: A dictionary where keys are pool names and values are sets of task names.
    """
    pool_tasks = defaultdict(list)
    for pool, lanes in pools.items():
        for lane in lanes:
            tasks_to_lane = lane_data.get(lane, [])
            pool_tasks[pool].extend(tasks_to_lane)
    return dict(pool_tasks)


def __color_subgraph(
    graph: nx.DiGraph, start_node: str, end_node: str, coloring: Dict[str, str]
) -> nx.DiGraph:
    """
    Generate a subgraph from start_node to end_node.

    :param graph: The directed graph to extract the subgraph from.
    :param start_node: The starting node of the subgraph.
    :param end_node: The ending node of the subgraph.
    :return: A subgraph containing nodes and edges between start_node and end_node.
    """
    list_of_paths = list(nx.all_simple_paths(graph, source=start_node, target=end_node))
    nodes_in_subgraph = set([node for path in list_of_paths for node in path])
    subgraph = graph.subgraph(nodes_in_subgraph).copy()
    # Check if all of the colored nodes have the same color
    used_colors = [coloring[node] for node in subgraph.nodes if node in coloring]

    if len(set(used_colors)) == 1:
        # Color all nodes in the subgraph with the same color
        color = used_colors[0]
        for node in subgraph.nodes:
            coloring[node] = color

    else:
        # If there are multiple colors/no colors, we fall back to the default coloring
        default_color = coloring.default_factory()
        for node in subgraph.nodes:
            if node not in coloring:
                # If the node is not colored, assign it the default color
                coloring[node] = default_color
    return coloring


def color_graph(graph: nx.DiGraph, pools: Dict[str, List]) -> List[Tuple[str, str]]:
    """
    Color the graph based on the pools.

    :param graph: The directed graph to color.
    :param pools: A dictionary where keys are pool names and values are sets of node contents.
    :return: A list of tuples with node id and color.
    """
    pool_with_most_tasks = max(pools, key=lambda k: len(pools[k]))
    coloring = defaultdict(lambda: pool_with_most_tasks)
    for pool, tasks in pools.items():
        # identify the node with this content
        for task in tasks:
            node_for_task = next(
                (
                    n
                    for n, attr in graph.nodes(data=True)
                    if attr.get("content") == task
                ),
                None,
            )
            if node_for_task:
                # color the node with the pool name
                coloring[node_for_task] = pool
    for node in graph.nodes:
        if node not in coloring.keys():
            if graph.nodes[node].get("type") == "diverging":
                # find its counterpart
                counterparts = graph.nodes[node].get("paired_with")
                for counterpart in counterparts:
                    if counterpart not in coloring.keys():
                        coloring = __color_subgraph(graph, node, counterpart, coloring)
            elif (
                graph.nodes[node].get("type") == "StartEvent"
                or graph.nodes[node].get("type") == "EndEvent"
            ):
                # color it with the most common color, i.e., the color of the pool with most tasks
                coloring[node] = pool_with_most_tasks
    for node in graph.nodes:
        if node not in coloring.keys():
            # If it is still not colored, color it with the most common color
            coloring[node] = pool_with_most_tasks
    return dict(coloring)


def __discover_edges_to_drop(
    G: nx.DiGraph, connected_component: Set[str]
) -> List[Tuple[str, str]]:
    """
    Discover edges to drop between components in the graph.

    :param G: The directed graph to discover edges from.
    :param connected_component: A set of node ids representing the submodel.
    :return: A list of edges to drop.
    """
    edges_to_drop = []
    for u, v in G.edges():
        if (u in connected_component and v not in connected_component) or (
            u not in connected_component and v in connected_component
        ):
            edges_to_drop.append((u, v))
    return edges_to_drop


def __add_intermediate_events_to_graph(G: nx.DiGraph, coloring: dict[str, str]):
    G_new = G.copy()
    coloring_new = coloring.copy()
    edges_in_graph = list(G.edges())
    edges_to_add = []
    edges_to_remove = []
    for u, v in edges_in_graph:
        # Check if the colors of the source (u) and destination (v) nodes are different.
        if coloring.get(u) != coloring.get(v):

            # Define unique names for the new intermediate nodes.
            # Using the original node names makes the new names more readable.
            throw_node_id = f"IntermediateThrowEvent_{hash(u)}_{hash(v)}"
            catch_node_id = f"IntermediateCatchEvent_{hash(u)}_{hash(v)}"

            # Add the new "throw" node to the graph and the coloring dictionary.
            # It inherits the color of the source node (u).
            G_new.add_node(throw_node_id, type="throw")
            coloring_new[throw_node_id] = coloring[u]

            # Add the new "catch" node to the graph and the coloring dictionary.
            # It inherits the color of the destination node (v).
            G_new.add_node(catch_node_id, type="catch")
            coloring_new[catch_node_id] = coloring[v]

            # Schedule the original edge for removal.
            edges_to_remove.append((u, v))

            # Schedule the new sequence of edges to be added.
            edges_to_add.append((u, throw_node_id))
            edges_to_add.append((throw_node_id, catch_node_id))
            edges_to_add.append((catch_node_id, v))

    # Apply all the collected changes to the graph at once.
    G_new.remove_edges_from(edges_to_remove)
    G_new.add_edges_from(edges_to_add)
    return G_new, coloring_new


def parse_xml(xml: bytes | str) -> etree._Element:
    root = None
    if isinstance(xml, str) and xml.startswith(("b'", 'b"')):
        try:
            # ast.literal_eval is the safe way to do this. NEVER use eval().
            xml_bytes = ast.literal_eval(xml)
        except (ValueError, SyntaxError):
            raise ValueError(
                f"Failed to parse string-formatted bytes: {xml_bytes[:100]}..."
            )

        parser = etree.XMLParser(remove_blank_text=True, recover=True, encoding="utf-8")
        root = etree.fromstring(xml_bytes, parser=parser)
    else:
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        root = etree.fromstring(xml.encode("utf-8"), parser)

    # check if root has nsmap
    if not root.nsmap:
        raise ValueError("The provided XML does not contain any namespace mappings.")
    return root


def _to_string(root: etree._Element) -> str:
    return etree.tostring(
        root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    ).decode("utf-8")


def remove_edge_information(root: etree._Element) -> etree._Element:
    """
    Identifies and removes all BPMNEdge elements from the XML tree
    using dynamically discovered namespaces.
    """
    bpmndi_ns = root.nsmap.get("bpmndi")
    if not bpmndi_ns:
        # Handle case where the namespace is not defined
        raise Exception(
            "BPMNDI namespace not found in the document. No edges will be removed."
        )

    edge_tag = f"{{{bpmndi_ns}}}BPMNEdge"
    edges_to_remove = root.findall(f".//{edge_tag}")

    for edge in edges_to_remove:
        parent = edge.getparent()
        if parent is not None:
            parent.remove(edge)

    return root


def identify_edges_id(root: etree._Element) -> List[str]:
    """
    Identifies the edges in the XML output and returns their 'bpmnElement' IDs
    using the findall method.
    """
    bpmndi_ns = root.nsmap.get("bpmndi")
    if not bpmndi_ns:
        raise Exception(
            "BPMNDI namespace not found in the document. Cannot identify edges."
        )

    edge_tag = f"{{{bpmndi_ns}}}BPMNEdge"
    edges = root.findall(f".//{edge_tag}")

    edge_ids = [edge.get("bpmnElement") for edge in edges]

    return [eid for eid in edge_ids if eid is not None]


def get_model_dimensions(root: etree._Element, padding: float = 30) -> Tuple[int, int]:
    """
    Get the dimensions of the model.
    """
    # dc:Bounds x="" and whatever afterwards
    OMGDC_NS = root.nsmap.get("omgdc")

    # For compatibility reasons, also check for "dc" namespace
    if not OMGDC_NS:
        OMGDC_NS = root.nsmap.get("dc")

    if not OMGDC_NS:
        raise Exception(
            "(OMG)DC namespace not found in the document. Cannot determine model dimensions."
        )

    boundaries_tag = f"{{{OMGDC_NS}}}Bounds"
    all_bounds = root.findall(f".//{boundaries_tag}")

    if not all_bounds:
        raise Exception(
            "No Bounds found in the document. Cannot determine model dimensions."
        )

    max_right_edge = 0.0
    max_bottom_edge = 0.0

    for bound in all_bounds:
        if not all(attr in bound.attrib for attr in ["x", "y", "width", "height"]):
            raise Exception("Bounds element missing required attributes.")

        x = float(bound.get("x"))
        y = float(bound.get("y"))
        width = float(bound.get("width"))
        height = float(bound.get("height"))
        max_right_edge = max(max_right_edge, x + width)
        max_bottom_edge = max(max_bottom_edge, y + height)

    return int(max_right_edge + padding), int(max_bottom_edge + padding)


def task_name_to_id(root: etree._Element) -> dict:
    """
    This function takes the xml output and the name of the element and returns the id of the element
    """
    BPMN_NS = root.nsmap.get("bpmn")
    if not BPMN_NS:
        raise Exception(
            "BPMN namespace not found in the document. Cannot map task names to IDs."
        )

    name_to_id = {}

    bpmn_tag = f"{{{BPMN_NS}}}"

    # Tags we want to find
    tags_to_find = [
        "task",
        "startEvent",
        "endEvent",
        "intermediateThrowEvent",
        "intermediateCatchEvent",
    ]
    results_iterators = [root.iterfind(f".//{bpmn_tag}{tag}") for tag in tags_to_find]

    all_elements = itertools.chain.from_iterable(results_iterators)

    for element in all_elements:
        element_id = element.get("id")
        if not element_id:
            continue
        key_name = element.get("name") or element_id
        name_to_id[key_name] = element_id

    return name_to_id


def __get_element_coordinates(
    root: etree._Element, element_id: str
) -> Tuple[float, float]:
    """
    This function takes the xml output and the id of the activity and returns the coordinates of the activity
    """
    ns = root.nsmap
    if "bpmndi" not in ns or "dc" not in ns:
        # Some tools use 'omgdc' as an alias for the 'dc' namespace URI
        if "omgdc" in ns and "dc" not in ns:
            ns["dc"] = ns["omgdc"]
        else:
            raise Exception("BPMNDI or DC namespaces not found.")

    query = f'.//bpmndi:BPMNShape[@bpmnElement="{element_id}"]/dc:Bounds'
    bounds_element = root.find(query, namespaces=ns)
    if bounds_element is not None:
        x = float(bounds_element.get("x"))
        y = float(bounds_element.get("y"))
        width = float(bounds_element.get("width"))
        height = float(bounds_element.get("height"))
        return (x, y, width, height)
    else:
        raise Exception(f"Element with id {element_id} not found in the XML output.")


def __order_structures(
    data: dict, task_name_to_id: dict, root: etree._Element
) -> List[str]:
    sorting = {}
    for structure in data.keys():
        min_x = float("inf")
        activities = data[structure]
        for activity in activities:
            activity_id = task_name_to_id.get(activity)
            if activity_id:
                x = __get_element_coordinates(root, activity_id)[0]
                if x < min_x:
                    min_x = x
        sorting[structure] = min_x
    # Sort them based on the minimal x
    ordered_structures = sorted(sorting, key=sorting.get)
    return ordered_structures


def order_lanes_and_pools(
    pool_data: Dict[str, str],
    lane_data: Dict[str, str],
    task_name_to_id: Dict[str, str],
    root: etree._Element,
) -> List[str]:
    # First, we order the pools
    pools_to_tasks = __pools_to_tasks(pool_data, lane_data)
    ordered_pools = __order_structures(pools_to_tasks, task_name_to_id, root)
    # Then, we order the lanes per pool
    resulting_pool_lane_order = {}
    for pool in ordered_pools:
        relevant_lanes = lane_data.keys() & pool_data[pool]
        filtered_lanes = {
            lane: lane_data[lane] for lane in relevant_lanes if lane in lane_data
        }
        ordered_lanes = __order_structures(filtered_lanes, task_name_to_id, root)
        resulting_pool_lane_order[pool] = ordered_lanes
    return resulting_pool_lane_order


def construct_pools(
    pool_data: Dict[str, List[str]],
    lane_data: Dict[str, List[str]],
    lane_width: int,
    lane_height: int,
    padding=50,
    vertical_padding=30,
) -> List[Pool]:
    """
    This function takes the xml output and the pool data and constructs a list of Pool objects accordingly.
    """
    # get the pools from the xml output
    current_height = 0
    list_of_pools = []
    # get the pool data
    for pool_name in pool_data.keys():
        # get the name of the pool
        lanes = pool_data[pool_name]
        lanes_filtered = {lane: lane_data[lane] for lane in lanes if lane in lane_data}
        constructed_lanes = construct_lanes(
            lanes_filtered, lane_width, lane_height, current_height
        )
        # get the up left and down right coordinates of the pool
        up_left = (0, current_height)
        down_right = (
            lane_width + vertical_padding,
            current_height + lane_height * len(lanes),
        )
        # add the padding accordingly
        list_of_pools.append(Pool(up_left, down_right, pool_name, constructed_lanes))
        current_height += lane_height * len(lanes) + padding
    return list_of_pools


def construct_lanes(
    lane_data: dict,
    lane_width: int,
    lane_height: int,
    current_height: int = 0,
    vertical_padding: int = 30,
) -> List[Lane]:
    """
    This function takes the xml output and the lane data and returns a list of lanes
    """
    # get the lanes from the xml output
    lanes = []
    # get the lane data
    for lane in lane_data.keys():
        # get the name of the lane
        name = lane
        # get the activities of the lane
        activities = lane_data[lane]
        # get the up left and down right coordinates of the lane
        up_left = (vertical_padding, current_height)
        current_height += lane_height
        down_right = (vertical_padding + lane_width, current_height)
        # create a new lane object
        lanes.append(Lane(up_left, down_right, name, activities))
    return lanes


def __edit_element_coordinates(
    root: etree._Element, element_id: str, coordinates: Tuple[float, float]
) -> etree._Element:
    """
    This function takes the xml output and the id of the activity and returns the xml output with the new coordinates
    """
    ns = root.nsmap
    if "dc" not in ns and "omgdc" in ns:
        ns["dc"] = ns["omgdc"]

    if "bpmndi" not in ns or ("dc" not in ns and "omgdc" not in ns):
        raise Exception("Required BPMN namespaces not found.")

    query = f'.//bpmndi:BPMNShape[@bpmnElement="{element_id}"]/dc:Bounds'
    bounds_element = root.find(query, namespaces=ns)

    # 3. If the element is found, modify its attributes IN PLACE.
    if bounds_element is not None:
        new_x, new_y = coordinates
        # .set() is the correct way to change an attribute's value.
        # Attribute values must be strings.
        bounds_element.set("x", str(new_x))
        bounds_element.set("y", str(new_y))
        print(f"Successfully updated coordinates for element '{element_id}'.")
    else:
        raise Exception(
            f"Element with id '{element_id}' not found in the XML. No changes made."
        )
    return root


def __get_y_coordinates_for_alignment(element_id: str, xml_output, lanes) -> float:
    """
    This function retrieves the y-coordinate for aligning an element based on its neighbors.
    """
    element_coordinates = __get_element_coordinates(xml_output, element_id)
    if not element_coordinates:
        return None
    # returns the middle y-coordinate of the element
    y_coordinate = element_coordinates[1] + element_coordinates[3] / 2
    corresponding_lane = next(
        (lane for lane in lanes if element_id in lane.get_elements()), None
    )
    return y_coordinate, corresponding_lane


def __check_intersection(shape1, shape2):
    """This function takes two shapes and returns True if they intersect"""
    return shape1.intersects(shape2)


def __update_sequence_flow_positions(
    sequence_flow_id, control_flow, root: etree._Element
) -> etree._Element:
    """
    This function takes the control flow and the xml output and returns the xml output with the new coordinates
    """
    ns = root.nsmap

    DI_NS_URI = "http://www.omg.org/spec/DD/20100524/DI"

    dc_ns = ns.get("dc") or ns.get("omgdc")
    xsi_ns = ns.get("xsi")

    if not all([dc_ns, xsi_ns]):
        raise Exception(
            "Error: Required namespaces (dc, xsi) not found in the document."
        )

    # Find the specific BPMNEdge element using an XPath query
    query = f'.//bpmndi:BPMNEdge[@bpmnElement="{sequence_flow_id}"]'
    edge_element = root.find(query, namespaces=ns)

    if edge_element is None:
        raise Exception(f"No match found for sequence flow {sequence_flow_id}")

    saved_attributes = dict(edge_element.attrib)
    edge_element.clear()
    edge_element.attrib.update(saved_attributes)  # Restore attributes after clear

    # Create and append the new waypoint elements.
    for x_val, y_val in control_flow:
        etree.SubElement(
            edge_element,
            f"{{{DI_NS_URI}}}waypoint",
            attrib={f"{{{xsi_ns}}}type": "dc:Point", "x": str(x_val), "y": str(y_val)},
        )
    etree.register_namespace("di", DI_NS_URI)

    return root


def __get_midway_point(
    bounds: Tuple[float, float, float, float]
) -> Tuple[float, float]:
    """
    This function takes the coordinates of the element and returns the middle point
    """
    x1, y1, width, height = bounds
    x = x1 + width / 2
    y = y1 + height / 2
    return (x, y)


def __find_location_of_flow(
    source_bounds: Tuple[float, float, float, float],
    target_bounds: Tuple[float, float, float, float],
) -> str:
    """
    This function takes the coordinates of the source and target and returns the location of the flow
    """
    # Use the centroids
    source_x, source_y = __get_midway_point(source_bounds)
    target_x, target_y = __get_midway_point(target_bounds)
    # Check the direction of the flow
    flow_direction = ""
    if source_x < target_x:
        flow_direction += "r"
    elif source_x > target_x:
        flow_direction += "l"
    if source_y < target_y:
        flow_direction += "u"
    elif source_y > target_y:
        flow_direction += "d"
    return flow_direction


def __get_docking_point(
    bounds: Tuple[float, float, float, float], docking_direction: DockingDirection
) -> Tuple[float, float]:
    """
    This function takes the direction and the coordinates of the element and returns the docking point
    """
    midway_point = __get_midway_point(bounds)
    _, _, width, height = bounds
    if docking_direction == DockingDirection.LEFT:
        return (midway_point[0] - width / 2, midway_point[1])
    elif docking_direction == DockingDirection.RIGHT:
        return (midway_point[0] + width / 2, midway_point[1])
    elif docking_direction == DockingDirection.TOP:
        return (midway_point[0], midway_point[1] + height / 2)
    elif docking_direction == DockingDirection.BOTTOM:
        return (midway_point[0], midway_point[1] - height / 2)


def __check_for_path_intersection(
    path: shapely.MultiLineString,
    shapes: List[shapely.box],
    source_shape: shapely.box,
    target_shape: shapely.box,
) -> bool:
    """
    This function takes the path and the shapes and returns True if the path intersects with any of the shapes
    """
    # Construct a list of all the shapes
    for shape in shapes:
        if __check_intersection(path, shape) or path.touches(shape):
            return True

    # Check if the intersection with the source and target is a point
    intersection_with_src = shapely.intersection(path, source_shape)
    intersection_with_tgt = shapely.intersection(path, target_shape)
    if intersection_with_src.is_empty and intersection_with_tgt.is_empty:
        return False
    elif isinstance(intersection_with_src, shapely.geometry.Point) and isinstance(
        intersection_with_tgt, shapely.geometry.Point
    ):
        return False
    return True


def __construct_auxiliary_points(
    path_start: Tuple[float, float],
    path_end: Tuple[float, float],
    docking_pt_src: DockingDirection,
    docking_pt_tgt: DockingDirection,
    offset,
) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    set_docking_pts = set([docking_pt_src, docking_pt_tgt])
    # TO BE REWRITTEN
    possible_aux_point_1, possible_aux_point_2 = [], []
    if path_start[0] == path_end[0] or path_start[1] == path_end[1]:
        # Base case, just return none twice
        possible_aux_point_1.append(None)
        possible_aux_point_2.append(None)
    # Now, let's try S-shape
    if set_docking_pts == {DockingDirection.LEFT, DockingDirection.RIGHT}:
        # S-shaped curvature with vertical twist
        aux_pt_1 = (path_start[0] + path_end[0]) / 2, path_start[1]
        aux_pt_2 = (path_start[0] + path_end[0]) / 2, path_end[1]
        possible_aux_point_1.append(aux_pt_1)
        possible_aux_point_2.append(aux_pt_2)
    elif set_docking_pts == {DockingDirection.TOP, DockingDirection.BOTTOM}:
        # S-shaped curvature with horizontal twist
        aux_pt_1 = path_start[0], (path_start[1] + path_end[1]) / 2
        aux_pt_2 = path_end[0], (path_start[1] + path_end[1]) / 2
        possible_aux_point_1.append(aux_pt_1)
        possible_aux_point_2.append(aux_pt_2)
    # A C-shape is only possible if the docking points are the same
    elif docking_pt_src == docking_pt_tgt:
        if docking_pt_src in {DockingDirection.LEFT, DockingDirection.RIGHT}:
            # C-shaped curvature with vertical twist
            aux_pt_1 = (path_start[0] + path_end[0]) / 2, path_start[1] + offset
            aux_pt_2 = (path_start[0] + path_end[0]) / 2, path_end[1] + offset
            possible_aux_point_1.append(aux_pt_1)
            possible_aux_point_2.append(aux_pt_2)
            # Minus outset, too
            aux_pt_1 = (path_start[0] + path_end[0]) / 2, path_start[1] - offset
            aux_pt_2 = (path_start[0] + path_end[0]) / 2, path_end[1] - offset
            possible_aux_point_1.append(aux_pt_1)
            possible_aux_point_2.append(aux_pt_2)
        else:
            # C-shaped curvature with horizontal twist
            aux_pt_1 = path_start[0] + offset, (path_start[1] + path_end[1]) / 2
            aux_pt_2 = path_end[0] + offset, (path_start[1] + path_end[1]) / 2
            possible_aux_point_1.append(aux_pt_1)
            possible_aux_point_2.append(aux_pt_2)
            # Minus outset, too
            aux_pt_1 = path_start[0] - offset, (path_start[1] + path_end[1]) / 2
            aux_pt_2 = path_end[0] - offset, (path_start[1] + path_end[1]) / 2
            possible_aux_point_1.append(aux_pt_1)
            possible_aux_point_2.append(aux_pt_2)

    # We have two possibilities here, we add both
    # 1. L-shaped with (x1, y2)
    possible_aux_point_1.append((path_start[0], path_end[1]))
    possible_aux_point_2.append(None)
    # 2. L-shaped with (x2, y1)
    possible_aux_point_1.append(None)
    possible_aux_point_2.append((path_end[0], path_start[1]))

    return possible_aux_point_1, possible_aux_point_2


def __get_docking_point_name(
    docking_point: Tuple[float, float], figure: Tuple[float, float, float, float]
) -> str:
    """
    This function takes the docking point and the figure and returns the name of the docking point
    """
    # Get the coordinates of the figure
    x1, y1, width, height = figure
    if docking_point[0] == x1 + width / 2 and docking_point[1] == y1:
        return DockingDirection.TOP
    elif docking_point[0] == x1 + width / 2 and docking_point[1] == y1 + height:
        return DockingDirection.BOTTOM
    elif docking_point[0] == x1 and docking_point[1] == y1 + height / 2:
        return DockingDirection.LEFT
    elif docking_point[0] == x1 + width and docking_point[1] == y1 + height / 2:
        return DockingDirection.RIGHT
    else:
        raise ValueError("Provided point is not a docking point")


def __turn_points_into_multi_linestring(
    points: List[Tuple[float, float]]
) -> shapely.MultiLineString:
    """
    This function takes a list of points (tuples) and returns a MultiLineString object
    """
    # First, turn them into LineStrings
    lines = []
    for i in range(len(points) - 1):
        line = shapely.LineString([points[i], points[i + 1]])
        lines.append(line)
    # Now, turn them into a MultiLineString
    return shapely.MultiLineString(lines)


def __check_for_flow_connectivity(
    current_path: List, prev_paths: List[List[Tuple[float, float]]]
) -> bool:
    outgoing_docking_points = [path[0] for path in prev_paths]
    incoming_docking_points = [path[-1] for path in prev_paths]
    return (
        current_path[0] in incoming_docking_points
        or current_path[-1] in outgoing_docking_points
    )


def __construct_possible_paths(
    source_docking_points: List[Tuple[float, float]],
    target_docking_points: List[Tuple[float, float]],
    shapes_to_consider: List,
    source_coords: Tuple[float, float, float, float],
    target_coords: Tuple[float, float, float, float],
    prev_paths: List[List[Tuple[float, float]]],
) -> List[shapely.LineString]:
    """
    This function takes the docking points of the source and target and returns the first suitable path
    That does not intersect with any of the shapes
    """
    paths = product(source_docking_points, target_docking_points)
    possible_full_paths = []
    backup_path = None
    source_shape = shapely.box(
        source_coords[0],
        source_coords[1],
        source_coords[0] + source_coords[2],
        source_coords[1] + source_coords[3],
    )
    target_shape = shapely.box(
        target_coords[0],
        target_coords[1],
        target_coords[0] + target_coords[2],
        target_coords[1] + target_coords[3],
    )
    remaining_shapes = [
        shape
        for shape in shapes_to_consider
        if not shapely.equals(shape, source_shape)
        and not shapely.equals(shape, target_shape)
    ]
    # Get target height for outset
    offset = 1.5 * max(target_coords[3], source_coords[3])
    for src, target in paths:
        # Check if the path intersects with any of the shapes
        docking_pt_source = __get_docking_point_name(src, source_coords)
        docking_pt_target = __get_docking_point_name(target, target_coords)
        auxiliary_point_1, auxiliary_point_2 = __construct_auxiliary_points(
            src, target, docking_pt_source, docking_pt_target, offset
        )
        for i in range(len(auxiliary_point_1)):
            points_to_add = []
            if auxiliary_point_1[i] is not None:
                points_to_add.append(auxiliary_point_1[i])
            if auxiliary_point_2[i] is not None:
                points_to_add.append(auxiliary_point_2[i])
            constructed_path = [src, *points_to_add, target]
            multilane_path = __turn_points_into_multi_linestring(constructed_path)
            backup_path = constructed_path
            if not __check_for_path_intersection(
                multilane_path, remaining_shapes, source_shape, target_shape
            ):
                # If it does not intersect, we can add it to the list
                possible_full_paths.append(
                    (
                        constructed_path,
                        __check_for_flow_connectivity(constructed_path, prev_paths),
                    )
                )

    if len(possible_full_paths) != 0:
        # First, sort them by the boolean argument, then by length of the path
        possible_full_paths = sorted(
            possible_full_paths, key=lambda x: (x[1], len(x[0]))
        )
        return possible_full_paths[0][0]
    print("No suitable path found, returning backup path")
    return backup_path


def connect_points(
    source_coords,
    target_coords,
    shapes: List[shapely.box],
    prev_paths: List[List[Tuple[float, float]]],
) -> Tuple[Tuple[float, float]]:
    """
    This function takes the source and target shapes and returns the docking point
    """
    # Check the direction of the flow
    __find_location_of_flow(source_coords, target_coords)
    possible_directions = [
        DockingDirection.LEFT,
        DockingDirection.RIGHT,
        DockingDirection.TOP,
        DockingDirection.BOTTOM,
    ]
    possible_docking_points_src = [
        __get_docking_point(source_coords, direction)
        for direction in possible_directions
    ]
    possible_docking_points_tgt = [
        __get_docking_point(target_coords, direction)
        for direction in possible_directions
    ]

    path = __construct_possible_paths(
        possible_docking_points_src,
        possible_docking_points_tgt,
        shapes,
        source_coords,
        target_coords,
        prev_paths,
    )

    return path


def __handle_sequence_flows(root: etree._Element, shapes: List[object]):
    """
    This function takes the xml output and the lanes and returns the xml output with the sequence flows
    """
    # Get the sequence flows
    flows = []
    ns = root.nsmap
    if "bpmn" not in ns:
        raise Exception(
            "BPMN namespace not found in the document. Cannot process sequence flows."
        )

    flow_elements = root.xpath("//bpmn:sequenceFlow", namespaces=ns)

    for flow in flow_elements:
        flow_id = flow.get("id")
        source_ref = flow.get("sourceRef")
        target_ref = flow.get("targetRef")
        flows.append((flow_id, source_ref, target_ref))
    connections_dict = {
        seq_flow: (source, target) for seq_flow, source, target in flows
    }
    # Get rid of previous sequence flows so we can add the new ones w/o any issues
    prev_paths = []
    message_flows = []
    for seq_flow, (source, target) in connections_dict.items():
        src_coords = __get_element_coordinates(root, source)
        tgt_coords = __get_element_coordinates(root, target)
        if "Intermediate" in source and "Intermediate" in target:
            # Intermediate events are not connected with sequence flows, but with message flows
            message_flows.append((seq_flow, source, target))
        # Should be embedded here though
        path = connect_points(src_coords, tgt_coords, shapes, prev_paths)
        print(f"I have found a new path for {seq_flow}: {path}")
        prev_paths.append(path)
        root = __update_sequence_flow_positions(seq_flow, path, root)
    return root, message_flows


def __align_tasks(
    lanes: List[Lane], xml_output: str, task_dict: Dict[str, str]
) -> Tuple[str, List[str]]:
    aligned_elements = []
    for lane in lanes:
        # get the up left and down right coordinates of the lane
        up_left = lane.get_up_left()
        activities = lane.get_activities()
        for activity in activities:
            # get the id of the activity
            id_activity = task_dict[activity]
            aligned_elements.append(id_activity)
            lane.add_element(id_activity)
            # edit the coordinates of the task
            task_coordinates = __get_element_coordinates(xml_output, id_activity)
            new_coordinates = (task_coordinates[0], task_coordinates[1] + up_left[1])
            xml_output = __edit_element_coordinates(
                xml_output, id_activity, new_coordinates
            )

    return xml_output, aligned_elements


def __identify_nearest_aligned_element(
    element_id: str,
    aligned_pool_elements: List[str],
    lanes: List[Lane],
    xml_output: str,
) -> str:
    """
    This function identifies the nearest aligned element in the pool.
    """
    min_x_distance = float("inf")
    nearest_element = None
    current_element_coordinates = __get_element_coordinates(xml_output, element_id)
    for aligned_element in aligned_pool_elements:
        element_coordinates = __get_element_coordinates(xml_output, aligned_element)
        if element_coordinates is None:
            continue
        x_distance = abs(current_element_coordinates[0] - element_coordinates[0])
        if x_distance < min_x_distance:
            min_x_distance = x_distance
            nearest_element = aligned_element
    # Identify to which lane it belongs

    return nearest_element


def __align_elements(
    xml_output: str,
    coloring: Dict[str, str],
    aligned_elements: List[str],
    lanes: List[Lane],
) -> Tuple[str, List[str]]:
    """ """
    for el_id, color in coloring.items():
        if el_id in aligned_elements:
            continue
        # Otherwise, we need to locate the nearest element within the same pool
        aligned_elements_within_pool = [
            el for el in aligned_elements if coloring.get(el) == color
        ]
        print(aligned_elements_within_pool)
        nearest_pool_element = __identify_nearest_aligned_element(
            el_id, aligned_elements_within_pool, lanes, xml_output
        )
        print(
            f"Element {el_id} is not aligned, nearest element is {nearest_pool_element}\n"
            f"Elements in the same pool are {aligned_elements_within_pool}\n"
            f"Color is {color} and already aligned elements are {aligned_elements} with coloring {coloring}\n"
        )
        if nearest_pool_element is not None:
            # Get the coordinates of the nearest element
            nearest_coordinates = __get_element_coordinates(
                xml_output, nearest_pool_element
            )
            # Get the lane of the nearest element
            nearest_y, corresponding_lane = __get_y_coordinates_for_alignment(
                nearest_pool_element, xml_output, lanes
            )
            current_element_coordinates = __get_element_coordinates(xml_output, el_id)
            y_coordinate = (
                current_element_coordinates[1] + corresponding_lane.get_up_left()[1]
            )
            xml_output = __edit_element_coordinates(
                xml_output, el_id, (current_element_coordinates[0], y_coordinate)
            )
            print(
                f"Nearest element {nearest_pool_element} has coordinates {nearest_coordinates} and y-coordinate {nearest_y}"
            )
            corresponding_lane.add_element(el_id)
            aligned_elements.append(el_id)
    return xml_output


def __create_shapes(elements, xml_output: str):
    """This function takes the xml output and returns a list of shapely objects"""
    list_of_shapes = []
    for element in elements:
        # get the coordinates of the element
        element_coordinates = __get_element_coordinates(xml_output, element)
        # create a shapely object
        shape = shapely.box(
            element_coordinates[0],
            element_coordinates[1],
            element_coordinates[0] + element_coordinates[2],
            element_coordinates[1] + element_coordinates[3],
        )

        # add the shape to the plot
        list_of_shapes.append(shape)
    return list_of_shapes


def __change_intermediate_throw_events_to_message_events(root: etree.Element) -> None:
    """
    This function changes all intermediate throw events to message events in the BPMN XML.
    """
    BPMN_NS = root.nsmap.get("bpmn")
    if not BPMN_NS:
        raise ValueError("BPMN namespace not found in the XML root.")

    for event in root.findall(f".//{{{BPMN_NS}}}intermediateThrowEvent"):
        # Should have       <bpmn:messageEventDefinition id="MessageEventDefinition_0soq2t8" /> within it
        # add it at the bottom of the event
        etree.SubElement(
            event,
            f"{{{BPMN_NS}}}messageEventDefinition",
            attrib={"id": f'MessageEventDefinition_{hash(event.get("id"))}'},
        )
    return root


def __add_collaboration(
    root: etree.Element, pools: List[Pool], msg_flows: List[Tuple[str, str, str]]
) -> etree.Element:
    """
    This function restructures a flat BPMN into a collaboration with pools and lanes,
    correctly handling message flows and updating the diagram plane.
    """
    BPMN_NS = root.nsmap.get("bpmn")
    BPMNDI_NS = root.nsmap.get("bpmndi")

    plane = root.find(f".//{{{BPMNDI_NS}}}BPMNPlane")

    if not BPMN_NS or not BPMNDI_NS:
        raise ValueError("BPMN or BPMNDI namespace not found in the XML root.")

    source_process = root.find(f".//{{{BPMN_NS}}}process")
    if source_process is None:
        raise ValueError("No <bpmn:process> element found in the source XML.")

    collaboration = etree.Element(
        f"{{{BPMN_NS}}}collaboration", attrib={"id": "Collaboration_1"}
    )

    # Create a set of message flow IDs for efficient lookup. These are flows
    # that should NOT be treated as sequence flows.
    msg_flow_ids = {flow_data[0] for flow_data in msg_flows}

    element_to_new_process_map = {}
    new_processes = []

    for pool in pools:
        process_id = f"Process_{hash(pool.get_name())}"
        etree.SubElement(
            collaboration,
            f"{{{BPMN_NS}}}participant",
            attrib={
                "id": f"Participant_{process_id}",
                "name": pool.get_name(),
                "processRef": process_id,
            },
        )
        new_process = etree.Element(
            f"{{{BPMN_NS}}}process",
            attrib={"id": process_id, "name": pool.get_name(), "isExecutable": "false"},
        )
        create_visual_shape(
            plane,
            f"Participant_{process_id}",
            [pool.get_up_left(), pool.get_down_right()],
            root,
        )

        laneset = etree.SubElement(new_process, f"{{{BPMN_NS}}}laneSet")

        for lane in pool.get_lanes():
            lane_element = etree.SubElement(
                laneset,
                f"{{{BPMN_NS}}}lane",
                attrib={"id": f"Lane_{hash(lane.get_name())}", "name": lane.get_name()},
            )
            create_visual_shape(
                plane,
                f"Lane_{hash(lane.get_name())}",
                [lane.get_up_left(), lane.get_down_right()],
                root,
            )
            for element_id in lane.get_elements():
                flow_node_ref = etree.SubElement(
                    lane_element, f"{{{BPMN_NS}}}flowNodeRef"
                )
                flow_node_ref.text = element_id
                element_to_new_process_map[element_id] = new_process
        new_processes.append(new_process)

    for element in list(source_process):
        element_id = element.get("id")

        # Check if it's a flow element (Task, Event, Gateway)
        if element_id in element_to_new_process_map:
            destination_process = element_to_new_process_map[element_id]
            destination_process.append(element)

        # Check if it's a flow connector
        elif element.tag == f"{{{BPMN_NS}}}sequenceFlow":
            # If the ID is in our set of message flows, DISCARD IT.
            # It will be recreated as a <messageFlow> later.
            if element_id in msg_flow_ids:
                continue  # Skip and do nothing with this element

            # Otherwise, it's a true sequence flow. Move it to the correct process.
            else:
                source_ref = element.get("sourceRef")
                if source_ref in element_to_new_process_map:
                    destination_process = element_to_new_process_map[source_ref]
                    destination_process.append(element)

    for proc in new_processes:
        root.append(proc)

    print(f"Creating message flows: {msg_flows}")
    for flow_id, source_id, target_id in msg_flows:
        etree.SubElement(
            collaboration,
            f"{{{BPMN_NS}}}messageFlow",
            attrib={"id": flow_id, "sourceRef": source_id, "targetRef": target_id},
        )

    root.append(collaboration)
    root.remove(source_process)

    root = __change_intermediate_throw_events_to_message_events(root)
    # Find the BPMNPlane and make sure it references the collaboration
    plane = root.find(f".//{{{BPMNDI_NS}}}BPMNPlane")
    if plane is not None:
        plane.set("bpmnElement", collaboration.get("id"))

    return root


def build_pools_with_collaboration(
    root: etree._Element, pools: List[Pool], msg_flows: List[Tuple[str, str, str]]
) -> str:
    """
    This function takes the xml output and the pools and returns the xml output with the pools.
    """

    __add_collaboration(root, pools, msg_flows)

    # Return the modified XML as a string
    return _to_string(root)


def create_visual_shape(
    plane: etree.Element,
    logical_id: str,
    coordinates: Tuple[Tuple[int, int], Tuple[int, int]],
    root,
):
    """
    Creates a BPMNShape with its Bounds on the BPMNPlane.

    Args:
        plane: The lxml element for the <bpmndi:BPMNPlane>.
        logical_id: The ID of the <bpmn:participant> or <bpmn:lane> to link to.
        coordinates: A tuple containing ((x1, y1), (x2, y2)) for top-left and bottom-right corners.
        ns: A dictionary of required namespaces ('bpmndi', 'omgdc').
    """
    BPMNDI_NS = root.nsmap.get("bpmndi")
    OMGDC_NS = root.nsmap.get("omgdc")

    top_left, bottom_right = coordinates
    x1, y1 = top_left
    x2, y2 = bottom_right

    bounds_attributes = {
        "x": str(x1),
        "y": str(y1),
        "width": str(x2 - x1),
        "height": str(y2 - y1),
    }

    # Create the <bpmndi:BPMNShape> for the pool or lane
    shape = etree.SubElement(
        plane,
        f"{{{BPMNDI_NS}}}BPMNShape",
        attrib={
            "id": f"{logical_id}_di",  # Standard convention: logical_id + _di
            "bpmnElement": logical_id,
            "isHorizontal": "true",  # Pools and horizontal lanes are marked this way
        },
    )

    # Create the <omgdc:Bounds> element inside the shape
    etree.SubElement(shape, f"{{{OMGDC_NS}}}Bounds", attrib=bounds_attributes)
