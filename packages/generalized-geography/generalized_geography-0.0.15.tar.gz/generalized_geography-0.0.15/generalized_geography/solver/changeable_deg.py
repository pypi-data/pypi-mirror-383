from math import inf
from typing import Dict, Hashable, List, NamedTuple, Tuple
from networkx import DiGraph

from generalized_geography.common.constants import LOOP, LOSE, UNKNOWN, WIN
from generalized_geography.types.bipartite import BipartiteNode
from generalized_geography.types.node_types import NodeType


def get_single_out_edges(graph: DiGraph) -> List[Tuple[Hashable, Hashable]]:
    single_out_edge_nodes = [
        u for u, deg in graph.out_degree() if u.pos == 0 and deg == 1]

    return [(u, v) for u in single_out_edge_nodes for v in graph.successors(u)]


def get_single_in_edges(graph: DiGraph) -> List[Tuple[Hashable, Hashable]]:
    single_in_edge_nodes = [
        v for v, deg in graph.in_degree() if v.pos == 1 and deg == 1]
    return [(u, v) for v in single_in_edge_nodes for u in graph.predecessors(v)]


def get_all_inferior_edges(graph: DiGraph) -> List[Tuple[Hashable, Hashable]]:
    single_out_edges = get_single_out_edges(graph)
    single_in_edges = get_single_in_edges(graph)

    return list(set(single_out_edges) | set(single_in_edges))


def remove_two_cycles(graph: DiGraph, weight_key: str = "num") -> List[Tuple[BipartiteNode, BipartiteNode, int]]:

    inferior_edges = get_all_inferior_edges(graph)
    to_remove = []

    for u, v in inferior_edges:
        if graph.has_edge(v, u):
            m = graph[v][u][weight_key]
            if m < 2:
                continue
            to_remove.append((v, u, m - m % 2))
    counter = {}
    for i in range(len(inferior_edges) - 1):
        start1, end1 = inferior_edges[i]
        for j in range(i + 1, len(inferior_edges)):
            start2, end2 = inferior_edges[j]

            if graph.has_edge(end1, start2) and graph.has_edge(end2, start1):
                num1 = graph[end1][start2][weight_key] - \
                    counter.get((end1, start2), 0)
                num2 = graph[end2][start1][weight_key] - \
                    counter.get((end2, start1), 0)
                if num1 <= 0 or num2 <= 0:
                    continue

                delete_num = min(num1, num2)
                counter[(end1, start2)] = counter.get(
                    (end1, start2), 0) + delete_num
                counter[(end2, start1)] = counter.get(
                    (end2, start1), 0) + delete_num
                to_remove.append((end1, start2, delete_num))
                to_remove.append((end2, start1, delete_num))

    for u, v, m in to_remove:
        if graph[u][v][weight_key] <= m:
            graph.remove_edge(u, v)
        else:
            graph[u][v][weight_key] -= m

    return to_remove


class CdegClassifyFastResult(NamedTuple):
    pruned_graph: DiGraph
    type_map: Dict[BipartiteNode, int]
    two_cycles: List[Tuple[BipartiteNode, BipartiteNode, int]]


def cdeg_classify_fast_once(graph: DiGraph, inplace: bool = False, weight_key: str = "num") -> CdegClassifyFastResult:
    if not inplace:
        graph = graph.copy()
    loop_map = {}
    stack = []
    type_map: Dict[BipartiteNode, NodeType] = {}
    two_cycles = remove_two_cycles(graph, weight_key=weight_key)

    def get_seed_type(node: BipartiteNode) -> NodeType:
        if node.pos == 0:
            if graph.out_degree(node) == 0:
                return LOSE
            else:
                return UNKNOWN
        else:
            outdeg = graph.out_degree(node)
            if outdeg >= 2:
                return UNKNOWN
            elif outdeg == 0:
                return LOSE
            else:
                succ = list(graph.successors(node))[0]
                if graph.out_degree(succ) != 1 or list(graph.successors(succ))[0] != node:
                    return UNKNOWN

                num = graph[node][succ][weight_key]
                if num % 2 == 1:
                    loop_map[node] = succ
                    return LOOP

    def set_seeds():
        for node in list(graph.nodes):
            nodeType = get_seed_type(node)
            if nodeType != UNKNOWN:
                type_map[node] = nodeType
                stack.append(node)

    set_seeds()

    while stack:
        node = stack.pop()
        preds = [pred for pred in graph.predecessors(
            node) if pred not in type_map]

        type = type_map[node]
        graph.remove_node(node)
        if node.pos == 0:
            if type == LOSE:
                for pred in preds:
                    type_map[pred] = WIN
                    stack.append(pred)
            else:
                for pred in preds:
                    pred_type = get_seed_type(pred)
                    if pred_type != UNKNOWN:
                        type_map[pred] = pred_type
                        stack.append(pred)
        else:
            if type == LOSE:
                for pred in preds:
                    pred_type = get_seed_type(pred)
                    if pred_type != UNKNOWN:
                        type_map[pred] = LOSE
                        stack.append(pred)
            else:
                for pred in preds:
                    type_map[pred] = type
                    stack.append(pred)
    return CdegClassifyFastResult(graph, type_map, two_cycles)


def cdeg_classify_fast(graph: DiGraph, inplace: bool = False, weight_key: str = "num") -> CdegClassifyFastResult:
    if not inplace:
        graph = graph.copy()

    total_two_cycles = []
    while True:
        result = cdeg_classify_fast_once(
            graph, inplace=True, weight_key=weight_key)
        total_two_cycles.extend(result.two_cycles)
        if len(result.pruned_graph.nodes) == len(graph.nodes):
            break
        graph = result.pruned_graph

    return CdegClassifyFastResult(graph, result.type_map, total_two_cycles)


def make_flow_graph(graph: DiGraph):
    flow_graph = DiGraph()
    for u, v, data in graph.edges(data=True):
        if u.pos == 1:
            capacity = data.get("num", 1)
        else:
            capacity = 999999999999
        flow_graph.add_edge(u, v, capacity=capacity)

    return flow_graph


if __name__ == "__main__":

    with open("dataset/oldict.txt", "r", encoding="UTF-8") as f:
        words = [word.strip() for word in f.read().split("\n")]
