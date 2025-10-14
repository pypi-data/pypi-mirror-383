from typing import List, Literal
from generalized_geography.common.constants import LOOP, LOSE, WIN
from generalized_geography.types.bipartite import BipartiteNode
from generalized_geography.types.node_types import NodeType, ResolvedNodeType


def resolve_node_type(node_type: NodeType) -> ResolvedNodeType:

    if node_type == LOOP:
        return WIN
    else:
        return node_type


def split_nodes_by_type(type_map: dict) -> tuple[List[BipartiteNode], List[BipartiteNode], List[BipartiteNode]]:
    lose_nodes = [node for node, ntype in type_map.items() if ntype == LOSE]
    win_nodes = [node for node, ntype in type_map.items() if ntype == WIN]
    loop_nodes = [node for node, ntype in type_map.items() if ntype == LOOP]

    return lose_nodes, win_nodes, loop_nodes


def split_nodes_by_resolved_type(type_map: dict) -> tuple[List[BipartiteNode], List[BipartiteNode]]:
    lose_nodes = [node for node, ntype in type_map.items(
    ) if resolve_node_type(ntype) == LOSE]
    win_nodes = [node for node, ntype in type_map.items()
                 if resolve_node_type(ntype) == WIN]

    return lose_nodes, win_nodes


def nodes_in_pos(nodes: List[BipartiteNode], pos: Literal[0, 1]) -> List[BipartiteNode]:
    return [node.name for node in nodes if node.pos == pos]
