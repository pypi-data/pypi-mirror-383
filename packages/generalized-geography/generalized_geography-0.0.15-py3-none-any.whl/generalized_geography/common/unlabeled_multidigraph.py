# 엣지 (u, v)의 개수를 "weight" attribute로 표현한 MultiDiGraph

from typing import Optional, Union
from networkx import MultiDiGraph, gn_graph
from networkx.classes.digraph import DiGraph
from networkx.exception import NetworkXError

ATTR_NAME = "num"


def create_weighted_digraph_from_multidigraph(multi_di_graph: MultiDiGraph) -> DiGraph:
    """
    NetworkX의 MultiDiGraph를 입력받아 각 엣지의 multiplicity를 weight로 갖는
    새로운 DiGraph를 반환합니다.

    Args:
        multi_di_graph: 입력 MultiDiGraph 객체.

    Returns:
        각 엣지의 multiplicity를 weight로 갖는 새로운 DiGraph 객체.
    """
    di_graph_with_weight = DiGraph()
    edge_multiplicity = {}

    for u, v in multi_di_graph.edges():
        if (u, v) not in edge_multiplicity:
            edge_multiplicity[(u, v)] = 0
        edge_multiplicity[(u, v)] += 1

    for (u, v), weight in edge_multiplicity.items():
        di_graph_with_weight.add_edge(u, v, **{ATTR_NAME: weight})

    return di_graph_with_weight

# edge가 weight 속성을 갖고 있다면, weight가 그 엣지의 개수를 의미함 그렇지 않으면 엣지의 개수는 1개


class UnlabeledMultiDiGraph(DiGraph):

    def __init__(self, G: Union[DiGraph, MultiDiGraph] = None, ** attr):
        if G and G.is_multigraph():
            G = create_weighted_digraph_from_multidigraph(G)
        super().__init__(G, **attr)

    def get_multiplicity(self, u, v):
        edge_data = self.get_edge_data(u, v)
        if edge_data is not None:
            if ATTR_NAME in edge_data:
                return edge_data[ATTR_NAME]
            else:
                return 1
        else:
            return 0

    def increase_edge(self, u, v, num=1):
        self.add_edge(
            u, v, **{ATTR_NAME: self.get_multiplicity(u, v) + num})

    def increase_edges_from(self, ebunch_to_add):
        for e in ebunch_to_add:
            ne = len(e)
            if ne == 3:
                u, v, num = e
            elif ne == 2:
                u, v = e
                num = 1
            else:
                raise NetworkXError("")
            self.increase_edge(u, v, num)

    def decrease_edge(self, u, v, num=1):

        curr_num = self.get_multiplicity(u, v)
        new_num = curr_num - num
        assert new_num >= 0
        if new_num == 0:
            if curr_num != 0:
                self.remove_edge(u, v)
        else:
            self.add_edge(u, v, **{ATTR_NAME: new_num})

    def decrease_edges_from(self, ebunch):
        for e in ebunch:
            ne = len(e)
            if ne == 3:
                u, v, num = e
            elif ne == 2:
                u, v = e
                num = 1
            else:
                raise NetworkXError("")
            self.decrease_edge(u, v, num)

    def multi_out_degree(self, node):
        return sum([m for _, _, m in self.out_edges(node, data=ATTR_NAME)])

    def multi_in_degree(self, node):
        return sum([m for _, _, m in self.in_edges(node, data=ATTR_NAME)])
