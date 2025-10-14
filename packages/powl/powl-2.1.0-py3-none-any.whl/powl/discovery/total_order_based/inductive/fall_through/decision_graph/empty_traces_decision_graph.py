from multiprocessing import Pool, Manager
from typing import Tuple, List, Optional, Dict, Any
from copy import copy

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL, EmptyTracesDFG
from powl.objects.BinaryRelation import BinaryRelation
from powl.objects.obj import DecisionGraph
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG


class POWLEmptyTracesDecisionGraphUVCL(EmptyTracesUVCL):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None,
              parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[DecisionGraph, List[IMDataStructureUVCL]]]:
        if cls.holds(obj, parameters):
            data_structure = copy(obj.data_structure)
            del data_structure[()]
            children = [IMDataStructureUVCL(data_structure)]
            dg = DecisionGraph(BinaryRelation(copy(children)), children, children, empty_path=True)
            return dg, children
        else:
            return None


class POWLEmptyTracesDecisionGraphDFG(EmptyTracesDFG):
    @classmethod
    def apply(
        cls,
        obj: IMDataStructureDFG,
        pool=None,
        manager=None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tuple[DecisionGraph, List[IMDataStructureDFG]]]:
        if cls.holds(obj, parameters):
            children = [IMDataStructureDFG(InductiveDFG(obj.data_structure.dfg))]
            dg = DecisionGraph(BinaryRelation(copy(children)), children, children, empty_path=True)
            return dg, children
        return None
