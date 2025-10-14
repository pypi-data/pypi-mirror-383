from typing import List, Optional, Dict, Any, Tuple
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from powl.discovery.total_order_based.inductive.cuts.factory import S, T, CutFactory
from powl.discovery.total_order_based.inductive.cuts.loop import POWLLoopCutUVCL
from powl.discovery.total_order_based.inductive.variants.decision_graph.max_decision_graph_cut import \
    MaximalDecisionGraphCutUVCL
from powl.discovery.total_order_based.inductive.variants.dynamic_clustering.dynamic_clustering_partial_order_cut import \
    DynamicClusteringPartialOrderCutUVCL
from powl.objects.obj import POWL
from pm4py.objects.dfg import util as dfu


class CutFactoryPOWLDecisionGraphClustering(CutFactory):

    @classmethod
    def get_cuts(cls, obj, parameters=None):
        return [MaximalDecisionGraphCutUVCL, POWLLoopCutUVCL, DynamicClusteringPartialOrderCutUVCL]

    @classmethod
    def find_cut(cls, obj: IMDataStructure, parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[POWL, List[T]]]:
        alphabet = sorted(dfu.get_vertices(obj.dfg), key=lambda g: g.__str__())
        if len(alphabet) < 2:
            return None
        for c in CutFactoryPOWLDecisionGraphClustering.get_cuts(obj):
            r = c.apply(obj, parameters)
            if r is not None:
                return r
        return None
