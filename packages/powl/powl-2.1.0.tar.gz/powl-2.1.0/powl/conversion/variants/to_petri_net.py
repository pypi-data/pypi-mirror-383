import time
import uuid
from itertools import product

from powl.conversion.utils.pn_reduction import merge_places_connected_with_silent_transition, \
    merge_places_with_identical_preset_or_postset
from powl.objects.obj import Transition, SilentTransition, StrictPartialOrder, OperatorPOWL, FrequentTransition, \
    DecisionGraph

import pm4py.objects.conversion.process_tree.variants.to_petri_net as pt_to_pn
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to, remove_place

from pm4py.objects.petri_net.utils import reduction
from pm4py.objects.process_tree.obj import Operator

REDUCE_IMPLICIT_PLACES = True


def merge_groups(a, b, groups):
    group_a = None
    group_b = None
    for group in groups:
        if a in group:
            group_a = group
        if b in group:
            group_b = group
    groups = [group for group in groups if group != group_a and group != group_b]
    groups.append(group_a.union(group_b))
    return groups


def add_transition_and_arcs(net, transition, p1, p2):
    net.transitions.add(transition)
    add_arc_from_to(p1, transition, net)
    add_arc_from_to(transition, p2, net)


def recursively_add_tree(powl, net, initial_entity_subtree, final_entity_subtree, counts, rec_depth,
                         flatten_frequency_tags, force_add_skip=False):

    if type(initial_entity_subtree) is PetriNet.Transition:
        initial_place = get_new_place(counts)
        net.places.add(initial_place)
        add_arc_from_to(initial_entity_subtree, initial_place, net)
    else:
        initial_place = initial_entity_subtree
    if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Place:
        final_place = final_entity_subtree
    else:
        final_place = get_new_place(counts)
        net.places.add(final_place)
        if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Transition:
            add_arc_from_to(final_place, final_entity_subtree, net)

    if force_add_skip:
        invisible = get_new_hidden_trans(counts, type_trans="skip")
        add_arc_from_to(initial_place, invisible, net)
        add_arc_from_to(invisible, final_place, net)

    if isinstance(powl, Transition):
        if isinstance(powl, SilentTransition):
            petri_trans = get_new_hidden_trans(counts, type_trans="skip")
            add_transition_and_arcs(net, petri_trans, initial_place, final_place)
        elif isinstance(powl, FrequentTransition):
            if flatten_frequency_tags:
                petri_trans = get_transition(counts, powl.activity, powl.activity)
                if powl.skippable:
                    silent_t = get_new_hidden_trans(counts, type_trans="skip")
                    if powl.selfloop:
                        add_transition_and_arcs(net, petri_trans, final_place, initial_place)
                        add_transition_and_arcs(net, silent_t, initial_place, final_place)
                    else:
                        add_transition_and_arcs(net, petri_trans, initial_place, final_place)
                        add_transition_and_arcs(net, silent_t, initial_place, final_place)
                else:
                    if powl.selfloop:
                        silent_t = get_new_hidden_trans(counts, type_trans="skip")
                        add_transition_and_arcs(net, petri_trans, initial_place, final_place)
                        add_transition_and_arcs(net, silent_t, final_place, initial_place)
                    else:
                        add_transition_and_arcs(net, petri_trans, initial_place, final_place)

            else:
                petri_trans = get_transition(counts, powl.label, powl.activity, powl.skippable, powl.selfloop)
                add_transition_and_arcs(net, petri_trans, initial_place, final_place)
        else:
            petri_trans = get_transition(counts, powl.label, powl.label)
            add_transition_and_arcs(net, petri_trans, initial_place, final_place)


    elif isinstance(powl, OperatorPOWL):
        tree_children = powl.children
        if powl.operator == Operator.XOR:
            for subtree in tree_children:
                net, counts, intermediate_place = recursively_add_tree(subtree, net, initial_place,
                                                                       final_place,
                                                                       counts,
                                                                       rec_depth + 1,
                                                                       flatten_frequency_tags)
        elif powl.operator == Operator.LOOP:
            new_initial_place = get_new_place(counts)
            net.places.add(new_initial_place)
            init_loop_trans = get_new_hidden_trans(counts, type_trans="init_loop")
            net.transitions.add(init_loop_trans)
            add_arc_from_to(initial_place, init_loop_trans, net)
            add_arc_from_to(init_loop_trans, new_initial_place, net)
            initial_place = new_initial_place
            loop_trans = get_new_hidden_trans(counts, type_trans="loop")
            net.transitions.add(loop_trans)

            exit_node = SilentTransition()
            do = tree_children[0]
            redo = tree_children[1]

            net, counts, int1 = recursively_add_tree(do, net, initial_place,
                                                     None, counts,
                                                     rec_depth + 1,
                                                     flatten_frequency_tags)
            net, counts, int2 = recursively_add_tree(redo, net, int1,
                                                     None, counts,
                                                     rec_depth + 1,
                                                     flatten_frequency_tags)
            net, counts, int3 = recursively_add_tree(exit_node, net, int1,
                                                     final_place, counts,
                                                     rec_depth + 1,
                                                     flatten_frequency_tags)

            looping_place = int2

            add_arc_from_to(looping_place, loop_trans, net)
            add_arc_from_to(loop_trans, initial_place, net)

    elif isinstance(powl, StrictPartialOrder):
        transitive_reduction = powl.order.get_transitive_reduction()
        tree_children = list(powl.children)
        tau_split = get_new_hidden_trans(counts, type_trans="tauSplit")
        net.transitions.add(tau_split)
        add_arc_from_to(initial_place, tau_split, net)
        tau_join = get_new_hidden_trans(counts, type_trans="tauJoin")
        net.transitions.add(tau_join)
        add_arc_from_to(tau_join, final_place, net)

        init_trans = []
        final_trans = []
        start_nodes = transitive_reduction.get_start_nodes()
        end_nodes = transitive_reduction.get_end_nodes()
        for subtree in tree_children:
            i_trans = get_new_hidden_trans(counts, type_trans="init_par")
            net.transitions.add(i_trans)
            if subtree in start_nodes:
                i_place = get_new_place(counts)
                net.places.add(i_place)
                add_arc_from_to(tau_split, i_place, net)

                add_arc_from_to(i_place, i_trans, net)

            f_trans = get_new_hidden_trans(counts, type_trans="final_par")
            net.transitions.add(f_trans)
            if subtree in end_nodes:
                f_place = get_new_place(counts)
                net.places.add(f_place)
                add_arc_from_to(f_trans, f_place, net)
                add_arc_from_to(f_place, tau_join, net)

            net, counts, intermediate_place = recursively_add_tree(subtree,
                                                                   net,
                                                                   i_trans,
                                                                   f_trans,
                                                                   counts,
                                                                   rec_depth + 1,
                                                                   flatten_frequency_tags)
            init_trans.append(i_trans)
            final_trans.append(f_trans)

        n = range(len(tree_children))
        for i, j in product(n, n):
            if transitive_reduction.is_edge_id(i, j):
                new_place = get_new_place(counts)
                net.places.add(new_place)
                add_arc_from_to(final_trans[i], new_place, net)
                add_arc_from_to(new_place, init_trans[j], net)

    elif isinstance(powl, DecisionGraph):

        real_children = powl.children # without artificial start/end nodes
        all_children = powl.order.nodes

        # create one unique input and one unique output places for each node
        node_to_pre_place = {}
        node_to_post_place = {}
        for child in real_children:
            pre_place = get_new_place(counts)
            post_place = get_new_place(counts)
            net.places.add(pre_place)
            net.places.add(post_place)
            node_to_pre_place[child] = pre_place
            node_to_post_place[child] = post_place
            net, counts, _ = recursively_add_tree(child, net, pre_place,
                                                  post_place, counts, rec_depth + 1,
                                                  flatten_frequency_tags)

        node_to_pre_place[powl.end] = final_place
        node_to_post_place[powl.start] = initial_place

        # Now create a silent transition for each edge
        for s in all_children:
            for t in all_children:
                if powl.order.is_edge(s, t):
                    silent = get_new_hidden_trans(counts)
                    net.transitions.add(silent)
                    add_arc_from_to(node_to_post_place[s], silent, net)
                    add_arc_from_to(silent, node_to_pre_place[t], net)

        return net, counts, final_place

    else:
        raise Exception("Unknown POWL operator!")

    return net, counts, final_place


def apply(powl, parameters=None):
    if parameters and "flatten_frequency_tags" in parameters:
        flatten_frequency_tags = parameters["flatten_frequency_tags"]
    else:
        flatten_frequency_tags = True

    counts = pt_to_pn.Counts()
    net = PetriNet('imdf_net_' + str(time.time()))
    initial_marking = Marking()
    final_marking = Marking()
    source = get_new_place(counts)
    source.name = "source"
    sink = get_new_place(counts)
    sink.name = "sink"
    net.places.add(source)
    net.places.add(sink)
    initial_marking[source] = 1
    final_marking[sink] = 1
    initial_mandatory = True
    final_mandatory = True
    if initial_mandatory:
        initial_place = get_new_place(counts)
        net.places.add(initial_place)
        tau_initial = get_new_hidden_trans(counts, type_trans="tau")
        net.transitions.add(tau_initial)
        add_arc_from_to(source, tau_initial, net)
        add_arc_from_to(tau_initial, initial_place, net)
    else:
        initial_place = source
    if final_mandatory:
        final_place = get_new_place(counts)
        net.places.add(final_place)
        tau_final = get_new_hidden_trans(counts, type_trans="tau")
        net.transitions.add(tau_final)
        add_arc_from_to(final_place, tau_final, net)
        add_arc_from_to(tau_final, sink, net)
    else:
        final_place = sink

    net, counts, last_added_place = recursively_add_tree(powl, net, initial_place, final_place, counts, 0,
                                                         flatten_frequency_tags=flatten_frequency_tags)

    if REDUCE_IMPLICIT_PLACES:

        net = merge_places_with_identical_preset_or_postset(net, source, sink)

        reduction.apply_simple_reduction(net)

        places = list(net.places)
        for place in places:
            if len(place.out_arcs) == 0 and place not in final_marking:
                remove_place(net, place)
            if len(place.in_arcs) == 0 and place not in initial_marking:
                remove_place(net, place)

        net = merge_places_connected_with_silent_transition(net, source, sink)

    return net, initial_marking, final_marking


def get_new_place(counts):
    """
    Create a new place in the Petri net
    """
    counts.inc_places()
    return PetriNet.Place('p_' + str(counts.num_places))


def get_new_hidden_trans(counts, type_trans="unknown"):
    """
    Create a new hidden transition in the Petri net
    """
    counts.inc_no_hidden()
    return PetriNet.Transition(type_trans + '_' + str(counts.num_hidden), None)


def get_transition(counts, label, activity, skippable=False, selfloop=False):
    """
    Create a transitions with the specified label in the Petri net
    """
    counts.inc_no_visible()
    return PetriNet.Transition(str(uuid.uuid4()), label, properties={"activity": activity,
                                                                     "skippable": skippable,
                                                                     "selfloop": selfloop})
