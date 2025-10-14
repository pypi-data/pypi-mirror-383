from typing import Optional, TypeVar, Dict, Any, Type

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureDFG
from powl.discovery.total_order_based.inductive.fall_through.empty_traces import POWLEmptyTracesDFG
from powl.discovery.total_order_based.inductive.variants.im_tree import IMBasePOWL
from powl.objects.obj import POWL

T = TypeVar('T', bound=IMDataStructureDFG)


class DFGIMBasePOWL(IMBasePOWL[T]):

    def empty_traces_cut(self) -> Type[POWLEmptyTracesDFG]:
        return POWLEmptyTracesDFG

    def apply(self, obj: T, parameters: Optional[Dict[str, Any]] = None, second_iteration: bool = False) -> POWL:

        empty_traces = self.empty_traces_cut().apply(obj, parameters)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1], parameters)

        powl = self.apply_base_cases(obj, parameters)
        if powl is not None:
            return powl

        cut = self.find_cut(obj, parameters)
        if cut is not None:
            powl = self._recurse(cut[0], cut[1], parameters=parameters)

        if powl is not None:
            return powl

        ft = self.fall_through(obj, parameters)
        return self._recurse(ft[0], ft[1], parameters=parameters)