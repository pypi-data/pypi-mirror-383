from typing import Optional, Tuple, List, TypeVar, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureLog
from powl.discovery.total_order_based.inductive.variants.dynamic_clustering_frequency.factory import \
    CutFactoryPOWLDynamicClusteringFrequency
from powl.discovery.total_order_based.inductive.variants.im_tree import IMBasePOWL
from powl.discovery.total_order_based.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from powl.objects.obj import POWL

T = TypeVar('T', bound=IMDataStructureLog)


class POWLInductiveMinerDynamicClusteringFrequency(IMBasePOWL):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.DYNAMIC_CLUSTERING

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        res = CutFactoryPOWLDynamicClusteringFrequency.find_cut(obj, parameters=parameters)
        return res
