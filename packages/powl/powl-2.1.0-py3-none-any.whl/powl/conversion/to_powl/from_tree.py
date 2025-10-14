from powl.objects.obj import POWL, Transition, SilentTransition, OperatorPOWL, StrictPartialOrder, Sequence
from pm4py.objects.process_tree.obj import ProcessTree, Operator as PTOperator


def apply(tree: ProcessTree) -> POWL:

    nodes = []

    for c in tree.children:
        nodes.append(apply(c))

    if tree.operator is None:
        if tree.label is not None:
            powl = Transition(label=tree.label)
        else:
            powl = SilentTransition()
    elif tree.operator == PTOperator.XOR:
        powl = OperatorPOWL(PTOperator.XOR, nodes)
    elif tree.operator == PTOperator.LOOP:
        powl = OperatorPOWL(PTOperator.LOOP, nodes)
    elif tree.operator == PTOperator.PARALLEL:
        powl = StrictPartialOrder(nodes=nodes)
    elif tree.operator == PTOperator.SEQUENCE:
        powl = Sequence(nodes)
    else:
        raise Exception("Unsupported process tree!")

    powl = powl.simplify()

    return powl