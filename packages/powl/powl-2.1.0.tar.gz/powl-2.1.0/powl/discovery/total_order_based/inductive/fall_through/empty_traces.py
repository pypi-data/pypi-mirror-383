from collections import Counter
from multiprocessing import Pool, Manager
from typing import Tuple, List, Optional, Dict, Any
from copy import copy

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL, EmptyTracesDFG
from powl.objects.obj import OperatorPOWL
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.dfg.obj import DFG
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG


class POWLEmptyTracesUVCL(EmptyTracesUVCL):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None,
              parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[OperatorPOWL, List[IMDataStructureUVCL]]]:
        if cls.holds(obj, parameters):
            data_structure = copy(obj.data_structure)
            del data_structure[()]
            return OperatorPOWL(Operator.XOR, []), [IMDataStructureUVCL(Counter()),
                                                        IMDataStructureUVCL(data_structure)]
        else:
            return None


class POWLEmptyTracesDFG(EmptyTracesDFG):
    @classmethod
    def apply(
        cls,
        obj: IMDataStructureDFG,
        pool=None,
        manager=None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tuple[OperatorPOWL, List[IMDataStructureDFG]]]:
        if cls.holds(obj, parameters):
            return OperatorPOWL(Operator.XOR, []), [
                IMDataStructureDFG(InductiveDFG(DFG())),
                IMDataStructureDFG(InductiveDFG(obj.data_structure.dfg)),
            ]
        return None