# Directed Edge Geography


from typing import Dict, Hashable, List, NamedTuple, Tuple
from networkx import DiGraph, descendants
from generalized_geography.common.constants import LOOP, LOSE, WIN
from generalized_geography.common.utils import resolve_node_type
from generalized_geography.types.node_types import NodeType


def remove_2_cycles(graph: DiGraph, weight_key: str = "num") -> List[Tuple[Hashable, Hashable]]:
    to_remove = []

    # self loop 짝수 개 검출
    for node in graph:
        if graph.has_edge(node, node):
            m = graph[node][node][weight_key]
            to_remove.append((node, node, m - m % 2))

    # (a,b), (b,a) 꼴 엣지 검출
    for u, v in [(u, v) for u, v in graph.edges if u > v]:
        if graph.has_edge(v, u):
            delete_num = min(graph[u][v][weight_key],
                             graph[v][u][weight_key])
            to_remove.extend([(u, v, delete_num), (v, u, delete_num)])

    for u, v, m in to_remove:
        graph[u][v][weight_key] -= m
        if graph[u][v][weight_key] <= 0:
            graph.remove_edge(u, v)

    return to_remove


class DegClassifyResult(NamedTuple):
    pruned_graph: DiGraph
    type_map: Dict[Hashable, int]
    two_cycle_edges: List[Tuple[Hashable, Hashable]]


def deg_classify_fast(graph: DiGraph, inplace: bool = False, weight_key: str = "num") -> DegClassifyResult:
    if not inplace:
        graph = graph.copy()
    two_cycle_edges = remove_2_cycles(graph, weight_key=weight_key)

    type_map = {}
    sinks = []
    for node in graph.nodes:
        if graph.out_degree(node) == 0:
            type_map[node] = LOSE
            sinks.append(node)
        elif graph.out_degree(node) == 1 and graph.has_edge(node, node):
            type_map[node] = LOOP
            sinks.append(node)

    while sinks:
        node = sinks.pop()
        preds = list(graph.predecessors(node))
        graph.remove_node(node)
        for pred in preds:
            if pred in type_map:
                continue
            if type_map.get(node) == LOSE:
                type_map[pred] = WIN
                sinks.append(pred)
            else:
                if graph.out_degree(pred) == 0:
                    type_map[pred] = LOSE
                    sinks.append(pred)
                elif graph.out_degree(pred) == 1 and graph.has_edge(pred, pred):
                    type_map[pred] = LOOP
                    sinks.append(pred)

    return DegClassifyResult(pruned_graph=graph, type_map=type_map, two_cycle_edges=two_cycle_edges)


def deg_is_win(graph: DiGraph, start_node: Hashable, weight_key: str = "num") -> bool:
    result = deg_classify_fast(graph, inplace=False, weight_key=weight_key)
    if start_node in result.type_map:
        return resolve_node_type(result.type_map[start_node]) == WIN

    reachable_nodes = descendants(graph, start_node) | {start_node}
    subgraph_view = graph.subgraph(reachable_nodes)

    for succ in list(subgraph_view.successors(start_node)):
        subgraph = subgraph_view.copy()
        subgraph[start_node][succ][weight_key] -= 1
        if subgraph[start_node][succ][weight_key] <= 0:
            subgraph.remove_edge(start_node, succ)

        if not deg_is_win(subgraph, succ, weight_key=weight_key):
            return True

    return False


def deg_classify_complete(graph: DiGraph, inplace: bool = False, weight_key: str = "num") -> Dict[Hashable, NodeType]:
    if not inplace:
        graph_copy = graph.copy()

    result = deg_classify_fast(graph_copy, inplace=True, weight_key=weight_key)

    type_map = {}

    for node in graph.nodes:
        if node in type_map:
            type_map[node] = resolve_node_type(result.type_map[node])
        else:
            type_map[node] = WIN if deg_is_win(
                graph, node, weight_key=weight_key) else LOSE

    return type_map


if __name__ == "__main__":
    pass
