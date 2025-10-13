# Directed Vertex Geography


from typing import Dict, Hashable, List, NamedTuple, Tuple
from networkx import DiGraph, descendants

from generalized_geography.common.constants import WIN
from generalized_geography.solver.rdg import rdg_classify


def remove_loops(graph: DiGraph) -> List[Tuple[Hashable, Hashable]]:
    loop_edges = [(node, node) for node in graph if graph.has_edge(node, node)]
    for node in graph:
        if graph.has_edge(node, node):
            graph.remove_edge(node, node)
    return loop_edges


class ClassifyDvgResult(NamedTuple):
    pruned_graph: DiGraph
    type_map: Dict[Hashable, int]
    loop_edges: List[Tuple[Hashable, Hashable]]


def dvg_classify_fast(graph: DiGraph, inplace: bool = False) -> ClassifyDvgResult:
    if not inplace:
        graph = graph.copy()
    loop_edges = remove_loops(graph)
    result = rdg_classify(graph, inplace=True)

    return ClassifyDvgResult(pruned_graph=graph, type_map=result.type_map, loop_edges=loop_edges)


def dvg_is_win(graph: DiGraph, start_node: Hashable) -> bool:

    graph = graph.copy()
    result = dvg_classify_fast(graph, inplace=True)

    if start_node in result.type_map:
        return result.type_map[start_node] == WIN

    reachable_nodes = descendants(graph, start_node)
    subgraph_view = graph.subgraph(reachable_nodes) | {start_node}
    for succ in graph.successors(start_node):
        subgraph: DiGraph = subgraph_view.copy()
        subgraph.remove_node(start_node)
        if not dvg_is_win(subgraph, succ):
            return True
    return False


def dvg_classify_complete(graph: DiGraph, inplace: bool = False) -> Dict[Hashable, bool]:
    type_map = {}
    if not inplace:
        graph = graph.copy()
    result = dvg_classify_fast(graph, inplace=True)

    for node in graph.nodes:
        if node in result.type_map:
            type_map[node] = result.type_map[node] == WIN
        else:
            type_map[node] = dvg_is_win(graph, node)
    return type_map


if __name__ == "__main__":
    g = DiGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    g.add_edge(2, 4)
    g.add_edge(4, 5)
    g.add_edge(5, 6)
    g.add_edge(6, 4)

    print(dvg_classify_fast(g))
    print(dvg_classify_complete(g))
