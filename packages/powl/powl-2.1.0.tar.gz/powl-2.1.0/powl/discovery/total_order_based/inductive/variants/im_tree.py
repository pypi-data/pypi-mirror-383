import os
from abc import ABC
from enum import Enum
from itertools import combinations
from typing import Optional, Tuple, List, TypeVar, Generic, Dict, Any, Type

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.variants.imf import IMFParameters
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.objects.dfg.obj import DFG

from powl.objects.obj import POWL, StrictPartialOrder, DecisionGraph, OperatorPOWL, Sequence
from powl.discovery.total_order_based.inductive.fall_through.empty_traces import POWLEmptyTracesUVCL
from powl.discovery.total_order_based.inductive.base_case.factory import BaseCaseFactory
from powl.discovery.total_order_based.inductive.cuts.factory import CutFactory
from powl.discovery.total_order_based.inductive.fall_through.factory import FallThroughFactory
from powl.discovery.total_order_based.inductive.utils.filtering import FILTERING_TYPE, FilteringType, \
    filter_most_frequent_variants, FILTERING_THRESHOLD, filter_most_frequent_variants_with_decreasing_factor
from powl.discovery.total_order_based.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from powl.objects.BinaryRelation import BinaryRelation
from pm4py.objects.process_tree.obj import Operator

from copy import copy


T = TypeVar('T', bound=IMDataStructureUVCL)

class Parameters(Enum):
    MULTIPROCESSING = "multiprocessing"


class IMBasePOWL(ABC, Generic[T]):

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        if parameters is None:
            parameters = {}

        enable_multiprocessing = exec_utils.get_param_value(
            Parameters.MULTIPROCESSING,
            parameters,
            constants.ENABLE_MULTIPROCESSING_DEFAULT,
        )

        if enable_multiprocessing:
            from multiprocessing import Pool, Manager

            self._pool = Pool(os.cpu_count() - 1)
            self._manager = Manager()
            self._manager.support_list = []
        else:
            self._pool = None
            self._manager = None

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.TREE

    def empty_traces_cut(self) -> Type[EmptyTracesUVCL]:
        return POWLEmptyTracesUVCL

    def apply(self, obj: T, parameters: Optional[Dict[str, Any]] = None, second_iteration: bool = False) -> POWL:

        # empty_traces = self.empty_traces_cut().apply(obj, parameters)
        # if empty_traces is not None:
        #     return self._recurse(empty_traces[0], empty_traces[1], parameters)

        noise_threshold = exec_utils.get_param_value(IMFParameters.NOISE_THRESHOLD, parameters, 0.0)

        empty_traces = self.empty_traces_cut().apply(obj, parameters)
        if empty_traces is not None:
            number_original_traces = sum(y for y in obj.data_structure.values())
            number_filtered_traces = sum(y for y in empty_traces[1][-1].data_structure.values())

            if number_original_traces - number_filtered_traces > noise_threshold * number_original_traces:
                return self._recurse(empty_traces[0], empty_traces[1], parameters)
            else:
                obj = empty_traces[1][-1]

        powl = self.apply_base_cases(obj, parameters)
        if powl is not None:
            return powl

        cut = self.find_cut(obj, parameters)
        if cut is not None:
            powl = self._recurse(cut[0], cut[1], parameters=parameters)

        if powl is not None:
            return powl

        if FILTERING_TYPE in parameters.keys():
            filtering_type = parameters[FILTERING_TYPE]
            if filtering_type not in FilteringType:
                raise KeyError("Invalid FILTERING_TYPE: " + str(filtering_type))

            if filtering_type is FilteringType.DFG_FREQUENCY:
                if not second_iteration:
                    noise_threshold = exec_utils.get_param_value(IMFParameters.NOISE_THRESHOLD, parameters, 0.0)
                    filtered_ds = self.__filter_dfg_noise(obj, noise_threshold)
                    tree = self.apply(filtered_ds, parameters=parameters, second_iteration=True)
                    if tree is not None:
                        return tree

            elif filtering_type is FilteringType.DYNAMIC:
                filtered_log = filter_most_frequent_variants(obj.data_structure)
                if len(filtered_log.data_structure) > 0:
                    return self.apply(filtered_log, parameters=parameters)

            elif filtering_type is FilteringType.DECREASING_FACTOR:
                if FILTERING_THRESHOLD in parameters.keys():
                    t = parameters[FILTERING_THRESHOLD]
                    if isinstance(t, float) and 0 <= t < 1:
                        t = [t]
                    if isinstance(t, list):
                        for factor in t:
                            if factor > 0:
                                    filtered_log = filter_most_frequent_variants_with_decreasing_factor(obj.data_structure,                                                                                                decreasing_factor=factor)
                                    if len(filtered_log.data_structure) == 0:
                                        break
                                    elif len(filtered_log.data_structure) < len(obj.data_structure):
                                        return self.apply(filtered_log, parameters=parameters)
                    else:
                        raise KeyError("Invalid filtering threshold!")
            else:
                raise KeyError("Invalid filtering type!")

        ft = self.fall_through(obj, parameters)
        return self._recurse(ft[0], ft[1], parameters=parameters)

    def apply_base_cases(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[POWL]:
        return BaseCaseFactory.apply_base_cases(obj, parameters=parameters)

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        return CutFactory.find_cut(obj, parameters=parameters)

    def fall_through(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Tuple[POWL, List[T]]:
        return FallThroughFactory.fall_through(obj, self._pool, self._manager, parameters=parameters)

    def _recurse(self, powl: POWL, objs: List[T], parameters: Optional[Dict[str, Any]] = None):
        children = [self.apply(obj, parameters=parameters) for obj in objs]
        if isinstance(powl, StrictPartialOrder):
            if isinstance(powl, Sequence):
                return Sequence(children)
            powl_new = StrictPartialOrder(children)
            for i, j in combinations(range(len(powl.children)), 2):
                if powl.order.is_edge_id(i, j):
                    powl_new.order.add_edge(children[i], children[j])
                elif powl.order.is_edge_id(j, i):
                    powl_new.order.add_edge(children[j], children[i])
            return powl_new
        elif isinstance(powl, DecisionGraph):
            new_order = BinaryRelation(children)
            for i, j in combinations(range(len(powl.children)), 2):
                if powl.order.is_edge(objs[i], objs[j]):
                    new_order.add_edge(children[i], children[j])
                elif powl.order.is_edge(objs[j], objs[i]):
                    new_order.add_edge(children[j], children[i])
            start_nodes = [children[i] for i in range(len(powl.children)) if objs[i] in powl.start_nodes]
            end_nodes = [children[i] for i in range(len(powl.children)) if objs[i] in powl.end_nodes]
            empty_path = powl.order.is_edge(powl.start, powl.end)
            return DecisionGraph(new_order, start_nodes, end_nodes, empty_path=empty_path)
        elif isinstance(powl, OperatorPOWL):
            if powl.operator == Operator.LOOP and len(children) > 2:
                new_child = OperatorPOWL(Operator.XOR, children[1:])
                children = [children[0], new_child]
            powl.children.extend(children)
            return powl
        else:
            raise Exception("Unsupported POWL type!")

    def __filter_dfg_noise(self, obj, noise_threshold):
        start_activities = copy(obj.dfg.start_activities)
        end_activities = copy(obj.dfg.end_activities)
        dfg = copy(obj.dfg.graph)
        outgoing_max_occ = {}
        for x, y in dfg.items():
            act = x[0]
            if act not in outgoing_max_occ:
                outgoing_max_occ[act] = y
            else:
                outgoing_max_occ[act] = max(y, outgoing_max_occ[act])
            if act in end_activities:
                outgoing_max_occ[act] = max(outgoing_max_occ[act], end_activities[act])
        dfg_list = sorted([(x, y) for x, y in dfg.items()], key=lambda x: (x[1], x[0]), reverse=True)
        dfg_list = [x for x in dfg_list if x[1] > noise_threshold * outgoing_max_occ[x[0][0]]]
        dfg_list = [x[0] for x in dfg_list]
        # filter the elements in the DFG
        graph = {x: y for x, y in dfg.items() if x in dfg_list}

        dfg = DFG()
        for sa in start_activities:
            dfg.start_activities[sa] = start_activities[sa]
        for ea in end_activities:
            dfg.end_activities[ea] = end_activities[ea]
        for act in graph:
            dfg.graph[act] = graph[act]

        return IMDataStructureUVCL(obj.data_structure, dfg)
