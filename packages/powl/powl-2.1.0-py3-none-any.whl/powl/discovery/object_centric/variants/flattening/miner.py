from pm4py.objects.ocel.obj import OCEL
from pm4py.algo.discovery.ocel.ocdfg.variants import classic as ocdfg_discovery
from enum import Enum
from pm4py.util import exec_utils
from collections import Counter
from typing import Optional, Dict, Any
from pm4py.algo.conformance.tokenreplay import algorithm as token_based_replay
from pm4py.objects.ocel.util import flattening
from copy import copy
from powl.conversion.converter import apply as powl_converter
from powl.discovery.total_order_based.algorithm import apply as powl_miner
from powl.discovery.total_order_based.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant


class Parameters(Enum):
    POWL_MINER_VARIANT = "powl_miner_variant"
    DOUBLE_ARC_THRESHOLD = "double_arc_threshold"
    DIAGNOSTICS_WITH_TBR = "diagnostics_with_token_based_replay"


def apply(
    ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None
) -> Dict[str, Any]:
    """
    Discovers an object-centric Petri net (without annotation) from the given object-centric event log,
    using the POWL Inductive Miner as process discovery algorithm.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ACTIVITY => the activity attribute to be used
        - Parameters.OBJECT_TYPE => the object type attribute to be used
        - Parameters.DOUBLE_ARC_THRESHOLD => the threshold for the attribution of the "double arc", as
        described in the paper.
        - Parameters.DIAGNOSTICS_WITH_TBR => performs token-based replay and stores the result in the return dict

    Returns
    -----------------
    ocpn
        Object-centric Petri net model, presented as a dictionary of properties:
        - activities: complete set of activities derived from the object-centric event log
        - object_types: complete set of object types derived from the object-centric event log
        - edges: dictionary connecting each object type to a set of directly-followed arcs between activities (expressed as tuples,
                  e.g., (act1, act2)). Every pair of activities is linked to some sets:
                - event_pairs: the tuples of event identifiers where the directly-follows arc occurs
                - total_objects: set of tuples containing two event and one object identifier, uniquely identifying an
                                  occurrence of the arc.
        - activities_indep: dictionary linking each activity, regardless of the object type, to some sets:
            - events: the event identifiers where the activity occurs
            - unique_objects: the object identifiers where the activity occurs
            - total_objects: the tuples of event and object identifiers where the activity occurs.
        - activities_ot: dictionary linking each object type to another dictionary, where the activities are linked to some sets:
            - events: the event identifiers where the activity occurs (with at least one object of the given object type)
            - unique_objects: the object identifiers of the given object type where the activity occurs
            - total_objects: the tuples of event and object identifiers where the activity occurs.
        - start_activities: dictionary linking each object type to another dictionary, where the start activities
                            of the given object type are linked to some sets:
            - events: the event identifiers where the start activity occurs (with at least one object of the given object type)
            - unique_objects: the object identifiers of the given object type where the start activity occurs
            - total_objects: the tuples of event and object identifiers where the start activity occurs.
        - end_activities: dictionary linking each object type to another dictionary, where the end activities
                          of the given object type are linked to some sets:
            - events: the event identifiers where the end activity occurs (with at least one object of the given object type)
            - unique_objects: the object identifiers of the given object type where the end activity occurs
            - total_objects: the tuples of event and object identifiers where the end activity occurs.
        - petri_nets: the accepted Petri nets (Petri net + initial marking + final marking) discovered by the process discovery algorithm
        - double_arcs_on_activity: dictionary linking each object type to another dictionary, where each arc of the Petri net
                                    is linked to a boolean (True if it is a double arc)
        - tbr_results: the results of the token-based replay operation (if required)
    """
    if parameters is None:
        parameters = {}

    double_arc_threshold = exec_utils.get_param_value(
        Parameters.DOUBLE_ARC_THRESHOLD, parameters, 0.8
    )

    if Parameters.POWL_MINER_VARIANT in parameters:
        powl_miner_variant = parameters[Parameters.POWL_MINER_VARIANT]
    else:
        powl_miner_variant = POWLDiscoveryVariant.MAXIMAL

    diagnostics_with_tbr = exec_utils.get_param_value(
        Parameters.DIAGNOSTICS_WITH_TBR, parameters, False
    )

    ocdfg_parameters = copy(parameters)
    ocdfg_parameters["compute_edges_performance"] = False
    ocpn = ocdfg_discovery.apply(ocel, parameters=ocdfg_parameters)

    petri_nets = {}
    double_arcs_on_activity = {}
    tbr_results = {}

    for ot in ocpn["object_types"]:
        activities_eo = ocpn["activities_ot"]["total_objects"][ot]

        is_activity_double = {}
        for act in activities_eo:
            ev_obj_count = Counter([x[0] for x in activities_eo[act]])
            this_single_amount = 0
            for y in ev_obj_count.values():
                if y == 1:
                    this_single_amount += 1
            this_single_amount = this_single_amount / len(ev_obj_count)

            if this_single_amount <= double_arc_threshold:
                is_activity_double[act] = True
            else:
                is_activity_double[act] = False

        double_arcs_on_activity[ot] = is_activity_double

        im_parameters = copy(parameters)
        # disables the fallthroughs, as computing the model on a myriad of different object types
        # could be really expensive
        im_parameters["disable_fallthroughs"] = True
        # for performance reasons, also disable the strict sequence cut (use
        # the normal sequence cut)
        im_parameters["disable_strict_sequence_cut"] = True

        flat_log = flattening.flatten(ocel, ot, parameters=parameters)

        powl = powl_miner(flat_log, variant=powl_miner_variant)
        petri_net = powl_converter(powl)

        if diagnostics_with_tbr:
            tbr_parameters = copy(parameters)
            tbr_parameters["enable_pltr_fitness"] = True
            tbr_parameters["show_progress_bar"] = False

            (
                replayed_traces,
                place_fitness_per_trace,
                transition_fitness_per_trace,
                notexisting_activities_in_model,
            ) = token_based_replay.apply(
                flat_log,
                petri_net[0],
                petri_net[1],
                petri_net[2],
                parameters=tbr_parameters,
            )
            place_diagnostics = {
                place: {"m": 0, "r": 0, "c": 0, "p": 0}
                for place in place_fitness_per_trace
            }
            trans_count = {trans: 0 for trans in petri_net[0].transitions}
            # computes the missing, remaining, consumed, and produced tokens
            # per place.
            for place, res in place_fitness_per_trace.items():
                place_diagnostics[place]["m"] += res["m"]
                place_diagnostics[place]["r"] += res["r"]
                place_diagnostics[place]["c"] += res["c"]
                place_diagnostics[place]["p"] += res["p"]

            # counts the number of times a transition has been fired during the
            # replay.
            for trace in replayed_traces:
                for trans in trace["activated_transitions"]:
                    trans_count[trans] += 1

            tbr_results[ot] = (place_diagnostics, trans_count)

        petri_nets[ot] = petri_net

    ocpn["petri_nets"] = petri_nets
    ocpn["double_arcs_on_activity"] = double_arcs_on_activity
    ocpn["tbr_results"] = tbr_results

    return ocpn