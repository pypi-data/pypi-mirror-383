from typing import Optional, Tuple, List, Dict, Any

from powl.discovery.total_order_based.inductive.variants.brute_force.factory import CutFactoryPOWLBruteForce
from powl.discovery.total_order_based.inductive.variants.im_tree import IMBasePOWL, T
from powl.discovery.total_order_based.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from powl.objects.obj import POWL


class POWLInductiveMinerBruteForce(IMBasePOWL):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.BRUTE_FORCE

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        res = CutFactoryPOWLBruteForce.find_cut(obj, parameters=parameters)
        return res
