from abc import ABC
from typing import Generic, Optional, Dict, Any

from powl.discovery.total_order_based.inductive.base_case.abc import BaseCase, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from powl.objects.obj import SilentTransition


class EmptyLogBaseCase(BaseCase[T], ABC, Generic[T]):

    @classmethod
    def leaf(cls, obj=T, parameters: Optional[Dict[str, Any]] = None) -> SilentTransition:
        return SilentTransition()


class EmptyLogBaseCaseUVCL(EmptyLogBaseCase[IMDataStructureUVCL]):

    @classmethod
    def holds(cls, obj=IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return len(obj.data_structure) == 0


class EmptyLogBaseCaseDFG(EmptyLogBaseCase[IMDataStructureDFG]):

    @classmethod
    def holds(
        cls,
        obj=IMDataStructureDFG,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        dfg = obj.dfg
        return (
            len(dfg.graph) == 0
            and len(dfg.start_activities) == 0
            and len(dfg.end_activities) == 0
        )

