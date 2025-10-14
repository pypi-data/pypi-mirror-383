# Directed Edge/Vertex Geography with Repetitions

from typing import Dict, Hashable, Tuple, NamedTuple
from networkx import DiGraph

from generalized_geography.common.constants import LOSE, WIN


class ClassifyRdgResult(NamedTuple):
    pruned_graph: DiGraph
    type_map: Dict[Hashable, int]


def rdg_classify(graph: DiGraph, inplace: bool = False) -> ClassifyRdgResult:
    if not inplace:
        graph = graph.copy()
    sinks = [node for node, deg in graph.out_degree() if deg == 0]
    type_map = {node: LOSE for node in sinks}
    while sinks:
        node = sinks.pop()
        preds = [pred for pred in graph.predecessors(
            node) if pred not in type_map]
        graph.remove_node(node)
        if type_map[node] == LOSE:
            for pred in preds:
                type_map[pred] = WIN
                sinks.append(pred)
        else:
            for pred in preds:
                if graph.out_degree(pred) == 0:
                    type_map[pred] = LOSE
                    sinks.append(pred)
    return ClassifyRdgResult(pruned_graph=graph, type_map=type_map)


if __name__ == "__main__":
    import networkx as nx
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4)])
    result = rdg_classify(G)
